from fastapi import Depends, HTTPException, status,Header
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.database import get_db
from app.models.users import User
from app.utils.security import verify_access_token

# tokenUrl must point to your login route path for Swagger UI 'Authorize' button
# oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

async def get_current_user(
    token: str = Depends(oauth2_scheme), 
    db: AsyncSession = Depends(get_db)
) -> User:
    # Clean 'Bearer ' prefix if passed manually via raw headers
    if token.startswith("Bearer "):
        token = token.split(" ")[1]

    # 1. Verify token & extract payload
    payload = verify_access_token(token)
    user_id: str = payload.get("sub")
    
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # 2. Fetch user asynchronously from Neon PostgreSQL
    result = await db.execute(select(User).where(User.id == int(user_id)))
    user = result.scalars().first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user account"
        )

    return user