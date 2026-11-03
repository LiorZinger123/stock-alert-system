import asyncio
import logging
from core.config import settings
from .db_sync_worker import DBSyncWorker
from core.database import AsyncSessionLocal
from ..shared.worker_asset_service import WorkerAssetService


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("WorkerMain")


async def main():
    logger.info("Initializing Worker dependencies...")
    
    asset_service = WorkerAssetService(AsyncSessionLocal)
    worker = DBSyncWorker(
        amqp_url=settings.RABBITMQ_URL,
        asset_service=asset_service,
    )
    
    logger.info("Worker started and listening to queue...")
    try:
        await worker.start()
    except Exception as e:
        logger.error(f"Worker crashed: {e}")
    finally:
        logger.info("Worker stopped.")


if __name__ == "__main__":
    asyncio.run(main())
