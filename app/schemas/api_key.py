# app/schemas/api_key.py
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class ApiKeyCreate(BaseModel):
    name: str = Field(..., example="Production Server", description="A friendly name to identify the key")
    expires_in_days: Optional[int] = Field(
        None, example=30, description="Optional lifetime in days. If null, the key does not expire."
    )


class ApiKeyCreateResponse(BaseModel):
    id: int
    name: str
    key_prefix: str
    api_key: str = Field(
        ..., 
        description="Full raw API key. Save this now—it will NOT be shown again!"
    )
    is_active: bool
    created_at: datetime
    expires_at: Optional[datetime]

    class Config:
        from_attributes = True


class ApiKeyResponse(BaseModel):
    id: int
    name: str
    key_prefix: str
    is_active: bool
    created_at: datetime
    expires_at: Optional[datetime]
    last_used_at: Optional[datetime]

    class Config:
        from_attributes = True