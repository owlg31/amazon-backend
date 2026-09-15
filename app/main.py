from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.core.config import settings
from app.api.v1 import analytics, addresses, auth, cart, categories, orders, payments, products, search, users
@asynccontextmanager
async def lifespan(app: FastAPI):
    yield


app = FastAPI(
    title=settings.app_name,
    description=(
        "Enterprise Production-Ready Amazon-style E-Commerce Backend System API "
        "built with FastAPI, SQLAlchemy 2.0 Async, PostgreSQL, Redis, MongoDB, and ChromaDB."
    ),
    version=settings.app_version,
    lifespan=lifespan,
)

for router in [
    auth.router,
    users.router,
    categories.router,
    products.router,
    addresses.router,
    cart.router,
    orders.router,
    payments.router,
    search.router,
    analytics.router,
]:
    app.include_router(router)


@app.get("/", tags=["Default"])
async def root():
    return {"message": "Amazon Backend System is running"}
