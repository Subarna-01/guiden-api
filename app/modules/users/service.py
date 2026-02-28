import datetime
from fastapi import status, HTTPException
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from app.core.security import hash_password, verify_password
from app.modules.users.enum import UserStatus
from app.modules.users.repository import UserRepository
from app.modules.users.schemas import UserCreate, UserLogin

user_repository = UserRepository()
class UserService:
    def __init__(self) -> None:
        pass

    async def create_user(self, request_body: UserCreate, db1: Session) -> JSONResponse:
        try:
            record = await user_repository.find_by_email(request_body.email, db1)

            if record:
                return JSONResponse(
                    content={
                        "message": "Email already exists",
                    },
                    status_code=status.HTTP_409_CONFLICT
                )
            
            data = {
                "email": request_body.email.lower(),
                "password_hash": hash_password(request_body.password),
                "status": UserStatus.ACTIVE.value,
                "ipv4_addr_created_at": None,
                "ipv4_addr_last_logged_in_at": None
            }

            new_record = await user_repository.create(data, db1)
            return JSONResponse(
                content={
                    "message": "User created successfully",
                    "data": {
                        "user_id": str(new_record.user_id),
                        "email": new_record.email
                    }
                },
                status_code=status.HTTP_201_CREATED
            )

        except Exception as e:
            print(e)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="An unexpected error has occurred"
            )
        
    async def authenticate(self, request_body: UserLogin, db1: Session) -> JSONResponse:
        try:
            record = await user_repository.find_by_email(request_body.email, db1)

            if not record or not verify_password(request_body.password, record.password_hash):
                return JSONResponse(
                    content={
                        "message": "Invalid email or password provided"
                    },
                    status_code=status.HTTP_401_UNAUTHORIZED
                )
            
            if record.status == UserStatus.INACTIVE.value:
                return JSONResponse(
                    content={
                        "message": "Account deactivated"
                    },
                    status_code=status.HTTP_403_FORBIDDEN
                )
            
            return JSONResponse(
                content={
                    "message": "Authentication successful",
                    "data": {
                        "user_id": str(record.user_id),
                        "email": record.email
                    }
                },
                status_code=status.HTTP_200_OK
            )

        except Exception as e:
            print(e)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="An unexpected error has occurred"
            )
        
    async def get_user_by_id(self, user_id: str, db1: Session) -> JSONResponse:
        try:
            record = await user_repository.find_by_id(user_id, db1)

            if not record or record.status == UserStatus.INACTIVE.value:
                return JSONResponse(
                    content={
                        "message": "User not found"
                    },
                    status_code=status.HTTP_404_NOT_FOUND
                )
            
            return JSONResponse(
                content={
                    "user_id": str(record.user_id),
                    "email": record.email
                },
                status_code=status.HTTP_200_OK
            )

        except Exception as e:
            print(e)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="An unexpected error has occurred"
            )
