import os
import datetime
import uuid
from fastapi import status, HTTPException, UploadFile
from fastapi.responses import JSONResponse
from sqlalchemy import cast, String
from sqlalchemy.orm import Session
from google.cloud import storage
from google.oauth2 import service_account
from app.core.security import jwt, password
from app.core.settings import settings
from app.modules.users.enum import UserStatus
from app.modules.users.models import User, UserProfilePicture
from app.modules.users.repository import UserRepository
from app.modules.users.schemas import UserCreate, UserLogin

user_repository = UserRepository()


class UserService:
    def __init__(self) -> None:
        self.storage_client = storage.Client(
            credentials=service_account.Credentials.from_service_account_file(
                os.path.join(os.getcwd(), "guiden-487312-85574ae787d2.json")
            )
        )
        self.bucket = self.storage_client.bucket(settings.USERS_BUCKET_NAME)

    async def create_user(self, request_body: UserCreate, db: Session) -> JSONResponse:
        try:
            record = await user_repository.find_by_email(request_body.email, db)

            if record:
                return JSONResponse(
                    content={
                        "message": "Email already exists",
                    },
                    status_code=status.HTTP_409_CONFLICT,
                )

            data = {
                "email": request_body.email.lower(),
                "password_hash": password.hash_password(request_body.password),
                "status": UserStatus.ACTIVE.value
            }

            new_record = await user_repository.create(data, db)
            return JSONResponse(
                content={
                    "message": "User created successfully",
                    "data": {
                        "user_id": str(new_record.user_id),
                        "email": new_record.email,
                    },
                },
                status_code=status.HTTP_201_CREATED,
            )

        except Exception as e:
            print(e)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="An unexpected error has occurred",
            )

    async def login_user(self, request_body: UserLogin, db: Session) -> JSONResponse:
        try:
            record = await user_repository.find_by_email(request_body.email, db)

            if not record or not password.verify_password(
                request_body.password, record.password_hash
            ):
                return JSONResponse(
                    content={"message": "Invalid email or password provided"},
                    status_code=status.HTTP_401_UNAUTHORIZED,
                )

            if record.status == UserStatus.INACTIVE.value:
                return JSONResponse(
                    content={"message": "Account deactivated"},
                    status_code=status.HTTP_403_FORBIDDEN,
                )

            token_payload = {
                "user_id": str(record.user_id),
                "email": record.email,
            }

            return JSONResponse(
                content={
                    "data": {
                        "token_type": "bearer",
                        "access_token": jwt.create_access_token(token_payload),
                        "refresh_token": jwt.create_refresh_token(token_payload),
                    }
                },
                status_code=status.HTTP_200_OK,
            )

        except Exception as e:
            print(e)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="An unexpected error has occurred",
            )

    async def get_user_by_id(self, user_id: str, db: Session) -> JSONResponse:
        try:
            record = await user_repository.find_by_id(user_id, db)

            if not record or record.status == UserStatus.INACTIVE.value:
                return JSONResponse(
                    content={"message": "User not found"},
                    status_code=status.HTTP_404_NOT_FOUND,
                )

            profile_picture_url = None

            user_profile_picture = db.query(UserProfilePicture).filter(cast(UserProfilePicture.user_id, String) == user_id).first()

            if (
                user_profile_picture
                and user_profile_picture.is_removed == False
            ):
                blob = self.bucket.blob(user_profile_picture.object_path)
                profile_picture_url = blob.generate_signed_url(
                    version="v4",
                    expiration=datetime.timedelta(days=7),
                    method="GET",
                )

            return JSONResponse(
                content={
                    "message": "User data fetched successfully",
                    "data": {
                        "user_id": str(record.user_id),
                        "email": record.email,
                        "profile_picture": {
                            "url": profile_picture_url,
                            "url_validity_in_days": 7 if profile_picture_url else None
                        },
                        "created_at": str(record.created_at),
                    }
                },
                status_code=status.HTTP_200_OK,
            )

        except Exception as e:
            print(e)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="An unexpected error has occurred",
            )

    async def update_profile_picture(self, file: UploadFile, user_id: str, requested_removal: bool, db: Session) -> JSONResponse:
        try:
            if not file.file:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="No files uploaded",
                )

            if not file.content_type.startswith("image/"):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Only image files allowed",
                )
            
            user = db.query(User).filter(cast(User.user_id, String) == user_id).first()

            if not user or user.status == UserStatus.INACTIVE.value:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="User not found",
                )
     
            user_profile_picture = db.query(UserProfilePicture).filter(cast(UserProfilePicture.user_id, String) == user_id).first()

            if not user_profile_picture and requested_removal:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Failed to remove profile picture",
                )

            file_extension = file.filename.split(".")[-1]
            blob_name = f"{user_id}/profile-picture/{user_id}.{file_extension}"
            blob = self.bucket.blob(blob_name)
            signed_url = None
    
            if not requested_removal:
                file_bytes = await file.read()

                blob.upload_from_string(file_bytes, content_type=file.content_type)

                signed_url = blob.generate_signed_url(
                    version="v4",
                    expiration=datetime.timedelta(days=7),
                    method="GET",
                )
            else:
                if user_profile_picture and user_profile_picture.object_path:
                    user_profile_picture.is_removed = True
                    user_profile_picture.updated_at = datetime.datetime.now(datetime.timezone.utc)
                    db.commit()
                    db.refresh(user_profile_picture)
                    
                    old_blob = self.bucket.blob(user_profile_picture.object_path)

                    try:
                        if old_blob.exists():
                            old_blob.delete()
                    except Exception as e:
                        print(str(e))
                        raise HTTPException(
                            status_code=status.HTTP_400_BAD_REQUEST,
                            detail="Failed to remove profile picture"
                        )
                    
                    return JSONResponse(
                        status_code=status.HTTP_200_OK,
                        content={
                            "message": "Profile picture updated successfully",
                            "data": {
                                "url": signed_url,
                                "url_validity_in_days": 7 if signed_url else None
                            },
                        },
                    )

            if not user_profile_picture:
                new_user_profile_picture = UserProfilePicture(user_id=user_id, object_path=blob_name)
                db.add(new_user_profile_picture)
                db.commit()
                db.refresh(new_user_profile_picture)
            else:
                if blob_name != user_profile_picture.object_path:
                    old_blob = self.bucket.blob(user_profile_picture.object_path)

                    try:
                        if old_blob.exists():
                            old_blob.delete()
                    except Exception as e:
                        print(str(e))
                        raise HTTPException(
                            status_code=status.HTTP_400_BAD_REQUEST,
                            detail="Failed to update profile picture"
                        )
                    
                    user_profile_picture.object_path = blob_name

                user_profile_picture.is_removed = False
                user_profile_picture.updated_at = datetime.datetime.now(datetime.timezone.utc)
                db.commit()
                db.refresh(user_profile_picture)

            return JSONResponse(
                status_code=status.HTTP_200_OK,
                content={
                    "message": "Profile picture updated successfully",
                    "data": {
                        "url": signed_url,
                        "url_validity_in_days": 7 if signed_url else None
                    },
                },
            )

        except HTTPException:
            db.rollback()
            raise

        except Exception as e:
            print(e)
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="An unexpected error has occurred",
            )
