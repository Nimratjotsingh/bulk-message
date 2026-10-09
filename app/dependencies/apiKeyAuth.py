# app/dependencies/apiKeyAuth.py
from typing import Annotated, Optional
from fastapi import Depends, Header, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.users import User
from app.services.api_key_service import verify_api_key_and_get_user


async def get_user_by_api_key(
    x_api_key: Annotated[Optional[str], Header(alias="X-API-Key")] = None,
    authorization: Annotated[Optional[str], Header()] = None,
    db: AsyncSession = Depends(get_db)
) -> User:
    """
    Extracts API Key from either:
    1. 'X-API-Key' custom header, or
    2. 'Authorization: Bearer bk_live_...' header
    """
    raw_key: Optional[str] = None

    if x_api_key:
        raw_key = x_api_key
    elif authorization and authorization.startswith("Bearer "):
        raw_key = authorization.split(" ")[1]

    if not raw_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="API Key required. Provide 'X-API-Key' header.",
            headers={"WWW-Authenticate": "ApiKey"}
        )

    return await verify_api_key_and_get_user(db, raw_key)