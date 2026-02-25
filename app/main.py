from fastapi import FastAPI
from app.core.settings import settings
from app.modules.users.router import users_router

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
)

app.include_router(users_router, prefix=settings.API_V1_STR)

