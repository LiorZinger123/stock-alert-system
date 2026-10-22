import asyncio
import logging
from .price_monitor import PriceMonitor
from core.database import AsyncSessionLocal
from services.container import market_cache
from services.container import rabbitmq_publisher
from ..shared.worker_alert_service import WorkerAlertService
from ..shared.worker_asset_service import WorkerAssetService
from services.notification_service import NotificationService


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("WorkerMain")


async def main():
    logger.info("Initializing worker dependencies...")
    
    alert_service = WorkerAlertService(AsyncSessionLocal)
    asset_service = WorkerAssetService(AsyncSessionLocal)
    monitor = PriceMonitor(
        market_cache=market_cache,
        alert_service=alert_service,
        asset_service=asset_service,
        rabbitmq_publisher=rabbitmq_publisher
    )
    
    logger.info("Worker started.")
    try:
        await monitor.run_loop()
    except Exception as e:
        logger.error(f"Worker crashed: {e}")
    finally:
        logger.info("Worker stopped.")

if __name__ == "__main__":
    asyncio.run(main())
