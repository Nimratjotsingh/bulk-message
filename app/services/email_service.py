# app/services/email_service.py
import aiosmtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.smtp import SmtpConfig
from app.models.users import User
from app.schemas.email import DirectEmailSendRequest
from app.services import smtp_service
from app.utils.smtp_security import decrypt_smtp_password


async def send_direct_email(
    db: AsyncSession, 
    request_data: DirectEmailSendRequest, 
    current_user: User
) -> dict:
    # 1. Fetch user's SMTP config (validates ownership & existence)
    config: SmtpConfig = await smtp_service.get_smtp_config_by_id(
        db, request_data.config_id, current_user.id
    )

    # 2. Decrypt password
    plain_password = decrypt_smtp_password(config.password)

    # 3. Construct MIMEMultipart message supporting HTML
    message = MIMEMultipart("alternative")
    message["From"] = f"{config.sender_name} <{config.sender_email}>" if config.sender_name else config.sender_email
    message["To"] = request_data.recipient_email
    message["Subject"] = request_data.subject

    # Attach HTML content (will also render as plain text in legacy clients)
    html_part = MIMEText(request_data.body, "html", "utf-8")
    message.attach(html_part)

    # 4. Dispatch email asynchronously via aiosmtplib
    try:
        await aiosmtplib.send(
            message,
            hostname=config.host,
            port=config.port,
            username=config.username,
            password=plain_password,
            use_tls=config.use_ssl,         # True for SSL (Port 465)
            start_tls=config.use_tls,       # True for TLS (Port 587)
            timeout=15
        )
        return {
            "status": "success",
            "message": f"Email successfully sent to {request_data.recipient_email}"
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to send email via SMTP server: {str(e)}"
        )