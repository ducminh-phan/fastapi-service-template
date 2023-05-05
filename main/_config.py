import logging
import os

from pydantic import BaseSettings


class Config(BaseSettings):
    ENVIRONMENT: str
    LOGGING_LEVEL: int = logging.INFO

    SQLALCHEMY_DATABASE_URI: str
    SQLALCHEMY_TRACK_MODIFICATIONS: bool = False

    class Config:
        case_sensitive = True
        env_file_encoding = "utf-8"


environment = os.environ.get("ENVIRONMENT", "local")
config = Config(
    ENVIRONMENT=environment,
    # ".env.{environment}" takes priority over ".env"
    _env_file=[".env", f".env.{environment}"],
)
