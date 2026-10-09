from contextlib import asynccontextmanager
import app.models
from fastapi import FastAPI, Depends
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db, base, engine
from app.routes import auth,smtp,email,apiKey,email2


@asynccontextmanager
async def lifespan(app: FastAPI):

    print("🚀 Starting application...")

    # Create tables
    async with engine.begin() as conn:
        await conn.run_sync(base.metadata.create_all)

    print("✅ Database tables initialized")


    try:
        async with engine.connect() as conn:
            await conn.execute(text("SELECT 1"))

        print("✅ Database connected successfully")

    except Exception as e:
        print(f"❌ Database connection failed: {e}")

    yield

    # Close database connection
    await engine.dispose()

    print("🛑 Database connection closed")


app = FastAPI(
    title="BulkMessage",
    version="1.0.0",
    lifespan=lifespan,
)


app.include_router(auth.router)
app.include_router(smtp.router)
app.include_router(email.router)
app.include_router(apiKey.router)
app.include_router(email2.router)
@app.get("/")
async def get_health(
    db: AsyncSession = Depends(get_db)
):
    try:
        await db.execute(text("SELECT 1"))

        return {
            "status": "success",
            "message": "Database connected successfully!"
        }

    except Exception as e:
        return {
            "status": "error",
            "message": f"Database connection failed: {str(e)}"
        }