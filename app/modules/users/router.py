from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from app.core.database.dependencies import get_db
from app.core.settings import settings
from app.modules.users.schemas import UserCreate
from app.modules.users.service import UserService

users_router = APIRouter(prefix="/users", tags=["users"])

user_service = UserService()

@users_router.post("/create")
async def create_user(request_body: UserCreate, db1: Session = Depends(lambda: next(get_db(settings.DB1_NAME)))) -> JSONResponse:
    return await user_service.create_user(request_body, db1)

