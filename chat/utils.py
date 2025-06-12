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

tables_list = [
    "respondents",
    "responses",
    "treatment_patterns",
    "proxy_respondents",
    "colleagues",
    "demographics",
    "completed_survey",
    "net_promoter_scores",
]

table_groups: List[TableInfo] = [
    TableInfo(
        name="respondents",
        query_engine_description="""
          This engine delves into the 'respondents' table, extracting and interpreting a wide array of data to profile survey participants. It focuses on analyzing attributes such as respondent names, job titles, organizational affiliations, contact details, and geographical information, including locality/city, region/state/province, and country for precise location analysis. The engine excels in uncovering insights into the respondents' professional backgrounds and geographic distribution. It also provides details on contact modalities, offering a nuanced understanding of the diversity and professional networks within the survey data.
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
          This engine delves into the 'completed_survey' table, focusing on dissecting survey completion data to glean insights into respondent engagement and 
          survey effectiveness. It analyzes elements such as survey year, completion status, and timestamps of creation, updating, and publication, 
          along with respondent demographics that include names, organizations, and locations. This detailed analysis aids in identifying trends and 
          patterns in survey participation, offering valuable insights into the temporal dynamics of respondent engagement and the geographic spread of participation.
        """,
        top_query_engine_description="""
          An engine specifically designed for the 'completed_survey' table, adept at analyzing survey completion trends and respondent demographics. 
          It evaluates respondent engagement and survey design effectiveness by examining completion rates, temporal patterns, 
          and the geographical distribution of participants.
        """,
    ),
    TableInfo(
        name="responses",
        query_engine_description="""
          This engine expertly navigates the 'responses' table, focusing on a detailed analysis of respondent's responses in surveys. 
          It processes a broad spectrum of data, including numbers of patient reported, specific defects, and categorizations (including sub-categories), 
          along with OMIM entry IDs and gene names related to these defects. Additionally, it analyzes respondent details such as names and organizational affiliations, 
          as well as geographic information. This thorough analysis enables the engine to discern trends, patterns, and emerging themes in responses, 
          especially in the context of patient reports and genetic information. It is instrumental for organizations seeking to understand complex survey outcomes and 
          extract actionable insights from detailed respondent feedback.
        """,
        top_query_engine_description="""
          A specialized tool for in-depth analysis of the 'responses' table, adept at interpreting a wide range of survey data. 
          It skillfully handles information from patient reports and genetic data to respondent demographics. 
          This engine is essential for extracting comprehensive insights from survey results, and for understanding intricate patterns in respondent feedback.
        """,
    ),
    TableInfo(
        name="treatment_patterns",
        query_engine_description="""
          This analytical engine navigates the 'treatment_patterns' table to offer in-depth insights into patient treatment patterns for Primary Immunodeficiency (PI). 
          It analyzes data on the total number of patients followed, those diagnosed with PI defects, those diagnosed through Jeffrey's Insights Genetic Sequencing Program, 
          and the diverse range of treatment approaches. These include immunoglobulin therapies (administered in clinics or at home), gene therapy, enzyme replacement, 
          and various types of transplantations, categorized by donor type and stem cell source. 
          The engine is adept at conducting row counts, comparing values across columns, and tracking changes over time using the 'survey_year' field. 
          It also correlates treatment data with geographical information, such as 'locality', 'region', and 'country_name', enabling multifaceted queries. 
          These range from extracting basic statistics to performing complex comparative analyses of treatment methods and outcomes.
    """,
        top_query_engine_description="""
          The top-level query engine excels in analyzing the 'treatment_patterns' table, adept at addressing queries related to patient numbers under observation, 
          those identified with PI defects, and the treatments administered. It analyzes data on immunoglobulin therapies across various settings, gene therapy, 
          and stem cell transplants, distinguished by donor type and stem cell source. This engine also compares these figures for comprehensive analysis, 
          such as evaluating the proportion of patients diagnosed through the Jeffrey Insights Program against the total number followed. 
          It is instrumental in evaluating treatment effectiveness and reach across demographics and time, thereby enhancing insights into treatment impacts and 
          patient outcomes.
    """,
    ),
    TableInfo(
        name="demographics",
        query_engine_description="""
          This engine specializes in analyzing the 'demographics' table, providing a detailed examination of the demographic distribution of patients covered in the survey. 
          It processes essential data such as age breakdowns, gender counts (male and female), and detailed geographical information, including locality, region, and country. 
          Additionally, it interprets temporal data like survey year, as well as organization and respondent details, offering a nuanced view of demographic trends and patterns within the survey population. The engine's proficiency in dissecting and understanding these demographic facets renders it invaluable for comprehending the diversity and demographic characteristics of the survey population.
        """,
        top_query_engine_description="""
          An engine proficient in demographic analysis, specifically focusing on the 'demographics' table. It excels in extracting and interpreting key demographic data, such as age distributions, gender ratios, and geographic details of patients or respondents. This engine is pivotal in providing a detailed demographic profile, thereby enriching the understanding of the survey population's diversity and characteristics.
        """,
    ),
    TableInfo(
        name="proxy_respondents",
        query_engine_description="""
          This engine delves into the 'proxy_respondents' table to extract and analyze data from individuals representing others in surveys. It focuses on the personal details of these proxies, including given names, family names, and email addresses. Additionally, the engine examines the temporal context of responses, including creation, update, and publication dates, as well as the respondents' affiliations with organizations, localities, regions, and countries. This analysis is pivotal for understanding the perspectives and roles of proxy respondents, particularly in representing patient groups or other entities. The engine's ability to parse this data aids in gaining a comprehensive understanding of representation dynamics in survey responses.
        """,
        top_query_engine_description="""
          An analytical tool specialized for the 'proxy_respondents' table, this engine interprets data from individuals representing others in surveys. It focuses on their personal and organizational details, along with geographic information, to understand their roles as representatives. This engine is crucial in elucidating the contributions and perspectives of proxy respondents across various regions and organizations.
        """,
    ),
    TableInfo(
        name="colleagues",
        query_engine_description="""
          This engine specializes in analyzing the 'colleagues' table, which is rich in data on the professional connections and collaborations of survey respondents. It assesses personal details such as given names, family names, and email addresses, in addition to organizational and geographic information, including organization names, localities, regions, and countries. By examining these data points, the engine maps and interprets the complex web of professional relationships among respondents. It offers valuable insights into networking patterns, collaborative links, and regional and organizational affiliations within the surveyed group. This analysis is vital in understanding the professional dynamics and connectivity within the respondent community.
        """,
        top_query_engine_description="""
            An engine adept at examining the 'colleagues' table, this tool focuses on unraveling the intricate professional networks and collaborations among survey respondents. It analyzes personal, organizational, and geographic details to illuminate the interconnectedness of respondents professionally. This engine plays a crucial role in uncovering the relational dynamics and collaborative structures within the survey community.
        """,
    ),
    TableInfo(
        name="net_promoter_scores",
        query_engine_description="""
          This engine specializes in the 'net_promoter_scores' table, focusing on analyzing respondent loyalty and satisfaction. It uniquely accesses respondent comments, providing valuable qualitative data alongside numerical scores. This access enables a more nuanced analysis, allowing the engine to interpret not just the scores but also the underlying reasons and sentiments expressed in the comments. Additionally, it examines survey year, completion status, and respondent demographics, offering a comprehensive understanding of satisfaction and loyalty trends across different groups and time periods.
        """,
        top_query_engine_description="""
          A sophisticated tool designed for the 'net_promoter_scores' table, this engine excels in extracting and analyzing respondent comments, providing deeper insights into customer or client satisfaction and loyalty. It skillfully combines the analysis of numerical scores with qualitative data from comments, enabling a multifaceted assessment of satisfaction levels and the underlying reasons. This approach is enhanced by the inclusion of demographic data, offering a comprehensive view of satisfaction trends and loyalty across various groups.
        """,
    ),
]
