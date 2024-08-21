"""
This module contains the settings for the application.
A single object of the settings is created which can be accessed throughout the application.
"""
import logging
from typing import Annotated, Literal, Any
from pydantic import (
    AnyUrl,
    BeforeValidator,
    computed_field,
)
from fastapi import FastAPI
from fastapi.routing import APIRoute
from fastapi.middleware.cors import CORSMiddleware
from pydantic_core import MultiHostUrl
from pydantic_settings import BaseSettings, SettingsConfigDict

logger = logging.getLogger(__name__)


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
    """
    This class holds all the settings for the application.
    """
    model_config = SettingsConfigDict(
        env_file=".env",
        env_ignore_empty=True,
        extra="ignore",
    )

    # General Application settings
    PROJECT_NAME: str
    API_V1_STR: str = "/api/v1"
    DOMAIN: str = "localhost"
    ENVIRONMENT: Literal["local", "development", "staging", "production", "mock"] = "local"
    # LOG_LEVEL: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = "DEBUG"

    @computed_field
    @property
    def server_host(self) -> str:
        # Use https for anything other than local development
        if self.ENVIRONMENT == "local":
            return f"http://{self.DOMAIN}"
        return f"https://{self.DOMAIN}"
    
    BACKEND_CORS_ORIGINS: Annotated[
        list[AnyUrl] | str, BeforeValidator(parse_cors)
    ] = []

    # Security settings
    JWT_ALGORITHM: str = "PS512"  # PS512 = RSASSA-PSS signature using SHA-512 and MGF1 padding with SHA-512
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 1  # 60 minutes * 24 hours * 1 days = 1 days
    KC_SERVER_URL: str
    KC_REALM_NAME: str
    KC_AUTH_CLIENT_ID: str
    KC_AUTH_CLIENT_SECRET: str
    KC_USER_MANAGER_CLIENT_ID: str
    KC_USER_MANAGER_CLIENT_SECRET: str
    KC_GROUP_MANAGER_CLIENT_ID: str
    KC_GROUP_MANAGER_CLIENT_SECRET: str

    @property
    def KC_CERTS_URL(self) -> str:
        return f"{self.KC_SERVER_URL}/realms/{self.KC_REALM_NAME}/protocol/openid-connect/certs"

    # Database settings
    POSTGRES_SERVER_URL: str | None = None
    POSTGRES_SERVER_PORT: int | None = None
    POSTGRES_DB: str | None = None
    POSTGRES_USER: str | None = None
    POSTGRES_PASSWORD: str | None = None

    @computed_field
    @property
    def SQLALCHEMY_DATABASE_URI(self) -> str:
        if not self.POSTGRES_SERVER_URL:
            raise ValueError("POSTGRES_SERVER_URL is not set")
        return MultiHostUrl.build(
            scheme="postgresql",
            username=self.POSTGRES_USER,
            password=self.POSTGRES_PASSWORD,
            host=self.POSTGRES_SERVER_URL,
            port=self.POSTGRES_SERVER_PORT,
            path=f"{self.POSTGRES_DB}",
        )
    
    # Email settings
    VERIFY_EMAIL: bool = False

global_settings = Settings()   

def set_cors_origins(origins: list[str], app: FastAPI) -> None:
    print("Adding CORS")
    for origin in origins:
        print("CORS origin: %s", origin)
    origins = [str(origin) for origin in origins if origin]
    print("Origins: %s", origins)
    app.add_middleware(
        CORSMiddleware,
        # allow_origins=origins,
        allow_origins=["http://localhost:5173"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

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
