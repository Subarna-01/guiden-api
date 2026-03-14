import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = os.getenv("PROJECT_NAME")

    POSTGRES_HOST: str = os.getenv("POSTGRES_HOST")
    POSTGRES_PORT: int = int(os.getenv("POSTGRES_PORT"))
    POSTGRES_USER: str = os.getenv("POSTGRES_USER")
    POSTGRES_PASSWORD: str = os.getenv("POSTGRES_PASSWORD")

    USERS_DB_NAME: str = os.getenv("USERS_DB_NAME")
    MASTER_DB_NAME: str = os.getenv("MASTER_DB_NAME")

    ALLOWED_ORIGINS: list = ["*"]
    ALLOWED_CREDENTIALS: bool = True
    ALLOWED_METHODS: list = ["*"]
    ALLOWED_HEADERS: list = ["*"]

    JWT_ALGORITHM: str = os.getenv("JWT_ALGORITHM")
    JWT_SECRET_KEY: str = os.getenv("JWT_SECRET_KEY")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES"))
    REFRESH_TOKEN_EXPIRE_DAYS: int = int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS"))

    USERS_BUCKET_NAME: str = os.getenv("USERS_BUCKET_NAME")
    MASTER_BUCKET_NAME: str = os.getenv("MASTER_BUCKET_NAME")

    GCS_PROJECT_ID: str = os.getenv("GCS_PROJECT_ID")
    GCS_SECRET_ID: str = os.getenv("GCS_SECRET_ID")
    GCS_SECRET_VERSION: str = os.getenv("GCS_SECRET_VERSION")
    GCS_SIGNED_URL_EXPIRE_MINUTES: int = int(os.getenv("GCS_SIGNED_URL_EXPIRE_MINUTES"))

    ELASTICSEARCH_CONNECTION_URL: str = os.getenv("ELASTICSEARCH_CONNECTION_URL")
    ELASTICSEARCH_USER: str = os.getenv("ELASTICSEARCH_USER")
    ELASTICSEARCH_PASSWORD: str = os.getenv("ELASTICSEARCH_PASSWORD")


settings = Settings()
