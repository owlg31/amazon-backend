from fastapi import APIRouter
from sqlalchemy import text

from app.core.config import settings
from app.db.postgres import AsyncSessionLocal
from app.schemas.common import HealthResponse
from app.services.providers import mongodb_status, redis_status, search_status

router = APIRouter(tags=["Health"])


@router.get("/health", response_model=HealthResponse)
async def health():
    database = "unavailable"
    try:
        async with AsyncSessionLocal() as db:
            await db.execute(text("SELECT 1"))
        database = "connected"
    except Exception:
        pass
    return HealthResponse(status="healthy", database=database, redis=await redis_status(), mongodb=await mongodb_status(), search=await search_status())
