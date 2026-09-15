async def redis_status() -> str:
    try:
        import redis.asyncio as redis
        from app.core.config import settings
        client = redis.from_url(settings.redis_url)
        await client.ping()
        await client.close()
        return "connected"
    except Exception:
        return "unavailable"


async def mongodb_status() -> str:
    try:
        from pymongo import AsyncMongoClient
        from app.core.config import settings
        client = AsyncMongoClient(settings.mongodb_url, serverSelectionTimeoutMS=500)
        await client.admin.command("ping")
        await client.close()
        return "connected"
    except Exception:
        return "unavailable"


async def search_status() -> str:
    try:
        import chromadb  # noqa: F401
        return "chroma-ready"
    except Exception:
        return "sql-fallback"
