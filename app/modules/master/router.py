from fastapi import APIRouter, Depends, Request, File, UploadFile, Form
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from functools import partial
from elasticsearch import Elasticsearch
from app.core.database.dependencies import get_db
from app.core.decorators.auth import require_auth
from app.core.elasticsearch.connection import elasticsearch_conn_manager
from app.core.settings import settings
from app.modules.master.enum import CountryImageType
from app.modules.master.schemas import CountryAdd
from app.modules.master.service import MasterService

master_router = APIRouter(prefix="", tags=["master"])

master_service = MasterService()


@master_router.post("/countries/add-country")
@require_auth
async def add_country(
    request: Request,
    request_body: CountryAdd,
    elasticsearch_client: Elasticsearch = Depends(
        elasticsearch_conn_manager.get_client
    ),
    db: Session = Depends(partial(get_db, settings.MASTER_DB_NAME)),
) -> JSONResponse:
    return await master_service.add_country(request_body, elasticsearch_client, db)


@master_router.post("/countries/images/upload")
@require_auth
async def upload_country_image(
    request: Request,
    country_id: int = Form(...),
    image_type: CountryImageType = Form(...),
    file: UploadFile = File(...),
    elasticsearch_client: Elasticsearch = Depends(
        elasticsearch_conn_manager.get_client
    ),
    db: Session = Depends(partial(get_db, settings.MASTER_DB_NAME)),
) -> JSONResponse:
    form = await request.form()
    return await master_service.upload_country_image(
        form, file, elasticsearch_client, db
    )


@master_router.get("/countries/codes")
@require_auth
async def get_country_codes(
    request: Request,
    db: Session = Depends(partial(get_db, settings.MASTER_DB_NAME)),
) -> JSONResponse:
    return await master_service.get_country_codes(db)


@master_router.get("/documents/government-valid/{country_id}")
@require_auth
async def get_valid_government_documents_by_country(
    request: Request,
    country_id: int,
    db: Session = Depends(partial(get_db, settings.MASTER_DB_NAME)),
) -> JSONResponse:
    return await master_service.get_valid_government_documents_by_country(
        country_id, db
    )
