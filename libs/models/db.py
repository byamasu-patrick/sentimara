import os

from dotenv import load_dotenv
from sqlalchemy import Boolean, Column, DateTime, Integer, String, Text
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime
import uuid
from sqlalchemy.dialects.postgresql import UUID, Numeric
from sqlalchemy.orm import relationship
from sqlalchemy import ForeignKey

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



class Client(Base):
    __tablename__ = "clients"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Personal Details
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    date_of_birth = Column(DateTime, nullable=False)
    email = Column(String(255), unique=True)
    phone = Column(String(20))
    
    # Identification
    id_type = Column(String(50), nullable=False)
    id_number = Column(String(50), nullable=False, unique=True)
    
    # Address
    street_address = Column(String(255))
    city = Column(String(100))
    state = Column(String(100))
    postal_code = Column(String(20))
    country = Column(String(100))
    
    # Income
    annual_income = Column(Numeric(15, 2))
    income_currency = Column(String(3))
    
    # Nationality
    nationality = Column(String(100))
    
    # Relationship
    transactions = relationship("Transaction", back_populates="client")


class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    transaction_number = Column(String(50), unique=True, nullable=False)
    client_id = Column(UUID(as_uuid=True), ForeignKey('clients.id'), nullable=False)
    transaction_type = Column(String(50), unique=True, nullable=False)
    amount = Column(Numeric(15, 2), nullable=False)
    currency = Column(String(3), nullable=False)  # ISO currency code
    transaction_date = Column(DateTime, default=datetime.utcnow, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationship
    client = relationship("Client", back_populates="transactions")