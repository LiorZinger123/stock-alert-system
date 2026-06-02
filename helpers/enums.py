from enum import Enum


class ConditionEnum(str, Enum):
    ABOVE = "above"
    BELOW = "below"


class AlertStatus(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    PENDING = "pending"
    SENT = "sent"
    FAILED = "failed"
