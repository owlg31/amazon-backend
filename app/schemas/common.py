from pydantic import BaseModel, ConfigDict, Field
from typing import Any


class MessageResponse(BaseModel):
    message: str


class HealthResponse(BaseModel):
    status: str
    database: str
    redis: str
    mongodb: str
    search: str


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class RefreshTokenRequest(BaseModel):
    refresh_token: str


class AnalyticsDashboardResponse(BaseModel):
    users: int
    products: int
    orders: int
    revenue: float


class SearchResult(BaseModel):
    id: int
    name: str
    description: str | None = None
    price: float
    stock: int


class GenericResponse(BaseModel):
    model_config = ConfigDict(extra="allow")
    data: Any
