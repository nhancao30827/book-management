from fastapi import FastAPI
from src.books.routes import book_router
from src.auth.routes import auth_router
from src.lifespan import lifespan

app = FastAPI()

app.include_router(book_router, prefix=f"/books")

version = "v1"

register_middleware(app)

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

app.include_router(
    auth_router,
    prefix=f"/api/{version}/auth",
    tags=["auth"]
)

app.include_router(
    review_router,
    prefix=f"/api/{version}/reviews",
    tags=["reviews"]
)