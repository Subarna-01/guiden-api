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

settings = Settings()