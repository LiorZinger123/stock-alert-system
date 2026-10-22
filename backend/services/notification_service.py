from typing import Optional
from db.models import Alert
from api.schemas.alerts import AlertStatus
from .rabbitmq_publisher import RabbitMQPublisher
from helpers.enums import QueueNotificationPayloadTypes
from helpers.constants import (
    EMAIL_NOTIFICATION_QUEUE_NAME, 
    ALERT_STATUS_NOTIFICATION_QUEUE_NAME, 
    PRICE_CHANGE_QUEUE_NAME
)


class NotificationService:
    def __init__(self, publisher: RabbitMQPublisher):
        self.publisher = publisher
        self.email_queue_name = EMAIL_NOTIFICATION_QUEUE_NAME
        self.alert_status_queue_name = ALERT_STATUS_NOTIFICATION_QUEUE_NAME
        self.price_change_queue_name = PRICE_CHANGE_QUEUE_NAME

    async def send_email_notification(self, alert: Alert, current_price: float) -> None:
        email_payload = {
            "user_id": alert.user_id,
            "alert_id": alert.id,
            "user_email": alert.owner.email,
            "symbol": alert.asset.symbol,
            "target_price": str(alert.target_price),
            "current_price": str(current_price),
            "condition": str(alert.condition.value) if hasattr(alert.condition, 'value') else str(alert.condition)
        }
        await self.publisher.publish(self.email_queue_name, email_payload)

    async def send_alert_status_notification(
        self, 
        user_id: int, 
        alert_id: int, 
        status: AlertStatus, 
        price: Optional[float] = None
    ) -> None:
        alert_status_payload = {
            "type": QueueNotificationPayloadTypes.ALERT_STATUS.value,
            "data": {
                "user_id": user_id,
                "alert_id": alert_id,
                "status": status.value,
                "triggered_price": price
            }
        }
        await self.publisher.publish(self.alert_status_queue_name, alert_status_payload)

    async def send_price_change_notification(self, user_id: int, payload: dict) -> None:
        price_change_payload = {
            "type": QueueNotificationPayloadTypes.PRICE_CHANGE.value,
            "data": {
                "user_id": user_id,
                **payload
            }
        }
        await self.publisher.publish(self.price_change_queue_name, price_change_payload)

    async def close(self):
        await self.publisher.close()
