from typing import Dict, Any
from fastapi import Request, HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from src.auth.utils import decode_token
from src.db.redis import token_in_blocklist
from src.auth.models import User
from typing import List, Any
from src.db.database import get_session
from sqlmodel.ext.asyncio.session import AsyncSession
from src.auth.service import UserService

class TokenBearer(HTTPBearer):
    async def __call__(self, request: Request) -> Dict[str, Any]:
        creds: HTTPAuthorizationCredentials = await super().__call__(request)

        if not creds or not creds.credentials:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail={"error": "Authorization token is missing"},
            )

        try:
            token_data = decode_token(creds.credentials)
        except Exception:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail={"error": "Invalid or expired token"},
            )

        jti = token_data.get("jti")
        if not jti:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={"error": "Token is missing JTI claim"},
            )

        if await token_in_blocklist(jti):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail={
                    "error": "This token is invalid or has been revoked",
                    "resolution": "Please get a new token",
                },
            )

        self.verify_token_data(token_data)
        return token_data

    def verify_token_data(self, token_data: Dict[str, Any]) -> None:
        raise NotImplementedError


class TypedTokenBearer(TokenBearer):
    required_type: str = "access"

    def verify_token_data(self, token_data: Dict[str, Any]) -> None:
        if token_data.get("type") != self.required_type:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Please provide a {self.required_type} token",
            )

class AccessTokenBearer(TypedTokenBearer):
    required_type = "access"


class RefreshTokenBearer(TypedTokenBearer):
    required_type = "refresh"

async def get_current_user(token_details: dict = Depends(AccessTokenBearer()), session: AsyncSession = Depends(get_session),):
    user_id = token_details["sub"]
    user = await UserService().get_user_by_id(user_id, session)
    user_email = user.email

    return user

class RoleChecker:
    def __init__(self, allowed_roles: list[str]) -> None:
        self.allowed_roles = allowed_roles

    def __call__(self, current_user: User = Depends(get_current_user)) -> Any:
        if current_user.role in self.allowed_roles:
            return True

        raise HTTPException(
            status_code = status.HTTP_403_FORBIDDEN,
            detail="You are not allowed to perform this action.",
        )


        