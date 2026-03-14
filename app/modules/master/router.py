from fastapi import APIRouter, Depends, Request, File, UploadFile, Form
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from functools import partial
from elasticsearch import Elasticsearch
from app.core.database.dependencies import get_db
from app.core.decorators.auth import require_auth
from app.core.elasticsearch.connection import elasticsearch_connection_manager
from app.core.settings import settings
from app.modules.master.enum import CountryImageType
from app.modules.master.schemas import CountryCreate
from app.modules.master.service import MasterService

master_router = APIRouter(prefix="/", tags=["master"])

master_service = MasterService()

@master_router.post("/countries/create")
@require_auth
async def create_country(
    request: Request, 
    request_body: CountryCreate, 
    client: Elasticsearch = Depends(elasticsearch_connection_manager.get_client), 
    db: Session = Depends(partial(get_db, settings.MASTER_DB_NAME))
) -> JSONResponse:
    return await master_service.create_country(request_body, client, db)
     
@master_router.post("/countries/images/upload")
@require_auth
async def upload_country_image(
    request: Request, 
    country_id: int = Form(...),
    image_type: CountryImageType = Form(...),
    file: UploadFile = File(...), 
    client: Elasticsearch = Depends(elasticsearch_connection_manager.get_client), 
    db: Session = Depends(partial(get_db, settings.MASTER_DB_NAME))
) -> JSONResponse:
    form = await request.form()
    return await master_service.upload_country_image(form, file, client, db)