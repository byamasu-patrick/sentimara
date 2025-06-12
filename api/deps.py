"""
This module provides a generator function for creating and managing asynchronous database sessions using SQLAlchemy's AsyncSession. The get_db function yields a database session that can be used throughout an asynchronous request lifecycle in a FastAPI application, ensuring that database connections are properly opened and closed.
"""
from typing import Generator

from sqlalchemy.ext.asyncio import AsyncSession

from libs.db.session import SessionLocal


async def get_db() -> Generator[AsyncSession, None, None]:
    async with SessionLocal() as db:
        yield db
