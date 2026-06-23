import logging
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status
from db.models import User
from api.schemas.auth import RegisterPayload


logger = logging.getLogger(__name__)


class UserService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_user_by_username(self, username: str) -> User | None:
        result = await self.db.execute(select(User).where(User.username == username))
        return result.scalars().first()
    
    async def get_user_by_email(self, email: str) -> User | None:
        result = await self.db.execute(select(User).where(User.email == email))
        return result.scalar_one_or_none()

    async def create_user(self, payload: RegisterPayload, hashed_password: str) -> User:
        new_user = User(
            username=payload.username,
            password=hashed_password,
            email=payload.email
        )
        self.db.add(new_user)
        
        try:
            await self.db.commit()
            await self.db.refresh(new_user)
            return new_user
        except Exception as e:
            await self.db.rollback()
            logger.error(f"Database error during user creation: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Could not create user in database."
            )

    async def create_oauth_user(self, email: str, username: str, provider: str, provider_id: str) -> User:
        new_user = User(
            email=email,
            username=username,
            password=None,
            provider=provider,
            provider_id=provider_id
        )
        self.db.add(new_user)
        
        try:
            await self.db.commit()
            await self.db.refresh(new_user)
            return new_user
        except Exception as e:
            await self.db.rollback()
            logger.error(f"Database error during OAuth user creation: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Could not create OAuth user in database."
            )
        
    async def update_user_oauth_id(self, user_id: int, provider: str, oauth_id: str):
        user = await self.db.get(User, user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
            
        user.provider_id = oauth_id
        user.provider = provider
        
        try:
            await self.db.commit()
            await self.db.refresh(user)
            return user
        except Exception as e:
            await self.db.rollback()
            logger.error(f"Database error during OAuth update for user {user_id}: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Could not update user authentication details."
            )
