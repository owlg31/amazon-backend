from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.dependencies import get_current_user
from app.core.security import create_access_token, create_refresh_token, decode_token, hash_password, verify_password
from app.db.postgres import get_db
from app.models import User
from app.schemas.auth import ChangePasswordSchema, ForgotPasswordRequest, LoginRequest, RefreshTokenRequest, TokenResponse, UserCreate, UserResponse

router = APIRouter(prefix="/api/v1/auth", tags=["Authentication"])


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(user_data: UserCreate, db: AsyncSession = Depends(get_db)):
    existing = (await db.execute(select(User).where(User.email == user_data.email))).scalar_one_or_none()
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")
    user = User(
        name=user_data.name,
        email=user_data.email,
        password_hash=hash_password(user_data.password),
        phone=user_data.phone,
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return UserResponse.from_model(user)


@router.post("/login", response_model=TokenResponse)
async def login(login_data: LoginRequest, db: AsyncSession = Depends(get_db)):
    user = (await db.execute(select(User).where(User.email == login_data.email))).scalar_one_or_none()
    if not user or not verify_password(login_data.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid email or password", headers={"WWW-Authenticate": "Bearer"})
    if not user.is_active:
        raise HTTPException(status_code=403, detail="User account is inactive")
    data = {"sub": str(user.id), "email": user.email}
    return {"access_token": create_access_token(data), "refresh_token": create_refresh_token(data), "token_type": "bearer"}


@router.post("/login/form", response_model=TokenResponse)
async def login_form(username: str, password: str, db: AsyncSession = Depends(get_db)):
    user = (await db.execute(select(User).where(User.email == username))).scalar_one_or_none()
    if not user or not verify_password(password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid username or password")
    data = {"sub": str(user.id), "email": user.email}
    return {"access_token": create_access_token(data), "refresh_token": create_refresh_token(data), "token_type": "bearer"}


@router.post("/refresh", response_model=TokenResponse)
async def refresh(body: RefreshTokenRequest, db: AsyncSession = Depends(get_db)):
    payload = decode_token(body.refresh_token, "refresh")
    user_id = payload.get("sub")
    user = (await db.execute(select(User).where(User.id == int(user_id)))).scalar_one_or_none()
    if not user or not user.is_active:
        raise HTTPException(status_code=401, detail="Invalid refresh token")
    data = {"sub": str(user.id), "email": user.email}
    return {"access_token": create_access_token(data), "refresh_token": create_refresh_token(data), "token_type": "bearer"}


@router.post("/forgot-password")
async def forgot_password(body: ForgotPasswordRequest):
    return {"message": "If the account exists, a password reset message has been generated."}


@router.get("/me", response_model=UserResponse)
async def me(user: User = Depends(get_current_user)):
    return UserResponse.from_model(user)


@router.post("/change-password")
async def change_password(body: ChangePasswordSchema, user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    if not verify_password(body.current_password, user.password_hash):
        raise HTTPException(status_code=400, detail="Current password is incorrect")
    user.password_hash = hash_password(body.new_password)
    await db.commit()
    return {"message": "Password changed successfully"}
