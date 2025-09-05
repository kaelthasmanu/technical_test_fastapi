import os
from typing import List

from dotenv import load_dotenv
from pydantic_settings import BaseSettings
from pydantic import ConfigDict

load_dotenv()

# Resolve ENV from OS to drive which Configs class to instantiate
ENV: str = os.getenv("ENV", "dev")


class Configs(BaseSettings):
    # base
    ENV: str = os.getenv("ENV", "dev")
    API: str = "/api"
    API_V1_STR: str = "/api/v1"
    API_V2_STR: str = "/api/v2"
    PROJECT_NAME: str = "todo-api"
    ENV_DATABASE_MAPPER: dict = {
        "prod": "todo",
        "stage": "stage-todo",
        "dev": "dev-todo",
        "test": "dev-todo",
    }
    DB_ENGINE_MAPPER: dict = {
        "postgresql": "postgresql",
        "mysql": "mysql+pymysql",
    }

    PROJECT_ROOT: str = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

    # date
    DATETIME_FORMAT: str = "%Y-%m-%dT%H:%M:%S"
    DATE_FORMAT: str = "%Y-%m-%d"

    # auth
    SECRET_KEY: str = os.getenv("SECRET_KEY", "")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 30  # 60 minutes * 24 hours * 30 days = 30 days

    # CORS
    BACKEND_CORS_ORIGINS: List[str] = ["*"]

    # logging
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    LOG_JSON: bool = os.getenv("LOG_JSON", "false").lower() == "true"
    LOG_FILE: str | None = os.getenv("LOG_FILE")
    LOG_ROTATION: str = os.getenv("LOG_ROTATION", "10 MB")
    LOG_RETENTION: str = os.getenv("LOG_RETENTION", "7 days")

    # database
    DB: str = os.getenv("DB", "postgresql")
    DB_USER: str = os.getenv("DB_USER")
    DB_PASSWORD: str = os.getenv("DB_PASSWORD")
    DB_HOST: str = os.getenv("DB_HOST")
    # Default port depends on engine: PostgreSQL 5432, MySQL 3306
    DB_PORT: str = os.getenv("DB_PORT", "5432" if DB == "postgresql" else "3306")
    # Only support postgresql and mysql; raise if unsupported
    DB_ENGINE: str = DB_ENGINE_MAPPER[DB]

    DATABASE_URI_FORMAT: str = "{db_engine}://{user}:{password}@{host}:{port}/{database}"

    DATABASE_URI: str = "{db_engine}://{user}:{password}@{host}:{port}/{database}".format(
        db_engine=DB_ENGINE,
        user=DB_USER,
        password=DB_PASSWORD,
        host=DB_HOST,
        port=DB_PORT,
        database=ENV_DATABASE_MAPPER[ENV],
    )

    # find query
    PAGE: int = 1
    PAGE_SIZE: int = 20
    ORDERING: str = "-id"
     
    model_config = ConfigDict(case_sensitive=True)


if ENV == "prod":
    pass
elif ENV == "stage":
    pass

# Export a singleton-like instance for convenience imports
configs = Configs()
