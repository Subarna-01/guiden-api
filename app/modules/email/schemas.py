from pydantic import BaseModel, EmailStr, Field, constr
from typing import Union, Annotated, Literal
from app.modules.email.enum import EmailTemplate

class UserVerifyOtpEmail(BaseModel):
    to: EmailStr
    otp: constr(min_length=4, max_length=4, pattern=r"^\d{4}$") # type: ignore
    otp_validity_mins: int
    template_name: Literal[EmailTemplate.VERIFY_OTP.value] = EmailTemplate.VERIFY_OTP.value # type: ignore

class UserAccountCreateEmail(BaseModel):
    to: EmailStr
    template_name: Literal[EmailTemplate.ACCOUNT_CREATE.value] = EmailTemplate.ACCOUNT_CREATE.value # type: ignore

Email = Annotated[
    Union[UserVerifyOtpEmail, UserAccountCreateEmail],
    Field(discriminator="template_name")
]
    