from fastapi import APIRouter, Depends, status, HTTPException
from sqlmodel.ext.asyncio.session import AsyncSession
from src.books.schemas import BookCreate, BookUpdate, BookRead
from src.books.service import BookService
from src.db.database import get_session
import uuid


book_router = APIRouter()
book_service = BookService()

@book_router.get("", response_model=list[BookRead])
async def get_all_books(session: AsyncSession = Depends(get_session)):
    return await book_service.get_all_books(session)


@book_router.post("", status_code=status.HTTP_201_CREATED, response_model=BookRead)
async def create_a_book(book_data: BookCreate, session: AsyncSession = Depends(get_session)):
    return await book_service.create_book(session, book_data)


@book_router.get("/{book_id}", response_model=BookRead)
async def get_book(book_id: uuid.UUID, session: AsyncSession = Depends(get_session)):
    return await book_service.get_book_by_id(session, book_id)


@book_router.patch("/{book_id}", response_model=BookRead)
async def update_book(book_id: uuid.UUID, book_update_data: BookUpdate, session: AsyncSession = Depends(get_session)):
    return await book_service.update_book(session, book_id, book_update_data)


@book_router.delete("/{book_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_book(book_id: uuid.UUID, session: AsyncSession = Depends(get_session)):
    await book_service.delete_book(session, book_id)