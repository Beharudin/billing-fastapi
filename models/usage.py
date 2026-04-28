from sqlalchemy import Column, String, Integer, DateTime
from core.database import Base
from datetime import datetime
import uuid

class UsageEvent(Base):
    __tablename__ = "usage_events"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    tenant_id = Column(String, index=True)
    event_type = Column(String)
    quantity = Column(Integer, default=1)
    created_at = Column(DateTime, default=datetime.utcnow)