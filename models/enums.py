from enum import Enum

class RoleEnum(str, Enum):
    ADMIN = "admin"
    MEMBER = "member"

class SubscriptionStatus(str, Enum):
    ACTIVE = "active"
    CANCELED = "canceled"
    PAST_DUE = "past_due"