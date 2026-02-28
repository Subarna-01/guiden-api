from fastapi import APIRouter, Depends, Query
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from app.core.database.dependencies import get_db
from app.core.settings import settings
from app.modules.users.schemas import UserCreate, UserLogin
from app.modules.users.service import UserService

users_router = APIRouter(prefix="/users", tags=["users"])

user_service = UserService()

@users_router.post("/create")
async def create_user(request_body: UserCreate, db1: Session = Depends(lambda: next(get_db(settings.DB1_NAME)))) -> JSONResponse:
    return await user_service.create_user(request_body, db1)

@users_router.post("/auth/login")
async def authenticate(request_body: UserLogin, db1: Session = Depends(lambda: next(get_db(settings.DB1_NAME)))) -> JSONResponse:
    return await user_service.authenticate(request_body, db1)

@users_router.get("/me")
async def get_user_by_id(user_id: str = Query(...), db1: Session = Depends(lambda: next(get_db(settings.DB1_NAME)))) -> JSONResponse:
    return await user_service.get_user_by_id(user_id, db1)
