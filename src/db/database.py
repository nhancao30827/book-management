from typing import AsyncGenerator
from sqlmodel import SQLModel
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy.ext.asyncio import create_async_engine, AsyncEngine, async_sessionmaker
from sqlalchemy.exc import SQLAlchemyError
from src.config import Config

# 1. Create the Async Engine
# This is the core connection to your database.
# echo=True logs SQL queries to the console (turn off for production).
engine: AsyncEngine = create_async_engine(
    Config.DATABASE_URL,
    echo=True,
    future=True
)

# 2. Create the Session Factory (Optimization)
# We create this ONCE globally. Doing this inside get_session() would create 
# a new factory for every single request, which is inefficient.
# expire_on_commit=False is required for async to prevent "Missing Greenlet" errors.
async_session_factory = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False
)

async def init_db():
    """
    Creates the database tables defined in your SQLModel models.
    Should be run on application startup.
    """
    try:
        # We use engine.begin() which automatically commits if no errors occur,
        # or rolls back if an exception is raised.
        async with engine.begin() as conn:
            # run_sync is needed because create_all is a synchronous method
            await conn.run_sync(SQLModel.metadata.create_all)
            print("Database tables created successfully.")
            
    except OSError as e:
        print(f"Connection error: Could not connect to the database at {Config.DATABASE_URL}.")
        print(f"Details: {e}")
    except SQLAlchemyError as e:
        print(f"Database error during initialization: {e}")

async def get_session() -> AsyncGenerator[AsyncSession, None]:
    """
    Dependency function to provide a database session.
    It yields a session and handles cleanup automatically.
    """
    async with async_session_factory() as session:
        try:
            # Yield the session to the route/function calling it
            yield session
            # If the logic above finishes without errors, we are good.
            # (Committing is usually done in the route or service layer, 
            # but some patterns commit here).
            
        except Exception as e:
            # If an exception occurs in your API logic (after yield),
            # we rollback the transaction to ensure data integrity.
            await session.rollback()
            print(f"An error occurred, rolling back session: {e}")
            raise  # Re-raise the exception so FastAPI/Framework knows an error happened
            
        finally:
            # The 'async with' block automatically closes the session,
            # but usually, explicitly closing ensures connection is returned to pool immediately.
            await session.close()