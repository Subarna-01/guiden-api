from datetime import date
from pydantic import BaseModel, constr, EmailStr
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
