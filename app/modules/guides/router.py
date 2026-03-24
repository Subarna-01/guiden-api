from fastapi import APIRouter, Depends, Query
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from functools import partial
from typing import Optional
from app.core.database.dependencies import get_db
from app.core.settings import settings
from app.modules.guides.enum import GuideFilterType
from app.modules.guides.schemas import GuideAccountCreate, GuideExistingRecordCheck
from app.modules.guides.service import GuideService, GuideCategoryService

guides_router = APIRouter(prefix="/guides", tags=["guides"])

guide_service = GuideService()

guide_category_service = GuideCategoryService()


@guides_router.post("/create-account")
async def create_account(
    request_body: GuideAccountCreate,
    db: Session = Depends(partial(get_db, settings.GUIDES_DB_NAME)),
) -> JSONResponse:
    return await guide_service.create_account(request_body, db)


@guides_router.post("/check-existing-record")
async def check_existing_record(
    request_body: GuideExistingRecordCheck,
    db: Session = Depends(partial(get_db, settings.GUIDES_DB_NAME)),
) -> JSONResponse:
    return await guide_service.check_existing_record(request_body, db)


@guides_router.get("/{guide_id}/profile")
async def get_account_details(
    guide_id: str,
    db: Session = Depends(partial(get_db, settings.GUIDES_DB_NAME)),
) -> JSONResponse:
    return await guide_service.get_account_details(guide_id, db)


@guides_router.get("/")
async def get_all(
    filter_type: Optional[GuideFilterType] = Query(default=None),
    filter: Optional[str] = Query(default=None),
    limit: int = Query(default=10, ge=1),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(partial(get_db, settings.GUIDES_DB_NAME)),
) -> JSONResponse:
    return await guide_service.get_all(filter_type, filter, limit, offset, db)


# Guide categories


@guides_router.get("/categories/all")
async def get_all(
    db: Session = Depends(partial(get_db, settings.GUIDES_DB_NAME)),
) -> JSONResponse:
    return await guide_category_service.get_all()
