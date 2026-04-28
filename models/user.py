from sqlalchemy import Column, String, Boolean
from core.database import Base
import uuid
from models.enums import RoleEnum

class User(Base):
    __tablename__ = "users"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    email = Column(String, unique=True, index=True)
    password = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    stripe_customer_id = Column(String, nullable=True)
    tenant_id = Column(String, index=True)
    role = Column(String, default=RoleEnum.MEMBER.value)