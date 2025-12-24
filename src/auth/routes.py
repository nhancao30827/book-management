from fastapi import APIRouter, Depends, status
from .schemas import UserCreateModel, UserBase, UserLoginModel
from .service import UserService
from src.db.database import get_session
from sqlmodel.ext.asyncio.session import AsyncSession
from fastapi.exceptions import HTTPException
from fastapi.responses import JSONResponse
from src.auth.dependencies import RefreshTokenBearer

auth_router = APIRouter()
user_service = UserService()

@auth_router.post("/signup", response_model=UserBase, status_code=status.HTTP_201_CREATED)
async def create_user_account(user_data: UserCreateModel, session: AsyncSession = Depends(get_session)):
    new_user = await user_service.register_user(user_data, session)
    
    if not new_user:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User with email already exists",
        )
    return new_user

@auth_router.get("/all_users", response_model=list[UserBase])
async def get_all_users(session: AsyncSession = Depends(get_session)):
    return await user_service.get_all_users(session)

@auth_router.post("/login")
async def login_users(login_data: UserLoginModel, session: AsyncSession = Depends(get_session)):
    result = await user_service.login_user(login_data, session)

    if not result:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )

    response = JSONResponse(
        content={
            "access_token": result["access_token"],
            "token_type": "bearer",
        }
    )

    # We keep cookie logic in the route because it's an HTTP concern
    response.set_cookie(
        key="refresh_token",
        value=result["refresh_token"],
        httponly=True,
        secure=True,
        samesite="strict",
    )

    return response

@auth_router.get("/refresh_token")
async def get_new_access_token(token_details: dict = Depends(RefreshTokenBearer())):
    try:
        result = user_service.refresh_access_token(token_details)
        return JSONResponse(content=result)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail=str(e)
        )

@auth_router.get('/logout')
async def revoke_token(token_details:dict=Depends(AccessTokenBearer())):
    await user_service.logout(token_details)
   