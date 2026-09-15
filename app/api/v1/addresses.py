from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.dependencies import get_current_user
from app.db.postgres import get_db
from app.models import Address, User
from app.schemas.address import AddressCreate, AddressResponse

router = APIRouter(prefix="/api/v1/addresses", tags=["Addresses"])


@router.post("", response_model=AddressResponse, status_code=201)
async def create_address(body: AddressCreate, user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    if body.is_default:
        await db.execute(update(Address).where(Address.user_id == user.id).values(is_default=False))
    obj = Address(user_id=user.id, **body.model_dump())
    db.add(obj)
    await db.commit()
    await db.refresh(obj)
    return obj


@router.get("", response_model=list[AddressResponse])
async def list_addresses(user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    return (await db.execute(select(Address).where(Address.user_id == user.id))).scalars().all()


@router.get("/{address_id}", response_model=AddressResponse)
async def get_address(address_id: int, user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    obj = (await db.execute(select(Address).where(Address.id == address_id, Address.user_id == user.id))).scalar_one_or_none()
    if not obj:
        raise HTTPException(status_code=404, detail="Address not found")
    return obj


@router.delete("/{address_id}")
async def delete_address(address_id: int, user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    obj = (await db.execute(select(Address).where(Address.id == address_id, Address.user_id == user.id))).scalar_one_or_none()
    if not obj:
        raise HTTPException(status_code=404, detail="Address not found")
    await db.delete(obj)
    await db.commit()
    return {"message": "Address deleted"}
