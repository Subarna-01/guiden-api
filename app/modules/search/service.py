from fastapi import status, HTTPException
from fastapi.responses import JSONResponse
from elasticsearch import Elasticsearch, NotFoundError
from app.core.logging import logger

class SearchService:
    def __init__(self) -> None:
        pass

    async def search(self, q: str, page: int, size: int, client: Elasticsearch) -> JSONResponse:
        try:
            country_query = {
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

            try:
                res = client.search(
                    index="countries",
                    body=country_query,
                    from_=(page - 1) * size,
                    size=size
                )
            except NotFoundError:
                return JSONResponse(
                    status_code=status.HTTP_200_OK,
                    content={
                        "query": q,
                        "page": page,
                        "size": size,
                        "total": 0,
                        "results": []
                    }
                )

            hits = res["hits"]["hits"]
            total = res["hits"]["total"]["value"]

            countries = [hit.get("_source", {}) for hit in hits]
            country_ids = [c.get("country_id") for c in countries if c.get("country_id")]

            image_map = {}
            if country_ids:
                try:
                    image_res = client.search(
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

                    for hit in image_res["hits"]["hits"]:
                        src = hit.get("_source", {})
                        cid = src.get("country_id")
                        if cid:
                            image_map[cid] = src.get("url")
                except NotFoundError:
                    image_map = {}

            results_dict = {
                "guides": [],
                "destinations": []
            }

            for c in countries:
                cid = c.get("country_id")
                results_dict["destinations"].append({
                    "id": cid,
                    "name": c.get("name"),
                    "type": "country",
                    "thumbnail": image_map.get(cid)
                })

            return JSONResponse(
                status_code=status.HTTP_200_OK,
                content={
                    "query": q,
                    "page": page,
                    "size": size,
                    "total": total,
                    "results": results_dict
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