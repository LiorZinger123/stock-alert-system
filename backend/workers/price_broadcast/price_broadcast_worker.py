import json
import asyncio
import logging
import aio_pika
from ..shared.worker_alert_service import WorkerAlertService
from services.notification_service import NotificationService
from helpers.constants import PRICE_BROADCAST_QUEUE_NAME, STOCK_PRICE_FANOUT_EXCHANGE


logger = logging.getLogger(__name__)


class PriceBroadcastWorker:
    def __init__(
        self,
        amqp_url: str,
        alert_service: WorkerAlertService,
        notification_service: NotificationService
    ):
        self.amqp_url = amqp_url
        self.alert_service = alert_service
        self.notification_service = notification_service
        self.queue_name = PRICE_BROADCAST_QUEUE_NAME

    async def start(self) -> None:
        connection = await aio_pika.connect_robust(self.amqp_url)
        async with connection:
            channel = await connection.channel()
            await channel.set_qos(prefetch_count=10)
            
            exchange = await channel.declare_exchange(
                name=STOCK_PRICE_FANOUT_EXCHANGE, 
                type=aio_pika.ExchangeType.FANOUT, 
                durable=True
            )
                        
            queue = await channel.declare_queue(self.queue_name, durable=True)
            
            await queue.bind(exchange)
            logger.info(f"PriceBroadcastWorker listening to dedicated queue via Fanout Exchange: {queue.name}")
            
            async with queue.iterator() as queue_iter:
                async for message in queue_iter:
                    try:
                        price_updates = json.loads(message.body.decode())
                        await self.process_price_updates(price_updates)
                        await message.ack()
                        
                    except Exception as e:
                        logger.exception(f"Error processing price broadcast message: {e}")
                        await asyncio.sleep(2)
                        await message.nack(requeue=False)

    async def process_price_updates(self, price_updates: dict[str, float]) -> None:
        if not price_updates:
            return

        logger.info(f"Broadcasting price updates for {len(price_updates)} symbols to users...")

        user_price_updates = await self.alert_service.get_user_alert_price_map(price_updates)
        
        for user_id, web_socket_payload in user_price_updates.items():
            await self.notification_service.send_price_change_notification(user_id, web_socket_payload)

        logger.info(f"Successfully broadcasted price updates to {len(user_price_updates)} users.")
