import uuid
from sqlalchemy import Column, Text, Boolean, TIMESTAMP, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from app.core.database.base import BaseUsersDb


class User(BaseUsersDb):
    __tablename__ = "users"
    __table_args__ = {"extend_existing": True}

    user_id = Column(
        "user_id", UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    email = Column("email", Text, unique=True, nullable=False)
    password_hash = Column("password_hash", Text, nullable=False)
    is_email_verified = Column(
        "is_email_verified", Boolean, nullable=False, default=True
    )
    status = Column("status", Text, nullable=False)
    created_at = Column(
        "created_at", TIMESTAMP(timezone=True), server_default=func.now()
    )
    updated_at = Column(
        "updated_at",
        TIMESTAMP(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
    )
    last_logged_in_at = Column(
        "last_logged_in_at", TIMESTAMP(timezone=True), server_default=func.now()
    )
    deactivated_at = Column("deactivated_at", TIMESTAMP(timezone=True))


class UserProfilePicture(BaseUsersDb):
    __tablename__ = "user_profile_pictures"
    __table_args__ = {"extend_existing": True}

    user_id = Column(
        "user_id",
        UUID(as_uuid=True),
        ForeignKey("users.user_id", ondelete="CASCADE"),
        primary_key=True,
        nullable=False,
    )
    object_path = Column("object_path", Text, nullable=False)
    is_removed = Column("is_removed", Boolean, default=False)
    created_at = Column(
        "created_at", TIMESTAMP(timezone=True), server_default=func.now()
    )
    updated_at = Column(
        "updated_at",
        TIMESTAMP(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
    )
