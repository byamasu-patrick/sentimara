# # def query_other_unclassified_diseases(pg_session):
# #     # Fetch data using the given SQL query
# #     sql_query = text("""
# #         SELECT
# #             psrod.*,
# #             psr.given_name || ' ' || psr.family_name AS respondent_name,
# #             psr.job_title AS job_title,
# #             psr.organization AS organization ,
# #             psr.address_country AS country,
# #             psr.address_locality AS locality,
# #             psr.address_locality AS region
# #         FROM pi_survey_responses_other_diseases psrod
# #         JOIN pi_survey_responses_other_diseases_pi_survey_respondent_links psrodpsrl ON psrodpsrl.pi_survey_responses_other_disease_id = psrod.id
# #         JOIN pi_survey_respondents psr ON psr.id = psrodpsrl.pi_survey_respondent_id;
# #     """)
# #     pg_results = pg_session.execute(sql_query).fetchall()

# #     return pg_results


# # def insert_into_sqlite_other_unclassified_disease(session, pg_other_unclassified_diseases):
# #     # Iterate through PostgreSQL results and insert into SQLite
# #     for pg_other_unclassified_disease in pg_other_unclassified_diseases:
# #         existing_unclassified_disease = session.query(
# #             OtherUnclassifiedDiseases).filter_by(id=pg_other_unclassified_disease.id).first()

# #         if existing_unclassified_disease:
# #             # Skip inserting if the id already exists
# #             continue
# #         new_response = OtherUnclassifiedDiseases(
# #             id=pg_other_unclassified_disease.id,
# #             created_at=pg_other_unclassified_disease.created_at,
# #             updated_at=pg_other_unclassified_disease.updated_at,
# #             published_at=pg_other_unclassified_disease.published_at,
# #             disease_name=pg_other_unclassified_disease.disease_name,
# #             gene_defect=pg_other_unclassified_disease.gene_defect,
# #             gene_mutations=pg_other_unclassified_disease.gene_mutations,
# #             number_of_patients=pg_other_unclassified_disease.number_of_patients,
# #             survey_year=pg_other_unclassified_disease.survey_year,
# #             respondent_name=pg_other_unclassified_disease.respondent_name,
# #             organization=pg_other_unclassified_disease.organization,
# #             country=pg_other_unclassified_disease.country,
# #             locality=pg_other_unclassified_disease.locality,
# #   #          region=pg_other_unclassified_disease.region
# #         )
# #         session.add(new_response)

# #     # Commit the changes to the SQLite database
# #     session.commit()


# # def query_other_classified_diseases(pg_session):
# #     # Fetch data using the given SQL query
# #     sql_query = text("""
# #         SELECT
# #             psro.*,
# #             psr.given_name || ' ' || psr.family_name AS respondent_name,
# #             psr.job_title AS job_title,
# #             psr.organization AS organization ,
# #             psr.address_country AS country,
# #             psr.address_locality AS locality,
# #             psr.address_locality AS region,
# #             psc.survey_category_name AS category_name
# #         FROM pi_survey_responses_2023_others psro
# #         JOIN pi_survey_responses_2023_others_pi_survey_respondent_links psropsrl ON psropsrl.pi_survey_responses_2023_other_id = psro.id
# #         JOIN pi_survey_respondents psr ON psr.id = psropsrl.pi_survey_respondent_id
# #         JOIN pi_survey_responses_2023_others_pi_survey_category_links psropscl ON psropscl.pi_survey_responses_2023_other_id  = psro.id
# #         JOIN pi_survey_categories psc ON psc.id = psropscl.pi_survey_category_id;
# #     """)
# #     pg_results = pg_session.execute(sql_query).fetchall()

# #     return pg_results


# # def insert_into_sqlite_other_classified_disease(session, pg_other_classified_diseases):
# #     # Iterate through PostgreSQL results and insert into SQLite
# #     for pg_other_classified_disease in pg_other_classified_diseases:
# #         existing_classified_disease = session.query(
# #             OtherClassifiedDiseases).filter_by(id=pg_other_classified_disease.id).first()

# #         if existing_classified_disease:
# #             # Skip inserting if the id already exists
# #             continue

# #         new_response = OtherClassifiedDiseases(
# #             id=pg_other_classified_disease.id,
# #             created_at=pg_other_classified_disease.created_at,
# #             updated_at=pg_other_classified_disease.updated_at,
# #             published_at=pg_other_classified_disease.published_at,
# #             disease_name=pg_other_classified_disease.disease_name,
# #             gene_defect=pg_other_classified_disease.gene_defect,
# #             gene_mutations=pg_other_classified_disease.gene_mutations,
# #             number_of_patients=pg_other_classified_disease.number_of_patients,
# #             category_name=pg_other_classified_disease.category_name,
# #             respondent_name=pg_other_classified_disease.respondent_name,
# #             organization=pg_other_classified_disease.organization,
# #             country=pg_other_classified_disease.country,
# #             locality=pg_other_classified_disease.locality,
# #  #           region=pg_other_classified_disease.region
# #         )
# #         session.add(new_response)

# #     # Commit the changes to the SQLite database
# #     session.commit()
