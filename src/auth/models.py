from sqlmodel import SQLModel, Field, Column
import sqlalchemy.dialects.postgresql as pg
from sqlalchemy.sql import func
from datetime import datetime
import uuid


class User(SQLModel, table=True):
    __tablename__ = "user_accounts"

    uid: uuid.UUID = Field(
        sa_column=Column(
            pg.UUID(as_uuid=True),
            primary_key=True,
            default=uuid.uuid4
        ),
        description="Unique identifier for the user account",
    )

    username: str = Field(index=True, unique=True)
    email: str = Field(index=True, unique=True)

    first_name: str 
    last_name: str 

    is_verified: bool = Field(default=False)

    password_hash: str = Field(exclude=True)

    created_at: datetime = Field(
        sa_column=Column(
            pg.TIMESTAMP(timezone=True),
            server_default=func.now(),
            nullable=False,
        )
    )

    def __repr__(self) -> str:
        return f"<User {self.username}>"
