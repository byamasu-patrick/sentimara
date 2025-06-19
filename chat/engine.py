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
from typing import List, Optional

import nest_asyncio
import openai
from dotenv import load_dotenv
from llama_index.agent.openai import OpenAIAgent
from llama_index.core import ServiceContext
from llama_index.core.base.llms.types import MessageRole
from llama_index.core.callbacks import CallbackManager
from llama_index.core.callbacks.base_handler import BaseCallbackHandler
from llama_index.core.indices.struct_store.sql_query import SQLTableRetrieverQueryEngine
from llama_index.core.indices.vector_store import VectorStoreIndex
from llama_index.core.llms import ChatMessage, MessageRole
from llama_index.core.node_parser import SimpleNodeParser
from llama_index.core.objects import ObjectIndex, SQLTableNodeMapping, SQLTableSchema
from llama_index.core.settings import Settings
from llama_index.core.tools import QueryEngineTool, ToolMetadata
from llama_index.core.utilities.sql_wrapper import SQLDatabase
from llama_index.llms.openai.base import OpenAI
from llama_index.question_gen.openai import OpenAIQuestionGenerator
from sqlalchemy.engine import create_engine
from sqlalchemy.orm import sessionmaker
from llama_index.core.workflow.handler import WorkflowHandler
from llama_index.llms.openai import OpenAI
from chat.constants import SUB_QUESTION_SYSTEM_PROMPT, SYSTEM_PROMPT
from chat.custom_sub_question_query_engine import CustomSubQuestionQueryEngine
from chat.qa_response_synth import get_custom_response_synth
from chat.core.settings import CustomSettings
from chat.utils import table_groups, tables_list
from core.config import settings
from libs.db.session import non_async_engine
from libs.models.chatdb import MessageRoleEnum, MessageStatusEnum
from schema import Conversation as ConversationSchema
from schema import Message as MessageSchema
from schema import QueryEngineInfo
from .workflow import (
    AgentConfig,
    ConciergeAgent,
)

load_dotenv()

logger = logging.getLogger(__name__)
logger.info("Applying nested asyncio patch")
nest_asyncio.apply()

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
    response = openai.completions.create(
        model=settings.MODEL,
        prompt=prompt_template,
        temperature=0.7,
    )

    return response.choices[0].text.strip()


class QueryEngineData:
    def __init__(self, name: str, query_engine: QueryEngineInfo):
        self._name: str = name
        self._query_engine: QueryEngineInfo = query_engine

    @property
    def name(self) -> str:
        return self._name

    @name.setter
    def name(self, value: str) -> None:
        if not isinstance(value, str):
            raise ValueError("Name must be a string.")
        self._name = value

    @property
    def query_engine(self) -> QueryEngineInfo:
        return self._query_engine

    @query_engine.setter
    def query_engine(self, value: QueryEngineInfo) -> None:
        if not isinstance(value, QueryEngineInfo):
            raise ValueError("Query engine name must be of type QueryEngineInfo.")
        self._query_engine = value

def init_azure_openai():
    from llama_index.core.constants import DEFAULT_TEMPERATURE
    from llama_index.embeddings.azure_openai import AzureOpenAIEmbedding
    from llama_index.llms.azure_openai import AzureOpenAI
    from llama_index.core import Settings

    # LLM Configuration
    max_tokens = os.getenv("LLM_MAX_TOKENS", 16384)
    llm_config = {
        "model": settings.MODEL,
        "deployment_name": settings.AZURE_LLM_DEPLOYMENT_NAME,
        "api_key": settings.AZURE_OPENAI_API_KEY,
        "azure_endpoint": settings.AZURE_OPENAI_ENDPOINT,
        "api_version": settings.AZURE_OPENAI_API_VERSION,
        "temperature": float(os.getenv("LLM_TEMPERATURE", DEFAULT_TEMPERATURE)),
        "max_tokens": int(max_tokens) if max_tokens is not None else 16384,
    }
    Settings.llm = AzureOpenAI(**llm_config)

    # Embedding Configuration
    dimensions = settings.EMBEDDING_DIM
    embed_config = {
        "model": settings.EMBEDDING_MODEL,
        "deployment_name": settings.AZURE_EMBEDDING_DEPLOYMENT_NAME,
        "api_key": settings.AZURE_OPENAI_API_KEY,
        "azure_endpoint": settings.AZURE_OPENAI_ENDPOINT,
        "api_version": settings.AZURE_OPENAI_API_VERSION,
        "dimensions": int(dimensions) if dimensions is not None else None,
    }
    Settings.embed_model = AzureOpenAIEmbedding(**embed_config)

    # Chunk settings
    Settings.chunk_size = int(os.getenv("CHUNK_SIZE", "1024"))
    Settings.chunk_overlap = int(os.getenv("CHUNK_OVERLAP", "20"))


def init_openai():
    from llama_index.core.constants import DEFAULT_TEMPERATURE
    from llama_index.embeddings.openai import OpenAIEmbedding
    from llama_index.llms.openai import OpenAI

    max_tokens = os.getenv("LLM_MAX_TOKENS", 16384)
    config = {
        "model": settings.MODEL,
        "temperature": float(os.getenv("LLM_TEMPERATURE", DEFAULT_TEMPERATURE)),
        "api_key": settings.OPENAI_API_KEY,
        "max_tokens": int(max_tokens) if max_tokens is not None else 16384,
    }
    Settings.llm = OpenAI(**config)

    dimensions = settings.EMBEDDING_DIM
    config = {
        "model": settings.EMBEDDING_MODEL,
        "dimensions": int(dimensions) if dimensions is not None else None,
    }
    Settings.embed_model = OpenAIEmbedding(**config)

    Settings.chunk_size = int(os.getenv("CHUNK_SIZE", "1024"))
    Settings.chunk_overlap = int(os.getenv("CHUNK_OVERLAP", "20"))

def init_anthropic():
    from llama_index.core.constants import DEFAULT_TEMPERATURE
    from llama_index.llms.anthropic import Anthropic
    from llama_index.embeddings.openai import OpenAIEmbedding

    max_tokens = os.getenv("LLM_MAX_TOKENS", 16384)
    config = {
        "model": settings.SQL_MODEL,
        "temperature": float(os.getenv("LLM_TEMPERATURE", DEFAULT_TEMPERATURE)),
        "api_key": settings.ANTHROPIC_API_KEY,
        "max_tokens": int(max_tokens) if max_tokens is not None else 16384,
    }
    CustomSettings.code_llm = Anthropic(**config)

    dimensions = settings.EMBEDDING_DIM
    config = {
        "model": settings.EMBEDDING_MODEL,
        "dimensions": int(dimensions) if dimensions is not None else None,
    }
    CustomSettings.embed_model = OpenAIEmbedding(**config)
    CustomSettings.chunk_size = int(os.getenv("CHUNK_SIZE", "1024"))
    CustomSettings.chunk_overlap = int(os.getenv("CHUNK_OVERLAP", "20"))

def table_index_builder(
    sql_database: SQLDatabase,
    table_context_dict: dict[str, str],
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
        objects=table_schema_objs,
        object_mapping=table_node_mapping,
        index_cls=VectorStoreIndex,
    )

    return obj_index


def build_query_engine(
    sql_database: SQLDatabase,
    table_context_dict: dict[str, str],  # type: ignore,
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
    from chat.core.prompt import TEXT_TO_SQL_PROMPT

    obj_index: ObjectIndex = table_index_builder(
        sql_database, table_context_dict=table_context_dict
    )

    kwargs = {
        "similarity_top_k": 3
    }

    query_engine = SQLTableRetrieverQueryEngine(
        sql_database=sql_database,
        table_retriever=obj_index.as_retriever(**kwargs), 
        llm=CustomSettings.code_llm,
        text_to_sql_prompt=TEXT_TO_SQL_PROMPT,
        sql_only=False,
    )

    return query_engine


def get_tool_service_context() -> ServiceContext:
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
    # Use a smaller chunk size to retrieve more granular results
    node_parser = SimpleNodeParser.from_defaults(
        chunk_size=Settings.chunk_size,
        chunk_overlap=Settings.chunk_size,
        callback_manager=Settings.callback_manager,
    )
    
    service_context = ServiceContext.from_defaults(
        callback_manager=Settings.callback_manager,
        llm=Settings.llm,
        embed_model=Settings.embed_model,
        node_parser=node_parser,
    )
    return service_context


def build() -> tuple[List[QueryEngineInfo], SQLTableRetrieverQueryEngine]:
    """
    Initializes and sets up query engines for database interaction.

    This function is responsible for creating and configuring various components necessary for the chat system's query processing.
    It establishes connections to both SQLite and PostgreSQL databases, seeds the databases, and initializes components such as
    OpenAI language models, embedding models, and node parsers. It then dynamically creates a list of QueryEngineInfo objects,
    each representing a configured query engine for specific tables in the database.

    Returns:
    List[QueryEngineInfo]: A list of QueryEngineInfo instances, each containing a configured query engine for database interaction.
    """
    db_uri = f"postgresql+psycopg2://{settings.DATABASE_USERNAME_DEV}:{settings.DATABASE_PASSWORD_DEV}@{settings.DATABASE_HOST_DEV}:{settings.DATABASE_PORT_DEV}/{settings.DATABASE_NAME_DEV}"

    # Create an SQLAlchemy engine for PostgreSQL
    pg_engine = create_engine(db_uri, echo=True)

    # Create a session for PostgreSQL
    # TODO: Variable name "SessionPG" doesn't conform to snake_case naming style
    SessionPG = sessionmaker(bind=pg_engine)
    pg_session = SessionPG()

    pg_session.close_all()
    # Create query engines dynamically
    query_engines: List[QueryEngineData] = []

    for group in table_groups:
        sql_database = SQLDatabase(engine=non_async_engine, include_tables=[group.name])

        sq_qe = build_query_engine(
            sql_database, {group.name: table_context_dict[group.name]}
        )
        query_engine: QueryEngineInfo = QueryEngineInfo(
            engine=sq_qe,  # type" ignore
            query_engine_description=group.query_engine_description,
            top_query_engine_description=group.top_query_engine_description,
        )
        query_engines.append(
            QueryEngineData(
                f"{group.name}_query_engine",
                query_engine,
            )
        )

    return query_engines


# Get the dynamically created query engines
query_engines = build()


def get_chat_history(
    chat_messages: List[MessageSchema],
    last_ai_message_id: Optional[str] = None,
) -> List[ChatMessage]:
    """
    Given a list of chat messages, return a list of ChatMessage instances.

    Failed chat messages are filtered out and then the remaining ones are
    sorted by created_at.
    """
    # pre-process chat messages
    chat_messages = []

    for m in chat_messages:
        if last_ai_message_id != m.id:
            if m.content.strip() and m.status == MessageStatusEnum.SUCCESS:
                chat_messages.append(m)

    # TODO: could be a source of high CPU utilization
    chat_messages = sorted(chat_messages, key=lambda m: m.created_at)  # type: ignore

    chat_history = []
    for message in chat_messages:
        role = (
            MessageRole.ASSISTANT
            if message.role == MessageRoleEnum.assistant
            else MessageRole.USER
        )
        chat_history.append(ChatMessage(content=message.content, role=role))  # type: ignore

    return chat_history

def get_query_engine_tools(
    callback_handler: BaseCallbackHandler,
):
    """
    Asynchronously creates and configures an OpenAIAgent for handling chat interactions.

    This function sets up an OpenAIAgent with various tools and configurations required for processing and responding to chat messages. It initializes the service context, sets up query engine tools, creates sub-question query engines, and prepares the top-level sub-tools for the chat system. The function also configures an OpenAI language model and processes the chat history to be used by the agent.

    Parameters:
    callback_handler (BaseCallbackHandler): The callback handler to be used in the service context.

    Returns:
    List[QueryEngineTool]: A list of QueryEngineTool instances configured for the chat system.
    """
    question_gen = OpenAIQuestionGenerator.from_defaults(
        llm=Settings.llm, verbose=True, prompt_template_str=SUB_QUESTION_SYSTEM_PROMPT
    )

    callback_manager = CallbackManager([callback_handler])
    Settings.callback_manager = callback_manager

    response_synth = get_custom_response_synth(
        callback_manager=callback_manager,
    )

    vector_sql_query_engine_tools = [
        QueryEngineTool(
            query_engine=query_engine.query_engine.engine,
            metadata=ToolMetadata(
                name=query_engine.name,
                description=query_engine.query_engine.query_engine_description,
            ),
            resolve_input_errors=True,
        )
        for query_engine in query_engines
    ]

    qualitative_question_engines = [
        CustomSubQuestionQueryEngine.from_defaults(
            query_engine_tools=[vector_sql_query_engine_tool],
            response_synthesizer=response_synth,
            llm=Settings.llm,
            verbose=settings.VERBOSE,
            question_gen=question_gen,
            use_async=True,
            callback_manager=callback_manager,
        )
        for vector_sql_query_engine_tool in vector_sql_query_engine_tools
    ]

    top_level_sub_tools = [
        QueryEngineTool(
            query_engine=qualitative_question_engine,
            metadata=ToolMetadata(
                name=f"qualitative_{query_engines[idx].name}",
                description=query_engines[
                    idx
                ].query_engine.top_query_engine_description.strip(),
            ),
            resolve_input_errors=True,
        )
        for idx, qualitative_question_engine in enumerate(qualitative_question_engines)
    ]

    return top_level_sub_tools


def get_agent_configs(
    callback_handler: BaseCallbackHandler,
) -> list[AgentConfig]:
    curr_date = datetime.utcnow().strftime("%Y-%m-%d")

    return [
        AgentConfig(
            name="PI Survey Data Analyst (7-Table Scope)",
            description="""Specialized agent for analyzing Primary Immunodeficiency survey data across 7 core tables. 
            Capabilities strictly limited to:
            - Patient demographics & geographic distribution
            - Treatment modalities and pattern analysis
            - Respondent network mapping
            - Survey completion metrics
            - Patient-reported experience measures
            
            Exclusively uses structured data from: 
            {tables}. Provides IUIS-aligned insights without external data integration.""".format(tables=", ".join(tables_list)),
            system_prompt=SYSTEM_PROMPT.format(
                table_names=tables_list, 
                curr_date=curr_date
            ),
            tools=get_query_engine_tools(callback_handler),
        ),
    ]


async def workflow_runner(
    callback_handler: BaseCallbackHandler,
    user_message: str,
    conversation: ConversationSchema,
    last_ai_message_id: Optional[str] = None,
):
    """Main function to run the workflow."""
    agent_configs = get_agent_configs(
        callback_handler=callback_handler,
    )
    workflow = ConciergeAgent(timeout=None)

    chat_messages: List[MessageSchema] = conversation.messages
    chat_history = get_chat_history(chat_messages, last_ai_message_id)
    logger.debug("Chat history: %s", chat_history)
    # draw a diagram of the workflow
    # draw_all_possible_flows(workflow, filename="workflow.html")

    handler: WorkflowHandler = workflow.run(
        user_msg=user_message,
        agent_configs=agent_configs,
        llm=Settings.llm,
        chat_history=chat_history,
    )

    return handler



async def get_chat_engine(
    callback_handler: BaseCallbackHandler,
    conversation: ConversationSchema,
    last_ai_message_id: Optional[str] = None,
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
    from llama_index.core.constants import DEFAULT_TEMPERATURE

    config = {
        "model": settings.MODEL,
        "temperature": float(os.getenv("LLM_TEMPERATURE", DEFAULT_TEMPERATURE)),
        "api_key": settings.OPENAI_API_KEY,
        "max_tokens": int(os.getenv("MAX_TOKENS", 4096)),
    }

    llm = OpenAI(**config)
    curr_date = datetime.utcnow().strftime("%Y-%m-%d")

    question_gen = OpenAIQuestionGenerator.from_defaults(
        llm=Settings.llm, verbose=True, prompt_template_str=SUB_QUESTION_SYSTEM_PROMPT
    )

    callback_manager = CallbackManager([callback_handler])
    Settings.callback_manager = callback_manager

    response_synth = get_custom_response_synth(
        callback_manager=callback_manager,
    )

    vector_sql_query_engine_tools = [
        QueryEngineTool(
            query_engine=query_engine.query_engine.engine,
            metadata=ToolMetadata(
                name=query_engine.name,
                # Correctly reference the attribute here
                description=query_engine.query_engine.query_engine_description,
            ),
            resolve_input_errors=True,
        )
        for query_engine in query_engines
    ]  # Use enumerate to get idx

    qualitative_question_engines = [
        CustomSubQuestionQueryEngine.from_defaults(
            query_engine_tools=[vector_sql_query_engine_tool],
            llm=Settings.llm,
            response_synthesizer=response_synth,
            verbose=settings.VERBOSE,
            question_gen=question_gen,
            use_async=True,
            callback_manager=callback_manager,
        )
        for vector_sql_query_engine_tool in vector_sql_query_engine_tools
    ]

    top_level_sub_tools = [
        QueryEngineTool(
            query_engine=qualitative_question_engine,
            metadata=ToolMetadata(
                name=f"qualitative_{query_engines[idx].name}",
                description=query_engines[
                    idx
                ].query_engine.top_query_engine_description.strip(),
            ),
            resolve_input_errors=True,
        )
        for idx, qualitative_question_engine in enumerate(qualitative_question_engines)
    ]

    chat_messages: List[MessageSchema] = conversation.messages
    chat_history = get_chat_history(chat_messages, last_ai_message_id)
    logger.debug("Chat history: %s", chat_history)

    chat_engine = OpenAIAgent.from_tools(
        tools=top_level_sub_tools,  # type: ignore
        llm=llm,  # type: ignore
        chat_history=chat_history,
        verbose=settings.VERBOSE,
        system_prompt=SYSTEM_PROMPT.format(
            table_names=tables_list, curr_date=curr_date
        ),
        callback_manager=Settings.callback_manager,  # type: ignore
        max_function_calls=3,
    )

    return chat_engine
