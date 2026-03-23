from pydantic import BaseModel, constr, EmailStr


class UserAccountCreate(BaseModel):
    email: EmailStr
    password: constr(min_length=8)  # type: ignore


class UserAccountLogin(BaseModel):
    email: EmailStr
    password: str

class UserPasswordReset(BaseModel):
    email: EmailStr
    new_password: constr(min_length=8)  # type: ignore
