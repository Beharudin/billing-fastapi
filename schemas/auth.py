from pydantic import BaseModel, Field, field_validator, EmailStr
from typing import Generic, TypeVar
from uuid import UUID
from models.enums import RoleEnum

T = TypeVar("T")


class BaseResponse(BaseModel, Generic[T]):
    message: str
    status: str
    data: T


class RegisterRequest(BaseModel):
    email: EmailStr = Field(...)
    password: str = Field(..., min_length=6)
    is_active: bool = True


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UserResponse(BaseModel):
    id: UUID
    email: str
    role: RoleEnum
    is_active: bool

    class Config:
        from_attributes = True


class RegisterResponse(BaseResponse[UserResponse]):
    pass


class LoginResponse(BaseResponse[TokenResponse]):
    pass


class AdminRegisterRequest(BaseModel):
    email: EmailStr
    password: str
    role: RoleEnum = RoleEnum.MEMBER
    is_active: bool = True