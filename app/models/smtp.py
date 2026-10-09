# app/models/smtp.py
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey  # <--- Make sure ForeignKey is imported
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import base

class SmtpConfig(base):
    __tablename__ = "smtp_configs"

    id = Column(Integer, primary_key=True, index=True)
    
    # FK linking smtp_configs.user_id -> users.id
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    
    name = Column(String, nullable=False)
    host = Column(String, nullable=False)
    port = Column(Integer, nullable=False, default=587)
    username = Column(String, nullable=False)
    password = Column(String, nullable=False)
    sender_email = Column(String, nullable=False)
    sender_name = Column(String, nullable=True)
    
    use_tls = Column(Boolean, default=True)
    use_ssl = Column(Boolean, default=False)
    is_default = Column(Boolean, default=False)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationship back to User model
    owner = relationship("User", back_populates="smtp_configs")