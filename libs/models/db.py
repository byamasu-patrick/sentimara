import os

from dotenv import load_dotenv
from sqlalchemy import Boolean, Column, DateTime, Integer, String, Text
from sqlalchemy.ext.declarative import declarative_base

from libs.db.session import non_async_engine

# Define the base class for declarative models
Base = declarative_base()
load_dotenv()

responses_table_name="responses"
responses_table_description="""
    This table contains records of survey responses detailing defects or conditions reported by physicians. \
    Each record relates to a defect, categorized hierarchically by category, sub_category., region and sub_region.

    Key Columns:

    defect: Main identifier of the reported defect or condition.
    category, sub_category: Represent the major and sub-level classifications of the defect.
    patients_reported: The number of patients diagnosed with the defect.
    location-related columns: Data on geographical distribution, including country_name, locality, region, and global region names.
    respondent_name, organization: Information about the physician or organization reporting the data.
    gene_name, inheritance_pattern, omim_entry_id: Genetic markers related to the defect.
    Query Usage:

    Summarize Defects: Use the defect column to retrieve records related to specific defects and analyze patient counts using patients_reported.
    Category-Level Analysis: If defect data is unavailable, queries can target category or sub_category for broader insights.
    Geographical Insights: Aggregate patient counts by region using location-related columns to analyze geographical distribution.
    Advanced Genetics: Filter defects based on genetic data (gene_name, omim_entry_id).
    Respondent Insights: Understand the reporting sources through respondent_name and organization columns.
    This table is ideal for analyzing defect prevalence, geographical patterns, and genetic trends in Primary Immunodeficiencies.
    
    # Note: When querying for CVID and/or other diseases/defects consider using survey "responses" table to get any relevant data \
    which can be aggregated based on world regions or disease categories or sub-categories
    # Example Query Pattern:
        question: Using provided survey data on Primary Immunodeficiency, identify the top three regions of CVID.
        response: To solve this you need to select from responses table where defect has 'cvid' and group by region.
"""

table_context_dict: dict[str, str] = {
    "respondents": """
        This table stores comprehensive information about all individuals who participated in the survey. Each record contains demographic, contact, \
        and organizational details of the respondents, and it links to other tables for survey progress and responses.

        Key Columns:

        respondent_name: The full name of the respondent.
        email: Email address for direct contact.
        locality: The city or locality of the respondent.
        region, country_name: Geographic information.
        job_title, organization: Professional details including the respondent's title and organization.
        is_administrator: Boolean indicating if the respondent holds administrative privileges.
        Query Usage:

        Progress Tracking: Use respondent_id to track the respondent's progress across survey tables by fetching the number of completed tables (table_id count).
        Geographic Analysis: Filter respondents by location details such as region, country_name, or locality for geographic-based analyses.
        Respondent Details: Retrieve detailed information on respondents based on their name or email for progress reporting.
    """,
}


class Respondent(Base):
    __tablename__ = "respondents"

    id = Column(Integer, primary_key=True)
    created_at = Column(DateTime)
    updated_at = Column(DateTime)
    published_at = Column(DateTime)
    respondent_name = Column(String)
    honorific_prefix = Column(String)
    honorific_suffix = Column(String)
    job_title = Column(String)
    organization = Column(String)
    address_formatted = Column(String)
    street_address = Column(String)
    locality = Column(String)
    region = Column(String)
    postal_code = Column(String)
    telephone = Column(String)
    email = Column(String)
    fax_number = Column(String)
    international_dialing_code = Column(String)
    post_office_box_number = Column(String)
    mobile_phone_number = Column(String)
    mobile_international_dialing_code = Column(String)
    fax_international_dialing_code = Column(String)
    full_name = Column(String)
    latitude = Column(String)
    longitude = Column(String)
    is_approved = Column(Boolean)
    is_newsletter_subscriber = Column(Boolean)
    is_administrator = Column(Boolean)
    country_name = Column(String)
    country_alternate_name = Column(String)
    world_region_name = Column(String(255), nullable=True)
    world_region_alternate_name = Column(String(255), nullable=True)
    world_sub_region_name = Column(String(255), nullable=True)
    world_sub_region_alternate_name = Column(String(255), nullable=True)


class Response(Base):
    __tablename__ = "responses"

    id = Column(Integer, primary_key=True, autoincrement=True)
    created_at = Column(Text)
    updated_at = Column(Text)
    patients_reported = Column(Integer)
    defect = Column(Text)
    category = Column(Text)
    sub_category = Column(Text)
    omim_entry_id = Column(Text)
    gene_name = Column(Text)
    inheritance_pattern = Column(Text)
    respondent_name = Column(Text)
    email = Column(Text)
    job_title = Column(Text)
    organization = Column(Text)
    locality = Column(Text)
    region = Column(Text)
    country_name = Column(String)
    country_alternate_name = Column(String)
    world_region_name = Column(String(255), nullable=True)
    world_region_alternate_name = Column(String(255), nullable=True)
    world_sub_region_name = Column(String(255), nullable=True)
    world_sub_region_alternate_name = Column(String(255), nullable=True)

