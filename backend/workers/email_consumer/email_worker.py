import json
import logging
from aio_pika.abc import AbstractIncomingMessage
from helpers.enums import AlertStatus
from .email_service import EmailService
from core.database import AsyncSessionLocal
from ..shared.worker_alert_service import WorkerAlertService
from services.notification_service import NotificationService


logger = logging.getLogger("EmailWorker")


class EmailWorker:
    def __init__(self, notification_service: NotificationService):
        self.email_service = EmailService()
        self.alert_service = WorkerAlertService(AsyncSessionLocal)
        self.notification_service = notification_service

    async def process_message(self, message: AbstractIncomingMessage):
        async with message.process():
            try:
                body = json.loads(message.body.decode())
                logger.info(f"Received message for alert: {body.get('alert_id')}")
                
                await self.send_email_task(**body)
                
            except Exception as e:
                logger.error(f"Error processing message: {e}")

    async def send_email_task(self, user_id: int, alert_id: int, user_email: str, symbol: str, 
                              target_price: str, current_price: str, condition: str) -> bool:
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
