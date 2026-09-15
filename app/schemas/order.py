from decimal import Decimal
from pydantic import BaseModel


class OrderCreate(BaseModel):
    address_id: int


class OrderItemResponse(BaseModel):
    product_id: int
    product_name: str
    quantity: int
    unit_price: Decimal


class OrderResponse(BaseModel):
    id: int
    total_amount: Decimal
    status: str
    address_id: int
    items: list[OrderItemResponse]
