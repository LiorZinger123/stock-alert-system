from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession
from db.models import User
from api.schemas.auth import RegisterPayload


class UserService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_user_by_username(self, username: str) -> User | None:
        result = await self.db.execute(select(User).where(User.username == username))
        return result.scalars().first()
    
    async def get_user_by_email(self, email: str):
        result = await self.db.execute(select(User).where(User.email == email))
        return result.scalar_one_or_none()

    async def create_user(self, payload: RegisterPayload, hashed_password: str) -> User:
        new_user = User(
            username=payload.username,
            password=hashed_password,
            email=payload.email
        )
        self.db.add(new_user)
        
        await self.db.commit()
        await self.db.refresh(new_user)
        return new_user
