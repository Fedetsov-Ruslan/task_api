from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.users.models import User
from src.auth.utils_jwt import hash_password

async def get_user(session: AsyncSession, username: str):
    query = select(User).where(User.username == username)
    result = await session.execute(query)
    user = result.scalars().first()
    
    if user is None:
        return None
    else:
        return user


async def get_add_user(session: AsyncSession, username: str, password: str):
    new_user = User(username=username, pasword_hash=hash_password(password))
    session.add(new_user)
    await session.commit()
    return {
        "message": "User created successfully",
        "username": new_user.username
    }