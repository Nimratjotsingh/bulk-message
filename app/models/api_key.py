# app/models/api_key.py
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import base


class ApiKey(base):
    __tablename__ = "api_keys"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    
    name = Column(String, nullable=False)  # Descriptive label e.g. "Production Server", "Zapier Integration"
    key_prefix = Column(String(12), nullable=False)  # First few chars e.g. "bk_live_1234" for user UI identification
    hashed_key = Column(String, nullable=False, unique=True, index=True)
    
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    expires_at = Column(DateTime(timezone=True), nullable=True)
    last_used_at = Column(DateTime(timezone=True), nullable=True)

    # Relationship back to User
    owner = relationship("User", back_populates="api_keys")