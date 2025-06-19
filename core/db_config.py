"""
Database configuration module that manages database connection settings and URLs.
This module is separate from the main config to avoid circular imports.
"""
import os
from dotenv import load_dotenv
from core.config import settings

load_dotenv()

# Define DB connection strings
LLM_DATABASE_URL = f"postgresql+psycopg2://{settings.POSTGRES_USER}:{settings.POSTGRES_PASSWORD}@{settings.POSTGRES_HOST_NAME}:{settings.POSTGRES_PORT}/{settings.POSTGRES_DB}"
LLM_DATABASE_URL_ASYNC = f"postgresql+asyncpg://{settings.POSTGRES_USER}:{settings.POSTGRES_PASSWORD}@{settings.POSTGRES_HOST_NAME}:{settings.POSTGRES_PORT}/{settings.POSTGRES_DB}"
