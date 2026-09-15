from decimal import Decimal
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.api.v1.dependencies import get_current_user
from app.db.postgres import get_db
from app.models import Address, CartItem, Order, OrderItem, Product, User
from app.schemas.order import OrderCreate, OrderItemResponse, OrderResponse

router = APIRouter(prefix="/api/v1/orders", tags=["Orders"])


@router.post("", response_model=OrderResponse, status_code=201)
async def create_order(body: OrderCreate, user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    address = (await db.execute(select(Address).where(Address.id == body.address_id, Address.user_id == user.id))).scalar_one_or_none()
    if not address:
        raise HTTPException(status_code=404, detail="Address not found")
    cart = (await db.execute(select(CartItem).where(CartItem.user_id == user.id).options(selectinload(CartItem.product)))).scalars().all()
    if not cart:
        raise HTTPException(status_code=400, detail="Cart is empty")
    total = Decimal("0")
    for item in cart:
        if item.product.stock < item.quantity:
            raise HTTPException(status_code=409, detail=f"Insufficient stock for {item.product.name}")
        total += item.product.price * item.quantity
    order = Order(user_id=user.id, address_id=body.address_id, total_amount=total, status="pending")
    db.add(order)
    await db.flush()
    for item in cart:
        item.product.stock -= item.quantity
        db.add(OrderItem(order_id=order.id, product_id=item.product.id, product_name=item.product.name, quantity=item.quantity, unit_price=item.product.price))
        await db.delete(item)
    await db.commit()
    await db.refresh(order)
    return await get_order(order.id, user, db)


@router.get("", response_model=list[OrderResponse])
async def list_orders(user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    orders = (await db.execute(select(Order).where(Order.user_id == user.id).options(selectinload(Order.items)).order_by(Order.id.desc()))).scalars().unique().all()
    return [_serialize(o) for o in orders]


def _serialize(order: Order) -> OrderResponse:
    return OrderResponse(id=order.id, total_amount=order.total_amount, status=order.status, address_id=order.address_id, items=[OrderItemResponse(product_id=i.product_id, product_name=i.product_name, quantity=i.quantity, unit_price=i.unit_price) for i in order.items])


@router.get("/{order_id}", response_model=OrderResponse)
async def get_order(order_id: int, user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    order = (await db.execute(select(Order).where(Order.id == order_id, Order.user_id == user.id).options(selectinload(Order.items)))).scalar_one_or_none()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    return _serialize(order)


@router.post("/{order_id}/cancel")
async def cancel_order(order_id: int, user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    order = (await db.execute(select(Order).where(Order.id == order_id, Order.user_id == user.id))).scalar_one_or_none()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    if order.status not in {"pending", "confirmed"}:
        raise HTTPException(status_code=409, detail="Order cannot be cancelled")
    order.status = "cancelled"
    await db.commit()
    return {"message": "Order cancelled"}
