from typing import List
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.users import User
from app.schemas.smtp import SmtpConfigCreate, SmtpConfigResponse, SmtpConfigUpdate
from app.services import smtp_service
from app.dependencies.currentUser import get_current_user

router = APIRouter(
    prefix="/smtp", 
    tags=["SMTP Management"], 
)


@router.post("/", response_model=SmtpConfigResponse, status_code=status.HTTP_201_CREATED)
async def create_smtp(
    smtp_data: SmtpConfigCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return await smtp_service.create_smtp_config(db, smtp_data, current_user)


@router.get("/", response_model=List[SmtpConfigResponse])
async def list_smtp_configs(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return await smtp_service.get_user_smtp_configs(db, current_user.id)


@router.get("/{config_id}", response_model=SmtpConfigResponse)
async def get_smtp_config(
    config_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return await smtp_service.get_smtp_config_by_id(db, config_id, current_user.id)


@router.put("/{config_id}", response_model=SmtpConfigResponse)
async def update_smtp(
    config_id: int,
    smtp_data: SmtpConfigUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return await smtp_service.update_smtp_config(db, config_id, smtp_data, current_user)


@router.delete("/{config_id}", status_code=status.HTTP_200_OK)
async def delete_smtp(
    config_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return await smtp_service.delete_smtp_config(db, config_id, current_user.id)


@router.post("/{config_id}/test", status_code=status.HTTP_200_OK)
async def test_smtp_server(
    config_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    config = await smtp_service.get_smtp_config_by_id(db, config_id, current_user.id)
    await smtp_service.test_smtp_connection(config)
    return {"status": "success", "message": "SMTP Connection tested successfully!"}