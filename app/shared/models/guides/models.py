import uuid
from sqlalchemy import (
    Column,
    String,
    Date,
    TIMESTAMP,
    ForeignKey,
    Boolean,
    Integer,
    Text,
)
from sqlalchemy.dialects.postgresql import UUID, CITEXT
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.core.database.base import BaseGuidesDb


class Guide(BaseGuidesDb):
    __tablename__ = "guides"
    __table_args__ = {"extend_existing": True}

    guide_id = Column(
        "guide_id", UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    legal_first_name = Column("legal_first_name", String(150), nullable=False)
    legal_middle_name = Column("legal_middle_name", String(150))
    legal_last_name = Column("legal_last_name", String(150), nullable=False)
    date_of_birth = Column("date_of_birth", Date, nullable=False)
    nationality = Column("nationality", String(50), nullable=False)
    gender = Column("gender", String(50), nullable=False)
    status = Column("status", String(50), nullable=False)
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
    deleted_at = Column("deleted_at", TIMESTAMP(timezone=True))

    guide_contact = relationship(
        "GuideContact",
        back_populates="guide",
        uselist=False,
        cascade="all, delete-orphan",
    )

    guide_government_document = relationship(
        "GuideGovernmentDocument", back_populates="guide", cascade="all, delete-orphan"
    )


class GuideContact(BaseGuidesDb):
    __tablename__ = "guide_contacts"
    __table_args__ = {"extend_existing": True}

    guide_id = Column(
        "guide_id",
        UUID(as_uuid=True),
        ForeignKey("guides.guide_id", ondelete="CASCADE"),
        primary_key=True,
        nullable=False,
    )
    email = Column("email", CITEXT, unique=True, nullable=False)
    is_email_verified = Column(
        "is_email_verified", Boolean, nullable=False, default=False
    )
    dialing_code = Column("dialing_code", String(10), nullable=False)
    mobile_number = Column("mobile_number", String(15), unique=True, nullable=False)
    is_mobile_number_verified = Column(
        "is_mobile_number_verified", Boolean, nullable=False, default=False
    )
    created_at = Column(
        "created_at", TIMESTAMP(timezone=True), server_default=func.now()
    )
    updated_at = Column(
        "updated_at",
        TIMESTAMP(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
    )

    guide = relationship("Guide", back_populates="guide_contact", uselist=False)


class GuideGovernmentDocument(BaseGuidesDb):
    __tablename__ = "guide_government_documents"
    __table_args__ = {"extend_existing": True}

    document_id = Column(
        "document_id", UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    guide_id = Column(
        "guide_id",
        UUID(as_uuid=True),
        ForeignKey("guides.guide_id", ondelete="CASCADE"),
        nullable=False,
    )
    document_type_id = Column("document_type_id", Integer, nullable=False)
    document_number = Column("document_number", String(50), unique=True, nullable=False)
    is_document_verified = Column(
        "is_document_verified", Boolean, nullable=False, default=False
    )
    created_at = Column(
        "created_at", TIMESTAMP(timezone=True), server_default=func.now()
    )

    guide = relationship("Guide", back_populates="guide_government_document")
