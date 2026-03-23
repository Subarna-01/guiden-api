import datetime
from fastapi import status, HTTPException, UploadFile
from fastapi.responses import JSONResponse
from sqlalchemy import cast, String
from sqlalchemy.orm import Session
from app.core.gcp.gcs_bucket import GCSBucket
from app.core.security.jwt import create_access_token, create_refresh_token
from app.core.security.password import hash_password, verify_password
from app.core.logging import logger
from app.core.settings import settings
from app.shared.models.users.models import User, UserProfilePicture
from app.modules.users.enum import UserAccountStatus
from app.modules.users.schemas import (
    UserAccountCreate,
    UserAccountLogin,
    UserPasswordReset,
)

gcs_bucket = GCSBucket(settings.USERS_BUCKET_NAME)


class UserService:
    def __init__(self) -> None:
        pass

    async def create_account(
        self, request_body: UserAccountCreate, db: Session
    ) -> JSONResponse:
        try:
            usr_entry = (
                db.query(User).filter(User.email == request_body.email.lower().strip()).first()
            )

            if usr_entry:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="This email already exists",
                )

            usr_entry = User(
                email=request_body.email.lower().strip(),
                password_hash=hash_password(request_body.password.strip()),
                status=UserAccountStatus.ACTIVE.value,
            )

            db.add(usr_entry)
            db.commit()
            db.refresh(usr_entry)

            return JSONResponse(
                status_code=status.HTTP_201_CREATED,
                content={
                    "message": "Account created successfully",
                    "data": {"user_id": str(usr_entry.user_id)},
                },
            )

        except HTTPException:
            db.rollback()
            raise

        except Exception as e:
            logger.error(str(e))
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="An unexpected error has occurred",
            )

    async def login_user(
        self, request_body: UserAccountLogin, db: Session
    ) -> JSONResponse:
        try:
            usr_entry = (
                db.query(User).filter(User.email == request_body.email.lower().strip()).first()
            )

            if not usr_entry or not verify_password(
                request_body.password.strip(), usr_entry.password_hash
            ):
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid email or password provided",
                )

            if usr_entry.status == UserAccountStatus.INACTIVE.value:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="This account has been deactivated. Kindly re-activate and try login again",
                )

            token_payload = {
                "user_id": str(usr_entry.user_id),
                "email": usr_entry.email,
            }

            return JSONResponse(
                status_code=status.HTTP_200_OK,
                content={
                    "message": "Authentication successful",
                    "data": {
                        "token_type": "bearer",
                        "access_token": create_access_token(token_payload),
                        "refresh_token": create_refresh_token(token_payload),
                    },
                },
            )

        except HTTPException:
            raise

        except Exception as e:
            logger.error(str(e))
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="An unexpected error has occurred",
            )

    async def get_account_details(self, user_id: str, db: Session) -> JSONResponse:
        try:
            usr_entry = (
                db.query(User).filter(cast(User.user_id, String) == user_id).first()
            )

            if not usr_entry or usr_entry.status == UserAccountStatus.INACTIVE.value:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
                )

            profile_pic_url = None

            usr_profile_pic_entry = (
                db.query(UserProfilePicture)
                .filter(cast(UserProfilePicture.user_id, String) == user_id)
                .first()
            )

            if usr_profile_pic_entry and usr_profile_pic_entry.is_removed == False:
                profile_pic_url = gcs_bucket.generate_signed_url(
                    usr_profile_pic_entry.object_path
                )

            return JSONResponse(
                status_code=status.HTTP_200_OK,
                content={
                    "message": "Account details fetched successfully",
                    "data": {
                        "user_id": str(usr_entry.user_id),
                        "email": usr_entry.email,
                        "profile_picture": {"url": profile_pic_url},
                    },
                },
            )

        except HTTPException:
            raise

        except Exception as e:
            logger.error(str(e))
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="An unexpected error has occurred",
            )

    async def upload_profile_picture(
        self, file: UploadFile, user_id: str, db: Session
    ) -> JSONResponse:
        try:
            if not file.filename:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST, detail="No file provided"
                )

            if not file.content_type.startswith("image/"):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Only image file allowed",
                )

            usr_entry = (
                db.query(User).filter(cast(User.user_id, String) == user_id).first()
            )

            if not usr_entry or usr_entry.status == UserAccountStatus.INACTIVE.value:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="User not found",
                )

            usr_profile_pic_entry = (
                db.query(UserProfilePicture)
                .filter(cast(UserProfilePicture.user_id, String) == user_id)
                .first()
            )

            file_extension = file.filename.split(".")[-1]
            blob_name = f"{user_id}/profile-picture/{user_id}.{file_extension}"
            blob = gcs_bucket.get_blob(blob_name)
            url = None

            if not usr_profile_pic_entry:
                usr_profile_pic_entry = UserProfilePicture(
                    user_id=user_id, object_path=blob_name
                )
                db.add(usr_profile_pic_entry)
            else:
                old_blob_exists = gcs_bucket.blob_exists(
                    usr_profile_pic_entry.object_path
                )
                if old_blob_exists:
                    try:
                        gcs_bucket.delete_blob(usr_profile_pic_entry.object_path)
                    except Exception as e:
                        logger.error(str(e))
                        raise HTTPException(
                            status_code=status.HTTP_400_BAD_REQUEST,
                            detail="Unable to upload profile picture",
                        )

                usr_profile_pic_entry.object_path = blob_name
                usr_profile_pic_entry.is_removed = False
                usr_profile_pic_entry.updated_at = datetime.datetime.now(
                    datetime.timezone.utc
                )

            try:
                file_bytes = await file.read()
                blob.upload_from_string(file_bytes, content_type=file.content_type)
                url = gcs_bucket.generate_signed_url(blob_name)
            except Exception as e:
                logger.error(str(e))
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Unable to upload profile picture",
                )

            db.commit()
            db.refresh(usr_profile_pic_entry)
            return JSONResponse(
                status_code=status.HTTP_200_OK,
                content={
                    "message": "Profile picture updated",
                    "data": {"url": url},
                },
            )

        except HTTPException:
            db.rollback()
            raise

        except Exception as e:
            logger.error(str(e))
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="An unexpected error has occurred",
            )

    async def delete_profile_picture(self, user_id: str, db: Session) -> JSONResponse:
        try:
            usr_profile_pic_entry = (
                db.query(UserProfilePicture)
                .filter(cast(UserProfilePicture.user_id, String) == user_id)
                .first()
            )

            if not usr_profile_pic_entry:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="No existing entry found",
                )

            if usr_profile_pic_entry.is_removed:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Profile picture already deleted",
                )

            if not usr_profile_pic_entry.object_path:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Object path not found",
                )

            blob_exists = gcs_bucket.blob_exists(usr_profile_pic_entry.object_path)

            if not blob_exists:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Unable to delete profile picture",
                )

            try:
                gcs_bucket.delete_blob(usr_profile_pic_entry.object_path)
            except Exception as e:
                logger.error(str(e))
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Unable to delete profile picture",
                )

            usr_profile_pic_entry.is_removed = True
            usr_profile_pic_entry.updated_at = datetime.datetime.now(
                datetime.timezone.utc
            )
            db.commit()
            db.refresh(usr_profile_pic_entry)

            return JSONResponse(
                status_code=status.HTTP_200_OK,
                content={"message": "Profile picture removed"},
            )

        except HTTPException:
            db.rollback()
            raise

        except Exception as e:
            logger.error(str(e))
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="An unexpected error has occurred",
            )

    async def reset_password(
        self, request_body: UserPasswordReset, db: Session
    ) -> JSONResponse:
        try:
            usr_entry = (
                db.query(User)
                .filter(
                    User.email == request_body.email.strip().lower(),
                    User.status == UserAccountStatus.ACTIVE.value,
                )
                .first()
            )

            if not usr_entry:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="User not found",
                )

            usr_entry.password_hash = hash_password(request_body.new_password.strip())
            usr_entry.updated_at = datetime.datetime.now(datetime.timezone.utc)

            db.commit()
            db.refresh(usr_entry)

            return JSONResponse(
                status_code=status.HTTP_200_OK,
                content={"message": "Password reset successfully"},
            )

        except HTTPException:
            raise

        except Exception as e:
            logger.error(str(e))
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="An unexpected error has occurred",
            )
