"""
This module is responsible for managing the configuration settings of the JMF-OpenAI-LLM Integration project.

It defines classes for setting up and validating various application configurations, including database connections,
API keys, CORS origins, log levels, and other environment-specific settings. The settings are primarily loaded from
environment variables, with support for different environments like local, preview, and production. Additional
properties and validators are used to preprocess and validate configuration data, ensuring the correct setup
of the application's runtime environment.
"""

import os
from enum import Enum
from typing import List, Union

from dotenv import load_dotenv
from pydantic import AnyHttpUrl, validator
from pydantic_settings import BaseSettings, SettingsConfigDict

# from libs.db.session import LLM_DATABASE_URL_ASYNC
from core.db_config import LLM_DATABASE_URL_ASYNC

load_dotenv()


class AppEnvironment(str, Enum):
    """
    Enum for app environments.
    """

    LOCAL = "local"
    PREVIEW = "preview"
    PRODUCTION = "production"


is_pull_request: bool = os.environ.get("IS_PULL_REQUEST") == "true"
is_preview_env: bool = os.environ.get("IS_PREVIEW_ENV") == "true"


class PreviewPrefixedSettings(BaseSettings):
    """
    Settings class that uses a different env_prefix for PR Preview deployments.

    PR Preview deployments should source their secret environment variables with
    the `PREVIEW_` prefix, while regular deployments should source them from the
    environment variables with no prefix.

    Some environment variables (like `DATABASE_URL`) use Render.com's capability to
    automatically set environment variables to their preview value for PR Preview
    deployments, so they are not prefixed.
    """

    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY")  # type: ignore
    ANTHROPIC_API_KEY: str = os.getenv("ANTHROPIC_API_KEY")  # type: ignore


class Settings(PreviewPrefixedSettings):
    """
    Application settings.
    """

    PROJECT_NAME: str = "ModellMind AI - Jeffrey Model Foundation"
    API_PREFIX: str = "/api"
    DATABASE_URL: str = LLM_DATABASE_URL_ASYNC
    LOG_LEVEL: str = "DEBUG"
    IS_PULL_REQUEST: bool = False
    RENDER: bool = False
    # CDN_BASE_URL: str
    VECTOR_STORE_TABLE_NAME: str = "pg_vector_store"
    # SENTRY_DSN: Optional[str]
    # RENDER_GIT_COMMIT: Optional[str]
    LOADER_IO_VERIFICATION_STR: str = "loaderio-e51043c635e0f4656473d3570ae5d9ec"
    MODEL: str = "gpt-4o"
    # SQL_MODEL: str = "claude-3-7-sonnet-20250219"
    SQL_MODEL: str = "claude-3-5-sonnet-latest"
    # Name of the embedding model to use.
    EMBEDDING_MODEL: str = "text-embedding-3-large"
    # Dimension of the embedding model to use.
    EMBEDDING_DIM: str = "1536"
    LLM_MAX_TOKENS: str = "16384"
    BACKEND_CORS_ORIGINS: List[AnyHttpUrl] = [
        "https://survey.info4pi.org",
        "http://localhost:3000",
        "http://localhost:3001",
    ]  # type: ignore
    # case_sensitive = True
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        env_prefix="",
        extra="allow",
    )

    @property
    # TODO: Attribute name "VERBOSE" doesn't conform to snake_case naming style
    def VERBOSE(self) -> bool:
        """
        Used for setting verbose flag in LlamaIndex modules.
        """
        return self.LOG_LEVEL == "DEBUG" or self.IS_PULL_REQUEST or not self.RENDER

    @validator("BACKEND_CORS_ORIGINS", pre=True)
    # TODO: Method 'assemble_cors_origins' should have "self" as first argument
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> Union[List[str], str]:
        """_summary_

        Args:
            v (Union[str, List[str]]): _description_

        Raises:
            ValueError: _description_

        Returns:
            Union[List[str], str]: _description_
        """
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, (list, str)):
            return v
        raise ValueError(v)

    @validator("DATABASE_URL", pre=True)
    def assemble_db_url(cls, v: str) -> str:
        """Preprocesses the database URL to make it compatible with asyncpg."""
        if not v or not v.startswith("postgres"):
            raise ValueError("Invalid database URL: " + str(v))
        return (
            v.replace("postgres://", "postgresql://")
            .replace("postgresql://", "postgresql+asyncpg://")
            .strip()
        )

    @validator("LOG_LEVEL", pre=True)
    # TODO: Method 'assemble_log_level' should have "self" as first argument
    def assemble_log_level(cls, v: str) -> str:
        """Preprocesses the log level to ensure its validity."""
        v = v.strip().upper()
        if v not in ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]:
            raise ValueError("Invalid log level: " + str(v))
        return v

    @validator("IS_PULL_REQUEST", pre=True)
    # TODO: Method 'assemble_is_pull_request' should have "self" as first argument
    def assemble_is_pull_request(cls, v: str) -> bool:
        """Preprocesses the IS_PULL_REQUEST flag.

        See Render.com docs for more info:
        https://render.com/docs/pull-request-previews#how-pull-request-previews-work
        """
        if isinstance(v, bool):
            return v
        return v.lower() == "true"

    @property
    # TODO: Attribute name "ENVIRONMENT" doesn't conform to snake_case naming style
    def ENVIRONMENT(self) -> AppEnvironment:
        """Returns the app environment."""
        if self.RENDER:
            if self.IS_PULL_REQUEST:
                return AppEnvironment.PREVIEW
            else:
                return AppEnvironment.PRODUCTION
        else:
            return AppEnvironment.LOCAL

    @property
    # TODO: Attribute name "UVICORN_WORKER_COUNT" doesn't conform to snake_case naming style
    def UVICORN_WORKER_COUNT(self) -> int:
        """_summary_

        Returns:
            int: _description_
        """
        if self.ENVIRONMENT == AppEnvironment.LOCAL:
            return 1
        # The recommended number of workers is (2 x $num_cores) + 1:
        # Source: https://docs.gunicorn.org/en/stable/design.html#how-many-workers
        # But the Render.com servers don't have enough memory to support that many workers,
        # so we instead go by the number of server instances that can be run given the memory
        return 3

    @property
    # TODO: Attribute name "SENTRY_SAMPLE_RATE" doesn't conform to snake_case naming style
    def SENTRY_SAMPLE_RATE(self) -> float:
        """_summary_

        Returns:
            float: _description_
        """
        # TODO: before full release, set this to 0.1 for production
        return 0.07 if self.ENVIRONMENT == AppEnvironment.PRODUCTION else 1.0


settings = Settings()
os.environ["OPENAI_API_KEY"] = settings.OPENAI_API_KEY
os.environ["ANTHROPIC_API_KEY"] = settings.ANTHROPIC_API_KEY
