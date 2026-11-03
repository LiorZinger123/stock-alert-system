import json
import logging
import asyncio
import aio_pika
from ..shared.worker_asset_service import WorkerAssetService
from helpers.constants import ASSETS_PRICES_RETRY_QUEUE, DLQ_NAME


logger = logging.getLogger(__name__)


class DBSyncWorker:
    def __init__(
        self,
        amqp_url: str,
        asset_service: WorkerAssetService,
    ):
        self.amqp_url = amqp_url
        self.asset_service = asset_service
        self.queue_name = ASSETS_PRICES_RETRY_QUEUE
        self.dlq_name = DLQ_NAME
        self.max_retries = 3

    async def start(self) -> None:
        connection = await aio_pika.connect_robust(self.amqp_url)
        async with connection:
            channel = await connection.channel()
            await channel.set_qos(prefetch_count=10)
            
            await channel.declare_queue(self.dlq_name, durable=True)
            queue = await channel.declare_queue(self.queue_name, durable=True)
            
            logger.info(f"DbSyncWorker listening to queue: {self.queue_name} (Max retries: {self.max_retries})")
            
            async with queue.iterator() as queue_iter:
                async for message in queue_iter:
                    try:
                        price_updates = json.loads(message.body.decode())
                        await self.process_price_updates(price_updates)
                        
                        await message.ack()
                        
                    except Exception as e:
                        logger.exception(f"Error processing price update message: {e}")
                        await asyncio.sleep(2)
                        
                        headers = dict(message.headers or {})
                        raw_retry_count = headers.get("x-retry-count", 0)
                        
                        retry_count = (
                            raw_retry_count 
                            if isinstance(raw_retry_count, int) 
                            else 0
                        )
                        
                        if retry_count < self.max_retries:
                            headers["x-retry-count"] = retry_count + 1
                            logger.warning(f"Retrying message (Attempt {retry_count + 1}/{self.max_retries})")
                            
                            await channel.default_exchange.publish(
                                aio_pika.Message(
                                    body=message.body,
                                    headers=headers,
                                    delivery_mode=message.delivery_mode
                                ),
                                routing_key=self.queue_name
                            )
                            await message.ack()
                        else:
                            logger.error(f"Message failed {self.max_retries} times. Moving to Dead Letter Queue: {self.dlq_name}")
                            
                            await channel.default_exchange.publish(
                                aio_pika.Message(
                                    body=message.body,
                                    headers=headers,
                                    delivery_mode=message.delivery_mode
                                ),
                                routing_key=self.dlq_name
                            )
                            await message.ack()

    async def process_price_updates(self, price_updates: list[dict[str, float]]) -> None:
        if not price_updates:
            return

        await self.asset_service.bulk_update_prices(price_updates)
