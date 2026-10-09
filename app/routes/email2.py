# app/routes/email.py
from typing import Optional
from fastapi import APIRouter, Depends, Header, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.users import User
from app.schemas.email import DirectEmailSendRequest
from app.services import email_service
from app.services.api_key_service import verify_api_key_and_get_user

from app.utils.security import verify_access_token

router = APIRouter(prefix="/email2", tags=["Email Dispatch"])


async def get_authenticated_user(
    x_api_key: Optional[str] = Header(None, alias="X-API-Key"),
    authorization: Optional[str] = Header(None),
    db: AsyncSession = Depends(get_db)
) -> User:
    """Accepts either JWT Bearer token OR X-API-Key for email sending."""
    # 1. Try API Key Header first
    if x_api_key:
        return await verify_api_key_and_get_user(db, x_api_key)

    # 2. Try Authorization Header (JWT or API Key)
    if authorization and authorization.startswith("Bearer "):
        token = authorization.split(" ")[1]
        if token.startswith("bk_live_"):
            return await verify_api_key_and_get_user(db, token)
        
        # Try JWT verification
        try:
            payload = verify_access_token(token)
            user_id = payload.get("sub")
            if user_id:
                from sqlalchemy.future import select
                res = await db.execute(select(User).where(User.id == int(user_id)))
                user = res.scalars().first()
                if user and user.is_active:
                    return user
        except Exception:
            pass

    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Authentication required. Provide a valid JWT token or 'X-API-Key' header."
    )


@router.post("/send", status_code=status.HTTP_200_OK)
async def send_email(
    request_data: DirectEmailSendRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_authenticated_user)
):
    return await email_service.send_direct_email(db, request_data, current_user)