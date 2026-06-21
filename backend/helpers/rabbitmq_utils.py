import json
import logging
import aio_pika
from core.config import settings
from services.connection_manager import manager
from helpers.constants import ALERT_STATUS_NOTIFICATION_QUEUE_NAME, PRICE_CHANGE_QUEUE_NAME


logger = logging.getLogger(__name__)


async def generic_queue_consumer(queue_name: str):
    connection = await aio_pika.connect_robust(settings.RABBITMQ_URL)
    async with connection:
        channel = await connection.channel()
        await channel.set_qos(prefetch_count=10)
        queue = await channel.declare_queue(queue_name, durable=True)

        async with queue.iterator() as queue_iter:
            async for message in queue_iter:
                async with message.process():
                    data = json.loads(message.body.decode())
                    payload = data.get("data", {})
                    user_id = payload.get("user_id")
                    if user_id:
                        await manager.send_to_user(user_id, data)
                    else:
                        logger.warning(f"Missing user_id in message: {data}")


async def alert_status_consumer():
    await generic_queue_consumer(ALERT_STATUS_NOTIFICATION_QUEUE_NAME)


async def price_change_consumer():
    await generic_queue_consumer(PRICE_CHANGE_QUEUE_NAME)
