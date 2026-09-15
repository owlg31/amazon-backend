from uuid import uuid4
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.dependencies import get_current_user
from app.db.postgres import get_db
from app.models import Order, Payment, User
from app.schemas.payment import PaymentCreate, PaymentResponse

router = APIRouter(prefix="/api/v1/payments", tags=["Payments"])


@router.post("", response_model=PaymentResponse, status_code=201)
async def create_payment(body: PaymentCreate, user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    order = (await db.execute(select(Order).where(Order.id == body.order_id, Order.user_id == user.id))).scalar_one_or_none()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    if (await db.execute(select(Payment).where(Payment.order_id == order.id))).scalar_one_or_none():
        raise HTTPException(status_code=409, detail="Payment already exists")
    payment = Payment(order_id=order.id, amount=order.total_amount, method=body.method, status="paid", provider_reference=f"DEMO-{uuid4().hex[:12].upper()}")
    order.status = "confirmed"
    db.add(payment)
    await db.commit()
    await db.refresh(payment)
    return payment


@router.get("/{payment_id}", response_model=PaymentResponse)
async def get_payment(payment_id: int, user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    payment = (await db.execute(select(Payment).join(Order, Order.id == Payment.order_id).where(Payment.id == payment_id, Order.user_id == user.id))).scalar_one_or_none()
    if not payment:
        raise HTTPException(status_code=404, detail="Payment not found")
    return payment
