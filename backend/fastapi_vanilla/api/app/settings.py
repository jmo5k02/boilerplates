import logging
from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Annotated, Literal, Any
from pydantic import AnyUrl, BeforeValidator, computed_field
from pydantic_core import MultiHostUrl

from fastapi.routing import APIRoute

logger = logging.getLogger("app_core")

def parse_cors(v: Any) -> list[str] | str:
    """
    This function is used to parse the CORS origins 
    that are passed as a comma-separated string in the .env file. or environment variables
    """
    logger.info("Parsing CORS origins: %s", v)
    if isinstance(v, str) and not v.startswith("["):
        logger.info(v)
        urls = [i.strip() for i in v.split(",")]
        logger.info(urls)
        return urls
    elif isinstance(v, list | str):
        logger.info(v)
        return v
    raise ValueError("CORS origins must be a comma-separated string or a list of strings")

class Settings(BaseSettings):

    model_config = SettingsConfigDict(
        env_file="./app/.env",
        env_ignore_empty=True,
        extra="ignore",
    )

    # General Application settings
    PROJECT_NAME: str = "FastAPI Vanilla Boilerplate"
    BACKEND_CORS_ORIGINS: str = ""
    API_V1_STR: str = "/api/v1"
    ENVIRONMENT: Literal["dev", "stage", "prod"] = "dev"
    testing: bool = bool(0)

    # Database settings
    POSTGRES_SERVER_URL: str | None
    POSTGRES_SERVER_HOST: str | None 
    POSTGRES_SERVER_PORT: int | None = None
    POSTGRES_USER: str | None = None
    POSTGRES_PASSWORD: str | None = None

    @computed_field
    @property
    def POSTGRES_DB(self) -> str:
        if not self.ENVIRONMENT:
            raise ValueError("ENVIRONMENT is not set")
        if self.testing:
            return f"app_test"
        return f"app_{self.ENVIRONMENT}"

    @computed_field
    @property
    def SQLALCHEMY_DATABASE_URI(self) -> str:
        if not self.POSTGRES_SERVER_URL:
            raise ValueError("POSTGRES_SERVER_URL is not set")
        return MultiHostUrl.build(
            scheme="postgresql+asyncpg",
            username=self.POSTGRES_USER,
            password=self.POSTGRES_PASSWORD,
            host=self.POSTGRES_SERVER_URL,
            port=self.POSTGRES_SERVER_PORT,
            path=f"{self.POSTGRES_DB}",
        )

settings = Settings()

@lru_cache
def get_settings() -> Settings:
    logger.info("Loading config settings from environment")
    return Settings()


def custom_generate_unique_id(route: APIRoute) -> str:
    """
    Generate a unique id for each request  
    This way we can identify each endpoint individually  
    """
    if len(route.tags) <= 1:
        if route.tags[0] != "health-check":
            raise ValueError("Route must have at least two tags. Parent for version and child for endpoint")
        return f"{route.tags[0]}-{route.name}"
    return f"{route.tags[0]}-{route.tags[1]}-{route.name}"
