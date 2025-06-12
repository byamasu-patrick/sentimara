"""
Database configuration module that manages database connection settings and URLs.
This module is separate from the main config to avoid circular imports.
"""

import os
from dotenv import load_dotenv

load_dotenv()

# Load environment variables
POSTGRES_USER = os.getenv("POSTGRES_USER")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD")
POSTGRES_DB = os.getenv("POSTGRES_DB")
POSTGRES_HOST_NAME = os.getenv("POSTGRES_HOST_NAME")
POSTGRES_PORT = os.getenv("POSTGRES_PORT")

# Define DB connection strings
LLM_DATABASE_URL = f"postgresql+psycopg2://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST_NAME}:{POSTGRES_PORT}/{POSTGRES_DB}"
LLM_DATABASE_URL_ASYNC = f"postgresql+asyncpg://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST_NAME}:{POSTGRES_PORT}/{POSTGRES_DB}"
