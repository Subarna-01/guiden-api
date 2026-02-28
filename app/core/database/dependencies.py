from typing import Generator
from sqlalchemy.orm import Session
from app.core.database.connection import db_connection_manager

def get_db(db_name: str) -> Generator[Session, None, None]:
    SessionLocal = db_connection_manager.get_session(db_name)
    
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()