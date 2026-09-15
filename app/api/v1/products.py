from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.postgres import get_db
from app.models import Product
from app.schemas.catalog import ProductCreate, ProductResponse, ProductUpdate

router = APIRouter(prefix="/api/v1/products", tags=["Products"])


@router.post("", response_model=ProductResponse, status_code=201)
async def create_product(body: ProductCreate, db: AsyncSession = Depends(get_db)):
    obj = Product(**body.model_dump())
    db.add(obj)
    await db.commit()
    await db.refresh(obj)
    return obj


@router.get("", response_model=list[ProductResponse])
async def list_products(skip: int = 0, limit: int = 50, db: AsyncSession = Depends(get_db)):
    limit = min(limit, 100)
    return (await db.execute(select(Product).offset(skip).limit(limit).order_by(Product.id.desc()))).scalars().all()


@router.get("/search/query", response_model=list[ProductResponse])
async def search_products(q: str, db: AsyncSession = Depends(get_db)):
    pattern = f"%{q}%"
    stmt = select(Product).where(or_(Product.name.ilike(pattern), Product.description.ilike(pattern)))
    return (await db.execute(stmt.limit(50))).scalars().all()


@router.get("/{product_id}", response_model=ProductResponse)
async def get_product(product_id: int, db: AsyncSession = Depends(get_db)):
    obj = await db.get(Product, product_id)
    if not obj:
        raise HTTPException(status_code=404, detail="Product not found")
    return obj


@router.put("/{product_id}", response_model=ProductResponse)
async def update_product(product_id: int, body: ProductUpdate, db: AsyncSession = Depends(get_db)):
    obj = await db.get(Product, product_id)
    if not obj:
        raise HTTPException(status_code=404, detail="Product not found")
    for key, value in body.model_dump(exclude_unset=True).items():
        setattr(obj, key, value)
    await db.commit()
    await db.refresh(obj)
    return obj


@router.delete("/{product_id}")
async def delete_product(product_id: int, db: AsyncSession = Depends(get_db)):
    obj = await db.get(Product, product_id)
    if not obj:
        raise HTTPException(status_code=404, detail="Product not found")
    await db.delete(obj)
    await db.commit()
    return {"message": "Product deleted"}
