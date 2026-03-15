from datetime import date
from pydantic import BaseModel, constr, EmailStr, field_validator, model_validator
from typing import Optional


class GuideAccountCreate(BaseModel):
    legal_first_name: constr(max_length=150, pattern=r"^[A-Za-z]+$")  # type: ignore
    legal_middle_name: Optional[constr(max_length=150, pattern=r"^[A-Za-z]+$")] = None  # type: ignore
    legal_last_name: constr(max_length=150, pattern=r"^[A-Za-z]+$")  # type: ignore
    date_of_birth: date
    nationality: str
    gender: str
    email: EmailStr
    is_email_verified: bool
    dialing_code: str
    mobile_number: constr(max_length=15, pattern=r"^[0-9]+$")  # type: ignore
    is_mobile_number_verified: bool
    document_type_id: int
    document_number: str
    is_document_verified: bool

    @field_validator(
        "legal_first_name",
        "legal_middle_name",
        "legal_last_name",
        "mobile_number",
        mode="before",
    )
    @classmethod
    def remove_whitespaces(cls, value):
        if value is None:
            return value
        return value.strip()


class GuideExistingRecordCheck(BaseModel):
    email: Optional[EmailStr] = None
    dialing_code: Optional[str] = None
    mobile_number: Optional[str] = None
    document_type_id: Optional[int] = None
    document_number: Optional[str] = None

    @field_validator(
        "mobile_number",
        "document_number",
        mode="before",
    )
    @classmethod
    def remove_whitespaces(cls, value):
        if value is None:
            return value
        return value.strip()

    @model_validator(mode="after")
    def validate_dialing_code_and_mobile_number(self):
        if (self.mobile_number and not self.dialing_code) or (
            self.dialing_code and not self.mobile_number
        ):
            raise ValueError("dialing_code and mobile_number must be provided together")
        return self

    @model_validator(mode="after")
    def validate_document_type_id_and_document_number(self):
        if (self.document_number and not self.document_type_id) or (
            self.document_type_id and not self.document_number
        ):
            raise ValueError(
                "document_type_id and document_number must be provided together"
            )
        return self
