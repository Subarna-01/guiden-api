from fastapi import status, HTTPException
from fastapi.responses import JSONResponse
from elasticsearch import Elasticsearch
from app.core.logging import logger

class SearchService:
    def __init__(self) -> None:
        pass

    async def search(self, q: str, page: int, size: int, client: Elasticsearch) -> JSONResponse:
        try:
            query = {
                    "query": {
                        "multi_match": {
                            "query": q.strip(),
                            "fields": [
                                "name^3",
                                "description"
                            ],
                            "type": "phrase_prefix"
                        }
                    }
                }
            
            res = client.search(
                    index="countries",
                    body=query,
                    from_=(page - 1) * size,
                    size=size
                )
            
            hits = res["hits"]["hits"]
            total = res["hits"]["total"]["value"]
            data = [hit["_source"] for hit in hits]
            return JSONResponse(
                status_code=status.HTTP_200_OK,
                content={
                    "query": q,
                    "page": page,
                    "size": size,
                    "total": total,
                    "results": data
                }
            )
        
        except HTTPException:
            raise

        except Exception as e:
            logger.error(str(e))
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="An unexpected error has occurred",
            )