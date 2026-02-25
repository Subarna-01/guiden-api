from sqlalchemy.orm import Session
from app.modules.users.models import User
from app.modules.users.schemas import UserCreate

class UserRepository:
    def create(self, db: Session, user_data: UserCreate) -> User:
        user = User(**user_data.dict())
        db.add(user)
        db.commit()
        db.refresh(user)
        return user