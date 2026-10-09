from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base
import os 
DATABASE_URL= os.getenv('DATABASE_URL')
engine = create_async_engine(
    DATABASE_URL,
    echo=True,       # Set to False in production
    future=True
)

# Create Async Session Factory
AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False
)

base = declarative_base()

async def get_db():
    async with AsyncSessionLocal() as db:
        yield db