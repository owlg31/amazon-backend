from decimal import Decimal
from pydantic import BaseModel, Field


class PaymentCreate(BaseModel):
    order_id: int
    method: str = Field(min_length=2, max_length=50)


class PaymentResponse(BaseModel):
    id: int
    order_id: int
    amount: Decimal
    method: str
    status: str
    provider_reference: str | None
