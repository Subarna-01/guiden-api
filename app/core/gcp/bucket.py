import json
from typing import Optional
from google.cloud import storage
from google.cloud.storage.bucket import Bucket as GCSBucket
from google.cloud import secretmanager
from google.oauth2 import service_account
from app.core.settings import settings

class Bucket:
    _instance: Optional["Bucket"] = None
    storage_client: storage.Client

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.init_storage_client()
        return cls._instance
    
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

    def get_bucket(self, bucket_name: str) -> GCSBucket:
        return self.storage_client.bucket(bucket_name)
    
bucket = Bucket()