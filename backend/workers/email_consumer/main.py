import asyncio
import logging
import aio_pika
from core.config import settings
from .email_worker import EmailWorker
from helpers.constants import EMAIL_NOTIFICATION_QUEUE_NAME


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("ConsumerWorker")


async def main():
    logger.info("Connecting to RabbitMQ...")
    
    email_worker = EmailWorker()
    connection = await aio_pika.connect_robust(settings.RABBITMQ_URL)
    
    async with connection:
        channel = await connection.channel()
        
        await channel.set_qos(prefetch_count=1)
        
        queue = await channel.declare_queue(EMAIL_NOTIFICATION_QUEUE_NAME, durable=True)
        logger.info(f"Worker started. Waiting for messages in {EMAIL_NOTIFICATION_QUEUE_NAME}...")
        
        await queue.consume(email_worker.process_message)
        await asyncio.Future()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Consumer Worker stopped.")
