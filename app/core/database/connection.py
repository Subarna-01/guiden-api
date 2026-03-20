from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from typing import Dict
from app.core.settings import settings
class DbConnectionManager:
    _instance = None
    _engines: Dict[str, any] = {}
    _sessions: Dict[str, any] = {}
    DATABASE_URL: str = (
        f"postgresql://{settings.POSTGRES_USER}:{settings.POSTGRES_PASSWORD}@{settings.POSTGRES_HOST}:{settings.POSTGRES_PORT}"
    )

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def init_engines(self, db_names):
        for db_name in db_names:
            engine = create_engine(
                f"{self.DATABASE_URL}/{db_name}", echo=False, future=True, isolation_level="READ COMMITTED"
            )
            SessionLocal = sessionmaker(bind=engine)
            self._engines[db_name] = engine
            self._sessions[db_name] = SessionLocal

    def get_engine(self, db_name):
        return self._engines.get(db_name)

    def get_session(self, db_name):
        return self._sessions.get(db_name)

    def close_all(self):
        for engine in self._engines.values():
            engine.dispose()

db_conn_manager = DbConnectionManager()
