from sqlmodel import SQLModel, Field, Column
import sqlalchemy.dialects.postgresql as pg
from datetime import datetime, date
import uuid

class Book(SQLModel, table=True):
    __tablename__ = "books"

    uid: uuid.UUID = Field(
        sa_column=Column(
            pg.UUID(as_uuid=True),
            primary_key=True,
            default=uuid.uuid4
        )
    )
    
    title: str = Field(...,max_length=255, index=True)
    author: str = Field(...,max_length=255)
    publisher: str = Field(...,max_length=255)
    published_date: date = Field(...)
    page_count: int
    language: str = Field(...,max_length=50)

    created_at: datetime = Field(
        sa_column=Column(pg.TIMESTAMP, default=datetime.utcnow)
    )
    updated_at: datetime = Field(
        sa_column=Column(pg.TIMESTAMP, default=datetime.utcnow, onupdate=datetime.utcnow)
    )

    def __repr__(self) -> str:
        return f"<Book {self.title}>"