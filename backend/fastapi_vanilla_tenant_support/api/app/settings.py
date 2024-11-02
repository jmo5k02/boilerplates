import logging
from typing import Literal
from functools import lru_cache

from pydantic import computed_field
from pydantic_core import MultiHostUrl
from pydantic_settings import BaseSettings, SettingsConfigDict

log = logging.getLogger(__name__)

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file="./app/.env",
        env_ignore_empty=True,
        extra="ignore",
    )

    # General application settings
    PROJECT_NAME: str
    BACKEND_CORS_ORIGINS: str
    API_V1_STR: str = "/api/v1"
    ENVIRONMENT: Literal["dev", "stage", "prod"]
    TESTING: bool

    @computed_field
    @property
    def OPENAPI_URL(self) -> str|None:
        """Only return OPENAPI URL in development environment"""
        if self.ENVIRONMENT == "dev":
            return f"/api/openapi.json"
        
    @computed_field
    @property
    def DOCS_URL(self) -> str|None:
        """Only return DOCS URL in development environment"""
        if self.ENVIRONMENT == "dev":
            return f"/api/docs"
        
    # Security settings
    SECRET_KEY: str = "c754b741006a47cc556a821e54b5d41e3241d0dd19dadd379196da8f4476eff1"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8  # 8 days
    MAX_LOGIN_ATTEMPTS: int = 5
    
    # Database settings
    POSTGRES_SERVER_HOST: str | None = None
    POSTGRES_SERVER_PORT: int | None = None
    POSTGRES_USER: str | None = None
    POSTGRES_PASSWORD: str | None = None

    @computed_field
    @property
    def POSTGRES_DB(self) -> str:
        if not self.ENVIRONMENT:
            raise ValueError("ENVIRONMENT is not set")
        if self.TESTING:
            return "app_test"
        return f"app_{self.ENVIRONMENT}"

    @computed_field
    @property
    def SQLALCHEMY_DATABASE_URI(self) -> str:
        if self.POSTGRES_SERVER_HOST:
            log.info("Building SQLALCHEMY_DATABASE_URI")
            url = MultiHostUrl.build(
                scheme="postgresql+asyncpg",
                username=self.POSTGRES_USER,
                password=self.POSTGRES_PASSWORD,
                host=self.POSTGRES_SERVER_HOST,
                port=self.POSTGRES_SERVER_PORT,
                path=f"{self.POSTGRES_DB}",
            )
            log.info(f"SQLALCHEMY_DATABASE_URI: {url}")
            return url
        
        else:
            error = f"Database settings are not set correctly \
            POSTGRES_SERVER_HOST: {self.POSTGRES_SERVER_HOST}, \
            POSTGRES_SERVER_PORT: {self.POSTGRES_SERVER_PORT}, \
            POSTGRES_USER: {self.POSTGRES_USER}"
            log.error(error)
            raise ValueError(error)
        
@lru_cache
def get_settings() -> Settings:
    return Settings()

settings = get_settings()