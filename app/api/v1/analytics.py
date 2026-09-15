from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import APIRouter, Depends

from app.db.postgres import get_db
from app.models import Order, Product, User
from app.schemas.common import AnalyticsDashboardResponse

router = APIRouter(prefix="/api/v1/analytics", tags=["Analytics"])


@router.get("/dashboard", response_model=AnalyticsDashboardResponse)
async def dashboard(db: AsyncSession = Depends(get_db)):
    users = await db.scalar(select(func.count(User.id))) or 0
    products = await db.scalar(select(func.count(Product.id))) or 0
    orders = await db.scalar(select(func.count(Order.id))) or 0
    revenue = await db.scalar(select(func.coalesce(func.sum(Order.total_amount), 0)).where(Order.status != "cancelled")) or 0
    return AnalyticsDashboardResponse(users=users, products=products, orders=orders, revenue=float(revenue))
