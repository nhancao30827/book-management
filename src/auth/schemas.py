from pydantic import BaseModel, Field, EmailStr
from datetime import datetime, date
import uuid

# Base model: common fields
class UserBase(BaseModel):
    uid: uuid.UUID
    username: str
    email: str
    first_name: str
    last_name: str
    is_verified: bool = False
    created_at: datetime


# Schema for reading (exclude password)
class UserRead(UserBase):
    pass

# Schema for creating
class UserCreateModel(BaseModel):
    username: str
    email: str
    first_name: str
    last_name: str
    password: str = Field(..., min_length=8, max_length=100)

# Schema for logging in
class UserLoginModel(BaseModel):
    email: str
    password: str
