# app/schemas/smtp.py
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr, Field


class SmtpConfigBase(BaseModel):
    name: str = Field(..., json_schema_extra={"example": "Work Gmail"})
    host: str = Field(..., json_schema_extra={"example": "smtp.gmail.com"})
    port: int = Field(587, json_schema_extra={"example": 587})
    username: str = Field(..., json_schema_extra={"example": "user@gmail.com"})
    sender_email: EmailStr = Field(..., json_schema_extra={"example": "user@gmail.com"})
    sender_name: Optional[str] = Field(None, json_schema_extra={"example": "John Doe"})
    use_tls: bool = True
    use_ssl: bool = False
    is_default: bool = False


class SmtpConfigCreate(SmtpConfigBase):
    password: str = Field(..., json_schema_extra={"example": "app-specific-password"})


class SmtpConfigUpdate(BaseModel):
    name: Optional[str] = Field(None, json_schema_extra={"example": "Work Gmail"})
    host: Optional[str] = Field(None, json_schema_extra={"example": "smtp.gmail.com"})
    port: Optional[int] = Field(None, json_schema_extra={"example": 587})
    username: Optional[str] = Field(None, json_schema_extra={"example": "user@gmail.com"})
    sender_email: Optional[EmailStr] = Field(None, json_schema_extra={"example": "user@gmail.com"})
    sender_name: Optional[str] = Field(None, json_schema_extra={"example": "John Doe"})
    use_tls: Optional[bool] = None
    use_ssl: Optional[bool] = None
    is_default: Optional[bool] = None
    password: Optional[str] = Field(None, json_schema_extra={"example": "new-app-specific-password"})


class SmtpConfigResponse(SmtpConfigBase):
    id: int
    user_id: int
    created_at: datetime

    class Config:
        from_attributes = True