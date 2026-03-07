from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from app.core.database.connection import db_connection_manager
from app.core.database.base import BaseUsersDb
from app.core.settings import settings
from app.modules.users.router import users_router

DB_NAMES = [settings.USERS_DB_NAME]

@asynccontextmanager
async def lifespan(app: FastAPI):
    db_connection_manager.init_engines(DB_NAMES)

    for db_name, Base in zip(DB_NAMES, [BaseUsersDb]):
        engine = db_connection_manager.get_engine(db_name)
        Base.metadata.create_all(bind=engine)

    yield

    db_connection_manager.close_all()


app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=settings.ALLOWED_CREDENTIALS,
    allow_methods=settings.ALLOWED_METHODS,
    allow_headers=settings.ALLOWED_HEADERS,
)

app.include_router(users_router, prefix=settings.API_V1_STR)
