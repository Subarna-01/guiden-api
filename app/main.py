import warnings
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from app.core.database.connection import db_connection_manager
from app.core.elasticsearch.connection import elasticsearch_connection_manager
from app.core.database import base
from app.core.settings import settings
from app.modules.master.router import master_router
from app.modules.search.router import search_router
from app.modules.users.router import users_router

warnings.filterwarnings("ignore")

DB_NAMES = [settings.MASTER_DB_NAME, settings.USERS_DB_NAME]
DB_BASES = [base.BaseMasterDb, base.BaseUsersDb]

@asynccontextmanager
async def lifespan(app: FastAPI):
    db_connection_manager.init_engines(DB_NAMES)

    for db_name, Base in zip(DB_NAMES, DB_BASES):
        engine = db_connection_manager.get_engine(db_name)
        Base.metadata.create_all(bind=engine)

    elasticsearch_connection_manager.init_client()

    yield
    
    db_connection_manager.close_all()
    elasticsearch_connection_manager.close_client()


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

app.include_router(master_router, prefix=settings.API_V1_STR)
app.include_router(search_router, prefix=settings.API_V1_STR)
app.include_router(users_router, prefix=settings.API_V1_STR)
