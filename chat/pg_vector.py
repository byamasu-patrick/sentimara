import sqlalchemy
from llama_index.vector_stores.postgres import PGVectorStore
from llama_index.vector_stores.types import VectorStore
from sqlalchemy import create_engine
from sqlalchemy.engine import make_url
from sqlalchemy.orm import sessionmaker

from core.config import settings
from libs.db.session import SessionLocal as AppSessionLocal
from libs.db.session import engine as app_engine

# TODO: Constant name "singleton_instance" doesn't conform to UPPER_CASE naming style
singleton_instance = None
# TODO: Constant name "did_run_setup" doesn't conform to UPPER_CASE naming style
did_run_setup = False


class CustomPGVectorStore(PGVectorStore):
    """
    Custom PGVectorStore that uses the same connection pool as the FastAPI app.
    """

    def _connect(self) -> None:
        self._engine = create_engine(self.connection_string)
        self._session = sessionmaker(self._engine)

        # Use our existing app engine and session so we can use the same connection pool
        self._async_engine = app_engine
        self._async_session = AppSessionLocal

    async def close(self) -> None:
        """_summary_"""
        self._session.close_all()
        self._engine.dispose()

        await self._async_engine.dispose()

    def _create_tables_if_not_exists(self) -> None:
        pass

    def _create_extension(self) -> None:
        pass

    async def run_setup(self) -> None:
        """_summary_"""
        global did_run_setup
        if did_run_setup:
            return
        async with AppSessionLocal() as session:
            async with session.begin():
                statement = sqlalchemy.text("CREATE EXTENSION IF NOT EXISTS vector")
                await session.execute(statement)
                await session.commit()

        async with AppSessionLocal() as session:
            async with session.begin():
                conn = await session.connection()
                await conn.run_sync(self._base.metadata.create_all)
        did_run_setup = True


async def get_vector_store_singleton() -> VectorStore:
    """_summary_

    Returns:
        VectorStore: _description_
    """
    global singleton_instance
    if singleton_instance is not None:
        return singleton_instance
    url = make_url(settings.DATABASE_URL)
    singleton_instance = CustomPGVectorStore.from_params(
        url.host,
        url.port or 5432,
        url.database,
        url.username,
        url.password,
        settings.VECTOR_STORE_TABLE_NAME,
    )
    return singleton_instance
