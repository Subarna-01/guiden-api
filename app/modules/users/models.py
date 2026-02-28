import uuid
from sqlalchemy import (
    Column,
    Text,
    Boolean,
    TIMESTAMP,
)
from sqlalchemy.dialects.postgresql import UUID, INET
from sqlalchemy.sql import func
from app.core.database.base import BaseDb1
class User(BaseDb1):
    __tablename__ = "users"
    __table_args__ = {"extend_existing": True}

    user_id = Column("user_id", UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column("email", Text, unique=True, nullable=False)
    password_hash = Column("password_hash", Text, nullable=False)
    is_otp_verified = Column("is_otp_verified", Boolean, nullable=False, default=True)
    status = Column("status", Text, nullable=False)
    created_at = Column("created_at", TIMESTAMP(timezone=True), server_default=func.now())
    updated_at = Column("updated_at", TIMESTAMP(timezone=True), server_default=func.now(), onupdate=func.now())
    last_logged_in_at = Column("last_logged_in_at", TIMESTAMP(timezone=True), server_default=func.now())
    deactivated_at = Column("deactivated_at", TIMESTAMP(timezone=True))
    ipv4_addr_created_at = Column("ipv4_addr_created_at", INET)
    ipv4_addr_last_logged_in_at = Column("ipv4_addr_last_logged_in_at", INET)
