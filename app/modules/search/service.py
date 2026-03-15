from fastapi import status, HTTPException
from fastapi.responses import JSONResponse
from elasticsearch import Elasticsearch
from app.core.logging import logger

class SearchService:
    def __init__(self) -> None:
        pass

    async def get_search_results(
        self, 
        q: str, 
        page: int, 
        size: int, 
        client: Elasticsearch
    ) -> JSONResponse:
        try:    
            country_res = client.search(
                            index="countries",
                            body={
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
                            },
                            from_=(page - 1) * size,
                            size=size
                        )

            hits = country_res["hits"]["hits"]
            total = country_res["hits"]["total"]["value"]

            countries = [hit.get("_source", {}) for hit in hits]
            country_ids = [c.get("country_id") for c in countries if c.get("country_id")]

            country_images = {}
            
            if country_ids:
                country_img_res = client.search(
                                    index="country_images",
                                    body={
                                        "query": {
                                            "bool": {
                                                "must": [
                                                    {"terms": {"country_id": country_ids}},
                                                    {"term": {"image_type": "thumbnail"}}
                                                ]
                                            }
                                        },
                                        "size": len(country_ids)
                                    }
                                )

                for hit in country_img_res["hits"]["hits"]:
                    src = hit.get("_source", {})
                    cid = src.get("country_id")
                    if cid:
                        country_images[cid] = src.get("url")

            data = {
                "guides": [],
                "destinations": []
            }

            for c in countries:
                cid = c.get("country_id")
                data["destinations"].append({
                    "id": cid,
                    "name": c.get("name"),
                    "type": "country",
                    "thumbnail": country_images.get(cid)
                })

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