from pydantic import BaseModel, EmailStr, Field

from app.schemas.common import RefreshTokenRequest, TokenResponse


class UserCreate(BaseModel):
    name: str = Field(min_length=2, max_length=100)
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)
    phone: str = Field(min_length=7, max_length=20)


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class UserResponse(BaseModel):
    id: int
    name: str
    email: EmailStr
    phone: str
    is_active: bool
    created_at: str | None = None

    @classmethod
    def from_model(cls, user):
        return cls(
            id=user.id,
            name=user.name,
            email=user.email,
            phone=user.phone,
            is_active=user.is_active,
            created_at=user.created_at.isoformat() if user.created_at else None,
        )


class ForgotPasswordRequest(BaseModel):
    email: EmailStr


class ChangePasswordSchema(BaseModel):
    current_password: str
    new_password: str = Field(min_length=8, max_length=128)


__all__ = ["UserCreate", "LoginRequest", "UserResponse", "ForgotPasswordRequest", "ChangePasswordSchema", "TokenResponse", "RefreshTokenRequest"]
