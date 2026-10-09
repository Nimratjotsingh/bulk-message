from sqlalchemy import Column,Integer,String,Boolean,DateTime;
from app.database import base

from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.models.smtp import SmtpConfig



class User(base):
    __tablename__='users'
    id=Column(Integer,primary_key=True,index=True)
    name=Column(String,nullable=False)
    email=Column(String(100),unique=True,index=True,nullable=False)
    phone=Column(String,unique=True,nullable=False)
    hashed_password=Column(String,nullable=False)
    is_active = Column(Boolean, default=True)
    created_at=(Column(DateTime(timezone=True),server_default=func.now()))
    smtp_configs = relationship("SmtpConfig", back_populates="owner", cascade="all, delete-orphan")
    api_keys = relationship("ApiKey", back_populates="owner", cascade="all, delete-orphan")  # 👈 Added relationship
()