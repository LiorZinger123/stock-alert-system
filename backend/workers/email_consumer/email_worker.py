import json
import logging
import aio_pika
from helpers.enums import AlertStatus
from .email_service import EmailService
from core.database import AsyncSessionLocal
from helpers.constants import EMAIL_NOTIFICATION_QUEUE_NAME
from ..shared.worker_alert_service import WorkerAlertService
from services.notification_service import NotificationService


logger = logging.getLogger("EmailWorker")


class EmailWorker:
    def __init__(
        self,
        amqp_url: str,
        notification_service: NotificationService
    ):
        self.amqp_url = amqp_url
        self.email_service = EmailService()
        self.alert_service = WorkerAlertService(AsyncSessionLocal)
        self.notification_service = notification_service
        self.queue_name = EMAIL_NOTIFICATION_QUEUE_NAME

    async def start(self) -> None:
        connection = await aio_pika.connect_robust(self.amqp_url)
        async with connection:
            channel = await connection.channel()
            await channel.set_qos(prefetch_count=1)
            
            queue = await channel.declare_queue(self.queue_name, durable=True)
            logger.info(f"EmailWorker listening to queue: {self.queue_name}")
            
            async with queue.iterator() as queue_iter:
                async for message in queue_iter:
                    async with message.process():
                        try:
                            body = json.loads(message.body.decode())
                            alert_id = body.get('alert_id')
                            logger.info(f"Received message for alert: {alert_id}")
                            
                            await self.send_email_task(**body)
                        except Exception as e:
                            logger.exception(f"Error processing email message: {e}")

    async def send_email_task(
        self, 
        user_id: int, 
        alert_id: int, 
        user_email: str, 
        symbol: str, 
        target_price: str, 
        current_price: str, 
        condition: str
    ) -> bool:
        logger.info(f"Processing email for alert {alert_id}")
        
        try:
            await self.email_service.send(
                email=user_email,
                alert_id=alert_id,
                price=float(current_price),
                condition=condition,
                ticker=symbol,
                target_price=target_price
            )
            await self.alert_service.update_alert_status(alert_id, AlertStatus.SENT)
            
            try:
                await self.notification_service.send_alert_status_notification(user_id, alert_id, AlertStatus.SENT)
            except Exception as e:
                logger.error(f"Failed to send status notification for {alert_id}: {e}")
                
            logger.info(f"Email sent and status updated for {alert_id}")
            return True
            
        except Exception as e:
            await self.alert_service.update_alert_status(alert_id, AlertStatus.FAILED)
            logger.error(f"Failed to send email for {alert_id}: {str(e)}")
            raise e
