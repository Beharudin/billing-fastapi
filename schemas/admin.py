from pydantic import BaseModel, EmailStr
from typing import Generic, TypeVar

T = TypeVar("T")


class BaseResponse(BaseModel, Generic[T]):
    message: str
    status: str
    data: T


class RevenueResponse(BaseModel):
    total_revenue: float


class PlanCreate(BaseModel):
    name: str
    # price provided by admin in dollars (e.g. 10.0 for $10.00)
    price: float
    interval: str = "month"


class PlanResponse(BaseModel):
    id: str
    name: str
    price_cents: int
    interval: str
    stripe_price_id: str  # Added stripe_price_id field

    class Config:
        from_attributes = True

class PlanFullResponse(BaseResponse[PlanResponse]):
    pass

class PlanListResponse(BaseResponse[list[PlanResponse]]):
    pass

class UserRoleUpdate(BaseModel):
    role: str


class UserResponse(BaseModel):
    id: str
    email: EmailStr
    tenant_id: str | None
    role: str

    class Config:
        from_attributes = True