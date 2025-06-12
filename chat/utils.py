"""
This module contains definitions and initializations for a list of tables and table groups 
used in a survey analysis context. It includes detailed descriptions for each table in the 
form of TableInfo objects, which provide insights into the purpose and usage of each table.

query_engine_description: Provides a detailed explanation of how each table's data is analyzed and interpreted by the AI. It describes the specific attributes and types of data contained in each table and how this data contributes to the overall survey analysis. These descriptions guide the AI in understanding the content and significance of each table.

top_query_engine_description: Offers a high-level overview of each table's analytical focus. It summarizes the key functionalities of the AI concerning each table, highlighting the primary insights and outcomes the AI can derive from the data.

In the context of the AI integration, these descriptions are crucial as they instruct the AI on how to utilize each table's data effectively. They align with the overarching goal of providing insights into Primary Immunodeficiencies and related medical data, as indicated in the SYSTEM_MESSAGE. The detailed and top-level descriptions ensure the AI can appropriately interpret and respond to queries by leveraging the specific data and insights each table offers.
"""

from typing import List
from schema import TableInfo
from inspect import signature
from pydantic import BaseModel, create_model
from pydantic.fields import FieldInfo
from typing import Any, Awaitable, Optional, Callable, Type, List, Tuple, Union, cast

from llama_index.core.tools import (
    FunctionTool,
    ToolOutput,
    ToolMetadata,
)
from llama_index.core.workflow import (
    Context,
)

AsyncCallable = Callable[..., Awaitable[Any]]

tables_list = [
    "respondents",
    "treatment_patterns",
    "proxy_respondents",
    "colleagues",
    "demographics",
    "completed_survey",
    "net_promoter_scores",
]

responses_table_name_="responses"

responses_table_query_engine_description="""
This engine specializes in complex analysis of survey responses. It processes patients_reported, and hierarchical disease classifications \
(defect, category, sub_category). The engine excels in genetic correlation studies using omim_entry_id and gene_name, \
analyzing inheritance patterns, and geographical distribution patterns across multiple granularities (locality to world_sub_region_name). \
It can perform: time-series analysis of patient reported, disease prevalence calculations, genetic-demographic correlations, geographical clustering analysis,\
and organizational contribution assessments. Advanced capabilities include trend analysis across world regions, inheritance pattern distribution studies, \
and multi-level categorical aggregations. The engine supports complex joins with demographic and treatment tables for comprehensive patient insights.

This engine can also be used to provide insights on how to prioritize investments based on most occuring PI defect across different regions or globally based on the number of patient reported.

N.B: Never use Primary Immunodeficiency (PI) as a category during aggregation.
    
# Note: When querying for CVID and/or other diseases/defects consider using survey "responses" table to get any relevant data \
which can be aggregated based on world regions or disease categories or sub-categories
"""

top_responses_query_engine_description="""
Expert system for comprehensive immunological survey analysis, specializing in patient reporting patterns, genetic-disease correlations, \
and global geographical distribution of Primary Immunodeficiencies. Handles complex queries across clinical categories, \
genetic markers (OMIM/gene data), inheritance patterns, and multi-level geographical hierarchies. Ideal for analyzing disease prevalence, \
geographical patterns, and organizational reporting trends. \
Supports advanced statistical analysis and temporal trending of patient data across various categories and subcategories.
"""



def create_schema_from_function(
    name: str,
    func: Union[Callable[..., Any], Callable[..., Awaitable[Any]]],
    additional_fields: Optional[
        List[Union[Tuple[str, Type, Any], Tuple[str, Type]]]
    ] = None,
) -> Type[BaseModel]:
    """Create schema from function."""
    fields = {}
    params = signature(func).parameters
    for param_name in params:
        # TODO: Very hacky way to remove the ctx parameter from the signature
        if param_name == "ctx":
            continue

        param_type = params[param_name].annotation
        param_default = params[param_name].default

        if param_type is params[param_name].empty:
            param_type = Any

        if param_default is params[param_name].empty:
            # Required field
            fields[param_name] = (param_type, FieldInfo())
        elif isinstance(param_default, FieldInfo):
            # Field with pydantic.Field as default value
            fields[param_name] = (param_type, param_default)
        else:
            fields[param_name] = (param_type, FieldInfo(default=param_default))

    additional_fields = additional_fields or []
    for field_info in additional_fields:
        if len(field_info) == 3:
            field_info = cast(Tuple[str, Type, Any], field_info)
            field_name, field_type, field_default = field_info
            fields[field_name] = (field_type, FieldInfo(default=field_default))
        elif len(field_info) == 2:
            # Required field has no default value
            field_info = cast(Tuple[str, Type], field_info)
            field_name, field_type = field_info
            fields[field_name] = (field_type, FieldInfo())
        else:
            raise ValueError(
                f"Invalid additional field info: {field_info}. "
                "Must be a tuple of length 2 or 3."
            )

    return create_model(name, **fields)  # type: ignore


class FunctionToolWithContext(FunctionTool):
    """
    A function tool that also includes passing in workflow context.

    Only overrides the call methods to include the context.
    """

    @classmethod
    def from_defaults(
        cls,
        fn: Optional[Callable[..., Any]] = None,
        name: Optional[str] = None,
        description: Optional[str] = None,
        return_direct: bool = False,
        fn_schema: Optional[Type[BaseModel]] = None,
        async_fn: Optional[AsyncCallable] = None,
        tool_metadata: Optional[ToolMetadata] = None,
    ) -> "FunctionTool":
        if tool_metadata is None:
            fn_to_parse = fn or async_fn
            assert fn_to_parse is not None, "fn or async_fn must be provided."
            name = name or fn_to_parse.__name__
            docstring = fn_to_parse.__doc__

            # TODO: Very hacky way to remove the ctx parameter from the signature
            signature_str = str(signature(fn_to_parse))
            signature_str = signature_str.replace(
                "ctx: llama_index.core.workflow.context.Context, ", ""
            )
            description = description or f"{name}{signature_str}\n{docstring}"
            if fn_schema is None:
                fn_schema = create_schema_from_function(
                    f"{name}", fn_to_parse, additional_fields=None
                )
            tool_metadata = ToolMetadata(
                name=name,
                description=description,
                fn_schema=fn_schema,
                return_direct=return_direct,
            )
        return cls(fn=fn, metadata=tool_metadata, async_fn=async_fn)

    def call(self, ctx: Context, *args: Any, **kwargs: Any) -> ToolOutput:
        """Call."""
        tool_output = self._fn(ctx, *args, **kwargs)
        return ToolOutput(
            content=str(tool_output),
            tool_name=self.metadata.name,
            raw_input={"args": args, "kwargs": kwargs},
            raw_output=tool_output,
        )

    async def acall(self, ctx: Context, *args: Any, **kwargs: Any) -> ToolOutput:
        """Call."""
        tool_output = await self._async_fn(ctx, *args, **kwargs)
        return ToolOutput(
            content=str(tool_output),
            tool_name=self.metadata.name,
            raw_input={"args": args, "kwargs": kwargs},
            raw_output=tool_output,
        )


table_groups: List[TableInfo] = [
    TableInfo(
        name="respondents",
        query_engine_description="""
          This engine delves into the 'respondents' table, extracting and interpreting a wide array of data to profile survey participants. \
          It focuses on analyzing attributes such as respondent names, job titles, organizational affiliations, contact details, and geographical information, \
          including locality/city, region/state/province, and country for precise location analysis. \
          The engine excels in uncovering insights into the respondents' professional backgrounds and geographic distribution. \
          It also provides details on contact modalities, offering a nuanced understanding of the diversity and professional networks within the survey data.
        """,
        top_query_engine_description="""
          An advanced engine tailored to the 'respondents' table, designed to analyze participant profiles, 
          encompassing professional backgrounds, contact information, and geographic data. 
          This engine provides a comprehensive snapshot of participant diversity and professional networks.
        """,
    ),
    TableInfo(
        name="completed_survey",
        query_engine_description="""
        This engine focuses on the completed_survey table, which captures data related to respondents who have fully completed the survey. \
        It provides a detailed analysis of survey completion status, including whether a respondent has completed the survey and when they did so. \
        Key temporal attributes such as created_at, updated_at, and published_at are examined to track the timing of survey completions.

        In addition to completion data, the engine assesses respondent demographics (such as respondent names, organizations, and locations), \
        along with geographical information (e.g., locality, region, and country). This analysis provides insights into engagement patterns, survey effectiveness, \
        and the geographical distribution of completed responses, helping identify both temporal and regional trends in survey participation.
        """,
        top_query_engine_description="""
        An engine optimized for analyzing the completed_survey table, this tool is designed to assess completion patterns and respondent demographics. It interprets key temporal data to understand when surveys were completed and evaluates geographical information to offer insights into the distribution of completed surveys. This engine is invaluable for studying respondent engagement and the overall effectiveness of survey design.
        """,
    ),
    TableInfo(
        name="treatment_patterns",
        query_engine_description="""
        Advanced analytics engine for comprehensive treatment pattern analysis in PI cases, specializing in temporal (survey_year) and geographical distribution of \
        treatments. Processes multiple treatment categories: IgG therapies (IVIG clinic/home, SCIG, others), gene therapy, PEG-ADA, and transplantations \
        (MRD, MUD, M-MUD, haplo-identical donors; stem cell sources: BM, PBSC, cord blood). Calculates treatment adoption rates, \
        comparing patients_followed vs patients_with_pi_defect and jeffrey_insights_program diagnoses. Performs trend analysis across years, \
        geographical hierarchies (locality to world_region), and organizations. Enables complex queries for treatment effectiveness, regional variations, \
        and temporal patterns. Supports comparative analysis between treatment modalities, geographical distribution of treatment preferences, 
        and organizational treatment patterns. Handles time-based queries using created_at, updated_at, and published_at timestamps.

        This engine can also be used to provide insights on how to prioritize investments based on various treatment modalities across different regions or globally.
        """,
        top_query_engine_description="""
        Specialized engine for analyzing PI treatment distributions and outcomes across multiple therapy types. Processes patient metrics \
        (followed, diagnosed, program-identified) and diverse treatments (immunoglobulin therapies, gene therapy, transplants with various donor/stem cell types). \
        Excels in geographical treatment pattern analysis, temporal trends, and treatment adoption rates. Supports complex queries comparing treatment modalities, \
        regional variations, and organizational practices. Essential for understanding treatment distribution, effectiveness patterns, \
        and healthcare delivery optimization across different geographical scales.
        
        This engine can also be used to provide insights on how to prioritize investments based on various treatment modalities across different regions or globally.
        """,
    ),
    TableInfo(
        name="demographics",
        query_engine_description="""
        Sophisticated demographic analysis engine specializing in multi-dimensional patient population studies across temporal and geographical dimensions. \
        Processes age-based distributions (patient_age, age_count), gender statistics (gender_male_count, gender_female_count), and hierarchical geographic data \
        (locality to world_sub_region). Performs temporal trend analysis using survey_year and timestamp fields (created_at, updated_at, published_at). \
        Excels in: age-group distribution analysis, gender ratio calculations, geographical demographic clustering, organizational demographic patterns, \
        and longitudinal demographic shifts. Supports complex queries including demographic density mapping, gender distribution across regions, \
        age-group comparisons across organizations, and temporal demographic evolution. Enables cross-regional analysis using alternate naming conventions \
        (country_alternate_name, world_region_alternate_name) for comprehensive global demographic insights.

        This engine can also be used to provide insights on what action can be taken based on various demographic data between make and female but also based on age 
        distribution across different regions or globally.
        """,
        top_query_engine_description="""
        Advanced demographic analysis system for patient population studies, specializing in age distribution patterns, gender statistics, \
        and geographical demographic mapping. Processes temporal trends across survey years, organizational patterns, \
        and multi-level geographical hierarchies. Excels in analyzing demographic variations across regions, age-group distributions, gender ratios, \
        and organizational demographic profiles. Essential for understanding patient population characteristics, regional demographic patterns, \
        and temporal demographic trends in healthcare studies.
        """,
    ),
    TableInfo(
        name="proxy_respondents",
        query_engine_description="""
        Specialized engine for analyzing authorized survey participants who submit data on behalf of primary respondents. \
        Processes delegate relationships through personal identifiers (given_name, family_name, email) and institutional affiliations. \
        Tracks proxy submission patterns across temporal dimensions (created_at, updated_at, published_at) and geographical hierarchies \
        (locality to world_sub_region). Enables analysis of delegation patterns, organizational proxy relationships, \
        and geographical distribution of proxy submissions. Supports complex queries for proxy authorization patterns, \
        institutional representation trends, and cross-regional proxy participation analysis. Essential for understanding survey data submission chains, \
        verifying data providence, and analyzing organizational delegation patterns in multi-participant survey scenarios.
        """,
        top_query_engine_description="""
        Advanced analysis engine for authorized proxy survey participants who actively submit data on behalf of primary respondents. \
        Specializes in tracking delegate relationships, submission patterns, and organizational representations across geographical hierarchies. \
        Essential for understanding proxy participation dynamics, institutional delegation patterns, and data submission authorization chains in survey responses.
        """,
    ),
    TableInfo(
        name="colleagues",
        query_engine_description="""
        Comprehensive analysis engine for tracking referenced healthcare professionals within respondent submissions who don't directly participate in surveys. \
        Processes professional network data through personal identifiers (given_name, family_name, email) and institutional connections. \
        Maps hierarchical professional relationships from individual to organizational levels across geographical dimensions (locality to world_sub_region). \
        Enables analysis of professional networks, institutional collaborations, and regional healthcare provider distributions. \
        Supports queries for understanding respondent-colleague relationships, organizational staff structures, \
        and geographical distribution of healthcare professionals referenced in survey responses.
        """,
        top_query_engine_description="""
        Specialized engine for analyzing referenced healthcare professionals in survey responses who are mentioned by active respondents but don't participate \
        directly. Focuses on mapping professional networks, institutional affiliations, and geographical distribution of referenced colleagues. \
        Essential for understanding the broader healthcare provider landscape and professional relationships within surveyed organizations.
        """,
    ),
    TableInfo(
        name="net_promoter_scores",
        query_engine_description="""
          This engine specializes in the 'net_promoter_scores' table, focusing on analyzing respondent loyalty and satisfaction. \
          It uniquely accesses respondent comments, providing valuable qualitative data alongside numerical scores. \
          This access enables a more nuanced analysis, allowing the engine to interpret not just the scores but also the underlying reasons and \
          sentiments expressed in the comments. Additionally, it examines survey year, completion status, and respondent demographics, \
          offering a comprehensive understanding of satisfaction and loyalty trends across different groups and time periods.
        """,
        top_query_engine_description="""
          A sophisticated tool designed for the 'net_promoter_scores' table, this engine excels in extracting and analyzing respondent comments, \
          providing deeper insights into customer or client satisfaction and loyalty. It skillfully combines the analysis of numerical scores with qualitative data \
          from comments, enabling a multifaceted assessment of satisfaction levels and the underlying reasons. This approach is enhanced by the inclusion of \
          demographic data, offering a comprehensive view of satisfaction trends and loyalty across various groups.
        """,
    ),
]
