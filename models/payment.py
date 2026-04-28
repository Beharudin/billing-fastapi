from sqlalchemy import Column, String, Float, DateTime, ForeignKey
from core.database import Base
from datetime import datetime
import uuid

class Payment(Base):
    __tablename__ = "payments"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id"))
    stripe_payment_intent = Column(String)
    amount = Column(Float)
    currency = Column(String, default="usd")
    status = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)