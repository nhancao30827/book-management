from fastapi import FastAPI
from sqlmodel import SQLModel
from src.books.routes import book_router
from contextlib import asynccontextmanager
from sqlalchemy.ext.asyncio import create_async_engine, AsyncEngine
from src.config import settings

engine: AsyncEngine = create_async_engine(
    settings.DATABASE_URL,
    echo=True
)

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Application is starting up...")
    await init_db()
    yield
    print("Application is shutting down...")


version = 'v1'

app = FastAPI(
    title='Bookly',
    description='A RESTful API for a book review web service',
    version=version,
    lifespan=lifespan
)

app.include_router(book_router,prefix=f"/api/{version}/books", tags=['books'])

async def init_db():
    async with engine.begin() as conn:
        from src.books.models import Book

        await conn.run_sync(SQLModel.metadata.create_all)