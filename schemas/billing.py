from pydantic import BaseModel

class CreateCheckoutRequest(BaseModel):
    price_id: str

class SubscriptionResponse(BaseModel):
    id: str
    status: str
    plan: str

    class Config:
        from_attributes = True


class CreateUsageRequest(BaseModel):
    feature: str
    quantity: int = 1
    subscription_id: str | None = None
