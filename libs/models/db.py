import os
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
from sqlalchemy import create_engine, Column, Integer, String, Boolean, DateTime, Text
from sqlalchemy.ext.declarative import declarative_base
# relationship

# Define the base class for declarative models
Base = declarative_base()
load_dotenv()
#  Load environment variables
POSTGRES_USER = os.getenv('POSTGRES_USER')
POSTGRES_PASSWORD = os.getenv('POSTGRES_PASSWORD')
POSTGRES_DB = os.getenv('POSTGRES_DB')
POSTGRES_HOST_NAME = os.getenv('POSTGRES_HOST_NAME')
# Define DB connection string
LLM_DATABASE_URL = f'postgresql+psycopg2://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST_NAME}:5432/{POSTGRES_DB}'
# Define the Respondent class representing the table

# table_context_dict: dict[str, Literal] = {
#     "respondents": (
#         """
#             This table stores information about all respondents who participated in the survey.
#             Here locality also mean city. Sometimes the prompt might be to give the progress per each respondent, always refer to
#             respondent_id to access more information about the respondent which a single record on this table is connected to for example (
#             city or locality, respondent name, location, or even country
#             ). Also you can make use of table_id to access the number of table that a particular respondent has completed.
#             For example:

#             Prompt: Give me the progress of 'name of the respondent' or 'email of the respondent'.
#             Thinking: Go fetch this table using the respondent id and where respondent name or email is 'name of the respondent' or 'email of the respondent',
#             and then give back the result of table id count with more details information for each table.
#         """
#     ),
#     "responses": (
#         """
#             This data model archives records pertaining to respondents' submissions on various defects or conditions.
#             The key column for referencing the specific condition or defect is the "defect" column within the responses table.

#             How to Extract Data:

#             Identifying the Defect: Begin by identifying the defect or condition mentioned in the prompt. This is crucial for tailoring the database query.
#             Fetching Relevant Data: With the defect identified, proceed to the responses table. Use the "defect" column to filter results that match the defect in question. This will provide a set of responses relevant to the defect.
#             Summation of Patients: If the goal is to determine the total number of patients reported with a particular defect, sum the values in the patients_reported column for all matching records.
#             Geographical Distribution: For geographical data, reference the country, locality, and region columns. Summarize the data by aggregating the number of patients for each unique geographical location.
#             Additional Details: Other details, such as the respondent's name, organization, or specific location, can be extracted directly from the respective columns in the responses table.

#             In addition to the 'defect' column, you can also use the 'table_description' column within the responses table to reference specific table to which the defects belong. If you don't find a result using the 'defect' column, you have the option to search using the 'table_description' column to retrieve the answer for your specific query.

#             When extracting data based on 'table_description' follow the same steps as described above for extracting data. However, in this case, instead of using 'defect' or 'condition' in your query, you should specify the table description or table name as it is essential for tailoring the database query to your needs.

#             Once you've identified the table, proceed with the next steps. In this scenario, you will utilize the 'table_description' column to filter the results that match the specified table. This process will provide you with a set of responses that are relevant to the chosen table.
#         """
#     ),
#     "progresses": (
#         """
#             This table tracks the progress of the PI survey in 2023, indicating whether the respondent has completed a particular survey table or not.
#         """
#     ),
#     "treatment_patterns": (
#         """
#             This data model captures information about different treatment patterns observed in Primary Immunodeficiency (PI) patients.
#             Access more information about the respondent which a single record on this table is connected to for example (
#             city or locality, respondent name, location, or even country
#             ).
#             For example

#             Prompt: Show me the top 5 regions based on the number of patients followed.

#             thinking: Here you are requested to select this table and get access to the location information like in this case 'region' or 'country', then perform a check on the number of patient followed and get access to
#             the number of patient followed reported by a particular respondent a filter the result by region.

#             The same way of thinking can be applied for other prompts that require a step by step way of thinking.
#         """
#     ),
#     "completed_survey_respondents": (
#         "This data model captures information about the number o people who have completed the survey."
#     ),
#     "respondent_logins": (
#         "This data model captures information about different number of login."
#     ),
#     "net_promoter_scores": (
#         "This data model captures information the feedback the respondent gave after completing the survey."
#     ),
#     "demographics": (
#         "This data model captures data model stores demographic information provided by survey respondents."
#     ),

#     # "other_unclassified_diseases": (
#     #     "This data model captures information about other disease that were not part of the survey, that were not classified in categories"
#     # ),
#     # "other_classified_diseases": (
#     #     "This data model captures information about other  disease that were not part of the survey, that were classified in categories"
#     # ),

#     "colleagues": (
#         """This data model captures information about colleagues who did not participate
#           in the Physician Survey"""
#     ),
#     "proxy_respondents": (
#         """
#             This data model captures information about proxy respondents who participate
#             in the Physician Survey for Primary Immunodeficiencies (PI) on behalf of other users.
#         """
#     )
# }
table_context_dict_2 = {

    "completed_survey": """
        This data model captures information about the number of people who have completed the survey.
    """,
    "net_promoter_scores": """
        This data model captures information about the feedback the respondent gave after completing the survey.
    """,
    "colleagues": """
        This data model captures information about colleagues who did not participate in the Physician Survey.
    """,

    "proxy_respondents": """
        This data model captures information about proxy respondents who participate in the Physician Survey for Primary Immunodeficiencies (PI) on behalf of other users.
    """
}
table_context_dict = {
    "respondents": """
        This table stores information about all respondents who participated in the survey.
        Here locality also means city. Sometimes the prompt might be to give the progress per each respondent; always refer to respondent_id to access more information about the respondent which a single record on this table is connected to, for example (city or locality, respondent name, location, or even country). Also, you can make use of table_id to access the number of tables that a particular respondent has completed. For example:
        Prompt: Give me the progress of 'name of the respondent' or 'email of the respondent'.
        Thinking: Go fetch this table using the respondent id and where respondent name or email is 'name of the respondent' or 'email of the respondent', and then give back the result of table id count with more detailed information for each table.
    """,

    "responses": """
        This data model archives records pertaining to respondents' submissions on various defects or conditions. category field represent the category which a defect belong to, and 
        sub_category represent the sub category to which the defect belongs to, you should take it as an hierarchy relationship where there is a major category and sub category. The sub category belong to a major categories.
        The key column for referencing the specific condition or defect is the "defect" column within the responses table.

        How to Extract Data:

        Identifying the Defect: Begin by identifying the defect or condition mentioned in the prompt. This is crucial for tailoring the database query.
        Fetching Relevant Data: With the defect identified, proceed to the responses table. Use the "defect" column to filter results that match the defect in question. This will provide a set of responses relevant to the defect.
        Summation of Patients: If the goal is to determine the total number of patients reported with a particular defect, sum the values in the patients_reported column for all matching records.
        Geographical Distribution: For geographical data, reference the country, locality, and region columns. Summarize the data by aggregating the number of patients for each unique geographical location.
        Additional Details: Other details, such as the respondent's name, organization, or specific location, can be extracted directly from the respective columns in the responses table.

        In addition to the 'defect' column, you can also use the 'category' and 'sub_category' column within the responses table to reference specific category of sub category to which the defects belong. If you don't find a result using the 'defect' column, you have the option to search using the 'category' or 'sub_category' column to retrieve the answer for your specific query.

    """,

    # "progresses": """
    #     This table tracks the progress of the PI survey in 2023, indicating whether the respondent has completed a particular survey table or not.
    # """,

    "treatment_patterns": """
        This data model captures information about different treatment patterns observed in Primary Immunodeficiency (PI) patients.
        Access more information about the respondent, which a single record on this table is connected to, for example (city or locality, respondent name, location, or even country).
        For example:
        Prompt: Show me the top 5 regions based on the number of patients followed.
        Thinking: Here you are requested to select this table and get access to the location information like in this case 'region' or 'country', then perform a check on the number of patients followed and get access to
        the number of patients followed reported by a particular respondent and filter the result by region.

        The same way of thinking can be applied for other prompts that require a step-by-step way of thinking.
    """,

    "completed_survey": """
        This data model captures information about the number of people who have completed the survey.
    """,
    "net_promoter_scores": """
        This data model captures information about the feedback the respondent gave after completing the survey.
    """,
    "colleagues": """
        This data model captures information about colleagues who did not participate in the Physician Survey.
    """,

    "proxy_respondents": """
        This data model captures information about proxy respondents who participate in the Physician Survey for Primary Immunodeficiencies (PI) on behalf of other users.
    """,
    # "respondent_logins": """
    #     This data model captures information about different numbers of login.
    # """,


    "demographics": """
        This data model stores demographic information provided by survey respondents.
    """,

}


class Respondent(Base):
    __tablename__ = 'respondents'

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
    # world_intermediate_region_name = Column(String(255), nullable=True)
    # world_intermediate_region_alternate_name = Column(
    #     String(255), nullable=True)


class Response(Base):
    __tablename__ = 'responses'

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
    organization = Column(Text)
    locality = Column(Text)
    region = Column(Text)
    country_name = Column(String)
    country_alternate_name = Column(String)
    world_region_name = Column(String(255), nullable=True)
    world_region_alternate_name = Column(String(255), nullable=True)
    world_sub_region_name = Column(String(255), nullable=True)
    world_sub_region_alternate_name = Column(String(255), nullable=True)
    # world_intermediate_region_name = Column(String(255), nullable=True)
    # world_intermediate_region_alternate_name = Column(
    #     String(255), nullable=True)
    # respondent_id = Column(Integer, ForeignKey('respondents.id'))
    # table_id = Column(
    #     Integer, ForeignKey('tables.id'))
    # defect_id = Column(
    #     Integer, ForeignKey('defects.id'))


class TreatmentPattern(Base):
    __tablename__ = 'treatment_patterns'

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
    patients_treated_by_transplant_stem_cell_src_other_name = Column(
        String(255))
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
    # respondent_id = Column(Integer, ForeignKey('respondents.id'))


class CompletedSurvey(Base):
    __tablename__ = 'completed_survey'

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
    # respondent_id = Column(Integer, ForeignKey('respondents.id'))


class Demographic(Base):
    __tablename__ = 'demographics'

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
    # respondent_id = Column(Integer, ForeignKey('respondents.id'))


class Colleagues(Base):
    __tablename__ = 'colleagues'

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
    # respondent_id = Column(Integer, ForeignKey('respondents.id'))


class ProxyRespondent(Base):
    __tablename__ = 'proxy_respondents'

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
    # respondent_id = Column(Integer, ForeignKey('respondents.id'))


# # Create an SQLite in-memory database
engine = create_engine(LLM_DATABASE_URL)


def init_db():
    # Create the table
    Base.metadata.create_all(engine)


# Create a session
Session = sessionmaker(bind=engine)


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
# respondent_id = Column(Integer, ForeignKey('respondents.id'))


class NetPromoterScore(Base):
    __tablename__ = 'net_promoter_scores'

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
    # respondent_id = Column(Integer, ForeignKey('respondents.id'))


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
