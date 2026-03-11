from pydantic import BaseModel, constr
from typing import Optional

class CountryCreate(BaseModel):
    name: constr(max_length=150) # type: ignore
    iso_code_2: constr(min_length=2, max_length=2) # type: ignore
    iso_code_3: constr(min_length=3, max_length=3) # type: ignore
    phone_code: constr(max_length=10) # type: ignore
    region: Optional[constr(max_length=150)] = None # type: ignore
    sub_region: Optional[constr(max_length=150)] = None # type: ignore
    description: str