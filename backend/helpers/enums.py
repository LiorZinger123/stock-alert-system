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


class QueueNotificationPayloadTypes(str, Enum):
    ALERT_STATUS = "ALERT_STATUS_UPDATE"
    PRICE_CHANGE = "PRICE_CHANGE_UPDATE"


class UserProviders(str, Enum):
    GOOGLE = "google"
