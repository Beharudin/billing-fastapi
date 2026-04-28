from sqlalchemy import Column, String, Integer, DateTime
from core.database import Base
from datetime import datetime
import uuid


class Plan(Base):
    __tablename__ = "plans"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String, unique=True, index=True)
    price_cents = Column(Integer)
    interval = Column(String, default="month")
    created_at = Column(DateTime, default=datetime.utcnow)
    stripe_price_id = Column(String, unique=True, nullable=False)
