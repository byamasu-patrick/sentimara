import os
from contextlib import asynccontextmanager

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy.orm import sessionmaker

# from core.config import settings
from core.db_config import LLM_DATABASE_URL, LLM_DATABASE_URL_ASYNC

load_dotenv()
#  Load environment variables
POSTGRES_USER = os.getenv("POSTGRES_USER")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD")
POSTGRES_DB = os.getenv("POSTGRES_DB")
POSTGRES_HOST_NAME = os.getenv("POSTGRES_HOST_NAME")
POSTGRES_PORT = os.getenv("POSTGRES_PORT")
# Define DB connection string
LLM_DATABASE_URL = f"postgresql+psycopg2://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST_NAME}:{POSTGRES_PORT}/{POSTGRES_DB}"

LLM_DATABASE_URL_ASYNC = f"postgresql+asyncpg://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST_NAME}:{POSTGRES_PORT}/{POSTGRES_DB}"

engine = create_async_engine(
    LLM_DATABASE_URL_ASYNC,
    pool_pre_ping=True,
    pool_size=10,
    max_overflow=20,
    pool_recycle=3600,
    pool_timeout=120,
    echo=True,  # Enable SQL logging for debugging
)

non_async_engine = create_engine(LLM_DATABASE_URL)
Session = sessionmaker(bind=non_async_engine)
SessionLocal = async_sessionmaker(autocommit=False, autoflush=False, bind=engine)

@asynccontextmanager
async def get_async_session():
    """Provide a transactional scope around a series of operations."""
    session = SessionLocal()
    try:
        yield session
        await session.commit()
    except Exception:
        await session.rollback()
        raise
    finally:
        await session.close()

# Function to dispose engine on shutdown
async def close_db_connection():
    await engine.dispose()
