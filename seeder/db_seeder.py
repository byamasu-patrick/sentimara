from sqlalchemy import text

from libs.models.db import (  # OtherClassifiedDiseases,; OtherUnclassifiedDiseases,; SurveyProgress,; RespondentLogin
  Colleagues,
  CompletedSurvey,
  Demographic,
  NetPromoterScore,
  ProxyRespondent,
  Respondent,
  Response,
  TreatmentPattern,
)


class DBSeeder:
    def __init__(self, pg_session, sqlite_session):
        self.pg_session = pg_session
        self.sqlite_session = sqlite_session

    def query_survey_respondents(self):
        sql_query = text("""
           SELECT
                r.id,
                r.created_at,
                r.updated_at,
                r.published_at,
                r.honorific_prefix,
                r.honorific_suffix,
                CONCAT(r.given_name, ' ', r.family_name) AS full_name,
                r.given_name,
                r.family_name,
                r.email,
                r.job_title,
                r.organization,
                r.address_locality,
                r.address_region,
                r.address_formatted,
                r.street_address,
                c.country_name AS country_name,
                c.country_alternate_name AS country_alternate_name,
                STRING_AGG(DISTINCT wr."name", ', ') AS world_regions,
                STRING_AGG(DISTINCT wr."alternate_name", ', ') AS world_regions_alternate_name,
                CASE
                    WHEN COUNT(DISTINCT wsr."name") > 1 THEN STRING_AGG(DISTINCT wsr."name", ', ')
                    ELSE MAX(DISTINCT wsr."name")
                END AS world_sub_regions,
                CASE
                    WHEN COUNT(DISTINCT wsr."alternate_name") > 1 THEN STRING_AGG(DISTINCT wsr."alternate_name", ', ')
                    ELSE MAX(DISTINCT wsr."alternate_name")
                END AS world_sub_regions_alternate_name,
                r.postal_code,
                r.telephone,
                r.fax_number,
                r.international_dialing_code,
                r.post_office_box_number,
                r.mobile_phone_number,
                r.mobile_international_dialing_code,
                r.fax_international_dialing_code,
                r.latitude,
                r.longitude,
                r.is_approved,
                r.is_newsletter_subscriber,
                r.is_administrator
            FROM pi_survey_respondents AS r
            LEFT JOIN pi_survey_respondents_country_links AS rccl ON rccl.pi_survey_respondent_id = r.id
            LEFT JOIN countries c ON c.id = rccl.country_id
            LEFT JOIN countries_world_regions_links cwrl ON cwrl.country_id = c.id
            LEFT JOIN world_regions wr ON wr.id = cwrl.world_region_id
            LEFT JOIN countries_world_sub_region_links cwsrl ON cwsrl.country_id = c.id
            LEFT JOIN world_sub_regions wsr ON wsr.id = cwsrl.world_sub_region_id
            GROUP BY
                r.id,
                r.created_at,
                r.updated_at,
                r.published_at,
                r.created_by_id,
                r.updated_by_id,
                r.honorific_prefix,
                r.honorific_suffix,
                r.address_formatted,
                r.street_address,
                r.postal_code,
                r.telephone,
                r.fax_number,
                r.international_dialing_code,
                r.post_office_box_number,
                r.mobile_phone_number,
                r.mobile_international_dialing_code,
                r.fax_international_dialing_code,
                r.latitude,
                r.longitude,
                r.is_approved,
                r.is_newsletter_subscriber,
                r.is_administrator,
                r.given_name,
                r.family_name,
                r.email,
                r.job_title,
                r.organization,
                r.address_locality,
                r.address_region,
                c.country_name,
                c.country_alternate_name;
        """)

        return self.pg_session.execute(sql_query).fetchall()

    def insert_into_sqlite_respondent(self, pg_respondents):
        for data in pg_respondents:
            existing_respondent = self.sqlite_session.query(
                Respondent).filter_by(id=data.id).first()

            if existing_respondent:
                continue
            new_respondent = Respondent(
                id=data.id,
                created_at=data.created_at,
                updated_at=data.updated_at,
                published_at=data.published_at,
                respondent_name=data.given_name + " " + data.family_name,
                honorific_prefix=data.honorific_prefix,
                honorific_suffix=data.honorific_suffix,
                job_title=data.job_title,
                organization=data.organization,
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
                full_name=data.full_name,
                latitude=data.latitude,
                longitude=data.longitude,
                is_approved=data.is_approved,
                is_newsletter_subscriber=data.is_newsletter_subscriber,
                is_administrator=data.is_administrator,
                country_name=data.country_name,
                country_alternate_name=data.country_alternate_name,
                world_region_name=data.world_regions,
                world_region_alternate_name=data.world_regions_alternate_name,
                world_sub_region_name=data.world_sub_regions,
                world_sub_region_alternate_name=data.world_sub_regions_alternate_name
            )
            self.sqlite_session.add(new_respondent)

        self.sqlite_session.commit()

    # def query_survey_progresses(self):
    #     # Define the SQL query
    #     sql_query = text('''
    #         SELECT
    #             psp.*,
    #             pst.table_description  AS table_description,
    #             psc.survey_category_name  AS category_name,
    #             psr.given_name || ' ' || psr.family_name AS respondent_name,
    #             psr.job_title AS job_title,
    #             psr.organization AS organization,
    #             psr.address_locality AS locality,
    #             psr.address_region  AS region,
    #             c.country_name AS country_name,
    #             c.country_alternate_name AS country_alternate_name,
    #             STRING_AGG(DISTINCT wr."name", ', ') AS world_regions,
    #             STRING_AGG(DISTINCT wr."alternate_name", ', ') AS world_regions_alternate_name,
    #             CASE
    #                 WHEN COUNT(DISTINCT wsr."name") > 1 THEN STRING_AGG(DISTINCT wsr."name", ', ')
    #                 ELSE MAX(DISTINCT wsr."name")
    #             END AS world_sub_regions,
    #             CASE
    #                 WHEN COUNT(DISTINCT wsr."alternate_name") > 1 THEN STRING_AGG(DISTINCT wsr."alternate_name", ', ')
    #                 ELSE MAX(DISTINCT wsr."alternate_name")
    #             END AS world_sub_regions_alternate_name
    #         FROM pi_survey_2023_progresses psp
    #         JOIN pi_survey_2023_progresses_pi_survey_2023_table_links psppstl ON psppstl.pi_survey_2023_progress_id = psp.id
    #         JOIN pi_survey_2023_tables pst ON pst.id = psppstl.pi_survey_2023_table_id
    #         JOIN pi_survey_2023_progresses_pi_survey_category_links psppscl ON psppscl.pi_survey_2023_progress_id = psp.id
    #         JOIN pi_survey_categories psc ON psc.id = psppscl.pi_survey_category_id
    #         JOIN pi_survey_2023_progresses_pi_survey_respondent_links psppsrl ON psppsrl.pi_survey_2023_progress_id = psp.id
    #         JOIN pi_survey_respondents psr ON psr.id = psppsrl.pi_survey_respondent_id
    #         LEFT JOIN pi_survey_respondents_country_links AS rccl ON rccl.pi_survey_respondent_id = psr.id
    #         LEFT JOIN countries c ON c.id = rccl.country_id
    #         LEFT JOIN countries_world_regions_links cwrl ON cwrl.country_id = c.id
    #         LEFT JOIN world_regions wr ON wr.id = cwrl.world_region_id
    #         LEFT JOIN countries_world_sub_region_links cwsrl ON cwsrl.country_id = c.id
    #         LEFT JOIN world_sub_regions wsr ON wsr.id = cwsrl.world_sub_region_id
    #         group by
    #             psp.id,
    #             pst.table_description,
    #             psc.survey_category_name,
    #             psr.job_title,
    #             psr.organization,
    #             psr.address_locality,
    #             psr.address_region,
    #             psr.given_name,
    #             psr.family_name,
    #             c.country_name,
    #             c.country_alternate_name;
    #     ''')

    #     # Retrieve data from pi_survey_categories table
    #     pg_progresses = self.pg_session.execute(sql_query).fetchall()
    #     return pg_progresses

    # def insert_into_sqlite_progress(self, pg_progresses):
    #     # Iterate through PostgreSQL results and insert into SQLite
    #     for data in pg_progresses:
    #         existing_progress = self.sqlite_session.query(
    #             SurveyProgress).filter_by(id=data.id).first()

    #         if existing_progress:
    #             # Skip inserting if the id already exists
    #             continue
    #         new_progress = SurveyProgress(
    #             id=data.id,
    #             is_complete=data.is_complete,
    #             created_at=data.created_at,
    #             updated_at=data.updated_at,
    #             published_at=data.published_at,
    #             respondent_name=data.respondent_name,
    #             organization=data.organization,
    #             table_description=data.table_description,
    #             category_name=data.category_name,
    #             locality=data.locality,
    #       #      region=data.region,
    #             country_name=data.country_name,
    #             country_alternate_name=data.country_alternate_name,
    #             world_region_name=data.world_regions,
    #             world_region_alternate_name=data.world_regions_alternate_name,
    #             world_sub_region_name=data.world_sub_regions,
    #             world_sub_region_alternate_name=data.world_sub_regions_alternate_name
    #         )
    #         self.sqlite_session.add(new_progress)
    #     self.sqlite_session.commit()

    def query_responses(self):
        # Fetch data using the given SQL query
        sql_query = text("""
            SELECT
                psrs.id,
                psrs.survey_answer AS patient_reported,
                psc.survey_category_name AS defect_category,
                pst.table_description  AS defect_sub_category,
                psq.survey_question AS defect,
                o.entry_id AS omim_entry_id,
                g.gene_name AS gene_name,
                gip.inheritance_pattern as genetic_inheritance_pattern,
                psr.given_name || ' ' || psr.family_name AS respondent_name,
                psr.job_title AS job_title, 
                psr.organization AS organization , 
                psr.address_locality AS locality, 
                psr.address_locality AS region,
                c.country_name AS country_name,
                c.country_alternate_name AS country_alternate_name,
                STRING_AGG(DISTINCT wr."name", ', ') AS world_regions,
                STRING_AGG(DISTINCT wr."alternate_name", ', ') AS world_regions_alternate_name,
                CASE
                    WHEN COUNT(DISTINCT wsr."name") > 1 THEN STRING_AGG(DISTINCT wsr."name", ', ')
                    ELSE MAX(DISTINCT wsr."name")
                END AS world_sub_regions,
                CASE
                    WHEN COUNT(DISTINCT wsr."alternate_name") > 1 THEN STRING_AGG(DISTINCT wsr."alternate_name", ', ')
                    ELSE MAX(DISTINCT wsr."alternate_name")
                END AS world_sub_regions_alternate_name,
                psrs.created_at,
                psrs.updated_at
            FROM pi_survey_responses_2023s psrs 
            JOIN pi_survey_responses_2023_s_pi_survey_2023_table_links psrspstl  ON psrspstl.pi_survey_responses_2023_id  = psrs.id
            JOIN pi_survey_2023_tables pst ON pst.id = psrspstl.pi_survey_2023_table_id 
            JOIN pi_survey_responses_2023_s_pi_survey_question_links psrspsql ON psrspsql.pi_survey_responses_2023_id  = psrs.id 
            JOIN pi_survey_questions psq ON psq.id = psrspsql.pi_survey_question_id
            JOIN pi_survey_responses_2023_s_pi_survey_respondent_links psrspsrl ON psrspsrl.pi_survey_responses_2023_id  = psrs.id
            JOIN pi_survey_respondents psr ON psr.id = psrspsrl.pi_survey_respondent_id
            LEFT JOIN pi_survey_respondents_country_links AS rccl ON rccl.pi_survey_respondent_id = psr.id
            LEFT JOIN countries c ON c.id = rccl.country_id
            LEFT JOIN countries_world_regions_links cwrl ON cwrl.country_id = c.id
            LEFT JOIN world_regions wr ON wr.id = cwrl.world_region_id
            LEFT JOIN countries_world_sub_region_links cwsrl ON cwsrl.country_id = c.id
            LEFT JOIN world_sub_regions wsr ON wsr.id = cwsrl.world_sub_region_id
            LEFT JOIN pi_survey_questions_pi_survey_category_links psqpscl ON psqpscl.pi_survey_question_id = psq.id 
            LEFT JOIN pi_survey_categories psc ON psc.id = psqpscl.pi_survey_category_id  
            LEFT JOIN pi_survey_questions_omim_databases_links psqodl  ON psqodl.pi_survey_question_id = psq.id 
            LEFT JOIN omims o ON o.id = psqodl.omim_id  
            LEFT JOIN pi_survey_questions_genes_links psqgl ON psqgl.pi_survey_question_id  = psq.id 
            LEFT JOIN genes g ON g.id = psqgl.gene_id 
            LEFT JOIN pi_survey_questions_genetic_inheritance_patterns_links psqgipl  ON psqgipl.pi_survey_question_id  = psq.id 
            LEFT JOIN genetic_inheritance_patterns gip  ON gip.id = psqgipl.genetic_inheritance_pattern_id    
            GROUP BY 
                psr.id,
                psrs.id,			
                psrs.survey_answer,
                pst.table_description,
                psq.survey_question,
                psr.job_title,
                psr.organization,
                psr.address_locality,
                psr.address_region,
                psr.given_name,
                psr.family_name,
                c.country_name,
                c.country_alternate_name,
                psc.survey_category_name,
                o.entry_id,
                g.gene_name,
                gip.inheritance_pattern;
        """)
        pg_results = self.pg_session.execute(sql_query).fetchall()

        return pg_results

    def insert_into_sqlite_response(self, pg_responses, batch_size=100):
        new_responses = []
        # Iterate through PostgreSQL results and insert into SQLite
        for pg_response in pg_responses:
            existing_response = self.sqlite_session.query(
                Response).filter_by(id=pg_response.id).first()

            if existing_response:
                # Skip inserting if the id already exists
                continue
            if pg_response.patient_reported.lower() != 'nan':
                patient_reported_int = int(pg_response.patient_reported)
                if patient_reported_int > 0:
                    new_response = Response(
                        id=pg_response.id,
                        created_at=pg_response.created_at,
                        updated_at=pg_response.updated_at,
                        patients_reported=patient_reported_int,
                        respondent_name=pg_response.respondent_name,
                        organization=pg_response.organization,
                        locality=pg_response.locality,
                        region=pg_response.region,
                        category=pg_response.defect_category,
                        sub_category=pg_response.defect_sub_category,
                        omim_entry_id=pg_response.omim_entry_id,
                        gene_name=pg_response.gene_name,
                        inheritance_pattern=pg_response.genetic_inheritance_pattern,
                        defect=pg_response.defect,
                        country_name=pg_response.country_name,
                        country_alternate_name=pg_response.country_alternate_name,
                        world_region_name=pg_response.world_regions,
                        world_region_alternate_name=pg_response.world_regions_alternate_name,
                        world_sub_region_name=pg_response.world_sub_regions,
                        world_sub_region_alternate_name=pg_response.world_sub_regions_alternate_name
                    )
                    new_responses.append(new_response)

                    try:
                        self.sqlite_session.add_all(new_responses)
                        self.sqlite_session.commit()
                        new_responses = []
                    except Exception as e:
                        self.sqlite_session.rollback()
                        # Add logging or error handling here
                        print(f"Error occurred: {e}")

        if new_responses:
            try:
                self.sqlite_session.add_all(new_responses)
                self.sqlite_session.commit()
            except Exception as e:
                self.sqlite_session.rollback()
                # Add logging or error handling here
                print(f"Error occurred: {e}")

    def query_treatment_patterns(self):
        # Fetch data using the given SQL query
        sql_query = text("""
            SELECT 
                pstp.*,
                psr.given_name || ' ' || psr.family_name AS respondent_name,
                psr.job_title AS job_title, 
                psr.organization AS organization,
                psr.address_locality AS locality, 
                psr.address_locality AS region,
			    c.country_name AS country_name,
			    c.country_alternate_name AS country_alternate_name,
			    STRING_AGG(DISTINCT wr."name", ', ') AS world_regions,
			    STRING_AGG(DISTINCT wr."alternate_name", ', ') AS world_regions_alternate_name,
			    CASE
			        WHEN COUNT(DISTINCT wsr."name") > 1 THEN STRING_AGG(DISTINCT wsr."name", ', ')
			        ELSE MAX(DISTINCT wsr."name")
			    END AS world_sub_regions,
			    CASE
			        WHEN COUNT(DISTINCT wsr."alternate_name") > 1 THEN STRING_AGG(DISTINCT wsr."alternate_name", ', ')
			        ELSE MAX(DISTINCT wsr."alternate_name")
		    END AS world_sub_regions_alternate_name
            FROM pi_survey_treatment_patterns pstp
            JOIN pi_survey_treatment_patterns_pi_survey_respondent_links pstppsrl ON pstppsrl.pi_survey_treatment_pattern_id = pstp.id
            JOIN pi_survey_respondents psr ON psr.id = pstppsrl.pi_survey_respondent_id
			LEFT JOIN pi_survey_respondents_country_links AS rccl ON rccl.pi_survey_respondent_id = psr.id
			LEFT JOIN countries c ON c.id = rccl.country_id
			LEFT JOIN countries_world_regions_links cwrl ON cwrl.country_id = c.id
			LEFT JOIN world_regions wr ON wr.id = cwrl.world_region_id
			LEFT JOIN countries_world_sub_region_links cwsrl ON cwsrl.country_id = c.id
			LEFT JOIN world_sub_regions wsr ON wsr.id = cwsrl.world_sub_region_id
			GROUP BY 
				pstp.id,				
				psr.job_title,
				psr.organization,
				psr.address_locality,
				psr.address_region,
				psr.given_name,
				psr.family_name,
				c.country_name,
				c.country_alternate_name;
        """)
        pg_results = self.pg_session.execute(sql_query).fetchall()

        return pg_results

    def insert_into_sqlite_treatment_patterns(self, pg_treatment_patterns):
        # Iterate through PostgreSQL results and insert into SQLite
        for pg_treatment_pattern in pg_treatment_patterns:
            existing_treatment_pattern = self.sqlite_session.query(
                TreatmentPattern).filter_by(id=pg_treatment_pattern.id).first()

            if existing_treatment_pattern:
                # Skip inserting if the id already exists
                continue

            new_treatment_pattern = TreatmentPattern(
                id=pg_treatment_pattern.id,
                survey_year=pg_treatment_pattern.survey_year,
                patients_followed=pg_treatment_pattern.patients_followed,
                patients_with_pi_defect=pg_treatment_pattern.patients_with_pi_defect,
                patients_receiving_ig_g_ivig_clinic=pg_treatment_pattern.patients_receiving_ig_g_ivig_clinic,
                patients_receiving_ig_g_ivig_home=pg_treatment_pattern.patients_receiving_ig_g_ivig_home,
                patients_receiving_ig_g_scig=pg_treatment_pattern.patients_receiving_ig_g_scig,
                patients_receiving_ig_g_other=pg_treatment_pattern.patients_receiving_ig_g_other,
                patients_treated_with_gene_therapy=pg_treatment_pattern.patients_treated_with_gene_therapy,
                patients_treated_with_peg_ada=pg_treatment_pattern.patients_treated_with_peg_ada,
                patients_treated_by_transplant_donor_type_mrd=pg_treatment_pattern.patients_treated_by_transplant_donor_type_mrd,
                patients_treated_by_transplant_donor_type_mud=pg_treatment_pattern.patients_treated_by_transplant_donor_type_mud,
                patients_treated_by_transplant_donor_type_m_mud=pg_treatment_pattern.patients_treated_by_transplant_donor_type_m_mud,
                patients_treated_by_transplant_donor_type_haplo=pg_treatment_pattern.patients_treated_by_transplant_donor_type_haplo,
                patients_treated_by_transplant_stem_cell_src_bm=pg_treatment_pattern.patients_treated_by_transplant_stem_cell_src_bm,
                patients_treated_by_transplant_stem_cell_src_pbsc=pg_treatment_pattern.patients_treated_by_transplant_stem_cell_src_pbsc,
                patients_treated_by_transplant_stem_cell_src_cord=pg_treatment_pattern.patients_treated_by_transplant_stem_cell_src_cord,
                patients_treated_by_transplant_stem_cell_src_other_name=pg_treatment_pattern.patients_treated_by_transplant_stem_cell_src_other_name,
                patients_treated_by_transplant_stem_cell_src_other_count=pg_treatment_pattern.patients_treated_by_transplant_stem_cell_src_other_count,
                created_at=pg_treatment_pattern.created_at,
                updated_at=pg_treatment_pattern.updated_at,
                published_at=pg_treatment_pattern.published_at,
                patients_diagnosed_through_jeffrey_insights_program=pg_treatment_pattern.patients_diagnosed_through_jeffrey_insights_program,
                respondent_name=pg_treatment_pattern.respondent_name,
                organization=pg_treatment_pattern.organization,
                locality=pg_treatment_pattern.locality,
                region=pg_treatment_pattern.region,
                country_name=pg_treatment_pattern.country_name,
                country_alternate_name=pg_treatment_pattern.country_alternate_name,
                world_region_name=pg_treatment_pattern.world_regions,
                world_region_alternate_name=pg_treatment_pattern.world_regions_alternate_name,
                world_sub_region_name=pg_treatment_pattern.world_sub_regions,
                world_sub_region_alternate_name=pg_treatment_pattern.world_sub_regions_alternate_name
            )
            self.sqlite_session.add(new_treatment_pattern)

        # Commit the changes to the SQLite database
        self.sqlite_session.commit()

    def query_demographics(self):
        # Fetch data using the given SQL query
        sql_query = text("""  
            SELECT 
                psdr.*,
                psr.given_name || ' ' || psr.family_name AS respondent_name,
                psr.job_title AS job_title, 
                psr.organization AS organization, 
                psr.address_locality AS locality, 
                psr.address_locality AS region,
			    c.country_name AS country_name,
			    c.country_alternate_name AS country_alternate_name,
			    STRING_AGG(DISTINCT wr."name", ', ') AS world_regions,
			    STRING_AGG(DISTINCT wr."alternate_name", ', ') AS world_regions_alternate_name,
			    CASE
			        WHEN COUNT(DISTINCT wsr."name") > 1 THEN STRING_AGG(DISTINCT wsr."name", ', ')
			        ELSE MAX(DISTINCT wsr."name")
			    END AS world_sub_regions,
			    CASE
			        WHEN COUNT(DISTINCT wsr."alternate_name") > 1 THEN STRING_AGG(DISTINCT wsr."alternate_name", ', ')
			        ELSE MAX(DISTINCT wsr."alternate_name")
		    	END AS world_sub_regions_alternate_name
            FROM pi_survey_demographic_responses psdr
            JOIN pi_survey_demographic_responses_pi_survey_respondent_links psdrpsrl  ON psdrpsrl.pi_survey_demographic_response_id  = psdr.id
            JOIN pi_survey_respondents psr ON psr.id = psdrpsrl.pi_survey_respondent_id
			LEFT JOIN pi_survey_respondents_country_links AS rccl ON rccl.pi_survey_respondent_id = psr.id
			LEFT JOIN countries c ON c.id = rccl.country_id
			LEFT JOIN countries_world_regions_links cwrl ON cwrl.country_id = c.id
			LEFT JOIN world_regions wr ON wr.id = cwrl.world_region_id
			LEFT JOIN countries_world_sub_region_links cwsrl ON cwsrl.country_id = c.id
			LEFT JOIN world_sub_regions wsr ON wsr.id = cwsrl.world_sub_region_id
			GROUP BY 
				psdr.id,				
				psr.job_title,
				psr.organization,
				psr.address_locality,
				psr.address_region,
				psr.given_name,
				psr.family_name,
				c.country_name,
				c.country_alternate_name;
        """)
        pg_results = self.pg_session.execute(sql_query).fetchall()

        return pg_results

    def insert_into_sqlite_demographic(self, pg_demographics):
        # Iterate through PostgreSQL results and insert into SQLite
        for pg_demographic in pg_demographics:
            existing_demographic = self.sqlite_session.query(
                Demographic).filter_by(id=pg_demographic.id).first()

            if existing_demographic:
                # Skip inserting if the id already exists
                continue
            new_response = Demographic(
                id=pg_demographic.id,
                created_at=pg_demographic.created_at,
                updated_at=pg_demographic.updated_at,
                published_at=pg_demographic.published_at,
                survey_year=pg_demographic.survey_year,
                age_count=pg_demographic.patient_age_count,
                gender_male_count=pg_demographic.patient_gender_male_count,
                gender_female_count=pg_demographic.patient_gender_female_count,
                patient_age=pg_demographic.patient_age,
                respondent_name=pg_demographic.respondent_name,
                organization=pg_demographic.organization,
                locality=pg_demographic.locality,
                region=pg_demographic.region,
                country_name=pg_demographic.country_name,
                country_alternate_name=pg_demographic.country_alternate_name,
                world_region_name=pg_demographic.world_regions,
                world_region_alternate_name=pg_demographic.world_regions_alternate_name,
                world_sub_region_name=pg_demographic.world_sub_regions,
                world_sub_region_alternate_name=pg_demographic.world_sub_regions_alternate_name
            )
            self.sqlite_session.add(new_response)

        # Commit the changes to the SQLite database
        self.sqlite_session.commit()

    def query_completions(self):
        # Fetch data using the given SQL query
        sql_query = text("""
            SELECT
                psrc.*,
                psr.given_name || ' ' || psr.family_name AS respondent_name,
                psr.job_title AS job_title,
                psr.organization AS organization,
                psr.address_locality AS locality,
                psr.address_locality AS region,
        		    c.country_name AS country_name,
        		    c.country_alternate_name AS country_alternate_name,
        		    STRING_AGG(DISTINCT wr."name", ', ') AS world_regions,
        		    STRING_AGG(DISTINCT wr."alternate_name", ', ') AS world_regions_alternate_name,
        		    CASE
        		        WHEN COUNT(DISTINCT wsr."name") > 1 THEN STRING_AGG(DISTINCT wsr."name", ', ')
        		        ELSE MAX(DISTINCT wsr."name")
        		    END AS world_sub_regions,
        		    CASE
        		        WHEN COUNT(DISTINCT wsr."alternate_name") > 1 THEN STRING_AGG(DISTINCT wsr."alternate_name", ', ')
        		        ELSE MAX(DISTINCT wsr."alternate_name")
        	    	END AS world_sub_regions_alternate_name
            FROM pi_survey_respondent_completions psrc
            JOIN pi_survey_respondent_completions_pi_survey_respondent_links psrcpsrl  ON psrcpsrl.pi_survey_respondent_completion_id  = psrc.id
            JOIN pi_survey_respondents psr ON psr.id = psrcpsrl.pi_survey_respondent_id
        		LEFT JOIN pi_survey_respondents_country_links AS rccl ON rccl.pi_survey_respondent_id = psr.id
        		LEFT JOIN countries c ON c.id = rccl.country_id
        		LEFT JOIN countries_world_regions_links cwrl ON cwrl.country_id = c.id
        		LEFT JOIN world_regions wr ON wr.id = cwrl.world_region_id
        		LEFT JOIN countries_world_sub_region_links cwsrl ON cwsrl.country_id = c.id
        		LEFT JOIN world_sub_regions wsr ON wsr.id = cwsrl.world_sub_region_id
        		GROUP BY
        			psrc.id,
        			psr.job_title,
        			psr.organization,
        			psr.address_locality,
        			psr.address_region,
        			psr.given_name,
        			psr.family_name,
        			c.country_name,
        			c.country_alternate_name;
        """)
        pg_results = self.pg_session.execute(sql_query).fetchall()

        return pg_results

    def insert_into_sqlite_completion(self, pg_completions):
        # Iterate through PostgreSQL results and insert into SQLite
        for pg_completion in pg_completions:
            existing_completion = self.sqlite_session.query(
                CompletedSurvey).filter_by(id=pg_completion.id).first()

            if existing_completion:
                # Skip inserting if the id already exists
                continue
            new_response = CompletedSurvey(
                id=pg_completion.id,
                created_at=pg_completion.created_at,
                updated_at=pg_completion.updated_at,
                published_at=pg_completion.published_at,
                is_completed=pg_completion.is_complete,
                survey_year=pg_completion.survey_year,
                respondent_name=pg_completion.respondent_name,
                organization=pg_completion.organization,
                locality=pg_completion.locality,
                region=pg_completion.region,
                country_name=pg_completion.country_name,
                country_alternate_name=pg_completion.country_alternate_name,
                world_region_name=pg_completion.world_regions,
                world_region_alternate_name=pg_completion.world_regions_alternate_name,
                world_sub_region_name=pg_completion.world_sub_regions,
                world_sub_region_alternate_name=pg_completion.world_sub_regions_alternate_name
            )
            self.sqlite_session.add(new_response)

        # Commit the changes to the SQLite database
        self.sqlite_session.commit()

    def query_colleagues(self):
        # Fetch data using the given SQL query
        sql_query = text("""  
            SELECT 
                psrc.*,
                psr.given_name || ' ' || psr.family_name AS respondent_name,
                psr.job_title AS job_title, 
                psr.organization AS organization, 
                psr.address_locality AS locality, 
                psr.address_locality AS region,
			    c.country_name AS country_name,
			    c.country_alternate_name AS country_alternate_name,
			    STRING_AGG(DISTINCT wr."name", ', ') AS world_regions,
			    STRING_AGG(DISTINCT wr."alternate_name", ', ') AS world_regions_alternate_name,
			    CASE
			        WHEN COUNT(DISTINCT wsr."name") > 1 THEN STRING_AGG(DISTINCT wsr."name", ', ')
			        ELSE MAX(DISTINCT wsr."name")
			    END AS world_sub_regions,
			    CASE
			        WHEN COUNT(DISTINCT wsr."alternate_name") > 1 THEN STRING_AGG(DISTINCT wsr."alternate_name", ', ')
			        ELSE MAX(DISTINCT wsr."alternate_name")
		    	END AS world_sub_regions_alternate_name
            FROM pi_survey_respondent_colleagues psrc
            JOIN pi_survey_respondent_colleagues_pi_survey_respondent_links psrcpsrl ON psrcpsrl.pi_survey_respondent_colleague_id  = psrc.id
            JOIN pi_survey_respondents psr ON psr.id = psrcpsrl.pi_survey_respondent_id
			LEFT JOIN pi_survey_respondents_country_links AS rccl ON rccl.pi_survey_respondent_id = psr.id
			LEFT JOIN countries c ON c.id = rccl.country_id
			LEFT JOIN countries_world_regions_links cwrl ON cwrl.country_id = c.id
			LEFT JOIN world_regions wr ON wr.id = cwrl.world_region_id
			LEFT JOIN countries_world_sub_region_links cwsrl ON cwsrl.country_id = c.id
			LEFT JOIN world_sub_regions wsr ON wsr.id = cwsrl.world_sub_region_id
			GROUP BY 
				psrc.id,				
				psr.job_title,
				psr.organization,
				psr.address_locality,
				psr.address_region,
				psr.given_name,
				psr.family_name,
				c.country_name,
				c.country_alternate_name;
        """)
        pg_results = self.pg_session.execute(sql_query).fetchall()

        return pg_results

    def insert_into_sqlite_colleague(self, pg_colleagues):
        # Iterate through PostgreSQL results and insert into SQLite
        for pg_colleague in pg_colleagues:
            existing_colleague = self.sqlite_session.query(
                Colleagues).filter_by(id=pg_colleague.id).first()

            if existing_colleague:
                # Skip inserting if the id already exists
                continue

            new_response = Colleagues(
                id=pg_colleague.id,
                created_at=pg_colleague.created_at,
                updated_at=pg_colleague.updated_at,
                published_at=pg_colleague.published_at,
                given_name=pg_colleague.given_name,
                family_name=pg_colleague.family_name,
                email=pg_colleague.email,
                respondent_name=pg_colleague.respondent_name,
                organization=pg_colleague.organization,
                locality=pg_colleague.locality,
                region=pg_colleague.region,
                country_name=pg_colleague.country_name,
                country_alternate_name=pg_colleague.country_alternate_name,
                world_region_name=pg_colleague.world_regions,
                world_region_alternate_name=pg_colleague.world_regions_alternate_name,
                world_sub_region_name=pg_colleague.world_sub_regions,
                world_sub_region_alternate_name=pg_colleague.world_sub_regions_alternate_name
            )
            self.sqlite_session.add(new_response)

        # Commit the changes to the SQLite database
        self.sqlite_session.commit()

    def query_proxy_respondents(self):
        # Fetch data using the given SQL query
        sql_query = text("""  
            SELECT 
                pspr.*,
                psr.given_name || ' ' || psr.family_name AS respondent_name,
                psr.job_title AS job_title, 
                psr.organization AS organization, 
                psr.address_locality AS locality, 
                psr.address_locality AS region,
			    c.country_name AS country_name,
			    c.country_alternate_name AS country_alternate_name,
			    STRING_AGG(DISTINCT wr."name", ', ') AS world_regions,
			    STRING_AGG(DISTINCT wr."alternate_name", ', ') AS world_regions_alternate_name,
			    CASE
			        WHEN COUNT(DISTINCT wsr."name") > 1 THEN STRING_AGG(DISTINCT wsr."name", ', ')
			        ELSE MAX(DISTINCT wsr."name")
			    END AS world_sub_regions,
			    CASE
			        WHEN COUNT(DISTINCT wsr."alternate_name") > 1 THEN STRING_AGG(DISTINCT wsr."alternate_name", ', ')
			        ELSE MAX(DISTINCT wsr."alternate_name")
		    	END AS world_sub_regions_alternate_name
            FROM pi_survey_proxy_respondents pspr
            JOIN pi_survey_proxy_respondents_pi_survey_respondents_links psprpsrl  ON psprpsrl.pi_survey_proxy_respondent_id  = pspr.id
            JOIN pi_survey_respondents psr ON psr.id = psprpsrl.pi_survey_respondent_id
			LEFT JOIN pi_survey_respondents_country_links AS rccl ON rccl.pi_survey_respondent_id = psr.id
			LEFT JOIN countries c ON c.id = rccl.country_id
			LEFT JOIN countries_world_regions_links cwrl ON cwrl.country_id = c.id
			LEFT JOIN world_regions wr ON wr.id = cwrl.world_region_id
			LEFT JOIN countries_world_sub_region_links cwsrl ON cwsrl.country_id = c.id
			LEFT JOIN world_sub_regions wsr ON wsr.id = cwsrl.world_sub_region_id
			GROUP BY 
				pspr.id,				
				psr.job_title,
				psr.organization,
				psr.address_locality,
				psr.address_region,
				psr.given_name,
				psr.family_name,
				c.country_name,
				c.country_alternate_name;
				
        """)
        pg_results = self.pg_session.execute(sql_query).fetchall()

        return pg_results

    def insert_into_sqlite_proxy_respondent(self, pg_proxy_respondents):
        # Iterate through PostgreSQL results and insert into SQLite
        for pg_proxy_respondent in pg_proxy_respondents:
            existing_proxy_respondent = self.sqlite_session.query(
                ProxyRespondent).filter_by(id=pg_proxy_respondent.id).first()

            if existing_proxy_respondent:
                # Skip inserting if the id already exists
                continue

            new_response = ProxyRespondent(
                id=pg_proxy_respondent.id,
                created_at=pg_proxy_respondent.created_at,
                updated_at=pg_proxy_respondent.updated_at,
                published_at=pg_proxy_respondent.published_at,
                given_name=pg_proxy_respondent.given_name,
                family_name=pg_proxy_respondent.family_name,
                email=pg_proxy_respondent.email,
                respondent_name=pg_proxy_respondent.respondent_name,
                organization=pg_proxy_respondent.organization,
                locality=pg_proxy_respondent.locality,
                region=pg_proxy_respondent.region,
                country_name=pg_proxy_respondent.country_name,
                country_alternate_name=pg_proxy_respondent.country_alternate_name,
                world_region_name=pg_proxy_respondent.world_regions,
                world_region_alternate_name=pg_proxy_respondent.world_regions_alternate_name,
                world_sub_region_name=pg_proxy_respondent.world_sub_regions,
                world_sub_region_alternate_name=pg_proxy_respondent.world_sub_regions_alternate_name
            )
            self.sqlite_session.add(new_response)

        # Commit the changes to the SQLite database
        self.sqlite_session.commit()

    def query_net_promoter_scores(self):
        # Fetch data using the given SQL query
        sql_query = text("""
            SELECT
                psnps.*,
                psr.given_name || ' ' || psr.family_name AS respondent_name,
                psr.job_title AS job_title,
                psr.organization AS organization,
                psr.address_locality AS locality,
                psr.address_locality AS region,
        		    c.country_name AS country_name,
        		    c.country_alternate_name AS country_alternate_name,
        		    STRING_AGG(DISTINCT wr."name", ', ') AS world_regions,
        		    STRING_AGG(DISTINCT wr."alternate_name", ', ') AS world_regions_alternate_name,
        		    CASE
        		        WHEN COUNT(DISTINCT wsr."name") > 1 THEN STRING_AGG(DISTINCT wsr."name", ', ')
        		        ELSE MAX(DISTINCT wsr."name")
        		    END AS world_sub_regions,
        		    CASE
        		        WHEN COUNT(DISTINCT wsr."alternate_name") > 1 THEN STRING_AGG(DISTINCT wsr."alternate_name", ', ')
        		        ELSE MAX(DISTINCT wsr."alternate_name")
        	    	END AS world_sub_regions_alternate_name
            FROM pi_survey_net_promoter_scores psnps
            JOIN pi_survey_net_promoter_scores_pi_survey_respondent_links psnpspsrl  ON psnpspsrl.pi_survey_net_promoter_score_id  = psnps.id
            JOIN pi_survey_respondents psr ON psr.id = psnpspsrl.pi_survey_respondent_id
        		LEFT JOIN pi_survey_respondents_country_links AS rccl ON rccl.pi_survey_respondent_id = psr.id
        		LEFT JOIN countries c ON c.id = rccl.country_id
        		LEFT JOIN countries_world_regions_links cwrl ON cwrl.country_id = c.id
        		LEFT JOIN world_regions wr ON wr.id = cwrl.world_region_id
        		LEFT JOIN countries_world_sub_region_links cwsrl ON cwsrl.country_id = c.id
        		LEFT JOIN world_sub_regions wsr ON wsr.id = cwsrl.world_sub_region_id
        		GROUP BY
        			psnps.id,
        			psr.job_title,
        			psr.organization,
        			psr.address_locality,
        			psr.address_region,
        			psr.given_name,
        			psr.family_name,
        			c.country_name,
        			c.country_alternate_name;
        """)
        pg_results = self.pg_session.execute(sql_query).fetchall()

        return pg_results

    def insert_into_sqlite_net_promoter_score(self, pg_net_promoter_scores):
        # Iterate through PostgreSQL results and insert into SQLite
        for pg_net_promoter_score in pg_net_promoter_scores:
            existing_promoter = self.sqlite_session.query(
                NetPromoterScore).filter_by(id=pg_net_promoter_score.id).first()

            if existing_promoter:
                # Skip inserting if the id already exists
                continue
            new_response = NetPromoterScore(
                id=pg_net_promoter_score.id,
                created_at=pg_net_promoter_score.created_at,
                updated_at=pg_net_promoter_score.updated_at,
                published_at=pg_net_promoter_score.published_at,
                score=pg_net_promoter_score.score,
                survey_year=pg_net_promoter_score.survey_year,
                is_survey_complete=pg_net_promoter_score.is_survey_complete,
                comments=pg_net_promoter_score.comments,
                respondent_name=pg_net_promoter_score.respondent_name,
                organization=pg_net_promoter_score.organization,
                locality=pg_net_promoter_score.locality,
                region=pg_net_promoter_score.region,
                country_name=pg_net_promoter_score.country_name,
                country_alternate_name=pg_net_promoter_score.country_alternate_name,
                world_region_name=pg_net_promoter_score.world_regions,
                world_region_alternate_name=pg_net_promoter_score.world_regions_alternate_name,
                world_sub_region_name=pg_net_promoter_score.world_sub_regions,
                world_sub_region_alternate_name=pg_net_promoter_score.world_sub_regions_alternate_name
            )
            self.sqlite_session.add(new_response)

        # Commit the changes to the SQLite database
        self.sqlite_session.commit()

    # def query_logins(self):
    #     # Fetch data using the given SQL query
    #     sql_query = text("""
    #         SELECT
    #             psrl.*,
    #             psr.given_name || ' ' || psr.family_name AS respondent_name,
    #             psr.job_title AS job_title,
    #             psr.organization AS organization,
    #             psr.address_locality AS locality,
    #             psr.address_locality AS region,
        # 		    c.country_name AS country_name,
        # 		    c.country_alternate_name AS country_alternate_name,
        # 		    STRING_AGG(DISTINCT wr."name", ', ') AS world_regions,
        # 		    STRING_AGG(DISTINCT wr."alternate_name", ', ') AS world_regions_alternate_name,
        # 		    CASE
        # 		        WHEN COUNT(DISTINCT wsr."name") > 1 THEN STRING_AGG(DISTINCT wsr."name", ', ')
        # 		        ELSE MAX(DISTINCT wsr."name")
        # 		    END AS world_sub_regions,
        # 		    CASE
        # 		        WHEN COUNT(DISTINCT wsr."alternate_name") > 1 THEN STRING_AGG(DISTINCT wsr."alternate_name", ', ')
        # 		        ELSE MAX(DISTINCT wsr."alternate_name")
        # 	    	END AS world_sub_regions_alternate_name
    #         FROM pi_survey_respondent_logins psrl
    #         JOIN pi_survey_respondent_logins_pi_survey_respondent_links psrlpsrl ON psrlpsrl.pi_survey_respondent_login_id = psrl.id
    #         JOIN pi_survey_respondents psr ON psr.id = psrlpsrl.pi_survey_respondent_id
        # 		LEFT JOIN pi_survey_respondents_country_links AS rccl ON rccl.pi_survey_respondent_id = psr.id
        # 		LEFT JOIN countries c ON c.id = rccl.country_id
        # 		LEFT JOIN countries_world_regions_links cwrl ON cwrl.country_id = c.id
        # 		LEFT JOIN world_regions wr ON wr.id = cwrl.world_region_id
        # 		LEFT JOIN countries_world_sub_region_links cwsrl ON cwsrl.country_id = c.id
        # 		LEFT JOIN world_sub_regions wsr ON wsr.id = cwsrl.world_sub_region_id
        # 		GROUP BY
        # 			psrl.id,
        # 			psr.job_title,
        # 			psr.organization,
        # 			psr.address_locality,
        # 			psr.address_region,
        # 			psr.given_name,
        # 			psr.family_name,
        # 			c.country_name,
        # 			c.country_alternate_name;
    #     """)
    #     pg_results = self.pg_session.execute(sql_query).fetchall()

    #     return pg_results

    # def insert_into_sqlite_login(self, pg_logins):
    #     # Iterate through PostgreSQL results and insert into SQLite
    #     for pg_login in pg_logins:
    #         existing_login = self.sqlite_session.query(
    #             RespondentLogin).filter_by(id=pg_login.id).first()

    #         if existing_login:
    #             # Skip inserting if the id already exists
    #             continue
    #         new_response = RespondentLogin(
    #             id=pg_login.id,
    #             created_at=pg_login.created_at,
    #             updated_at=pg_login.updated_at,
    #             published_at=pg_login.published_at,
    #             ip_address=pg_login.ip_address,
    #             user_agent=pg_login.user_agent,
    #             browser_name=pg_login.browser_name,
    #             browser_version=pg_login.browser_version,
    #             operating_system=pg_login.operating_system,
    #             operating_system_version=pg_login.operating_system_version,
    #             screen_resolution=pg_login.screen_resolution,
    #             language=pg_login.language,
    #             respondent_name=pg_login.respondent_name,
    #             organization=pg_login.organization,
    #             locality=pg_login.locality,
    #           #  region=pg_login.region,
    #             country_name=pg_login.country_name,
    #             country_alternate_name=pg_login.country_alternate_name,
    #             world_region_name=pg_login.world_regions,
    #             world_region_alternate_name=pg_login.world_regions_alternate_name,
    #             world_sub_region_name=pg_login.world_sub_regions,
    #             world_sub_region_alternate_name=pg_login.world_sub_regions_alternate_name
    #         )
    #         self.sqlite_session.add(new_response)

    #     # Commit the changes to the SQLite database
    #     self.sqlite_session.commit()

    def fetch_survey_data(self):
        pg_respondents = self.query_survey_respondents()
        # pg_progresses = self.query_survey_progresses()
        pg_responses = self.query_responses()
        pg_treatment_patterns = self.query_treatment_patterns()
        pg_demographics = self.query_demographics()
        pg_completions = self.query_completions()
        pg_colleagues = self.query_colleagues()
        pg_proxy_respondents = self.query_proxy_respondents()
        pg_net_promoter_scores = self.query_net_promoter_scores()
        # pg_logins = self.query_logins()

        return (pg_respondents, pg_responses, pg_treatment_patterns, pg_demographics, pg_colleagues, pg_proxy_respondents, pg_completions, pg_net_promoter_scores)

    def seed(self):
        #   Fetch postgreSQL pg_other_unclassified_diseases, pg_other_classified_diseases,
        (pg_respondents, pg_responses, pg_treatment_patterns, pg_demographics,
         pg_colleagues, pg_proxy_respondents, pg_completions, pg_net_promoter_scores) = self.fetch_survey_data()

        self.insert_into_sqlite_respondent(pg_respondents)

        # self.insert_into_sqlite_progress(pg_progresses)
        self.insert_into_sqlite_response(pg_responses)
        self.insert_into_sqlite_treatment_patterns(pg_treatment_patterns)

        self.insert_into_sqlite_completion(pg_completions)
        # self.insert_into_sqlite_login(pg_logins)
        self.insert_into_sqlite_net_promoter_score(pg_net_promoter_scores)
        self.insert_into_sqlite_demographic(pg_demographics)

        # # insert_into_sqlite_other_unclassified_disease(
        # #     sqlite_session, pg_other_unclassified_diseases)
        # # insert_into_sqlite_other_classified_disease(
        # #     sqlite_session, pg_other_classified_diseases)
        self.insert_into_sqlite_colleague(pg_colleagues)
        self.insert_into_sqlite_proxy_respondent(pg_proxy_respondents)
