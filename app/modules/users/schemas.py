from pydantic import BaseModel, constr, EmailStr


class UserAccountCreate(BaseModel):
    email: EmailStr
    password: constr(min_length=8)  # type: ignore


class UserAccountLogin(BaseModel):
    email: EmailStr
    password: str
