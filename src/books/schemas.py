from pydantic import BaseModel, Field, field_validator
from datetime import date, datetime
import uuid

# --- 1. Base Model: Shared properties ---
class BookBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=255, examples=["Clean Code"])
    author: str = Field(..., min_length=2, max_length=100, examples=["Robert C. Martin"])
    publisher: str = Field(..., min_length=2, max_length=100, examples=["Prentice Hall"])
    published_date: date = Field(..., examples=["2008-08-01"])
    page_count: int = Field(..., gt=0, examples=[464]) # gt=0: greater than 0
    language: str = Field(default="English", min_length=2, max_length=50)

# --- 2. Create Model: For POST requests ---
class BookCreate(BookBase):
    @field_validator('published_date')
    @classmethod
    def validate_published_date(cls, v: date):
        if v > date.today():
            raise ValueError("The published date cannot be in the future")
        return v

# --- 3. Update Model: For PATCH requests (All fields optional) ---
class BookUpdate(BaseModel):
    title: str | None = Field(None, min_length=1, max_length=255)
    author: str | None = Field(None, min_length=2, max_length=100)
    publisher: str | None = Field(None, min_length=2, max_length=100)
    published_date: date | None = None
    page_count: int | None = Field(None, gt=0)
    language: str | None = Field(None, min_length=2)

    @field_validator('published_date')
    @classmethod
    def validate_update_date(cls, v: date | None):
        if v and v > date.today():
            raise ValueError("The published date cannot be in the future")
        return v

# --- 4. Read Model: For API responses ---
class BookRead(BookBase):
    uid: uuid.UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        # This allows the model to work with SQLAlchemy objects (ORMs)
        from_attributes = True