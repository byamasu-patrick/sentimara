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
    "treatment_patterns": """
        This table captures data on treatment modalities for Primary Immunodeficiency (PI) patients. \
        Each record links to a respondent providing detailed information on treatment types, patient counts, and geographic locations.

        Key Columns:

        patients_followed: Number of PI patients under follow-up.
        patients_with_pi_defect: Patients diagnosed with a PI defect.
        Immunoglobulin Therapy (IgG): Columns tracking patients receiving different types of IgG treatments (ivig_clinic, ivig_home, scig, other).
        Gene Therapy: Data on patients treated with gene therapy.
        Transplantation: Details on patients treated by stem cell transplant, with donor types (mrd, mud, haplo) and stem cell sources (bm, pbsc, cord, other).
        Geographic Information: Includes region, country_name, locality, and broader world regions.
        Query Usage:

        Geographical Analysis: Aggregate patient counts across regions or countries using region, locality, and country_name.
        Treatment Breakdown: Analyze trends in different treatment methods, such as IgG therapy or transplantation, using columns like patients_receiving_ig_g_ivig_clinic or patients_treated_by_transplant_donor_type_mrd.
        Respondent Details: Retrieve the name or organization of the respondent using respondent_name and organization.
        Cross-Reference with Defects: Combine this table with defect-related tables for more detailed analysis of treatment effectiveness per defect.
        This table allows queries for treatment patterns and their geographical distribution, supporting deep analysis of PI patient management across different regions and therapy types.
    """,
    "completed_survey": """
        This table captures data about respondents who have completed the survey, including the year of the survey and whether the survey was marked as complete. It also contains information about the respondents' geographic and organizational details.

        Key Columns:

        is_completed: A boolean indicating whether the respondent completed the survey.
        survey_year: Year the survey was conducted.
        Respondent Data: Columns like respondent_name and organization link the record to the respondent.
        Geographic Data: Location-based data such as locality, region, country_name, and world_region_name.
        Query Usage:

        Completion Rate: Analyze the number of completed surveys across different regions and years.
        Respondent Breakdown: Retrieve information about survey completion status for respondents by region or organization.
    """,
    "net_promoter_scores": """
        This table captures feedback provided by respondents about the platform after completing the survey. It includes the respondent's net promoter score (NPS), comments, \
        and related geographic details.

        Key Columns:

        score: The NPS score given by the respondent (typically ranging from 0 to 10).
        comments: Feedback or comments left by the respondent.
        is_survey_complete: Indicates whether the survey was completed when the score was submitted.
        Respondent Data: Details like respondent_name and organization link the NPS record to the respondent.
        Geographic Data: Location information such as locality, region, and country_name.
        Query Usage:

        NPS Analysis: Retrieve NPS scores by region, survey year, or respondent organization.
        Feedback Insights: Extract comments and perform sentiment analysis based on geographic and organizational data.
    """,
    "colleagues": """
        This table captures data about colleagues who did not directly participate in the Physician Survey, but for whom information was provided by \
        the main respondent. It holds identifying details of the colleagues and links them to specific geographic and organizational data.

        Key Columns:

        given_name, family_name: First and last names of the colleague.
        email: Contact information for the colleague.
        Respondent Data: Columns like respondent_name and organization link the colleague to the respondent who provided the information.
        Geographic Data: locality, region, country_name, world_region_name, and world_sub_region_name provide location data associated with the colleague.
        Query Usage:

        Colleague Information: Retrieve colleague names and contact details, alongside geographic context.
        Geographic Analysis: Analyze location trends by cross-referencing region, country_name, and world region columns with colleague data.
    """,
    "proxy_respondents": """
        This table stores data about proxy respondents who completed the Physician Survey on behalf of other physicians. \
        Proxy respondents' personal and organizational information is captured.

        Key Columns:

        given_name, family_name: First and last names of the proxy respondent.
        email: Contact information for the proxy respondent.
        Respondent Data: respondent_name links to the main survey respondent for whom the proxy was acting.
        Geographic Data: Columns like locality, region, country_name, and world_region_name provide the proxy respondent's geographic information.
        Query Usage:

        Proxy Respondent Data: Retrieve proxy respondent details and organization affiliations.
        Regional Proxy Analysis: Perform queries based on geographic location to analyze the distribution of proxy respondents across different regions.
    """,
    "demographics": """
        This table stores demographic information for patients with Primary Immunodeficiency (PI), including age groups, gender distribution, \
        and geographic location data provided by survey respondents.

        Key Columns:

        age_count: Total number of patients in the given age group.
        gender_male_count: Count of male patients.
        gender_female_count: Count of female patients.
        patient_age: Describes the age group of the patients (e.g., "0-5", "6-10", etc.).
        Respondent and Geographic Data: Columns like respondent_name, organization, locality, region, country_name, world_region_name, and world_sub_region_name capture where the data originates and from which country or region.
        Query Usage:

        Patient Age Distribution: Use patient_age and age_count to analyze the distribution of patients across different age groups.
        Gender-Based Analysis: Leverage gender_male_count and gender_female_count to assess gender distribution among patients, per age group or region.
        Regional Demographics: Combine columns like region, country_name, and locality with demographic data to understand patient demographics by geography.
        Respondent Data: Retrieve demographic data specific to individual respondents using respondent_name and organization.
        This table allows for queries on age and gender demographics of PI patients, along with geographic insights to better understand population distribution across regions.
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


class TreatmentPattern(Base):
    __tablename__ = "treatment_patterns"

    id = Column(Integer, primary_key=True)
    survey_year = Column(String(255))
    patients_followed = Column(Integer)
    patients_with_pi_defect = Column(Integer)
    patients_receiving_ig_g_ivig_clinic = Column(Integer)
    patients_receiving_ig_g_ivig_home = Column(Integer)
    patients_receiving_ig_g_scig = Column(Integer)
    patients_receiving_ig_g_other = Column(Integer)
    patients_treated_with_gene_therapy = Column(Integer)
    patients_treated_with_peg_ada = Column(Integer)
    patients_treated_by_transplant_donor_type_mrd = Column(Integer)
    patients_treated_by_transplant_donor_type_mud = Column(Integer)
    patients_treated_by_transplant_donor_type_m_mud = Column(Integer)
    patients_treated_by_transplant_donor_type_haplo = Column(Integer)
    patients_treated_by_transplant_stem_cell_src_bm = Column(Integer)
    patients_treated_by_transplant_stem_cell_src_pbsc = Column(Integer)
    patients_treated_by_transplant_stem_cell_src_cord = Column(Integer)
    patients_treated_by_transplant_stem_cell_src_other_name = Column(String(255))
    patients_treated_by_transplant_stem_cell_src_other_count = Column(Integer)
    created_at = Column(Text)
    updated_at = Column(Text)
    published_at = Column(Text)
    patients_diagnosed_through_jeffrey_insights_program = Column(Integer)
    respondent_name = Column(Text)
    organization = Column(Text)
    locality = Column(Text)
    region = Column(Text)
    country_name = Column(String)
    country_alternate_name = Column(String)
    world_region_name = Column(String(255), nullable=True)
    world_region_alternate_name = Column(String(255), nullable=True)
    world_sub_region_name = Column(String(255), nullable=True)
    world_sub_region_alternate_name = Column(String(255), nullable=True)


class CompletedSurvey(Base):
    __tablename__ = "completed_survey"

    id = Column(Integer, primary_key=True)
    survey_year = Column(String(255))
    is_completed = Column(Boolean)
    created_at = Column(DateTime)
    updated_at = Column(DateTime)
    published_at = Column(DateTime)
    respondent_name = Column(Text)
    organization = Column(Text)
    locality = Column(Text)
    region = Column(Text)
    country_name = Column(String)
    country_alternate_name = Column(String)
    world_region_name = Column(String(255), nullable=True)
    world_region_alternate_name = Column(String(255), nullable=True)
    world_sub_region_name = Column(String(255), nullable=True)
    world_sub_region_alternate_name = Column(String(255), nullable=True)


class Demographic(Base):
    __tablename__ = "demographics"

    id = Column(Integer, primary_key=True)
    created_at = Column(DateTime)
    updated_at = Column(DateTime)
    published_at = Column(DateTime)
    survey_year = Column(String(255))
    age_count = Column(Integer)
    gender_male_count = Column(Integer)
    gender_female_count = Column(Integer)
    patient_age = Column(String(255))
    respondent_name = Column(Text)
    organization = Column(Text)
    locality = Column(Text)
    region = Column(Text)
    country_name = Column(String)
    country_alternate_name = Column(String)
    world_region_name = Column(String(255), nullable=True)
    world_region_alternate_name = Column(String(255), nullable=True)
    world_sub_region_name = Column(String(255), nullable=True)
    world_sub_region_alternate_name = Column(String(255), nullable=True)


class Colleagues(Base):
    __tablename__ = "colleagues"

    id = Column(Integer, primary_key=True)
    given_name = Column(String(255))
    family_name = Column(String(255))
    email = Column(String(255))
    created_at = Column(DateTime)
    updated_at = Column(DateTime)
    published_at = Column(DateTime)
    respondent_name = Column(Text)
    organization = Column(Text)
    locality = Column(Text)
    region = Column(Text)
    country_name = Column(String)
    country_alternate_name = Column(String)
    world_region_name = Column(String(255), nullable=True)
    world_region_alternate_name = Column(String(255), nullable=True)
    world_sub_region_name = Column(String(255), nullable=True)
    world_sub_region_alternate_name = Column(String(255), nullable=True)


class ProxyRespondent(Base):
    __tablename__ = "proxy_respondents"

    id = Column(Integer, primary_key=True)
    given_name = Column(String(255))
    family_name = Column(String(255))
    email = Column(String(255))
    created_at = Column(DateTime)
    updated_at = Column(DateTime)
    published_at = Column(DateTime)
    respondent_name = Column(Text)
    organization = Column(Text)
    locality = Column(Text)
    region = Column(Text)
    country_name = Column(String)
    country_alternate_name = Column(String)
    world_region_name = Column(String(255), nullable=True)
    world_region_alternate_name = Column(String(255), nullable=True)
    world_sub_region_name = Column(String(255), nullable=True)
    world_sub_region_alternate_name = Column(String(255), nullable=True)


class NetPromoterScore(Base):
    __tablename__ = "net_promoter_scores"

    id = Column(Integer, primary_key=True)
    score = Column(Integer)
    survey_year = Column(String(255))
    is_survey_complete = Column(Boolean)
    comments = Column(Text)
    created_at = Column(DateTime)
    updated_at = Column(DateTime)
    published_at = Column(DateTime)
    respondent_name = Column(Text)
    organization = Column(Text)
    locality = Column(Text)
    region = Column(Text)
    country_name = Column(String)
    country_alternate_name = Column(String)
    world_region_name = Column(String(255), nullable=True)
    world_region_alternate_name = Column(String(255), nullable=True)
    world_sub_region_name = Column(String(255), nullable=True)
    world_sub_region_alternate_name = Column(String(255), nullable=True)


def init_db():
    # Create the table
    Base.metadata.create_all(non_async_engine)


# class SurveyProgress(Base):
#     __tablename__ = 'progresses'

#     id = Column(Integer, primary_key=True)
#     is_complete = Column(Boolean)
#     created_at = Column(String)
#     updated_at = Column(String)
#     published_at = Column(String)
#     respondent_name = Column(Text)
#     organization = Column(Text)
#     locality = Column(Text)
#   #  region = Column(Text)
#     table_description = Column(Text)
#     category_name = Column(Text)
#     country_name = Column(Text)
#     country_alternate_name = Column(String)
#     world_region_name = Column(String(255), nullable=True)
#     world_region_alternate_name = Column(String(255), nullable=True)
#     world_sub_region_name = Column(String(255), nullable=True)
#     world_sub_region_alternate_name = Column(String(255), nullable=True)
#     # world_intermediate_region_name = Column(String(255), nullable=True)
#     # world_intermediate_region_alternate_name = Column(
#     #     String(255), nullable=True)
#     # # Foreign key reference to PiSurvey2023Table
#     # table_id = Column(Integer, ForeignKey('tables.id'))
#     # # Foreign key reference to SurveyCategory
#     # category_id = Column(Integer, ForeignKey('categories.id'))
#     # # Foreign key reference to PiSurveyRespondent
#     # respondent_id = Column(Integer, ForeignKey('respondents.id'))


# class OtherUnclassifiedDiseases(Base):
#     __tablename__ = 'other_unclassified_diseases'

#     id = Column(Integer, primary_key=True)
#     disease_name = Column(String(255))
#     gene_defect = Column(String(255))
#     gene_mutations = Column(String(255))
#     number_of_patients = Column(Integer)
#     survey_year = Column(String(255))
#     created_at = Column(DateTime)
#     updated_at = Column(DateTime)
#     published_at = Column(DateTime)
#     respondent_name = Column(Text)
#     organization = Column(Text)
#     country = Column(Text)
#     locality = Column(Text)
# #     region = Column(Text)
#     # respondent_id = Column(Integer, ForeignKey('respondents.id'))


# class OtherClassifiedDiseases(Base):
#     __tablename__ = 'other_classified_diseases'

#     id = Column(Integer, primary_key=True)
#     created_at = Column(DateTime)
#     updated_at = Column(DateTime)
#     published_at = Column(DateTime)
#     disease_name = Column(String(255))
#     gene_defect = Column(String(255))
#     gene_mutations = Column(Text)
#     number_of_patients = Column(Integer)
#     respondent_name = Column(Text)
#     organization = Column(Text)
#     country = Column(Text)
#     locality = Column(Text)
#  #   region = Column(Text)
#     category_name = Column(Text)
#     # respondent_id = Column(Integer, ForeignKey('respondents.id'))
#     # category_id = Column(
#     #     Integer, ForeignKey('categories.id'))

# class RespondentLogin(Base):
#     __tablename__ = 'respondent_logins'

#     id = Column(Integer, primary_key=True)
#     ip_address = Column(String(255))
#     created_at = Column(DateTime)
#     updated_at = Column(DateTime)
#     published_at = Column(DateTime)
#     user_agent = Column(String(255))
#     browser_name = Column(String(255))
#     browser_version = Column(String(255))
#     operating_system = Column(String(255))
#     operating_system_version = Column(String(255))
#     screen_resolution = Column(String(255))
#     language = Column(String(255))
#     respondent_name = Column(Text)
#     organization = Column(Text)
#     locality = Column(Text)
#     # region = Column(Text)
#     country_name = Column(String)
#     country_alternate_name = Column(String)
#     world_region_name = Column(String(255), nullable=True)
#     world_region_alternate_name = Column(String(255), nullable=True)
#     world_sub_region_name = Column(String(255), nullable=True)
#     world_sub_region_alternate_name = Column(String(255), nullable=True)
