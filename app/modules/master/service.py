from fastapi import status, HTTPException
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from elasticsearch import Elasticsearch
from app.core.logging import logger
from app.shared.models.master.models import Country
from app.modules.master.schemas import CountryCreate

class MasterService:
    def __init__(self) -> None:
        pass

    async def create_country(self, data: CountryCreate, client: Elasticsearch,  db: Session) -> JSONResponse:
        try:
            country_entry = db.query(Country)\
                        .filter(Country.name == data.name)\
                        .first()

            if country_entry:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="Country already exists"
                )
            
            country_entry = Country(**data.model_dump())
            
            db.add(country_entry)
            db.commit()
            db.refresh(country_entry)

            client.index(
                index="countries",
                id=country_entry.country_id,
                document=data.model_dump()
            )

            return JSONResponse(
                status_code=status.HTTP_201_CREATED,
                content={
                    "message": "Country added successfully"
                },
            )
        
        except HTTPException:
            raise

        except Exception as e:
            logger.error(str(e))
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="An unexpected error has occurred",
            )