from decimal import Decimal
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.dependencies import get_current_user
from app.db.postgres import get_db
from app.models import CartItem, Product, User
from app.schemas.cart import CartItemAdd, CartItemResponse, CartItemUpdate, CartResponse

router = APIRouter(prefix="/api/v1/cart", tags=["Cart"])


async def _cart(user_id: int, db: AsyncSession):
    rows = (await db.execute(select(CartItem).where(CartItem.user_id == user_id).options(selectinload(CartItem.product)).order_by(CartItem.id))).scalars().all()
    items = []
    total = Decimal("0")
    for item in rows:
        subtotal = item.product.price * item.quantity
        total += subtotal
        items.append(CartItemResponse(product_id=item.product_id, product_name=item.product.name, quantity=item.quantity, unit_price=item.product.price, subtotal=subtotal))
    return CartResponse(items=items, total=total)


@router.get("", response_model=CartResponse)
async def get_cart(user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    return await _cart(user.id, db)


@router.post("/items", response_model=CartResponse)
async def add_to_cart(body: CartItemAdd, user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    product = await db.get(Product, body.product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    if product.stock < body.quantity:
        raise HTTPException(status_code=409, detail="Insufficient stock")
    item = (await db.execute(select(CartItem).where(CartItem.user_id == user.id, CartItem.product_id == body.product_id))).scalar_one_or_none()
    if item:
        item.quantity += body.quantity
    else:
        db.add(CartItem(user_id=user.id, product_id=body.product_id, quantity=body.quantity))
    await db.commit()
    return await _cart(user.id, db)


@router.patch("/items/{product_id}", response_model=CartResponse)
async def update_cart(product_id: int, body: CartItemUpdate, user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    item = (await db.execute(select(CartItem).where(CartItem.user_id == user.id, CartItem.product_id == product_id))).scalar_one_or_none()
    if not item:
        raise HTTPException(status_code=404, detail="Cart item not found")
    item.quantity = body.quantity
    await db.commit()
    return await _cart(user.id, db)


@router.delete("/items/{product_id}")
async def remove_from_cart(product_id: int, user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    item = (await db.execute(select(CartItem).where(CartItem.user_id == user.id, CartItem.product_id == product_id))).scalar_one_or_none()
    if not item:
        raise HTTPException(status_code=404, detail="Cart item not found")
    await db.delete(item)
    await db.commit()
    return {"message": "Item removed from cart"}
