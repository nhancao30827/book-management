from fastapi import FastAPI
from src.books.routes import book_router
from src.lifespan import lifespan

app = FastAPI()

app.include_router(book_router, prefix=f"/books")

version = "v1"

app = FastAPI(
    title="Bookly",
    description="A RESTful API for a book review web service",
    version=version,
    lifespan=lifespan
)

app.include_router(
    book_router,
    prefix=f"/api/{version}/books",
    tags=["books"]
)
