from fastapi import status, HTTPException
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from sqlalchemy import cast, String, func
from sqlalchemy.exc import IntegrityError
from app.core.logging import logger
from app.shared.models.guides.models import Guide, GuideContact, GuideCategory
from app.modules.guides.enum import GuideAccountStatus
from app.modules.guides.schemas import GuideAccountCreate, GuideExistingRecordCheck


class GuideService:
    def __init__(self) -> None:
        pass

    async def create_account(
        self, request_body: GuideAccountCreate, db: Session
    ) -> JSONResponse:
        try:
            await self.check_existing_record(
                GuideExistingRecordCheck(
                    email=request_body.email,
                    dialing_code=request_body.dialing_code,
                    mobile_number=request_body.mobile_number,
                ),
                db,
            )

            guide_entry = Guide(
                legal_first_name=request_body.legal_first_name,
                legal_middle_name=request_body.legal_middle_name,
                legal_last_name=request_body.legal_last_name,
                date_of_birth=request_body.date_of_birth,
                country=request_body.country,
                gender=request_body.gender,
                status=GuideAccountStatus.ACTIVE.value,
            )

            guide_entry.guide_contact = GuideContact(
                email=request_body.email.lower(),
                is_email_verified=request_body.is_email_verified,
                dialing_code=request_body.dialing_code,
                mobile_number=request_body.mobile_number,
                is_mobile_number_verified=request_body.is_mobile_number_verified,
            )

            db.add(guide_entry)
            db.commit()

            return JSONResponse(
                status_code=status.HTTP_201_CREATED,
                content={
                    "message": "Account created successfully",
                    "data": {"guide_id": str(guide_entry.guide_id)},
                },
            )

        except HTTPException:
            raise

        except IntegrityError as e:
            db.rollback()
            logger.error(str(e))
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(e),
            )

        except Exception as e:
            db.rollback()
            logger.error(str(e))
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="An unexpected error has occurred",
            )

    async def check_existing_record(
        self, request_body: GuideExistingRecordCheck, db: Session
    ) -> JSONResponse:
        try:
            if (
                "email" in request_body.model_fields_set
                and request_body.email is not None
            ):
                guide_contact_entry = (
                    db.query(GuideContact)
                    .join(Guide, Guide.guide_id == GuideContact.guide_id)
                    .filter(
                        GuideContact.email == request_body.email.lower(),
                        Guide.status == GuideAccountStatus.ACTIVE.value,
                    )
                    .first()
                )

                if guide_contact_entry:
                    raise HTTPException(
                        status_code=status.HTTP_409_CONFLICT,
                        detail="This email already exists",
                    )

            if (
                "dialing_code" in request_body.model_fields_set
                and request_body.dialing_code is not None
                and "mobile_number" in request_body.model_fields_set
                and request_body.mobile_number is not None
            ):
                guide_contact_entry = (
                    db.query(GuideContact)
                    .join(Guide, Guide.guide_id == GuideContact.guide_id)
                    .filter(
                        GuideContact.dialing_code == request_body.dialing_code,
                        GuideContact.mobile_number == request_body.mobile_number,
                        Guide.status == GuideAccountStatus.ACTIVE.value,
                    )
                    .first()
                )

                if guide_contact_entry:
                    raise HTTPException(
                        status_code=status.HTTP_409_CONFLICT,
                        detail="This mobile number already exists",
                    )

            return JSONResponse(
                status_code=status.HTTP_200_OK,
                content={"message": "No existing record found"},
            )

        except HTTPException:
            raise

        except Exception as e:
            logger.error(str(e))
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="An unexpected error has occurred",
            )

    async def get_current_guide(self, guide_id: str, db: Session) -> JSONResponse:
        try:
            guide_entry = (
                db.query(Guide)
                .filter(
                    cast(Guide.guide_id, String) == guide_id,
                    Guide.status == GuideAccountStatus.ACTIVE.value,
                )
                .first()
            )

            if not guide_entry:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Guide not found",
                )

            guide_contact = guide_entry.guide_contact

            return JSONResponse(
                status_code=status.HTTP_200_OK,
                content={
                    "status": "success",
                    "data": {
                        "guide_id": str(guide_entry.guide_id),
                        "legal_first_name": guide_entry.legal_first_name,
                        "legal_middle_name": guide_entry.legal_middle_name,
                        "legal_last_name": guide_entry.legal_last_name,
                        "date_of_birth": str(guide_entry.date_of_birth),
                        "country": guide_entry.country,
                        "gender": guide_entry.gender,
                        "contact": (
                            {
                                "email": guide_contact.email if guide_contact else None,
                                "is_email_verified": (
                                    guide_contact.is_email_verified
                                    if guide_contact
                                    else None
                                ),
                                "dialing_code": (
                                    guide_contact.dialing_code
                                    if guide_contact
                                    else None
                                ),
                                "mobile_number": (
                                    guide_contact.mobile_number
                                    if guide_contact
                                    else None
                                ),
                                "is_mobile_number_verified": (
                                    guide_contact.is_mobile_number_verified
                                    if guide_contact
                                    else None
                                ),
                            }
                            if guide_contact
                            else None
                        ),
                        "account_status": guide_entry.status,
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

    async def get_all_categories(self, db: Session) -> JSONResponse:
        try:
            categories = db.query(
                GuideCategory.category_id,
                GuideCategory.category_name,
                GuideCategory.preview_image_path,
            ).all()

            _data = [
                {
                    "category_id": entry.category_id,
                    "category_name": entry.category_name,
                    "preview_image_path": entry.preview_image_path,
                }
                for entry in categories
            ]

            return JSONResponse(
                status_code=status.HTTP_200_OK,
                content={"status": "success", "data": _data},
            )

        except HTTPException:
            raise

        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="An unexpected error occurred",
            )

    async def filter_by_category(self, db: Session) -> JSONResponse:
        try:
            guide_entries = db.query(
                Guide.guide_id,
                func.concat(
                    Guide.legal_first_name,
                    " ",
                    func.coalesce(Guide.legal_middle_name, ""),
                    " ",
                    Guide.legal_last_name,
                ).label("full_name"),
                Guide.country,
            )

            _data = [
                {
                    "guide_id": str(entry.guide_id),
                    "full_name": " ".join(entry.full_name.split()),
                    "country": entry.country,
                }
                for entry in guide_entries
            ]

            return JSONResponse(
                status_code=status.HTTP_200_OK,
                content={"status": "success", "data": _data},
            )

        except HTTPException:
            raise

        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="An unexpected error occurred",
            )
