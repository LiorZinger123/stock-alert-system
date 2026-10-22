import asyncio
import logging
from core.config import settings
from .email_worker import EmailWorker
from services.container import rabbitmq_publisher
from services.notification_service import NotificationService


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("WorkerMain")


async def main():
    logger.info("Initializing Worker dependencies...")

    notification_service = NotificationService(rabbitmq_publisher)
    
    worker = EmailWorker(
        amqp_url=settings.RABBITMQ_URL,
        notification_service=notification_service
    )
    
    logger.info("Worker started and listening to queue...")
    try:
        await worker.start()
    except Exception as e:
        logger.error(f"Worker crashed: {e}")
    finally:
        await notification_service.close()
        logger.info("Worker stopped.")


if __name__ == "__main__":
    asyncio.run(main())
