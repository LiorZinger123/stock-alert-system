import json
import logging
import asyncio
import aio_pika
from core.config import settings
from services.wb_connection_manager import ws_connection_manager
from helpers.constants import ALERT_STATUS_NOTIFICATION_QUEUE_NAME, PRICE_CHANGE_QUEUE_NAME


logger = logging.getLogger(__name__)


async def generic_queue_consumer(queue_name: str):
    while True:
        try:
            logger.info(f"Connecting consumer to queue: {queue_name}...")
            connection = await aio_pika.connect_robust(settings.RABBITMQ_URL)
            async with connection:
                channel = await connection.channel()
                await channel.set_qos(prefetch_count=10)
                queue = await channel.declare_queue(queue_name, durable=True)
                logger.info(f"Successfully listening on queue: {queue_name}")

                async with queue.iterator() as queue_iter:
                    async for message in queue_iter:
                        async with message.process():
                            data = json.loads(message.body.decode())
                            payload = data.get("data", {})
                            user_id = payload.get("user_id")
                            if user_id:
                                await ws_connection_manager.send_to_user(user_id, data)
                            else:
                                logger.warning(f"Missing user_id in message: {data}")
        except asyncio.CancelledError:
            logger.info(f"Consumer for {queue_name} cancelled successfully.")
            break
        except Exception as e:
            logger.error(f"Consumer error on queue '{queue_name}': {e}. Retrying connection in 5s...", exc_info=True)
            await asyncio.sleep(5)


async def alert_status_consumer():
    await generic_queue_consumer(ALERT_STATUS_NOTIFICATION_QUEUE_NAME)


async def price_change_consumer():
    await generic_queue_consumer(PRICE_CHANGE_QUEUE_NAME)
