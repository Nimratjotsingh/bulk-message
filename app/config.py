import os

SECRET_KEY = os.getenv("SECRET_KEY", "your-super-secret-key-change-this-in-production")
ALGORITHM = "HS256"
SMTP_SECRET_KEY=os.getenv("SMTP_SECRET_KEY")
ACCESS_TOKEN_EXPIRE_MINUTES = 30