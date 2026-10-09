# app/services/api_key_service.py
from datetime import datetime, timedelta, timezone
from typing import List, Optional
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.models.api_key import ApiKey
from app.models.users import User
from app.schemas.api_key import ApiKeyCreate, ApiKeyCreateResponse
from app.utils.api_key_security import generate_raw_api_key, hash_api_key, extract_key_prefix


async def create_api_key(
    db: AsyncSession, key_data: ApiKeyCreate, current_user: User
) -> ApiKeyCreateResponse:
    try:
        raw_key = generate_raw_api_key()
        hashed_key = hash_api_key(raw_key)
        prefix = extract_key_prefix(raw_key)

        expires_at: Optional[datetime] = None
        if key_data.expires_in_days:
            expires_at = datetime.now(timezone.utc) + timedelta(days=key_data.expires_in_days)

        db_key = ApiKey(
            user_id=current_user.id,
            name=key_data.name,
            key_prefix=prefix,
            hashed_key=hashed_key,
            is_active=True,
            expires_at=expires_at
        )

        db.add(db_key)
        await db.commit()
        await db.refresh(db_key)

        # Return full raw_key ONLY ONCE in the response
        return ApiKeyCreateResponse(
            id=db_key.id,
            name=db_key.name,
            key_prefix=db_key.key_prefix,
            api_key=raw_key,
            is_active=db_key.is_active,
            created_at=db_key.created_at,
            expires_at=db_key.expires_at
        )
    except:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create API Key"
        )



async def get_user_api_keys(db: AsyncSession, user_id: int) -> List[ApiKey]:
    result = await db.execute(
        select(ApiKey).where(ApiKey.user_id == user_id).order_by(ApiKey.created_at.desc())
    )
    
    return result.scalars().all()


async def revoke_api_key(db: AsyncSession, key_id: int, user_id: int) -> dict:
    result = await db.execute(
        select(ApiKey).where(ApiKey.id == key_id, ApiKey.user_id == user_id)
    )
    key = result.scalars().first()

    if not key:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="API Key not found"
        )

    key.is_active = False
    await db.commit()
    return {"status": "success", "message": f"API Key '{key.name}' has been revoked."}


async def verify_api_key_and_get_user(db: AsyncSession, raw_key: str) -> User:
    """Hashes the incoming raw key, verifies activity/expiration, and updates last_used_at."""
    hashed_input = hash_api_key(raw_key)

    result = await db.execute(
        select(ApiKey).where(ApiKey.hashed_key == hashed_input)
    )
    api_key_record = result.scalars().first()

    if not api_key_record or not api_key_record.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or revoked API Key",
            headers={"WWW-Authenticate": "ApiKey"}
        )

    # Check expiration
    if api_key_record.expires_at:
        now = datetime.now(timezone.utc)
        # Ensure comparison is offset-aware
        exp_time = api_key_record.expires_at
        if exp_time.tzinfo is None:
            exp_time = exp_time.replace(tzinfo=timezone.utc)
        
        if now > exp_time:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="API Key has expired",
                headers={"WWW-Authenticate": "ApiKey"}
            )

    # Update last_used_at timestamp
    api_key_record.last_used_at = datetime.now(timezone.utc)
    await db.commit()

    # Fetch and return key owner
    user_result = await db.execute(
        select(User).where(User.id == api_key_record.user_id)
    )
    user = user_result.scalars().first()

    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User account associated with this API key is inactive or disabled"
        )

    return user