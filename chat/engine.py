
import os
import openai
import logging
import nest_asyncio
from dotenv import load_dotenv
from datetime import datetime
from core.config import settings
from typing import List, Literal
from chat.constants import text_to_sql_tmpl
from chat.utils import tables_list
from llama_index.llms import OpenAI
from llama_index.agent import OpenAIAgent
from llama_index.llms.base import MessageRole
from llama_index.llms import ChatMessage, OpenAI
from llama_index.tools import QueryEngineTool, ToolMetadata
from llama_index.prompts import PromptTemplate
from llama_index.query_engine import PGVectorSQLQueryEngine
from llama_index.query_engine import SubQuestionQueryEngine
from chat.qa_response_synth import get_custom_response_synth
from llama_index.node_parser.simple import SimpleNodeParser
from libs.models.chatdb import MessageRoleEnum, MessageStatusEnum
from llama_index import SQLDatabase, VectorStoreIndex, ServiceContext
from llama_index.callbacks.base import BaseCallbackHandler, CallbackManager
from llama_index.objects import SQLTableNodeMapping, ObjectIndex, SQLTableSchema

from sqlalchemy.orm import sessionmaker
from sqlalchemy.engine import create_engine
from libs.models.db import engine
from llama_index.indices.struct_store import (
    SQLTableRetrieverQueryEngine,
)
# from llama_index.vector_stores.types import (
#     MetadataFilters,
#     ExactMatchFilter,
# )
from chat.constants import (
    SYSTEM_MESSAGE,
    NODE_PARSER_CHUNK_OVERLAP,
    NODE_PARSER_CHUNK_SIZE,
)
from llama_index.embeddings.openai import (
    OpenAIEmbedding,
    OpenAIEmbeddingMode,
    OpenAIEmbeddingModelType,
)
from schema import (
    Message as MessageSchema,
    Conversation as ConversationSchema,
)

from seeder.db_seeder import DBSeeder
from libs.models.db import (
    Session,
    init_db,
    engine,
    table_context_dict
)

load_dotenv()
DATABASE_HOST_DEV = os.getenv('DATABASE_HOST_DEV')
DATABASE_NAME_DEV = os.getenv('DATABASE_NAME_DEV')
DATABASE_PASSWORD_DEV = os.getenv('DATABASE_PASSWORD_DEV')
DATABASE_PORT_DEV = os.getenv('DATABASE_PORT_DEV')
DATABASE_USERNAME_DEV = os.getenv('DATABASE_USERNAME_DEV')
logger = logging.getLogger(__name__)

logger.info("Applying nested asyncio patch")
nest_asyncio.apply()

init_db()


def get_conversation_headline(prompt: str):
    prompt_template = f""""
        Given the a question below, your task is to create a conversation headline from the question provided below. 
        The headline need to be simple and concise.
         
        Say for example if a question is 'how many respondent have participated in this survey?' The headline can be 'Respondent information help'
        
        Below is the prompt:

        Prompt: {prompt}
    """
    response = openai.Completion.create(
        engine="text-davinci-003",
        prompt=prompt_template,
        temperature=0.7,
        max_tokens=100
    )

    return response.choices[0].text.strip()


def table_index_builder(
        sql_database: SQLDatabase, table_context_dict: dict[str, Literal]
) -> ObjectIndex:
    table_node_mapping = SQLTableNodeMapping(sql_database)
    table_schema_objs: list[SQLTableSchema] = []

    # Build our table schema
    for table_name in table_context_dict:
        # one SQLTableSchema for each table
        table_schema = (SQLTableSchema(
            table_name=table_name, context_str=table_context_dict[table_name]))
        table_schema_objs.append(table_schema)

    obj_index = ObjectIndex.from_objects(
        table_schema_objs,
        table_node_mapping,
        VectorStoreIndex,
    )

    return obj_index


def build_query_engine(
        sql_database: SQLDatabase, service_context: ServiceContext, table_context_dict: dict[str, str]
) -> SQLTableRetrieverQueryEngine:
    # build object index
    # obj_index:  ObjectIndex = table_index_builder(
    #     sql_database,
    #     table_context_dict=table_context_dict)

    # kwargs = {"similarity_top_k": 3}
    # query_engine = SQLTableRetrieverQueryEngine(
    #     sql_database=sql_database,
    #     table_retriever=obj_index.as_retriever(**kwargs),
    #     service_context=service_context
    # )

    text_to_sql_prompt = PromptTemplate(text_to_sql_tmpl)

    query_engine = PGVectorSQLQueryEngine(
        sql_database=sql_database,
        text_to_sql_prompt=text_to_sql_prompt,
        service_context=service_context,
        context_query_kwargs=table_context_dict,
    )

    return query_engine


def get_tool_service_context(
    callback_handlers: List[BaseCallbackHandler],
) -> ServiceContext:
    llm = OpenAI(
        temperature=0.1,
        model="gpt-4",
        streaming=True,
        api_key=settings.OPENAI_API_KEY,
        additional_kwargs={"api_key": settings.OPENAI_API_KEY},
    )
    callback_manager = CallbackManager(callback_handlers)
    embedding_model = OpenAIEmbedding(
        mode=OpenAIEmbeddingMode.SIMILARITY_MODE,
        model_type=OpenAIEmbeddingModelType.TEXT_EMBED_ADA_002,
        api_key=settings.OPENAI_API_KEY,
    )
    # Use a smaller chunk size to retrieve more granular results
    node_parser = SimpleNodeParser.from_defaults(
        chunk_size=NODE_PARSER_CHUNK_SIZE,
        chunk_overlap=NODE_PARSER_CHUNK_OVERLAP,
        callback_manager=callback_manager,
    )
    service_context = ServiceContext.from_defaults(
        callback_manager=callback_manager,
        llm=llm,
        embed_model=embedding_model,
        node_parser=node_parser,
    )
    return service_context


def build() -> SQLTableRetrieverQueryEngine:

    sqlite_session = Session()
    db_uri = f'postgresql+psycopg2://{DATABASE_USERNAME_DEV}:{DATABASE_PASSWORD_DEV}@{DATABASE_HOST_DEV}:{DATABASE_PORT_DEV}/{DATABASE_NAME_DEV}'

    # Create an SQLAlchemy engine for PostgreSQL
    pg_engine = create_engine(db_uri, echo=True)

    # Create a session for PostgreSQL
    SessionPG = sessionmaker(bind=pg_engine)
    pg_session = SessionPG()

    DBSeeder(pg_session, sqlite_session).seed()

    pg_session.close_all()
    # Initiate connection to the Database

    sql_database = SQLDatabase(engine, include_tables=[
        "respondents",
        "responses",
        # "progresses",
        "treatment_patterns",
        "proxy_respondents",
        "colleagues",
        "demographics"
        # "net_promoter_scores",
        # "respondent_logins",
        # "completed_survey_respondents"
    ])

    llm = OpenAI(
        temperature=0.1,
        model="gpt-4",
        streaming=True,
        api_key=settings.OPENAI_API_KEY,
        additional_kwargs={"api_key": settings.OPENAI_API_KEY}
    )

    embedding_model = OpenAIEmbedding(
        mode=OpenAIEmbeddingMode.SIMILARITY_MODE,
        model_type=OpenAIEmbeddingModelType.TEXT_EMBED_ADA_002,
        api_key=settings.OPENAI_API_KEY,
    )

    # Use a smaller chunk size to retrieve more granular results
    node_parser = SimpleNodeParser.from_defaults(
        chunk_size=NODE_PARSER_CHUNK_SIZE,
        chunk_overlap=NODE_PARSER_CHUNK_OVERLAP,
    )
    service_context = ServiceContext.from_defaults(
        llm=llm,
        embed_model=embedding_model,
        node_parser=node_parser
    )

    query_engine = build_query_engine(
        sql_database, service_context, table_context_dict)

    return query_engine


query_engine = build()


def get_chat_history(
    chat_messages: List[MessageSchema],
) -> List[ChatMessage]:
    """
        Given a list of chat messages, return a list of ChatMessage instances.

        Failed chat messages are filtered out and then the remaining ones are
        sorted by created_at.
    """
    # pre-process chat messages
    chat_messages = [
        m
        for m in chat_messages
        if m.content.strip() and m.status == MessageStatusEnum.SUCCESS
    ]
    # TODO: could be a source of high CPU utilization
    chat_messages = sorted(chat_messages, key=lambda m: m.created_at)

    chat_history = []
    for message in chat_messages:
        role = (
            MessageRole.ASSISTANT
            if message.role == MessageRoleEnum.assistant
            else MessageRole.USER
        )
        chat_history.append(ChatMessage(content=message.content, role=role))

    return chat_history


async def get_chat_engine(
    callback_handler: BaseCallbackHandler,
    conversation: ConversationSchema,
) -> OpenAIAgent:
    service_context = get_tool_service_context([callback_handler])

    vector_sql_query_engine_tools = [
        QueryEngineTool(
            query_engine=query_engine,
            metadata=ToolMetadata(
                name="sql_query_engine",
                description="""
                    A query engine that can fetch data from the sql database and perform some computation and answer questions about survey respondents, treatment modalities, patient demographics, 
                    survey responses, and many other questions that the user pre-selected for the conversation.
                    Any questions about organization-related information should be asked here queries about organizational attributes, respondent geography, and other pre-selected topics. Users can gain insights from a multitude of perspectives, from an individual respondent's demographic to an aggregated view of treatment modalities across regions.
                """.strip(),
            ))
    ]

    response_synth = get_custom_response_synth(service_context)

    qualitative_question_engine = SubQuestionQueryEngine.from_defaults(
        query_engine_tools=vector_sql_query_engine_tools,
        service_context=service_context,
        response_synthesizer=response_synth,
        verbose=settings.VERBOSE,
        use_async=True,
    )

    top_level_sub_tools = [
        QueryEngineTool(
            query_engine=qualitative_question_engine,
            metadata=ToolMetadata(
                name="qualitative_question_engine",
                description="""
                    A query engine that can answer qualitative questions about survey respondents, treatment modalities, patient demographics, 
                    survey responses, and many other questions that the user pre-selected for the conversation.
                    Any questions about organization-related information should be asked here.
                """.strip(),
            ),
        ),
    ]

    chat_llm = OpenAI(
        temperature=0.1,
        model="gpt-4",
        streaming=True,
        api_key=settings.OPENAI_API_KEY,
        additional_kwargs={"api_key": settings.OPENAI_API_KEY},
    )
    chat_messages: List[MessageSchema] = conversation.messages
    chat_history = get_chat_history(chat_messages)
    logger.debug("Chat history: %s", chat_history)

    curr_date = datetime.utcnow().strftime("%Y-%m-%d")

    chat_engine = OpenAIAgent.from_tools(
        tools=top_level_sub_tools,
        llm=chat_llm,
        chat_history=chat_history,
        verbose=settings.VERBOSE,
        system_prompt=SYSTEM_MESSAGE.format(
            table_names=tables_list, curr_date=curr_date),
        callback_manager=service_context.callback_manager,
        max_function_calls=3,
    )

    return chat_engine
