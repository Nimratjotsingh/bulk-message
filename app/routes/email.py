# app/routes/email.py
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.users import User
from app.schemas.email import DirectEmailSendRequest
from app.services import email_service
from app.dependencies.currentUser import get_current_user

router = APIRouter(
    prefix="/email", 
    tags=["Email Dispatch"], 
)


@router.post("/send", status_code=status.HTTP_200_OK)
async def send_email(
    request_data: DirectEmailSendRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
   
    return await email_service.send_direct_email(db, request_data, current_user)