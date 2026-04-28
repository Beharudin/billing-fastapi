from sqlalchemy import Column, String, Boolean, DateTime, Text
from core.database import Base
from datetime import datetime
import uuid


class WebhookEvent(Base):
    __tablename__ = "webhook_events"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    stripe_event_id = Column(String, unique=True, index=True)
    event_type = Column(String)
    payload = Column(Text)
    processed = Column(Boolean, default=False)
    processed_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
