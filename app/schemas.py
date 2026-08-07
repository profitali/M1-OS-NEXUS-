from pydantic import BaseModel, EmailStr
from typing import Optional

class UserBase(BaseModel):
    email: EmailStr

class UserCreate(UserBase):
    password: str

class UserOut(UserBase):
    id: int
    is_active: bool
    class Config:
        orm_mode = True

class Token(BaseModel):
    access_token: str
    token_type: str

class AppBase(BaseModel):
    name: str
    description: Optional[str] = None

class AppCreate(AppBase):
    owner_id: Optional[int] = None

class AppOut(AppBase):
    id: int
    owner_id: Optional[int] = None
    class Config:
        orm_mode = True

class BuildCreate(BaseModel):
    app_id: int
    platform: Optional[str] = "android"

class BuildOut(BaseModel):
    id: int
    app_id: int
    status: str
    platform: str
    output_url: Optional[str] = None
    class Config:
        orm_mode = True
