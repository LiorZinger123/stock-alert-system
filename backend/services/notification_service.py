import json
import aio_pika
from typing import Optional
from db.models import Alert
from api.schemas.alerts import AlertStatus
from helpers.enums import QueueNotificationPayloadTypes
from helpers.constants import EMAIL_NOTIFICATION_QUEUE_NAME, ALERT_STATUS_NOTIFICATION_QUEUE_NAME, PRICE_CHANGE_QUEUE_NAME


class NotificationService:
    def __init__(self, amqp_url: str):
        self.amqp_url = amqp_url
        self.email_queue_name = EMAIL_NOTIFICATION_QUEUE_NAME
        self.alert_status_queue_name = ALERT_STATUS_NOTIFICATION_QUEUE_NAME
        self.price_change_queue_name = PRICE_CHANGE_QUEUE_NAME
        self.connection = None
        self.channel = None

    async def getchannel(self):
        if self.connection is None or self.connection.is_closed:
            self.connection = await aio_pika.connect_robust(self.amqp_url)
        if self.channel is None or self.channel.is_closed:
            self.channel = await self.connection.channel()
        return self.channel

    async def queue_notification(self, queue_name: str, message_body: dict) -> None:
        channel = await self.getchannel()

        queue = await channel.declare_queue(queue_name, durable=True)

        await channel.default_exchange.publish(
            aio_pika.Message(
                body=json.dumps(message_body).encode(),
                delivery_mode=aio_pika.DeliveryMode.PERSISTENT
            ),
            routing_key=queue.name,
        )

    async def close(self):
        if self.connection and not self.connection.is_closed:
            await self.connection.close()

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
        await self.queue_notification(self.email_queue_name, email_payload)

    async def send_alert_status_notification(self, user_id: int, alert_id: int, status: AlertStatus, price: Optional[float]) -> None:
        alert_status_payload = {
            "type": QueueNotificationPayloadTypes.ALERT_STATUS.value,
            "data": {
                "user_id": user_id,
                "alert_id": alert_id,
                "status": status.value,
                "triggered_price": price
            }
        }

        await self.queue_notification(self.alert_status_queue_name, alert_status_payload)

    async def send_price_change_notification(self, user_id: int, payload: dict[int, float]) -> None:
        price_change_payload = {
            "type": QueueNotificationPayloadTypes.PRICE_CHANGE.value,
            "data": {
                "user_id": user_id,
                **payload
            }
        }

        await self.queue_notification(self.price_change_queue_name, price_change_payload)
