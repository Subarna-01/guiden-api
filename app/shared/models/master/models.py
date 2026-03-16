from sqlalchemy import (
    Column,
    BigInteger,
    String,
    Text,
    Boolean,
    TIMESTAMP,
    ForeignKey,
    Integer,
)
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.core.database.base import BaseMasterDb


class Country(BaseMasterDb):
    __tablename__ = "countries"
    __table_args__ = {"extend_existing": True}

    country_id = Column("country_id", BigInteger, primary_key=True, autoincrement=True)
    country_name = Column("country_name", String(150), nullable=False)
    iso_code_2 = Column("iso_code_2", String(2), unique=True, nullable=False)
    iso_code_3 = Column("iso_code_3", String(3), unique=True, nullable=False)
    dialing_code = Column("dialing_code", String(10), nullable=False)
    region = Column("region", String(150))
    sub_region = Column("sub_region", String(150))
    description = Column("description", Text)
    is_active = Column("is_active", Boolean, nullable=False, default=True)
    created_at = Column(
        "created_at", TIMESTAMP(timezone=True), server_default=func.now()
    )
    updated_at = Column(
        "updated_at",
        TIMESTAMP(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
    )

    images = relationship(
        "CountryImage", back_populates="country", cascade="all, delete-orphan"
    )
    nationality = relationship(
        "Nationality",
        back_populates="country",
        cascade="all, delete-orphan",
    )
    document_validations = relationship(
        "GovernmentDocumentValidCountry",
        back_populates="country",
        cascade="all, delete-orphan",
    )


class CountryImage(BaseMasterDb):
    __tablename__ = "country_images"
    __table_args__ = {"extend_existing": True}

    _id = Column("_id", BigInteger, primary_key=True, autoincrement=True)
    country_id = Column(
        "country_id",
        BigInteger,
        ForeignKey("countries.country_id", ondelete="CASCADE"),
        nullable=False,
    )
    object_path = Column("object_path", Text, nullable=False)
    image_type = Column("image_type", String(50), nullable=False)
    is_active = Column("is_active", Boolean, nullable=False, default=True)
    created_at = Column(
        "created_at", TIMESTAMP(timezone=True), server_default=func.now()
    )
    updated_at = Column(
        "updated_at",
        TIMESTAMP(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
    )

    country = relationship("Country", back_populates="images")


class Nationality(BaseMasterDb):
    __tablename__ = "nationalities"
    __table_args__ = {"extend_existing": True}

    nationality_id = Column(
        "nationality_id", Integer, primary_key=True, autoincrement=True
    )

    nationality_name = Column(
        "nationality_name", String(150), nullable=False, unique=True
    )

    country_id = Column(
        "country_id", BigInteger, ForeignKey("countries.country_id", ondelete="CASCADE")
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

    country = relationship("Country", back_populates="nationality")


class GovernmentDocumentType(BaseMasterDb):
    __tablename__ = "government_document_types"
    __table_args__ = {"extend_existing": True}

    document_type_id = Column(
        "document_type_id", Integer, primary_key=True, autoincrement=True
    )
    document_type = Column("document_type", String(50), unique=True, nullable=False)
    is_active = Column("is_active", Boolean, nullable=False, default=True)
    created_at = Column(
        "created_at", TIMESTAMP(timezone=True), server_default=func.now()
    )
    updated_at = Column(
        "updated_at",
        TIMESTAMP(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
    )

    valid_countries = relationship(
        "GovernmentDocumentValidCountry",
        back_populates="document_type",
        cascade="all, delete-orphan",
    )


class GovernmentDocumentValidCountry(BaseMasterDb):
    __tablename__ = "government_document_valid_countries"
    __table_args__ = {"extend_existing": True}

    document_type_id = Column(
        "document_type_id",
        Integer,
        ForeignKey("government_document_types.document_type_id", ondelete="CASCADE"),
        primary_key=True,
        nullable=False,
    )
    country_id = Column(
        "country_id",
        BigInteger,
        ForeignKey("countries.country_id", ondelete="CASCADE"),
        nullable=False,
    )
    is_active = Column("is_active", Boolean, nullable=False, default=True)
    created_at = Column(
        "created_at", TIMESTAMP(timezone=True), server_default=func.now()
    )
    updated_at = Column(
        "updated_at",
        TIMESTAMP(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
    )

    document_type = relationship(
        "GovernmentDocumentType", back_populates="valid_countries"
    )
    country = relationship("Country", back_populates="document_validations")
