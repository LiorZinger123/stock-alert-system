import json
import logging
import aio_pika
from db.models import Alert
from helpers.enums import ConditionEnum
from api.schemas.alerts import AlertStatus
from helpers.constants import STOCK_PRICE_UPDATED_QUEUE_NAME
from ..shared.worker_alert_service import WorkerAlertService
from services.notification_service import NotificationService


logger = logging.getLogger(__name__)


class TriggerCheckerWorker:
    def __init__(
        self,
        amqp_url: str,
        alert_service: WorkerAlertService,
        notification_service: NotificationService
    ):
        self.amqp_url = amqp_url
        self.alert_service = alert_service
        self.notification_service = notification_service
        self.queue_name = STOCK_PRICE_UPDATED_QUEUE_NAME

    async def start(self) -> None:
        connection = await aio_pika.connect_robust(self.amqp_url)
        async with connection:
            channel = await connection.channel()
            await channel.set_qos(prefetch_count=10)
            
            queue = await channel.declare_queue(self.queue_name, durable=True)
            
            logger.info(f"TriggerCheckerWorker listening to queue: {self.queue_name}")
            
            async with queue.iterator() as queue_iter:
                async for message in queue_iter:
                    async with message.process():
                        try:
                            price_updates = json.loads(message.body.decode())
                            await self.process_price_updates(price_updates)
                        except Exception as e:
                            logger.exception(f"Error processing price update message: {e}")

    async def process_price_updates(self, price_updates: dict[str, float]) -> None:
        if not price_updates:
            return

        logger.info(f"Received price updates for {len(price_updates)} symbols. Checking triggers...")
        
        triggered_count = 0
        
        async for alert in self.alert_service.stream_active_alerts():
            symbol = alert.asset.symbol
            if symbol in price_updates:
                current_price = price_updates[symbol]
                
                if self.check_condition(alert, current_price):
                    await self.trigger_notification(alert, current_price)
                    triggered_count += 1

        logger.info(f"Finished processing batch. Triggered {triggered_count} alerts.")

    def check_condition(self, alert: Alert, current_price: float) -> bool:
        if alert.condition == ConditionEnum.ABOVE.value:
            return current_price >= alert.target_price
        elif alert.condition == ConditionEnum.BELOW.value:
            return current_price <= alert.target_price
        return False

    async def trigger_notification(self, alert: Alert, current_price: float) -> None:
        await self.alert_service.mark_alert_as_pending(alert.id, current_price)
        await self.notification_service.send_email_notification(alert, current_price)
        await self.notification_service.send_alert_status_notification(
            alert.user_id, alert.id, AlertStatus.PENDING, current_price
        )
