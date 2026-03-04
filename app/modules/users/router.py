from fastapi import APIRouter, Depends, UploadFile, File, Query
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from functools import partial
from app.core.database.dependencies import get_db
from app.core.security import jwt
from app.core.settings import settings
from app.modules.users.schemas import UserCreate, UserLogin
from app.modules.users.service import UserService

users_router = APIRouter(prefix="/users", tags=["users"])

user_service = UserService()


@users_router.post("/create")
async def create_user(
    request_body: UserCreate,
    db: Session = Depends(partial(get_db, settings.USERS_DB_NAME)),
) -> JSONResponse:
    return await user_service.create_user(request_body, db)


@users_router.post("/auth/login")
async def login_user(
    request_body: UserLogin,
    db: Session = Depends(partial(get_db, settings.USERS_DB_NAME)),
) -> JSONResponse:
    return await user_service.login_user(request_body, db)


@users_router.get("/me")
async def get_user_by_id(
    data=Depends(jwt.authenticate),
    db: Session = Depends(partial(get_db, settings.USERS_DB_NAME)),
) -> JSONResponse:
    if not isinstance(data, dict):
        return data
    return await user_service.get_user_by_id(data.get("user_id"), db)


@users_router.put("/me/profile-picture")
async def update_profile_picture(
    file: UploadFile = File(...),
    data=Depends(jwt.authenticate),
    requested_removal: bool = Query(False),
    db: Session = Depends(partial(get_db, settings.USERS_DB_NAME)),
) -> JSONResponse:
    if not isinstance(data, dict):
        return data
    return await user_service.update_profile_picture(file, data.get("user_id"), requested_removal, db)
