from sqlalchemy import Column, BigInteger, String, Text, Boolean, TIMESTAMP, ForeignKey
from sqlalchemy.sql import func
from app.core.database.base import BaseMasterDb

class Country(BaseMasterDb):
    __tablename__ = "countries"
    __table_args__ = {"extend_existing": True}

    country_id = Column("country_id", BigInteger, primary_key=True, autoincrement=True)
    name = Column("name", String(150), nullable=False)
    iso_code_2 = Column("iso_code_2", String(2), unique=True, nullable=False)
    iso_code_3 = Column("iso_code_3", String(3), unique=True, nullable=False)
    phone_code = Column("phone_code", String(10), nullable=False)
    region = Column("region", String(150))
    sub_region = Column("sub_region", String(150))
    description = Column("description", Text)
    is_active = Column("is_active", Boolean, nullable=False, default=True)
    created_at = Column("created_at", TIMESTAMP(timezone=True), server_default=func.now())
    updated_at = Column("updated_at", TIMESTAMP(timezone=True), server_default=func.now(), onupdate=func.now())

class CountryImage(BaseMasterDb):
    __tablename__ = "country_images"
    __table_args__ = {"extend_existing": True}

    _id = Column("_id", BigInteger, primary_key=True, autoincrement=True)
    country_id = Column("country_id", BigInteger, ForeignKey("countries.country_id", ondelete="CASCADE"), nullable=False)
    object_path = Column("object_path", Text, nullable=False)
    image_type = Column("image_type", String(50), nullable=False)
    is_active = Column("is_active", Boolean, nullable=False, default=True)
    created_at = Column("created_at", TIMESTAMP(timezone=True), server_default=func.now())
    updated_at = Column("updated_at", TIMESTAMP(timezone=True), server_default=func.now(), onupdate=func.now())