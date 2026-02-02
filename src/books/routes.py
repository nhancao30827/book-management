from fastapi import APIRouter, Depends, status
from sqlmodel.ext.asyncio.session import AsyncSession
import uuid

# Imports
from src.books.schemas import BookCreate, BookUpdate, BookRead
from src.books.service import BookService
from src.db.database import get_session
from src.auth.dependencies import RoleChecker, AccessTokenBearer

# 1. Bỏ dependencies=[Depends(role_checker)] ở đây để test xem lỗi do đâu
book_router = APIRouter() 

@book_router.post("/create_book", status_code=status.HTTP_201_CREATED, response_model=BookRead)
async def create_a_book(
    book_data: BookCreate, 
    session: AsyncSession = Depends(get_session), 
    # 2. Dùng AccessTokenBearer() để lấy thông tin user
    token_details: dict = Depends(AccessTokenBearer()),
    # 3. Đưa role_checker vào đây để nó chạy sau khi Token đã được xác thực
    #_: any = Depends(RoleChecker(["admin", "user"])) 
):
    user_uid = token_details.get("sub")
    return await book_service.create_book(session, book_data, user_uid)

@book_router.get("", response_model=list[BookRead])
async def get_all_books(session: AsyncSession = Depends(get_session)):
    return await book_service.get_all_books(session)

@book_router.get("/{book_id}", response_model=BookRead)
async def get_book(book_id: uuid.UUID, session: AsyncSession = Depends(get_session)):
    return await book_service.get_book_by_id(session, book_id)

@book_router.patch("/{book_id}", response_model=BookRead)
async def update_book(
    book_id: uuid.UUID, 
    book_update_data: BookUpdate, 
    session: AsyncSession = Depends(get_session)
):
    return await book_service.update_book(session, book_id, book_update_data)

@book_router.delete("/{book_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_book(book_id: uuid.UUID, session: AsyncSession = Depends(get_session)):
    await book_service.delete_book(session, book_id)
    return None