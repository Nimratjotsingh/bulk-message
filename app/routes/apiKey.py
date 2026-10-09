# app/routes/api_key.py
from typing import List
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.users import User
from app.schemas.api_key import ApiKeyCreate, ApiKeyCreateResponse, ApiKeyResponse
from app.services import api_key_service
from app.dependencies.currentUser import get_current_user

router = APIRouter(
    prefix="/api-keys",
    tags=["API Key Management"],
   
)


@router.post("/", response_model=ApiKeyCreateResponse, status_code=status.HTTP_201_CREATED)
async def create_new_api_key(
    key_data: ApiKeyCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Generates a new API Key. Save the raw key string immediately—it cannot be retrieved again!"""
    return await api_key_service.create_api_key(db, key_data, current_user)


@router.get("/", response_model=List[ApiKeyResponse])
async def list_api_keys(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Lists all API keys created by the current user."""
    return await api_key_service.get_user_api_keys(db, current_user.id)


@router.delete("/{key_id}", status_code=status.HTTP_200_OK)
async def revoke_api_key(
    key_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Revokes an API Key, making it immediately unusable."""
    return await api_key_service.revoke_api_key(db, key_id, current_user.id)