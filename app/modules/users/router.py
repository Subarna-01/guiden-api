from fastapi import APIRouter, Depends, UploadFile, File, Request
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from functools import partial
from app.core.database.dependencies import get_db
from app.core.decorators.auth import require_auth
from app.core.settings import settings
from app.modules.users.schemas import UserAccountCreate, UserAccountLogin
from app.modules.users.service import UserService

users_router = APIRouter(prefix="/users", tags=["users"])

user_service = UserService()


@users_router.post("/create-account")
async def create_account(
    request_body: UserAccountCreate,
    db: Session = Depends(partial(get_db, settings.USERS_DB_NAME)),
) -> JSONResponse:
    return await user_service.create_account(request_body, db)


@users_router.post("/auth/login")
async def login_user(
    request_body: UserAccountLogin,
    db: Session = Depends(partial(get_db, settings.USERS_DB_NAME)),
) -> JSONResponse:
    return await user_service.login_user(request_body, db)


@users_router.get("/me")
@require_auth
async def get_account_details(
    request: Request, db: Session = Depends(partial(get_db, settings.USERS_DB_NAME))
) -> JSONResponse:
    return await user_service.get_account_details(request.state.user_id, db)


@users_router.post("/me/profile-picture")
@require_auth
async def upload_profile_picture(
    request: Request,
    file: UploadFile = File(...),
    db: Session = Depends(partial(get_db, settings.USERS_DB_NAME)),
) -> JSONResponse:
    return await user_service.upload_profile_picture(file, request.state.user_id, db)


@users_router.delete("/me/profile-picture")
@require_auth
async def delete_profile_picture(
    request: Request, db: Session = Depends(partial(get_db, settings.USERS_DB_NAME))
) -> JSONResponse:
    return await user_service.delete_profile_picture(request.state.user_id, db)
