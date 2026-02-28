from fastapi import FastAPI
from contextlib import asynccontextmanager
from app.core.database.connection import db_connection_manager
from app.core.database.base import BaseDb1
from app.core.settings import settings
from app.modules.users.router import users_router

DB_NAMES = [settings.DB1_NAME]

@asynccontextmanager
async def lifespan(app: FastAPI):
    
    # Initialize all db connections on app startup and bind tables
    db_connection_manager.init_engines(DB_NAMES)
    
    for db_name, Base in zip(DB_NAMES, [BaseDb1]):
        engine = db_connection_manager.get_engine(db_name)
        Base.metadata.create_all(bind=engine)
        
    yield

    # Close all db connections post app shutdown
    db_connection_manager.close_all()

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    lifespan=lifespan
)

app.include_router(users_router, prefix=settings.API_V1_STR)

