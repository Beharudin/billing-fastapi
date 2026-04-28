from sqlalchemy import Column, String, ForeignKey, DateTime
from core.database import Base
from datetime import datetime
import uuid

class Subscription(Base):
    __tablename__ = "subscriptions"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id"))
    stripe_subscription_id = Column(String)
    status = Column(String)
    plan = Column(String)
    current_period_end = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)