"""
This module is responsible for managing the configuration settings of the JMF-OpenAI-LLM Integration project. 

It defines classes for setting up and validating various application configurations, including database connections, 
API keys, CORS origins, log levels, and other environment-specific settings. The settings are primarily loaded from 
environment variables, with support for different environments like local, preview, and production. Additional 
properties and validators are used to preprocess and validate configuration data, ensuring the correct setup 
of the application's runtime environment.
"""
import os
from dotenv import load_dotenv
from enum import Enum
from typing import List, Union
from pydantic import BaseSettings, AnyHttpUrl, validator

load_dotenv()

#  Load environment variables
POSTGRES_USER = os.getenv("POSTGRES_USER")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD")
POSTGRES_DB = os.getenv("POSTGRES_DB")
POSTGRES_HOST_NAME = os.getenv("POSTGRES_HOST_NAME")
# Define DB connection string
LLM_DATABASE_URL = f"postgresql+asyncpg://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST_NAME}:5432/{POSTGRES_DB}"


class AppConfig(BaseSettings.Config):
    """
    Config for settings classes that allows for
    combining Settings classes with different env_prefix settings.

    Taken from here:
    https://github.com/pydantic/pydantic/issues/1727#issuecomment-658881926
    """

    case_sensitive = True

    @classmethod
    def prepare_field(cls, field) -> None:
        """
        Prepares each field in the settings class for processing.

        This method is an override of the default field preparation method. It is used to 
        modify the field's configuration before it is processed by Pydantic. Specifically, 
        it checks for the presence of 'env_names' in field_info and, if not present, 
        proceeds with the default field preparation process.

        Parameters:
        field: The field to be prepared. It contains all the metadata and configurations 
              related to a specific setting.

        Returns:
        None: The method modifies the field in place and does not return anything.
        """
        if "env_names" in field.field_info.extra:
            return
        return super().prepare_field(field)


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

    OPENAI_API_KEY: str = os.getenv("OPEN_API_JMF_LLM_KEY")

    class Config(AppConfig):
        """_summary_

        Args:
            AppConfig (_type_): _description_
        """
        env_prefix = "PREVIEW_" if is_pull_request or is_preview_env else ""


class Settings(PreviewPrefixedSettings):
    """
    Application settings.
    """

    PROJECT_NAME: str = "JMF-OpenAI-LLM-Integration"
    API_PREFIX: str = "/api"
    DATABASE_URL: str = LLM_DATABASE_URL
    LOG_LEVEL: str = "DEBUG"
    IS_PULL_REQUEST: bool = False
    RENDER: bool = False
    # CDN_BASE_URL: str
    VECTOR_STORE_TABLE_NAME: str = "pg_vector_store"
    # SENTRY_DSN: Optional[str]
    # RENDER_GIT_COMMIT: Optional[str]
    LOADER_IO_VERIFICATION_STR: str = "loaderio-e51043c635e0f4656473d3570ae5d9ec"

    BACKEND_CORS_ORIGINS: List[AnyHttpUrl] = [
        "https://survey.info4pi.org",
        "http://localhost:3000",
    ]

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

    class Config(AppConfig):
        """_summary_

        Args:
            AppConfig (_type_): _description_
        """
        env_prefix = ""


settings = Settings()
os.environ["OPENAI_API_KEY"] = settings.OPENAI_API_KEY
