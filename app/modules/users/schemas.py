from pydantic import BaseModel, constr, EmailStr


class UserCreate(BaseModel):
    email: EmailStr
    password: constr(min_length=8)  # type: ignore


class UserLogin(BaseModel):
    email: EmailStr
    password: str
