from fastapi import status, HTTPException
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from app.core.logging import logger
from app.shared.models.guides.models import Guide, GuideContact, GuideGovernmentDocument
from app.modules.guides.enum import GuideAccountStatus
from app.modules.guides.schemas import GuideAccountCreate


class GuideService:
    def __init__(self) -> None:
        pass

    async def create_account(
        self, request_body: GuideAccountCreate, db: Session
    ) -> JSONResponse:
        try:
            guide_entry = Guide(
                legal_first_name=request_body.legal_first_name,
                legal_middle_name=request_body.legal_middle_name,
                legal_last_name=request_body.legal_last_name,
                date_of_birth=request_body.date_of_birth,
                nationality=request_body.nationality,
                gender=request_body.gender,
                status=GuideAccountStatus.ACTIVE.value,
            )

            guide_entry.guide_contact = GuideContact(
                email=request_body.email,
                is_email_verified=request_body.is_email_verified,
                dialing_code=request_body.dialing_code,
                mobile_number=request_body.mobile_number,
                is_mobile_number_verified=request_body.is_mobile_number_verified,
            )

            guide_entry.guide_government_document = GuideGovernmentDocument(
                document_type_id=request_body.document_type_id,
                document_number=request_body.document_number,
                is_document_verified=request_body.is_document_verified,
            )

            db.add(guide_entry)
            db.commit()

            return JSONResponse(
                status_code=status.HTTP_201_CREATED,
                content={
                    "message": "Account created successfully",
                    "data": {"guide_id": guide_entry.guide_id},
                },
            )

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
