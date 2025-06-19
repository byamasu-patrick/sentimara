import logging
import os
import sys
from contextlib import asynccontextmanager

import alembic.config
from alembic import command 
import uvicorn
from alembic import script
from alembic.config import Config
from alembic.runtime import migration
from dotenv import load_dotenv
from fastapi import FastAPI
from llama_index.core.node_parser.text.utils import split_by_sentence_tokenizer
from sqlalchemy.engine import Engine
from starlette.middleware.cors import CORSMiddleware

from api.api import api_router
from chat.engine import init_azure_openai, init_anthropic
from core.config import settings
from libs.db.session import non_async_engine, close_db_connection
from libs.db.wait_for_db import check_database_connection
from loader_io import loader_io_router

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
DATABASE_HOST_DEV = os.getenv("DATABASE_HOST_DEV")
DATABASE_NAME_DEV = os.getenv("DATABASE_NAME_DEV")
DATABASE_PASSWORD_DEV = os.getenv("DATABASE_PASSWORD_DEV")
DATABASE_PORT_DEV = os.getenv("DATABASE_PORT_DEV")
DATABASE_USERNAME_DEV = os.getenv("DATABASE_USERNAME_DEV")

# alembic_cfg = Config("alembic.ini")
# # Run the migration
# command.upgrade(alembic_cfg, "head")


def check_current_head(alembic_cfg: Config, connectable: Engine) -> bool:
    directory = script.ScriptDirectory.from_config(alembic_cfg)
    with connectable.begin() as connection:
        context = migration.MigrationContext.configure(connection)
        return set(context.get_current_heads()) == set(directory.get_heads())


logger = logging.getLogger(__name__)


def __setup_logging(log_level: str):
    log_level = getattr(logging, log_level.upper())
    log_formatter = logging.Formatter(
        "%(asctime)s [%(threadName)-12.12s] [%(levelname)-5.5s]  %(message)s"
    )
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)

    stream_handler = logging.StreamHandler(sys.stdout)
    stream_handler.setFormatter(log_formatter)
    root_logger.addHandler(stream_handler)
    logger.info("Set up logging with log level %s", log_level)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # init_open
    init_azure_openai()
    init_anthropic()
    # first wait for DB to be connectable
    await check_database_connection()
    # Initialize Alembic configuration
    cfg = Config("alembic.ini")
    # Change DB URL to use psycopg2 driver for this specific check
    db_url = settings.DATABASE_URL.replace(
        "postgresql+asyncpg://", "postgresql+psycopg2://"
    )
    cfg.set_main_option("sqlalchemy.url", db_url)
    if not check_current_head(cfg, non_async_engine):
        raise Exception("Database is not up to date. Please run `alembic upgrade head`")

    # Some setup is required to initialize the llama-index sentence splitter
    split_by_sentence_tokenizer()
    yield
    # Shutdown - cleanup connections
    await close_db_connection()


app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_PREFIX}/openapi.json",
    lifespan=lifespan,
)
# if settings.BACKEND_CORS_ORIGINS:
# # allow all origins
# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=settings.BACKEND_CORS_ORIGINS,
#     allow_origin_regex="*",
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(api_router, prefix=settings.API_PREFIX)
app.mount(f"/{settings.LOADER_IO_VERIFICATION_STR}", loader_io_router)


def start():
    print("Running in AppEnvironment: " + settings.ENVIRONMENT.value)
    __setup_logging(settings.LOG_LEVEL)
    # __setup_sentry()
    """Launched with `poetry run start` at root level"""
    if settings.RENDER:
        # on render.com deployments, run migrations
        logger.debug("Running migrations")
        alembic_args = ["--raiseerr", "upgrade", "head"]
        alembic.config.main(argv=alembic_args)
        logger.debug("Migrations complete")
    else:
        logger.debug("Skipping migrations")
    live_reload = not settings.RENDER
    uvicorn.run(
        "app:app",
        host="0.0.0.0",
        port=8000,
        reload=live_reload,
        workers=settings.UVICORN_WORKER_COUNT,
    )

if __name__ == "__main__":
    start()
