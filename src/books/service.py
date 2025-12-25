from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import select, desc
from fastapi import HTTPException, status
from src.books.models import Book
from src.books.schemas import BookCreate, BookUpdate
from src.db.redis import add_jti_to_blocklist
import uuid

class BookService:
    async def get_all_books(self, session: AsyncSession) -> list[Book]:
        statement = select(Book).order_by(desc(Book.created_at))
        result = await session.exec(statement)
        return result.all()

    async def get_book_by_id(self, session: AsyncSession, book_id: uuid.UUID) -> Book:
        statement = select(Book).where(Book.uid == book_id)
        result = await session.exec(statement)
        book = result.one_or_none()

        if not book:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Book not found")
        
        return book

    async def create_book(self, session: AsyncSession, book_data: BookCreate) -> Book:
        book_dict = book_data.model_dump()
        new_book = Book(**book_dict)
        session.add(new_book)
        await session.commit()
        await session.refresh(new_book)
        return new_book

    async def update_book(self, session: AsyncSession, book_id: uuid.UUID, book_data: BookUpdate) -> Book:
        statement = select(Book).where(Book.uid == book_id)
        result = await session.exec(statement)
        book = result.one_or_none()

        if not book:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Book not found")

        for key, value in book_data.model_dump(exclude_unset=True).items():
            setattr(book, key, value)

        await session.commit()
        await session.refresh(book)
        return book


    async def delete_book(self, session: AsyncSession, book_id: uuid.UUID):
        statement = select(Book).where(Book.uid == book_id)
        result = await session.exec(statement)
        book = result.one_or_none()

        if not book:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Book not found")

        await session.delete(book)
        await session.commit()
        return status.HTTP_200_OK