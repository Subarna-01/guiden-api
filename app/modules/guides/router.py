from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from functools import partial
from app.core.database.dependencies import get_db
from app.core.settings import settings
from app.modules.guides.schemas import GuideAccountCreate, GuideExistingRecordCheck
from app.modules.guides.service import GuideService

guides_router = APIRouter(prefix="/guides", tags=["guides"])

guide_service = GuideService()


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


@guides_router.get("/me")
async def get_current_guide(
    guide_id: str,
    db: Session = Depends(partial(get_db, settings.GUIDES_DB_NAME)),
) -> JSONResponse:
    return await guide_service.get_current_guide(guide_id, db)


@guides_router.get("/categories")
async def get_all_categories(
    db: Session = Depends(partial(get_db, settings.GUIDES_DB_NAME)),
) -> JSONResponse:
    return await guide_service.get_all_categories(db)


@guides_router.get("/filter-by-category")
async def filter_by_category(
    db: Session = Depends(partial(get_db, settings.GUIDES_DB_NAME)),
) -> JSONResponse:
    return await guide_service.filter_by_category(db)
