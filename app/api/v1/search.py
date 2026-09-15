from fastapi import APIRouter, Depends
from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.postgres import get_db
from app.models import Product
from app.schemas.common import SearchResult

router = APIRouter(prefix="/api/v1/search", tags=["Search"])


@router.get("", response_model=list[SearchResult])
async def search(q: str, db: AsyncSession = Depends(get_db)):
    pattern = f"%{q}%"
    products = (await db.execute(select(Product).where(or_(Product.name.ilike(pattern), Product.description.ilike(pattern))).limit(50))).scalars().all()
    return [SearchResult(id=p.id, name=p.name, description=p.description, price=float(p.price), stock=p.stock) for p in products]
