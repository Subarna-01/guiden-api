from elasticsearch import Elasticsearch
from app.core.settings import settings

class ElasticSearchConnectionManager:
    _instance = None
    _client = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def init_client(self):
        if self._client is None:
            self._client = Elasticsearch(
                hosts=[settings.ELASTICSEARCH_CONNECTION_URL],
                basic_auth=(settings.ELASTICSEARCH_USER, settings.ELASTICSEARCH_PASSWORD),
                request_timeout=30
            )

    def get_client(self):
        return self._client
    
    def close_client(self):
        if self._client:
            self._client.close()
            self._client = None
    
elasticsearch_connection_manager = ElasticSearchConnectionManager()