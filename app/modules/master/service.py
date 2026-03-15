import datetime
from starlette.datastructures import FormData
from fastapi import status, HTTPException, UploadFile
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from elasticsearch import Elasticsearch
from app.core.gcp.gcs_bucket import GCSBucket
from app.core.logging import logger
from app.core.settings import settings
from app.shared.models.master.models import (
    Country,
    CountryImage,
    GovernmentDocumentType,
    GovernmentDocumentValidCountry,
)
from app.modules.master.schemas import CountryAdd

gcs_bucket = GCSBucket(settings.MASTER_BUCKET_NAME)


class MasterService:
    def __init__(self) -> None:
        pass

    async def add_country(
        self, data: CountryAdd, elasticsearch_client: Elasticsearch, db: Session
    ) -> JSONResponse:
        try:
            country_entry = (
                db.query(Country)
                .filter(Country.country_name == data.country_name)
                .first()
            )

            if country_entry:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="Country already exists",
                )

            country_entry = Country(**data.model_dump())

            db.add(country_entry)
            db.commit()
            db.refresh(country_entry)

            elasticsearch_client.index(
                index="countries",
                id=country_entry.country_id,
                document={
                    "country_id": country_entry.country_id,
                    **data.model_dump(),
                },
            )
            return JSONResponse(
                status_code=status.HTTP_201_CREATED,
                content={"message": "Country added successfully"},
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

    async def upload_country_image(
        self,
        form: FormData,
        file: UploadFile,
        elasticsearch_client: Elasticsearch,
        db: Session,
    ) -> JSONResponse:
        try:
            country_id = form.get("country_id")
            image_type = form.get("image_type")

            if not file.filename:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST, detail="No file provided"
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
                    detail="Duplicate form keys found",
                )

            country_entry = (
                db.query(Country).filter(Country.country_id == country_id).first()
            )

            if not country_entry or not country_entry.is_active:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Country not found",
                )

            country_img_entry = (
                db.query(CountryImage)
                .filter(
                    CountryImage.country_id == country_id,
                    CountryImage.image_type == image_type,
                )
                .first()
            )

            file_extension = file.filename.split(".")[-1]
            blob_name = f"countries/{country_id}/{image_type}/{country_entry.name}.{file_extension}"
            blob = gcs_bucket.get_blob(blob_name)
            url = None
            is_new = False

            if not country_img_entry:
                is_new = True
                country_img_entry = CountryImage(
                    country_id=country_id, object_path=blob_name, image_type=image_type
                )
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
                            detail="Unable to upload image",
                        )

                country_img_entry.object_path = blob_name
                country_img_entry.is_active = True
                country_img_entry.updated_at = datetime.datetime.now(
                    datetime.timezone.utc
                )

            try:
                file_bytes = await file.read()
                blob.upload_from_string(file_bytes, content_type=file.content_type)
                url = blob.public_url
            except Exception as e:
                logger.error(str(e))
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Unable to upload image",
                )

            db.commit()
            db.refresh(country_img_entry)

            if is_new:
                elasticsearch_client.create(
                    index="country_images",
                    id=f"{country_id}_{image_type}",
                    document={
                        "country_id": country_entry.country_id,
                        "image_type": image_type,
                        "url": url,
                    },
                )
            else:
                elasticsearch_client.update(
                    index="country_images",
                    id=f"{country_id}_{image_type}",
                    doc={
                        "country_id": country_entry.country_id,
                        "image_type": image_type,
                        "url": url,
                    },
                )

            return JSONResponse(
                status_code=status.HTTP_200_OK,
                content={
                    "message": "Image uploaded successfully",
                    "data": {"url": url},
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

    async def get_country_codes(self, db: Session) -> JSONResponse:
        try:
            countries = (
                db.query(
                    Country.country_id,
                    Country.country_name,
                    Country.iso_code_2,
                    Country.iso_code_3,
                    Country.dialing_code,
                )
                .filter(Country.is_active == True)
                .order_by(Country.country_id)
                .all()
            )

            if not countries:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND, detail="No countries found"
                )

            return JSONResponse(
                status_code=status.HTTP_200_OK,
                content={
                    "message": "Country codes fetched successfully",
                    "data": [
                        {
                            "country_id": country.country_id,
                            "country_name": country.country_name,
                            "iso_code_2": country.iso_code_2,
                            "iso_code_3": country.iso_code_3,
                            "dialing_code": country.dialing_code,
                        }
                        for country in countries
                    ],
                },
            )

        except HTTPException:
            raise

        except Exception as e:
            logger.error(str(e))
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="An unexpected error has occurred",
            )

    async def get_valid_government_documents_by_country(
        self, country_id: int, db: Session
    ) -> JSONResponse:
        try:
            country_entry = (
                db.query(Country)
                .filter(Country.country_id == country_id, Country.is_active == True)
                .first()
            )

            if not country_entry:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND, detail="Country not found"
                )

            valid_documents = (
                db.query(GovernmentDocumentType)
                .join(
                    GovernmentDocumentValidCountry,
                    GovernmentDocumentType.document_type_id
                    == GovernmentDocumentValidCountry.document_type_id,
                )
                .filter(
                    GovernmentDocumentValidCountry.country_id == country_id,
                    GovernmentDocumentValidCountry.is_active == True,
                    GovernmentDocumentType.is_active == True,
                )
                .all()
            )

            if not valid_documents:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"No documents found for {country_entry.country_name}",
                )

            return JSONResponse(
                status_code=status.HTTP_200_OK,
                content={
                    "message": f"Documents fetched successfully for {country_entry.country_name}",
                    "data": {
                        "country_id": country_id,
                        "documents": [
                            {
                                "document_type_id": doc.document_type_id,
                                "document_type": doc.document_type,
                            }
                            for doc in valid_documents
                        ],
                    },
                },
            )

        except HTTPException:
            raise

        except Exception as e:
            logger.error(str(e))
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="An unexpected error has occurred",
            )
