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
    "clients",
    "transactions",
]


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
        name="clients",
        query_engine_description="""
          This engine explores the 'clients' table, extracting detailed personal, demographic, and financial information about each client. \
          It focuses on analyzing attributes such as name, date of birth, nationality, income, contact details (email, phone), and address \
          (city, state, country). It also interprets identification information like ID type and number. \
          The engine excels at building client profiles for segmentation, verification, and regional or income-based analysis.
        """,
        top_query_engine_description="""
          An advanced engine tailored to the 'clients' table, designed to analyze client demographics, identity verification data, and financial details. \
          It delivers comprehensive insights into client profiles, income levels, and geographic distribution.
        """,
    ),
    TableInfo(
        name="transactions",
        query_engine_description="""
          This engine focuses on the 'transactions' table, analyzing all client-related financial transactions. \
          It interprets attributes such as transaction type, amount, currency, and transaction date, while linking each transaction to the appropriate client via client_id. \
          It supports trend analysis, transactional behavior monitoring, currency usage evaluation, and temporal financial activity reporting.
        """,
        top_query_engine_description="""
          An advanced engine for the 'transactions' table, designed to assess transaction patterns, volumes, types, and currency flows over time. \
          Ideal for financial activity analysis and linking monetary behavior to specific client segments.
        """,
    ),
]