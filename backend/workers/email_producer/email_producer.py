import logging
import asyncio
from db.models import Alert
from helpers.enums import ConditionEnum
from api.schemas.alerts import AlertStatus
from ..shared.worker_alert_service import WorkerAlertService
from ..shared.worker_asset_service import WorkerAssetService
from services.notification_service import NotificationService


logger = logging.getLogger(__name__)


class EmailProducer:
    def __init__(self,
                 alert_service: WorkerAlertService,
                 asset_service: WorkerAssetService,
                 notification_service: NotificationService
                ):
        self.alert_service = alert_service
        self.asset_service = asset_service
        self.notification_service = notification_service

    async def run_loop(self) -> None:
        logger.info("PriceMonitor started...")
        while True:
            try:
                logger.debug("Starting worker iteration...")
                await self.run_worker()
                logger.debug("Worker iteration completed successfully.")
            except asyncio.CancelledError:
                logger.info("PriceMonitor is shutting down...")
                break
            except Exception as e:
                logger.exception(f"Critical error in PriceMonitor: {e}")
            
            logger.debug("Sleeping for 60 seconds...")
            await asyncio.sleep(60)
    
    async def run_worker(self) -> None:
        logger.info("Starting email_producer iteration")
        
        active_symbols = await self.alert_service.get_active_symbols()
        current_prices = await self.asset_service.get_latest_prices(active_symbols)
        
        alert_count = 0
        triggered_count = 0
        
        async for alert in self.alert_service.stream_active_alerts():
            alert_count += 1
            price = current_prices.get(alert.asset.symbol)
            
            if price is not None:
                if self.check_condition(alert, price):
                    await self.trigger_notification(alert, price)
                    triggered_count += 1
            else:
                logger.warning(f"No price found for {alert.asset.symbol} (Alert ID: {alert.id})")
                
        logger.info(f"Finished. Processed {alert_count}, pushed to queue: {triggered_count}.")
    
    def check_condition(self, alert: Alert, current_price: float) -> bool:
        if alert.condition == ConditionEnum.ABOVE.value:
            return current_price >= alert.target_price
            
        elif alert.condition == ConditionEnum.BELOW.value:
            return current_price <= alert.target_price
            
        return False

    async def trigger_notification(self, alert: Alert, current_price: float) -> None:
        await self.notification_service.send_email_notification(alert, current_price)
        await self.alert_service.mark_alert_as_pending(alert.id, current_price)
        await self.notification_service.send_alert_status_notification(alert.user_id, alert.id, AlertStatus.PENDING, current_price)
