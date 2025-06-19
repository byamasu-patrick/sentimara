import os
from dotenv import load_dotenv
import urllib

load_dotenv()

# Encode username and password
POSTGRES_USER = urllib.parse.quote_plus(os.getenv("POSTGRES_USER"))
POSTGRES_PASSWORD = urllib.parse.quote_plus(os.getenv("POSTGRES_PASSWORD"))

POSTGRES_HOST_NAME = os.getenv("POSTGRES_HOST_NAME")
POSTGRES_PORT = os.getenv("POSTGRES_PORT")
POSTGRES_DB = os.getenv("POSTGRES_DB")

LLM_DATABASE_URL = f"postgresql+psycopg2://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST_NAME}:{POSTGRES_PORT}/{POSTGRES_DB}"
LLM_DATABASE_URL_ASYNC = f"postgresql+asyncpg://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST_NAME}:{POSTGRES_PORT}/{POSTGRES_DB}"
