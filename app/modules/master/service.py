import datetime
from starlette.datastructures import FormData
from fastapi import status, HTTPException, UploadFile
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from elasticsearch import Elasticsearch
from app.core.gcp.gcs_bucket import GCSBucket
from app.core.logging import logger
from app.core.settings import settings
from app.shared.models.master.models import Country, CountryImage
from app.modules.master.schemas import CountryCreate

gcs_bucket = GCSBucket(settings.MASTER_BUCKET_NAME)

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
                document={
                    **data.model_dump(),
                    "country_id": country_entry.country_id
                }
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
        
    async def upload_country_image(self, form: FormData, file: UploadFile, client: Elasticsearch, db: Session) -> JSONResponse:
        try:            
            country_id = form.get("country_id")
            image_type = form.get("image_type")
                        
            if not file.filename:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="No file provided"
                )

            if not file.content_type.startswith("image/"):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Only image file allowed",
                )
            
            keys = set()
            duplicate_keys = set()

            for key, _ in form.multi_items():
                if key in keys:
                    duplicate_keys.add(key)
                keys.add(key)

            if duplicate_keys:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Duplicate form keys found"
                )
            
            country_entry = db.query(Country)\
                            .filter(Country.country_id == country_id)\
                            .first()
            
            if not country_entry or not country_entry.is_active:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Country not found",
                )
            
            country_img_entry = db.query(CountryImage)\
                                    .filter(
                                        CountryImage.country_id == country_id,
                                        CountryImage.image_type == image_type
                                    )\
                                    .first()
            
            file_extension = file.filename.split(".")[-1]
            blob_name = f"countries/{country_id}/{image_type}/{country_entry.name}.{file_extension}"
            blob = gcs_bucket.get_blob(blob_name)
            url = None
            
            if not country_img_entry:
                country_img_entry = CountryImage(country_id=country_id, object_path=blob_name, image_type=image_type)
                db.add(country_img_entry)
            else:
                old_blob_exists = gcs_bucket.blob_exists(country_img_entry.object_path)
                if old_blob_exists:
                    try:
                        gcs_bucket.delete_blob(country_img_entry.object_path)
                    except Exception as e:
                        logger.error(str(e))
                        raise HTTPException(
                            status_code=status.HTTP_400_BAD_REQUEST,
                            detail="Unable to upload image"
                        )

                country_img_entry.object_path = blob_name
                country_img_entry.is_active = True
                country_img_entry.updated_at = datetime.datetime.now(datetime.timezone.utc)

            try:
                file_bytes = await file.read()
                blob.upload_from_string(file_bytes, content_type=file.content_type)
                url = blob.public_url
            except Exception as e:
                logger.error(str(e))
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Unable to upload image"
                )
        
            db.commit()
            db.refresh(country_img_entry)

            client.index(
                index="country_images",
                id=country_entry.country_id,
                document={
                    "country_id": country_entry.country_id,
                    "image_type": image_type,
                    "url": url
                }
            )
            return JSONResponse(
                status_code=status.HTTP_200_OK,
                content={
                    "message": "Image uploaded successfully",
                    "data": {
                        "url": url
                    },
                },
            )

        except HTTPException:
            db.rollback()
            raise

        except Exception as e:
            logger.error(str(e))
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="An unexpected error has occurred",
            )