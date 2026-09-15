from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.postgres import get_db
from app.models import Category
from app.schemas.catalog import CategoryCreate, CategoryResponse

router = APIRouter(prefix="/api/v1/categories", tags=["Categories"])


@router.post("", response_model=CategoryResponse, status_code=201)
async def create_category(body: CategoryCreate, db: AsyncSession = Depends(get_db)):
    if (await db.execute(select(Category).where(Category.name == body.name))).scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Category already exists")
    obj = Category(**body.model_dump())
    db.add(obj)
    await db.commit()
    await db.refresh(obj)
    return obj


@router.get("", response_model=list[CategoryResponse])
async def list_categories(db: AsyncSession = Depends(get_db)):
    return (await db.execute(select(Category).order_by(Category.id.desc()))).scalars().all()


@router.get("/{category_id}", response_model=CategoryResponse)
async def get_category(category_id: int, db: AsyncSession = Depends(get_db)):
    obj = await db.get(Category, category_id)
    if not obj:
        raise HTTPException(status_code=404, detail="Category not found")
    return obj


@router.put("/{category_id}", response_model=CategoryResponse)
async def update_category(category_id: int, body: CategoryCreate, db: AsyncSession = Depends(get_db)):
    obj = await db.get(Category, category_id)
    if not obj:
        raise HTTPException(status_code=404, detail="Category not found")
    obj.name = body.name
    obj.description = body.description
    await db.commit()
    await db.refresh(obj)
    return obj


@router.delete("/{category_id}")
async def delete_category(category_id: int, db: AsyncSession = Depends(get_db)):
    obj = await db.get(Category, category_id)
    if not obj:
        raise HTTPException(status_code=404, detail="Category not found")
    await db.delete(obj)
    await db.commit()
    return {"message": "Category deleted"}
