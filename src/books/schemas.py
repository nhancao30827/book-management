from pydantic import BaseModel
from datetime import date, datetime
import uuid


class BookBase(BaseModel):
    title: str
    author: str
    publisher: str
    published_date: date
    page_count: int
    language: str


class BookCreate(BookBase):
    pass


class BookUpdate(BaseModel):
    title: str | None = None
    author: str | None = None
    publisher: str | None = None
    published_date: date | None = None
    page_count: int | None = None
    language: str | None = None


class BookRead(BookBase):
    uid: uuid.UUID
    created_at: datetime
    updated_at: datetime

