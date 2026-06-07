import json
import aio_pika
from db.models import Alert
from helpers.constants import EMAIL_NOTIFICATION_QUEUE_NAME


class NotificationService:
    def __init__(self, amqp_url: str):
        self.amqp_url = amqp_url
        self.queue_name = EMAIL_NOTIFICATION_QUEUE_NAME

    async def queue_notification(self, alert: Alert, current_price: float) -> None:
        connection = await aio_pika.connect_robust(self.amqp_url)
        
        async with connection:
            channel = await connection.channel()

            await channel.declare_queue(self.queue_name, durable=True)

            message_body = {
                "alert_id": alert.id,
                "user_email": alert.owner.email,
                "symbol": alert.asset.symbol,
                "target_price": str(alert.target_price),
                "current_price": str(current_price),
                "condition": str(alert.condition.value) if hasattr(alert.condition, 'value') else str(alert.condition)
            }

            await channel.default_exchange.publish(
                aio_pika.Message(
                    body=json.dumps(message_body).encode(),
                    delivery_mode=aio_pika.DeliveryMode.PERSISTENT
                ),
                routing_key=self.queue_name,
            )
