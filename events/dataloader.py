from sqlalchemy import text
from libs.models.db import (
    Respondent,
    Response,
    SurveyProgress,
    TreatmentPattern,
    RespondentLogin,
    CompletedSurveyRespondents,
    NetPromoterScore,
    PatientDemographic
)


def upsert_respondent(pg_session, sqlite_session, id: int) -> None:
    # Define the SQL query using bind parameters to prevent SQL injection
    sql_query = text(
        "SELECT * FROM pi_survey_respondents WHERE id=:respondent_id")

    # Retrieve data from pi_survey_respondents table
    pg_respondents = pg_session.execute(
        sql_query, {'respondent_id': id}).fetchall()

    pg_respondent = pg_respondents[0]
    # Update the record in SQLite
    upsert_into_sqlite_respondent(sqlite_session, pg_respondent)


def upsert_responses(pg_session, sqlite_session, id: int) -> None:
    # Fetch data using the given SQL query
    sql_query = text("""
        SELECT 
            psrs.*,
            psrspstl.pi_survey_2023_table_id  AS table_id,
            psrspsql.pi_survey_question_id AS disease_id,
            psrspsrl.pi_survey_respondent_id AS respondent_id
        FROM pi_survey_responses_2023s psrs 
        JOIN pi_survey_responses_2023_s_pi_survey_2023_table_links psrspstl  ON psrspstl.pi_survey_responses_2023_id  = psrs.id
        JOIN pi_survey_responses_2023_s_pi_survey_question_links psrspsql ON psrspsql.pi_survey_responses_2023_id  = psrs.id 
        JOIN pi_survey_responses_2023_s_pi_survey_respondent_links psrspsrl ON psrspsrl.pi_survey_responses_2023_id  = psrs.id
        WHERE psrs.id=:response_id
    """)
    # Retrieve data from pi_survey_respondents table
    pg_responses = pg_session.execute(
        sql_query, {'response_id': id}).fetchall()

    pg_response = pg_responses[0]

    upsert_into_sqlite_responses(sqlite_session, pg_response)


def upsert_into_sqlite_responses(session, pg_response):
    response = session.query(Response).filter_by(id=pg_response.id).first()

    if response:
        response.created_at = pg_response.created_at
        response.updated_at = pg_response.updated_at
        response.published_at = pg_response.published_at
        response.is_quantitative = pg_response.is_survey_answer_quantitative
        response.patients_reported = int(pg_response.survey_answer)
        # Commit the changes
        session.commit()
        print(f"Response {pg_response.id} updated successfully!")
    else:
        print(f"Response with ID {pg_response.id} not found!")
        new_response = Response(
            id=pg_response.id,
            created_at=pg_response.created_at,
            updated_at=pg_response.updated_at,
            published_at=pg_response.published_at,
            is_quantitative=pg_response.is_survey_answer_quantitative,
            patients_reported=int(pg_response.survey_answer),
            defect_id=pg_response.disease_id,
            table_id=pg_response.table_id,
            respondent_id=pg_response.respondent_id
        )
        session.add(new_response)
        session.commit()
        print(f"Response {pg_response.id} added successfully!")


def upsert_into_sqlite_respondent(session, data):

    respondent = session.query(Respondent).filter_by(id=data.id).first()

    if respondent:
        # Update existing record attributes
        respondent.created_at = data.created_at
        respondent.updated_at = data.updated_at
        respondent.published_at = data.published_at
        respondent.given_name = data.given_name
        respondent.additional_name = data.additional_name
        respondent.family_name = data.family_name
        respondent.honorific_prefix = data.honorific_prefix
        respondent.honorific_suffix = data.honorific_suffix
        respondent.job_title = data.job_title
        respondent.organization = data.organization
        respondent.country = data.address_country
        respondent.country_code = data.address_country_code
        respondent.address_formatted = data.address_formatted
        respondent.street_address = data.street_address
        respondent.locality = data.address_locality
        respondent.region = data.address_region
        respondent.postal_code = data.postal_code
        respondent.telephone = data.telephone
        respondent.email = data.email
        respondent.fax_number = data.fax_number
        respondent.international_dialing_code = data.international_dialing_code
        respondent.post_office_box_number = data.post_office_box_number
        respondent.mobile_phone_number = data.mobile_phone_number
        respondent.mobile_international_dialing_code = data.mobile_international_dialing_code
        respondent.fax_international_dialing_code = data.fax_international_dialing_code
        respondent.password = data.password
        respondent.full_name = data.full_name
        respondent.latitude = data.latitude
        respondent.longitude = data.longitude
        respondent.is_approved = data.is_approved
        respondent.is_newsletter_subscriber = data.is_newsletter_subscriber
        respondent.is_administrator = data.is_administrator
        # Commit the changes
        session.commit()
        print(f"Respondent {data.id} updated successfully!")
    else:
        print(f"Respondent with ID {data.id} not found!")
        new_respondent = Respondent(
            id=data.id,
            created_at=data.created_at,
            updated_at=data.updated_at,
            published_at=data.published_at,
            given_name=data.given_name,
            additional_name=data.additional_name,
            family_name=data.family_name,
            honorific_prefix=data.honorific_prefix,
            honorific_suffix=data.honorific_suffix,
            job_title=data.job_title,
            organization=data.organization,
            country=data.address_country,
            country_code=data.address_country_code,
            address_formatted=data.address_formatted,
            street_address=data.street_address,
            locality=data.address_locality,
            region=data.address_region,
            postal_code=data.postal_code,
            telephone=data.telephone,
            email=data.email,
            fax_number=data.fax_number,
            international_dialing_code=data.international_dialing_code,
            post_office_box_number=data.post_office_box_number,
            mobile_phone_number=data.mobile_phone_number,
            mobile_international_dialing_code=data.mobile_international_dialing_code,
            fax_international_dialing_code=data.fax_international_dialing_code,
            password=data.password,
            full_name=data.full_name,
            latitude=data.latitude,
            longitude=data.longitude,
            is_approved=data.is_approved,
            is_newsletter_subscriber=data.is_newsletter_subscriber,
            is_administrator=data.is_administrator
        )
        session.add(new_respondent)
        session.commit()
        print(f"Respondent {data.id} added successfully!")


def upsert_progresses(pg_session, sqlite_session, id: int):
    sql_query = text('''
        SELECT 
            psp.*,
            psppstl.pi_survey_2023_table_id AS table_id,
            psppscl.pi_survey_category_id AS category_id,
            psppsrl.pi_survey_respondent_id AS respondent_id
        FROM pi_survey_2023_progresses psp 
        JOIN pi_survey_2023_progresses_pi_survey_2023_table_links psppstl ON psppstl.pi_survey_2023_progress_id = psp.id
        JOIN pi_survey_2023_progresses_pi_survey_category_links psppscl ON psppscl.pi_survey_2023_progress_id = psp.id 
        JOIN pi_survey_2023_progresses_pi_survey_respondent_links psppsrl ON psppsrl.pi_survey_2023_progress_id = psp.id
        WHERE psp.id=:progress_id
    ''')
    # Retrieve data from pi_survey_respondents table
    pg_progresses = pg_session.execute(
        sql_query, {'progress_id': id}).fetchall()

    pg_progress = pg_progresses[0]

    upsert_into_sqlite_progress(sqlite_session, pg_progress)


def upsert_into_sqlite_progress(session, data):

    progress = session.query(SurveyProgress).filter_by(id=data.id).first()

    if progress:
        # Update existing record attributes
        progress.is_complete = data.is_complete
        progress.created_at = data.created_at
        progress.updated_at = data.updated_at
        progress.published_at = data.published_at
        # Commit the changes
        session.commit()
        print(f"Progress {data.id} updated successfully!")
    else:
        print(f"Progress with ID {data.id} not found!")
        new_progress = SurveyProgress(
            id=data.id,
            is_complete=data.is_complete,
            created_at=data.created_at,
            updated_at=data.updated_at,
            published_at=data.published_at,
            table_id=data.table_id,
            category_id=data.category_id,
            respondent_id=data.respondent_id
        )
        session.add(new_progress)
        session.commit()
        print(f"Progress {data.id} added successfully!")


def upsert_treatment_patterns(pg_session, sqlite_session, id: int):
    sql_query = text("""
        SELECT 
            pstp.*,
            pstppsrl.pi_survey_respondent_id AS respondent_id
        FROM pi_survey_treatment_patterns pstp
        JOIN pi_survey_treatment_patterns_pi_survey_respondent_links pstppsrl ON pstppsrl.pi_survey_treatment_pattern_id = pstp.id
        WHERE pstp.id=:pattern_id;
    """)
    # Retrieve data from pi_survey_respondents table
    pg_patterns = pg_session.execute(
        sql_query, {'pattern_id': id}).fetchall()

    pg_pattern = pg_patterns[0]
    upsert_into_sqlite_pattern(sqlite_session, pg_pattern)


def upsert_into_sqlite_pattern(session, data):

    pattern = session.query(
        TreatmentPattern).filter_by(id=data.id).first()

    if pattern:
        # Update existing record attributes
        pattern.survey_year = data.survey_year
        pattern.patients_followed = data.patients_followed
        pattern.patients_with_pi_defect = data.patients_with_pi_defect
        pattern.patients_receiving_ig_g_ivig_clinic = data.patients_receiving_ig_g_ivig_clinic
        pattern.patients_receiving_ig_g_ivig_home = data.patients_receiving_ig_g_ivig_home
        pattern.patients_receiving_ig_g_scig = data.patients_receiving_ig_g_scig
        pattern.patients_receiving_ig_g_other = data.patients_receiving_ig_g_other
        pattern.patients_treated_with_gene_therapy = data.patients_treated_with_gene_therapy
        pattern.patients_treated_with_peg_ada = data.patients_treated_with_peg_ada
        pattern.patients_treated_by_transplant_donor_type_mrd = data.patients_treated_by_transplant_donor_type_mrd
        pattern.patients_treated_by_transplant_donor_type_mud = data.patients_treated_by_transplant_donor_type_mud
        pattern.patients_treated_by_transplant_donor_type_m_mud = data.patients_treated_by_transplant_donor_type_m_mud
        pattern.patients_treated_by_transplant_donor_type_haplo = data.patients_treated_by_transplant_donor_type_haplo
        pattern.patients_treated_by_transplant_stem_cell_src_bm = data.patients_treated_by_transplant_stem_cell_src_bm
        pattern.patients_treated_by_transplant_stem_cell_src_pbsc = data.patients_treated_by_transplant_stem_cell_src_pbsc
        pattern.patients_treated_by_transplant_stem_cell_src_cord = data.patients_treated_by_transplant_stem_cell_src_cord
        pattern.patients_treated_by_transplant_stem_cell_src_other_name = data.patients_treated_by_transplant_stem_cell_src_other_name
        pattern.patients_treated_by_transplant_stem_cell_src_other_count = data.patients_treated_by_transplant_stem_cell_src_other_count
        pattern.created_at = data.created_at
        pattern.updated_at = data.updated_at
        pattern.published_at = data.published_at
        pattern.patients_diagnosed_through_jeffrey_insights_program = data.patients_diagnosed_through_jeffrey_insights_program
        # Commit the changes
        session.commit()
        print(f"Pattern {data.id} updated successfully!")
    else:
        print(f"Pattern with ID {data.id} not found!")
        new_treatment_pattern = TreatmentPattern(
            id=data.id,
            survey_year=data.survey_year,
            patients_followed=data.patients_followed,
            patients_with_pi_defect=data.patients_with_pi_defect,
            patients_receiving_ig_g_ivig_clinic=data.patients_receiving_ig_g_ivig_clinic,
            patients_receiving_ig_g_ivig_home=data.patients_receiving_ig_g_ivig_home,
            patients_receiving_ig_g_scig=data.patients_receiving_ig_g_scig,
            patients_receiving_ig_g_other=data.patients_receiving_ig_g_other,
            patients_treated_with_gene_therapy=data.patients_treated_with_gene_therapy,
            patients_treated_with_peg_ada=data.patients_treated_with_peg_ada,
            patients_treated_by_transplant_donor_type_mrd=data.patients_treated_by_transplant_donor_type_mrd,
            patients_treated_by_transplant_donor_type_mud=data.patients_treated_by_transplant_donor_type_mud,
            patients_treated_by_transplant_donor_type_m_mud=data.patients_treated_by_transplant_donor_type_m_mud,
            patients_treated_by_transplant_donor_type_haplo=data.patients_treated_by_transplant_donor_type_haplo,
            patients_treated_by_transplant_stem_cell_src_bm=data.patients_treated_by_transplant_stem_cell_src_bm,
            patients_treated_by_transplant_stem_cell_src_pbsc=data.patients_treated_by_transplant_stem_cell_src_pbsc,
            patients_treated_by_transplant_stem_cell_src_cord=data.patients_treated_by_transplant_stem_cell_src_cord,
            patients_treated_by_transplant_stem_cell_src_other_name=data.patients_treated_by_transplant_stem_cell_src_other_name,
            patients_treated_by_transplant_stem_cell_src_other_count=data.patients_treated_by_transplant_stem_cell_src_other_count,
            created_at=data.created_at,
            updated_at=data.updated_at,
            published_at=data.published_at,
            patients_diagnosed_through_jeffrey_insights_program=data.patients_diagnosed_through_jeffrey_insights_program,
            respondent_id=data.respondent_id
        )
        session.add(new_treatment_pattern)
        session.commit()
        print(f"Pattern {data.id} added successfully!")


def upsert_respondent_logins(pg_session, sqlite_session, id: int):
    # Fetch data using the given SQL query
    sql_query = text("""                
        SELECT 
            psrl.*,
            psrlpsrl.pi_survey_respondent_id AS respondent_id
        FROM pi_survey_respondent_logins psrl 
        JOIN pi_survey_respondent_logins_pi_survey_respondent_links psrlpsrl ON psrlpsrl.pi_survey_respondent_login_id = psrl.id
        WHERE psrl.id=:login_id;
    """)
    # Retrieve data from pi_survey_respondents table
    pg_logins = pg_session.execute(
        sql_query, {'login_id': id}).fetchall()

    pg_login = pg_logins[0]
    upsert_into_sqlite_login(sqlite_session, pg_login)


def upsert_into_sqlite_login(session, data):

    login = session.query(
        RespondentLogin).filter_by(id=data.id).first()

    if login:
        # Update existing record attributes
        login.created_at = data.created_at
        login.updated_at = data.updated_at
        login.published_at = data.published_at
        login.ip_address = data.ip_address
        login.user_agent = data.user_agent
        login.browser_name = data.browser_name
        login.browser_version = data.browser_version
        login.operating_system = data.operating_system
        login.operating_system_version = data.operating_system_version
        login.screen_resolution = data.screen_resolution
        login.language = data.language
        # Commit the changes
        session.commit()
        print(f"Login {data.id} updated successfully!")
    else:
        print(f"Login with ID {data.id} not found!")
        new_response = RespondentLogin(
            id=data.id,
            created_at=data.created_at,
            updated_at=data.updated_at,
            published_at=data.published_at,
            ip_address=data.ip_address,
            user_agent=data.user_agent,
            browser_name=data.browser_name,
            browser_version=data.browser_version,
            operating_system=data.operating_system,
            operating_system_version=data.operating_system_version,
            screen_resolution=data.screen_resolution,
            language=data.language,
            respondent_id=data.respondent_id
        )
        session.add(new_response)
        session.commit()
        print(f"Login {data.id} added successfully!")


def upsert_completions(pg_session, sqlite_session, id: int):
    # Fetch data using the given SQL query
    sql_query = text("""
        SELECT 
            psrc.*,
            psrcpsrl.pi_survey_respondent_id AS respondent_id
        FROM pi_survey_respondent_completions psrc
        JOIN pi_survey_respondent_completions_pi_survey_respondent_links psrcpsrl  ON psrcpsrl.pi_survey_respondent_completion_id  = psrc.id
        WHERE psrc.id=:completion_id;

    """)
    # Retrieve data from pi_survey_respondents table
    pg_completions = pg_session.execute(
        sql_query, {'completion_id': id}).fetchall()

    pg_completion = pg_completions[0]
    upsert_into_sqlite_completion(sqlite_session, pg_completion)


def upsert_into_sqlite_completion(session, data):

    completed = session.query(
        CompletedSurveyRespondents).filter_by(id=data.id).first()

    if completed:
        # Update existing record attributes
        completed.created_at = data.created_at
        completed.updated_at = data.updated_at
        completed.published_at = data.published_at
        completed.is_completed = data.is_complete
        completed.survey_year = data.survey_year
        # Commit the changes
        session.commit()
        print(f"Completion {data.id} updated successfully!")
    else:
        print(f"Completion with ID {data.id} not found!")
        new_response = CompletedSurveyRespondents(
            id=data.id,
            created_at=data.created_at,
            updated_at=data.updated_at,
            published_at=data.published_at,
            is_completed=data.is_complete,
            survey_year=data.survey_year,
            respondent_id=data.respondent_id
        )
        session.add(new_response)
        session.commit()
        print(f"Completion {data.id} added successfully!")


def upsert_net_promoter_scores(pg_session, sqlite_session, id: int):
    # Fetch data using the given SQL query
    sql_query = text("""                
        SELECT 
            psnps.*,
            psnpspsrl.pi_survey_respondent_id AS respondent_id
        FROM pi_survey_net_promoter_scores psnps 
        JOIN pi_survey_net_promoter_scores_pi_survey_respondent_links psnpspsrl  ON psnpspsrl.pi_survey_net_promoter_score_id  = psnps.id
        WHERE psnps.id=:promoter_id;
    """)
    # Retrieve data from pi_survey_respondents table
    pg_promoters = pg_session.execute(
        sql_query, {'promoter_id': id}).fetchall()

    pg_promoter = pg_promoters[0]
    upsert_into_sqlite_promoter(sqlite_session, pg_promoter)


def upsert_into_sqlite_promoter(session, data):

    promoter = session.query(
        NetPromoterScore).filter_by(id=data.id).first()

    if promoter:
        # Update existing record attributes
        promoter.created_at = data.created_at
        promoter.updated_at = data.updated_at
        promoter.published_at = data.published_at
        promoter.score = data.score
        promoter.survey_year = data.survey_year
        promoter.is_survey_complete = data.is_survey_complete
        promoter.comments = data.comments
        # Commit the changes
        session.commit()
        print(f"Promoter {data.id} updated successfully!")
    else:
        print(f"Promoter with ID {data.id} not found!")
        new_response = NetPromoterScore(
            id=data.id,
            created_at=data.created_at,
            updated_at=data.updated_at,
            published_at=data.published_at,
            score=data.score,
            survey_year=data.survey_year,
            is_survey_complete=data.is_survey_complete,
            comments=data.comments,
            respondent_id=data.respondent_id
        )
        session.add(new_response)
        session.commit()
        print(f"Promoter {data.id} added successfully!")


def upsert_demographic_responses(pg_session, sqlite_session, id: int):
    # Fetch data using the given SQL query
    sql_query = text("""  
        SELECT 
            psdr.*,
            psdrpsrl.pi_survey_respondent_id AS respondent_id
        FROM pi_survey_demographic_responses psdr
        JOIN pi_survey_demographic_responses_pi_survey_respondent_links psdrpsrl  ON psdrpsrl.pi_survey_demographic_response_id  = psdr.id
        WHERE psdr.id=:demographic_id;
    """)
    # Retrieve data from pi_survey_respondents table
    pg_demographics = pg_session.execute(
        sql_query, {'demographic_id': id}).fetchall()

    pg_demographic = pg_demographics[0]
    upsert_into_sqlite_demographic(sqlite_session, pg_demographic)


def upsert_into_sqlite_demographic(session, data):

    demographic = session.query(
        PatientDemographic).filter_by(id=data.id).first()

    if demographic:
        # Update existing record attributes
        demographic.created_at = data.created_at
        demographic.updated_at = data.updated_at
        demographic.published_at = data.published_at
        demographic.survey_year = data.survey_year
        demographic.patient_age_count = data.patient_age_count
        demographic.patient_gender_male_count = data.patient_gender_male_count
        demographic.patient_gender_female_count = data.patient_gender_female_count
        demographic.patient_age = data.patient_age
        # Commit the changes
        session.commit()
        print(f"Demographic {data.id} updated successfully!")
    else:
        print(f"Demographic with ID {data.id} not found!")
        new_response = PatientDemographic(
            id=data.id,
            created_at=data.created_at,
            updated_at=data.updated_at,
            published_at=data.published_at,
            survey_year=data.survey_year,
            patient_age_count=data.patient_age_count,
            patient_gender_male_count=data.patient_gender_male_count,
            patient_gender_female_count=data.patient_gender_female_count,
            patient_age=data.patient_age,
            respondent_id=data.respondent_id
        )
        session.add(new_response)
        session.commit()
        print(f"Demographic {data.id} added successfully!")
