from chat.utils import tables_list
from llama_index.response_synthesizers import BaseSynthesizer
from llama_index.indices.service_context import ServiceContext
from llama_index.prompts.prompts import RefinePrompt, QuestionAnswerPrompt
from llama_index.prompts.prompt_type import PromptType
from llama_index.response_synthesizers.factory import get_response_synthesizer


def get_custom_response_synth(
    service_context: ServiceContext,
) -> BaseSynthesizer:
    table_names = "\n".join("- " + table_name for table_name in tables_list)

    refine_template_str = f"""
        A user has a set of table names and has asked a question about them. \
        The table names have the following titles:

        {table_names}

        The original query is as follows: {{query_str}}
        We have provided an existing answer: {{existing_answer}}
        We have the opportunity to refine the existing answer \
        (only if needed) with some more context below.
        ------------
        {{context_msg}}
        ------------
        Given the new context, refine the original answer to better \
        answer the query. \
        If the context isn't useful, return the original answer.
        Refined Answer:
    """.strip()

    refine_prompt = RefinePrompt(
        template=refine_template_str,
        prompt_type=PromptType.REFINE,
    )

    qa_template_str = f"""
        A user has a set of table names and has asked a question about them. \
        The table names have the following titles:
        {table_names}

        Context information is below.
        ---------------------
        {{context_str}}
        ---------------------
        Given the context information and not prior knowledge, \
        answer the query.
        Query: {{query_str}}
        Answer:
    """.strip()

    qa_prompt = QuestionAnswerPrompt(
        template=qa_template_str,
        prompt_type=PromptType.QUESTION_ANSWER,
    )

    return get_response_synthesizer(
        service_context,
        refine_template=refine_prompt,
        text_qa_template=qa_prompt,
        # structured_answer_filtering=True,
    )
