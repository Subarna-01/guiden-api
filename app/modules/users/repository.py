from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from app.modules.users.models import User

class UserRepository:
    def create(self, data: dict, db: Session) -> User:
        record = User(**data)
        try:
            db.add(record)
            db.commit()
            db.refresh(record)
            return record
        except SQLAlchemyError as e:
            db.rollback()
            raise e
    
    def find_by_email(self, email: str, db: Session) -> User:
        return db.query(User).filter(User.email == email).first()