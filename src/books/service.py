from typing import Sequence, Optional
import uuid

from fastapi import HTTPException, status
from sqlmodel import select, desc
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy.exc import SQLAlchemyError, IntegrityError

from src.books.models import Book
from src.books.schemas import BookCreate, BookUpdate

class BookService:
    async def get_all_books(self, session: AsyncSession) -> Sequence[Book]:
        """
        Retrieve all books from the database, ordered by creation date (descending).
        """
        try:
            statement = select(Book).order_by(desc(Book.created_at))
            result = await session.exec(statement)
            return result.all()
        except SQLAlchemyError as e:
            # Log the error here if you have a logger configured
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="An error occurred while fetching books."
            )

    async def get_book_by_id(self, session: AsyncSession, book_id: uuid.UUID) -> Book:
        """
        Retrieve a specific book by its UUID.
        Raises HTTP 404 if not found.
        """
        statement = select(Book).where(Book.uid == book_id)
        result = await session.exec(statement)
        book = result.one_or_none()

        if not book:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, 
                detail=f"Book with ID {book_id} not found"
            )
        
        return book

    async def create_book(self, session: AsyncSession, book_data: BookCreate, token_details: dict) -> Book:
        """
        Create a new book in the database.
        Raises HTTP 409 if a unique constraint is violated.
        """
        try:
            book_dict = book_data.model_dump()
            new_book = Book(**book_dict)
            user_uid = token_details.get("sub")
            new_book.user_uid = user_uid
            session.add(new_book)
            await session.commit()
            await session.refresh(new_book)
            return new_book
            
        except IntegrityError:
            await session.rollback()
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="A book with these details already exists."
            )
        except SQLAlchemyError:
            await session.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="An error occurred while creating the book."
            )

    async def update_book(
        self, session: AsyncSession, book_id: uuid.UUID, book_data: BookUpdate
    ) -> Book:
        """
        Update an existing book. Only updates fields provided in the request (PATCH behavior).
        """
        # Reuse get_book_by_id to handle the 404 check
        book = await self.get_book_by_id(session, book_id)

        # Update model attributes
        update_data = book_data.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(book, key, value)

        try:
            await session.commit()
            await session.refresh(book)
            return book
            
        except IntegrityError:
            await session.rollback()
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Update failed due to unique constraint violation."
            )
        except SQLAlchemyError:
            await session.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="An error occurred while updating the book."
            )

    async def delete_book(self, session: AsyncSession, book_id: uuid.UUID) -> None:
        """
        Delete a book by ID.
        """
        # Reuse get_book_by_id to handle the 404 check
        book = await self.get_book_by_id(session, book_id)

        try:
            await session.delete(book)
            await session.commit()
        except SQLAlchemyError:
            await session.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="An error occurred while deleting the book."
            )