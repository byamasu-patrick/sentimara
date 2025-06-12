from bs4 import BeautifulSoup

from events.dataloader import (  # upsert_progresses,; upsert_respondent_logins,; upsert_completions,; upsert_demographic_responses
    upsert_net_promoter_scores,
    upsert_respondent,
    upsert_responses,
    upsert_completions,
    upsert_demographic_responses,
    upsert_treatment_patterns,
)


def remove_html_tags(input_string):
    if input_string is None:
        return ""
    soup = BeautifulSoup(input_string, "html.parser")
    clean_text = soup.get_text()
    return clean_text


condition_to_function_map = {
    "pi_survey_respondents": upsert_respondent,
    "pi_survey_responses_2023s": upsert_responses,
    # "pi_survey_2023_progresses": upsert_progresses,
    "pi_survey_treatment_patterns": upsert_treatment_patterns,
    "pi_survey_respondent_completions": upsert_completions,
    # "pi_survey_respondent_logins": upsert_respondent_logins,
    "pi_survey_net_promoter_scores": upsert_net_promoter_scores,
    "pi_survey_demographic_responses": upsert_demographic_responses
}
