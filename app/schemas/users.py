from pydantic import BaseModel, EmailStr

from datetime import datetime

# Shared properties
class UserBase(BaseModel):
    name: str
    email: EmailStr
    phone: str

# Properties required for User Creation (Signup Request)
class UserCreate(UserBase):
    password: str

# Properties for Login Request
class UserLogin(BaseModel):
    email: EmailStr
    password: str

# Properties returned in API Responses (Excludes password)
class UserResponse(UserBase):
    id: int
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True  # Allows Pydantic to read SQLAlchemy ORM objects