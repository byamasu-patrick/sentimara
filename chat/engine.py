"""
The engine module is responsible for setting up and managing the core functionalities of the chat system. 
It includes functions for initializing the conversation engine, building query engines for database interaction, 
processing chat messages, and creating instances of OpenAI agents for handling chat interactions. 
This module plays a central role in integrating various components like database handling, 
query processing, and chat interface to facilitate effective communication and data retrieval.
"""

import logging
import os
from datetime import datetime
from typing import List, Literal

import nest_asyncio
import openai
from dotenv import load_dotenv
from llama_index import ServiceContext, SQLDatabase, VectorStoreIndex
from llama_index.agent import OpenAIAgent
from llama_index.callbacks.base import BaseCallbackHandler, CallbackManager
from llama_index.embeddings.openai import (
    OpenAIEmbedding,
    OpenAIEmbeddingMode,
    OpenAIEmbeddingModelType,
)
from llama_index.indices.struct_store import SQLTableRetrieverQueryEngine
from llama_index.llms import ChatMessage, OpenAI
from llama_index.llms.base import MessageRole
from llama_index.node_parser import SimpleNodeParser
from llama_index.objects import ObjectIndex, SQLTableNodeMapping, SQLTableSchema
from llama_index.prompts import PromptTemplate
from llama_index.query_engine import PGVectorSQLQueryEngine, SubQuestionQueryEngine
from llama_index.tools import QueryEngineTool, ToolMetadata
from sqlalchemy.engine import create_engine
from sqlalchemy.orm import sessionmaker

# from llama_index.vector_stores.types import (
#     MetadataFilters,
#     ExactMatchFilter,
# )
from chat.constants import (
    NODE_PARSER_CHUNK_OVERLAP,
    NODE_PARSER_CHUNK_SIZE,
    SYSTEM_MESSAGE,
    TEXT_TO_SQL_TMPL,
)
from chat.qa_response_synth import get_custom_response_synth
from chat.utils import table_groups, tables_list
from core.config import settings
from libs.models.chatdb import MessageRoleEnum, MessageStatusEnum

# TODO: Unused LLM_DATABASE_URL imported from libs.models.db
from libs.models.db import (
    LLM_DATABASE_URL,
    Session,
    engine,
    init_db,
    table_context_dict,
)
from schema import Conversation as ConversationSchema
from schema import Message as MessageSchema
from schema import QueryEngineInfo
from seeder.db_seeder import DBSeeder

load_dotenv()
DATABASE_HOST_DEV = os.getenv("DATABASE_HOST_DEV")
DATABASE_NAME_DEV = os.getenv("DATABASE_NAME_DEV")
DATABASE_PASSWORD_DEV = os.getenv("DATABASE_PASSWORD_DEV")
DATABASE_PORT_DEV = os.getenv("DATABASE_PORT_DEV")
DATABASE_USERNAME_DEV = os.getenv("DATABASE_USERNAME_DEV")
logger = logging.getLogger(__name__)

logger.info("Applying nested asyncio patch")
nest_asyncio.apply()


OPENAI_TOOL_LLM_NAME = "gpt-4"
OPENAI_CHAT_LLM_NAME = "gpt-4"

init_db()


def get_conversation_headline(prompt: str):
    """
    Generates a concise and informative headline from a given survey question.

    This function utilizes the OpenAI Completion API to create a headline that captures the essence of the input question in a brief and clear manner. It formats the input question into a prompt template and requests a headline generation from the API.

    Parameters:
    prompt (str): The survey question from which a headline is to be generated.

    Returns:
    str: A headline derived from the survey question, providing a succinct summary or overview of the question's topic.
    """
    prompt_template = f""""
    Create a concise headline from the given question. The headline should be simple and clearly reflect the essence of the question.
    
    For example, if the question is 'How many respondents have participated in this survey?', a suitable headline could be 'Survey Participation Overview'.
    
    Question: {prompt}
    """
    response = openai.Completion.create(
        engine="text-davinci-003",
        prompt=prompt_template,
        temperature=0.7,
        max_tokens=100,
    )

    return response.choices[0].text.strip()


def table_index_builder(
    # TODO: Redefining name 'table_context_dict' from outer scope (line 39)
    sql_database: SQLDatabase,
    table_context_dict: dict[str, Literal],
) -> ObjectIndex:
    """
    Builds and returns an ObjectIndex based on the schema of tables in a SQL database.

    This function creates an index of table schemas, which is useful for organizing and accessing
    database information efficiently. It iterates over each table name provided in the table context
    dictionary, constructs a schema object for each table, and then compiles these into an ObjectIndex.

    Parameters:
    sql_database (SQLDatabase): The SQL database instance containing the tables.
    table_context_dict (dict[str, Literal]): A dictionary mapping table names to their context strings.

    Returns:
    ObjectIndex: An index of SQLTableSchema objects representing the schema of each table in the database.
    """
    table_node_mapping = SQLTableNodeMapping(sql_database)
    table_schema_objs: list[SQLTableSchema] = []

    # Build our table schema
    for table_name in table_context_dict:
        table_schema = SQLTableSchema(
            table_name=table_name, context_str=table_context_dict[table_name]
        )
        table_schema_objs.append(table_schema)

    obj_index = ObjectIndex.from_objects(
        table_schema_objs,
        table_node_mapping,
        VectorStoreIndex,
    )

    return obj_index


def build_query_engine(
    sql_database: SQLDatabase,
    service_context: ServiceContext,
    # TODO: Redefining name 'table_context_dict' from outer scope (line 52)
    table_context_dict: dict[str, str],
) -> SQLTableRetrieverQueryEngine:
    """
    Constructs and returns a SQLTableRetrieverQueryEngine for querying the SQL database.

    This function initializes a query engine that is capable of converting natural language queries into SQL queries.
    It uses a text-to-SQL prompt template to guide this conversion process and leverages the provided service context
    for query execution. The query engine is configured with specific context parameters for each table in the database,
    as defined in the table_context_dict.

    Parameters:
    sql_database (SQLDatabase): The SQL database to be queried.
    service_context (ServiceContext): The service context used for query execution and other operations.
    table_context_dict (dict[str, str]): A dictionary mapping table names to context-specific parameters for querying.

    Returns:
    SQLTableRetrieverQueryEngine: A query engine configured for the specified SQL database and service context.
    """
    text_to_sql_prompt = PromptTemplate(TEXT_TO_SQL_TMPL)

    query_engine = PGVectorSQLQueryEngine(
        sql_database=sql_database,
        text_to_sql_prompt=text_to_sql_prompt,
        service_context=service_context,
        context_query_kwargs=table_context_dict,
    )

    return query_engine


def get_tool_service_context(
    callback_handlers: List[BaseCallbackHandler], temperature: float
) -> ServiceContext:
    """
    Creates and configures a ServiceContext object for use with OpenAI agents.

    This function sets up a ServiceContext with the specified temperature for the OpenAI model,
    initializes the callback manager with the provided callback handlers, and configures the
    embedding model for use in the chat system. It plays a crucial role in integrating different
    components necessary for handling chat interactions and data processing.

    Parameters:
    callback_handlers (List[BaseCallbackHandler]): A list of callback handlers to be used in the callback manager.
    temperature (float): The temperature setting for the OpenAI model, controlling the creativity of the responses.

    Returns:
    ServiceContext: An instance of ServiceContext configured with the necessary components for the chat system.
    """
    # function implementation
    llm = OpenAI(
        temperature=temperature,
        model="gpt-3.5-turbo-0613",
        streaming=False,
        api_key=settings.OPENAI_API_KEY,
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


def build() -> List[QueryEngineInfo]:
    """
    Initializes and sets up query engines for database interaction.

    This function is responsible for creating and configuring various components necessary for the chat system's query processing.
    It establishes connections to both SQLite and PostgreSQL databases, seeds the databases, and initializes components such as
    OpenAI language models, embedding models, and node parsers. It then dynamically creates a list of QueryEngineInfo objects,
    each representing a configured query engine for specific tables in the database.

    Returns:
    List[QueryEngineInfo]: A list of QueryEngineInfo instances, each containing a configured query engine for database interaction.
    """
    sqlite_session = Session()
    db_uri = f"postgresql+psycopg2://{DATABASE_USERNAME_DEV}:{DATABASE_PASSWORD_DEV}@{DATABASE_HOST_DEV}:{DATABASE_PORT_DEV}/{DATABASE_NAME_DEV}"

    # Create an SQLAlchemy engine for PostgreSQL
    pg_engine = create_engine(db_uri, echo=True)

    # Create a session for PostgreSQL
    # TODO: Variable name "SessionPG" doesn't conform to snake_case naming style
    SessionPG = sessionmaker(bind=pg_engine)
    pg_session = SessionPG()

    DBSeeder(pg_session, sqlite_session).seed()

    pg_session.close_all()
    llm = OpenAI(
        temperature=0.1,
        model=OPENAI_TOOL_LLM_NAME,
        streaming=False,
        api_key=settings.OPENAI_API_KEY,
    )

    embedding_model = OpenAIEmbedding(
        mode=OpenAIEmbeddingMode.SIMILARITY_MODE,
        model_type=OpenAIEmbeddingModelType.TEXT_EMBED_ADA_002,
        api_key=settings.OPENAI_API_KEY,
    )

    node_parser = SimpleNodeParser.from_defaults(
        chunk_size=NODE_PARSER_CHUNK_SIZE,
        chunk_overlap=NODE_PARSER_CHUNK_OVERLAP,
    )
    service_context = ServiceContext.from_defaults(
        llm=llm, embed_model=embedding_model, node_parser=node_parser
    )
    # TODO: Redefining name 'query_engines' from outer scope (line 211)
    # Create query engines dynamically
    query_engines: List[QueryEngineInfo] = []

    for group in table_groups:
        sql_database = SQLDatabase(engine, include_tables=[group.name])

        sq_qe = build_query_engine(
            sql_database, service_context, {group.name: table_context_dict[group.name]}
        )
        query_engine: QueryEngineInfo = QueryEngineInfo(
            engine=sq_qe,
            query_engine_description=group.query_engine_description,
            top_query_engine_description=group.top_query_engine_description,
        )
        query_engines.append(query_engine)

    return query_engines


# Get the dynamically created query engines
query_engines = build()


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
    temperature: float,
) -> OpenAIAgent:
    """
    Asynchronously creates and configures an OpenAIAgent for handling chat interactions.

    This function sets up an OpenAIAgent with various tools and configurations required for processing and responding to chat messages. It initializes the service context, sets up query engine tools, creates sub-question query engines, and prepares the top-level sub-tools for the chat system. The function also configures an OpenAI language model and processes the chat history to be used by the agent.

    Parameters:
    callback_handler (BaseCallbackHandler): The callback handler to be used in the service context.
    conversation (ConversationSchema): The schema representing the conversation for which the chat engine is being set up.
    temperature (float): The temperature setting for the OpenAI model, controlling the creativity of the responses.

    Returns:
    OpenAIAgent: An instance of OpenAIAgent configured with the necessary tools and settings for chat interaction.
    """
    service_context = get_tool_service_context(
        [callback_handler], temperature=temperature
    )
    # [callback_handler])
    vector_sql_query_engine_tools = [
        QueryEngineTool(
            query_engine=query_engine.engine,
            metadata=ToolMetadata(
                name=f"sql_query_engine_{idx}",
                # Correctly reference the attribute here
                description=query_engine.query_engine_description,
            ),
        )
        for idx, query_engine in enumerate(query_engines)
    ]  # Use enumerate to get idx

    response_synth = get_custom_response_synth(service_context)

    qualitative_question_engines = [
        SubQuestionQueryEngine.from_defaults(
            query_engine_tools=[vector_sql_query_engine_tool],
            service_context=service_context,
            response_synthesizer=response_synth,
            verbose=settings.VERBOSE,
            use_async=True,
        )
        for idx, vector_sql_query_engine_tool in enumerate(
            vector_sql_query_engine_tools
        )
    ]

    top_level_sub_tools = [
        QueryEngineTool(
            query_engine=qualitative_question_engine,
            metadata=ToolMetadata(
                name=f"qualitative_question_engine_{idx}",
                description=query_engines[idx].top_query_engine_description.strip(),
            ),
        )
        for idx, qualitative_question_engine in enumerate(qualitative_question_engines)
    ]

    chat_llm = OpenAI(
        temperature=temperature,
        model=OPENAI_CHAT_LLM_NAME,
        streaming=True,
        api_key=settings.OPENAI_API_KEY,
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
        # TODO: Should the SYSTEM_MESSAGE constant NOT be renamed to something more descriptive like SYSTEM_PROMPT, or SUPER_PROMPT?
        system_prompt=SYSTEM_MESSAGE.format(
            table_names=tables_list, curr_date=curr_date
        ),
        callback_manager=service_context.callback_manager,
        max_function_calls=3,
    )

    return chat_engine
