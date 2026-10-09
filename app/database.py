from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base

DATABASE_URL="postgresql://neondb_owner:npg_UmCYkKLVd9f4@ep-odd-meadow-b5wajn3j-pooler.c-7.us-east-2.aws.neon.tech/neondb?sslmode=require&channel_binding=require"
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