# app/schemas/email.py
from pydantic import BaseModel, EmailStr, Field

class DirectEmailSendRequest(BaseModel):
    config_id: int = Field(..., description="ID of the SmtpConfig to use for sending")
    recipient_email: EmailStr = Field(..., description="Target email address")
    subject: str = Field(..., example="Welcome to our platform!")
    body: str = Field(..., description="Email body content (supports HTML or plain text)")