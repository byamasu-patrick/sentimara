import os
from dotenv import load_dotenv

load_dotenv()
raw_port = os.getenv("POSTGRES_PORT")
# Encode username and password
POSTGRES_USER = os.getenv("POSTGRES_USER")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD")

POSTGRES_HOST_NAME = os.getenv("POSTGRES_HOST_NAME")
POSTGRES_PORT = int(raw_port) if raw_port and raw_port.isdigit() else 5432
POSTGRES_DB = os.getenv("POSTGRES_DB")

LLM_DATABASE_URL = f"postgresql+psycopg2://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST_NAME}:{POSTGRES_PORT}/{POSTGRES_DB}"
LLM_DATABASE_URL_ASYNC = f"postgresql+asyncpg://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST_NAME}:{POSTGRES_PORT}/{POSTGRES_DB}"
