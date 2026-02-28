from sqlalchemy import cast, String
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from app.modules.users.models import User

class UserRepository:
    async def create(self, data: dict, db: Session) -> User:
        record = User(**data)
        try:
            db.add(record)
            db.commit()
            db.refresh(record)
            return record
        except SQLAlchemyError as e:
            db.rollback()
            raise e
    
    async def find_by_id(self, user_id: str, db: Session) -> User:
        return db.query(User).filter(cast(User.user_id, String) == user_id).first()
    
    async def find_by_email(self, email: str, db: Session) -> User:
        return db.query(User).filter(User.email == email.lower()).first()
    