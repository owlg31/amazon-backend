from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.api.v1.dependencies import get_current_user
from app.db.postgres import get_db
from app.models import User
from app.schemas.auth import UserResponse

router = APIRouter(prefix="/api/v1/users", tags=["Users"])


@router.get("/me", response_model=UserResponse)
async def get_profile(user: User = Depends(get_current_user)):
    return UserResponse.from_model(user)


@router.put("/me", response_model=UserResponse)
async def update_profile(name: str, phone: str, user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    user.name = name
    user.phone = phone
    await db.commit()
    await db.refresh(user)
    return UserResponse.from_model(user)


@router.delete("/me")
async def deactivate_account(user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    user.is_active = False
    await db.commit()
    return {"message": "Account deactivated"}
