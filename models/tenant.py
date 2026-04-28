from sqlalchemy import Column, String
from core.database import Base
import uuid

class Tenant(Base):
    __tablename__ = "tenants"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String, index=True)
    stripe_customer_id = Column(String, nullable=True)