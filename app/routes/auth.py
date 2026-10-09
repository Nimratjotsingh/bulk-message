from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.schemas.users import UserCreate, UserLogin, UserResponse
from app.services.auth_service import create_user_service, authenticate_user_service

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/signup", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def signup(user_data: UserCreate, db: AsyncSession = Depends(get_db)):
    return await create_user_service(user_data, db)


@router.post("/login")
async def login(login_data: UserLogin, db: AsyncSession = Depends(get_db)):
    return await authenticate_user_service(login_data, db)