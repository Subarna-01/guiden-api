import json
import datetime
from google.cloud import storage, secretmanager
from google.cloud.storage.bucket import Bucket
from google.cloud.storage.blob import Blob
from google.oauth2 import service_account
from app.core.settings import settings

class GCSBucket:
    def __init__(self, bucket_name: str) -> None:
        self.bucket_name = bucket_name
        self.init_storage_client()

    def init_storage_client(self) -> None:
        secret_client = secretmanager.SecretManagerServiceClient()
        secret_path = (
            f"projects/{settings.GCS_PROJECT_ID}/secrets/{settings.GCS_SECRET_ID}/versions/{settings.GCS_SECRET_VERSION}"
        )
        response = secret_client.access_secret_version(name=secret_path)
        secret_payload = response.payload.data.decode("UTF-8")
        service_account_info = json.loads(secret_payload)
        credentials = service_account.Credentials.from_service_account_info(service_account_info)
        self.storage_client = storage.Client(credentials=credentials)

    def get_bucket(self) -> Bucket:
        return self.storage_client.bucket(self.bucket_name)
    
    def get_blob(self, blob_name: str) -> Blob:
        return self.get_bucket().blob(blob_name)
    
    def blob_exists(self, blob_name: str) -> bool:
        return  self.get_blob(blob_name).exists()
    
    def generate_signed_url(
        self,
        blob_name: str,
        method: str = "GET",
    ) -> str:
        url: str = self.get_blob(blob_name).generate_signed_url(
            version="v4",
            expiration=datetime.timedelta(minutes=settings.GCS_SIGNED_URL_EXPIRE_MINUTES),
            method=method,
        )
        return url

    def delete_blob(self, blob_name: str) -> None:
        self.get_blob(blob_name).delete()

    