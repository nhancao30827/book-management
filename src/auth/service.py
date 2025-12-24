from .models import User
from .schemas import UserCreateModel
from .utils import generate_password_hash
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import select
from datetime import datetime
from src.auth.utils import create_access_token, create_refresh_token, verify_password
from src.auth.dependencies import RefreshTokenBearer

class UserService:
    async def get_user_by_email(self, email: str, session: AsyncSession):
        statement = select(User).where(User.email == email)

        result = await session.exec(statement)

        user = result.first()

        return user

    async def user_exists(self, email, session: AsyncSession):
        user = await self.get_user_by_email(email, session)

        return True if user is not None else False

    async def create_user(self, user_data: UserCreateModel, session: AsyncSession):
        user_data_dict = user_data.model_dump()

        new_user = User(**user_data_dict)

        new_user.password_hash = generate_password_hash(user_data_dict["password"])

        session.add(new_user)
        await session.flush()
        await session.commit()
        await session.refresh(new_user)

        return new_user

# Get all users
    async def get_all_users(self, session: AsyncSession):
        statement = select(User)

        result = await session.exec(statement)

        users = result.all()

        return users

    def refresh_access_token(self, token_details: dict):
        expiry_timestamp = token_details.get("exp")
        user_id = token_details.get("sub")

        # Logic check
        if datetime.fromtimestamp(expiry_timestamp) > datetime.now():
            new_access_token = create_access_token(user_id=user_id)
            return {"access_token": new_access_token}
        
        raise ValueError("Token has expired")
    
    async def register_user(self, user_data, session: AsyncSession):
        """Logic for checking existence and creating a user."""
        email = user_data.email
        user_exists = await user_service.user_exists(email, session)

        if user_exists:
            return None # Or raise a custom UserAlreadyExistsError
        
        return await user_service.create_user(user_data, session)

    async def login_user(self, login_data, session: AsyncSession):
        """Logic for verifying credentials and generating tokens."""
        user = await self.get_user_by_email(login_data.email, session)

        if not user or not verify_password(login_data.password, user.password_hash):
            return None # Or raise an InvalidCredentialsError

        access_token = create_access_token(user_id=str(user.uid))
        refresh_token = create_refresh_token(user_id=str(user.uid))

        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "user": user
        }
    
    async def logout(self, token_details:dict=Depends(AccessTokenBearer())):
        jti = token_details['jti']

        await add_jti_to_blocklist(jti)

        return JSONResponse(
            content={
                "message":"Logged Out Successfully"
            },
            status_code=status.HTTP_200_OK
        )
        
        