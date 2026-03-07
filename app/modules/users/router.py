from fastapi import APIRouter, Depends, UploadFile, File
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from functools import partial
from app.core.database.dependencies import get_db
from app.core.security import jwt
from app.core.settings import settings
from app.modules.users.schemas import UserAccountCreate, UserAccountLogin
from app.modules.users.service import UserService

users_router = APIRouter(prefix="/users", tags=["users"])

user_service = UserService()

@users_router.post("/create-account")
async def create_account(request_body: UserAccountCreate, db: Session = Depends(partial(get_db, settings.USERS_DB_NAME))) -> JSONResponse:
    return await user_service.create_account(request_body, db)

@users_router.post("/auth/login")
async def login_user(request_body: UserAccountLogin, db: Session = Depends(partial(get_db, settings.USERS_DB_NAME))) -> JSONResponse:
    return await user_service.login_user(request_body, db)

@users_router.get("/me")
async def get_account_details(decoded_token_data: dict = Depends(jwt.authenticate), db: Session = Depends(partial(get_db, settings.USERS_DB_NAME))) -> JSONResponse:
    return await user_service.get_account_details(decoded_token_data.get("user_id"), db)

@users_router.put("/me/profile-picture")
async def update_profile_picture(file: UploadFile = File(...), decoded_token_data: dict = Depends(jwt.authenticate), db: Session = Depends(partial(get_db, settings.USERS_DB_NAME))) -> JSONResponse:
    return await user_service.update_profile_picture(file, decoded_token_data.get("user_id"), db)

@users_router.delete("/me/profile-picture")
async def delete_profile_picture(decoded_token_data: dict = Depends(jwt.authenticate), db: Session = Depends(partial(get_db, settings.USERS_DB_NAME)) ) -> JSONResponse:
    return await user_service.delete_profile_picture(decoded_token_data.get("user_id"), db)