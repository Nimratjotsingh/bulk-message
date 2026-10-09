# app/services/smtp_service.py
import smtplib
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import update
from fastapi import HTTPException, status

from app.models.smtp import SmtpConfig
from app.models.users import User
from app.schemas.smtp import SmtpConfigCreate, SmtpConfigUpdate
from app.utils.smtp_security import encrypt_smtp_password, decrypt_smtp_password


async def create_smtp_config(
    db: AsyncSession, smtp_data: SmtpConfigCreate, current_user: User
) -> SmtpConfig:
    # If set as default, unset existing defaults asynchronously
    if smtp_data.is_default:
        await _unset_other_defaults(db, current_user.id)

    encrypted_pwd = encrypt_smtp_password(smtp_data.password)

    new_config = SmtpConfig(
        **smtp_data.model_dump(exclude={"password"}),
        password=encrypted_pwd,
        user_id=current_user.id
    )
    db.add(new_config)
    await db.commit()
    await db.refresh(new_config)
    return new_config


async def get_user_smtp_configs(db: AsyncSession, user_id: int) -> List[SmtpConfig]:
    # ✅ Fixed: Use select() instead of db.query()
    result = await db.execute(select(SmtpConfig).where(SmtpConfig.user_id == user_id))
    return result.scalars().all()


async def get_smtp_config_by_id(db: AsyncSession, config_id: int, user_id: int) -> SmtpConfig:
    # ✅ Fixed: Use select() instead of db.query()
    result = await db.execute(
        select(SmtpConfig).where(
            SmtpConfig.id == config_id, 
            SmtpConfig.user_id == user_id
        )
    )
    config = result.scalars().first()

    if not config:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="SMTP Configuration not found"
        )
    return config


async def update_smtp_config(
    db: AsyncSession, config_id: int, smtp_data: SmtpConfigUpdate, current_user: User
) -> SmtpConfig:
    config = await get_smtp_config_by_id(db, config_id, current_user.id)
    update_data = smtp_data.model_dump(exclude_unset=True)

    if update_data.get("is_default"):
        await _unset_other_defaults(db, current_user.id)

    if "password" in update_data and update_data["password"]:
        update_data["password"] = encrypt_smtp_password(update_data["password"])

    for key, value in update_data.items():
        setattr(config, key, value)

    await db.commit()
    await db.refresh(config)
    return config


async def delete_smtp_config(db: AsyncSession, config_id: int, user_id: int):
    config = await get_smtp_config_by_id(db, config_id, user_id)
    await db.delete(config)
    await db.commit()
    return {"message": "SMTP configuration deleted successfully"}


async def test_smtp_connection(config: SmtpConfig) -> bool:
    """Attempts an authentication handshake with the target SMTP server."""
    plain_password = decrypt_smtp_password(config.password)
    try:
        if config.use_ssl:
            server = smtplib.SMTP_SSL(config.host, config.port, timeout=10)
        else:
            server = smtplib.SMTP(config.host, config.port, timeout=10)
            if config.use_tls:
                server.starttls()

        server.login(config.username, plain_password)
        server.quit()
        return True
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"SMTP Connection Test Failed: {str(e)}"
        )


async def _unset_other_defaults(db: AsyncSession, user_id: int):
    # ✅ Fixed: Use update() statement for async session
    stmt = (
        update(SmtpConfig)
        .where(SmtpConfig.user_id == user_id, SmtpConfig.is_default == True)
        .values(is_default=False)
    )
    await db.execute(stmt)