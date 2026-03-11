from fastapi import APIRouter, Query, Depends
from fastapi.responses import JSONResponse
from elasticsearch import Elasticsearch
from app.core.elasticsearch.connection import elasticsearch_connection_manager
from app.core.security import jwt
from app.modules.search.service import SearchService

search_router = APIRouter(prefix="/search", tags=["search"])

search_service = SearchService()

@search_router.get("/")
async def search(q: str = Query(...), page: int = 1, size: int = 10, decoded_token_data: dict = Depends(jwt.authenticate), client: Elasticsearch = Depends(elasticsearch_connection_manager.get_client)) -> JSONResponse:
    return await search_service.search(q, page, size, client)
     