import math
import asyncio
import logging
import yfinance as yf
from db.models import Alert
from helpers.enums import ConditionEnum, AlertStatus
from ..shared.worker_alert_service import WorkerAlertService
from services.cache_managers import MarketCache, NotificationService


logger = logging.getLogger(__name__)


class PriceMonitor:
    def __init__(self, market_cache: MarketCache, alert_service: WorkerAlertService, notification_service: NotificationService):
        self.market_cache = market_cache
        self.alert_service = alert_service
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
        logger.info("Starting Worker iteration")
        
        active_symbols = await self.alert_service.get_active_symbols()
        logger.info(f"Fetched {len(active_symbols)} active symbols from DB")
        
        current_prices = await self.market_cache.get_prices(active_symbols)
        missing_symbols = [s for s, p in current_prices.items() if p is None]

        if missing_symbols:
            logger.warning(f"Found {len(missing_symbols)} missing prices. Fetching from API...")
            loop = asyncio.get_running_loop()
            new_prices = await loop.run_in_executor(None, self.fetch_prices_from_api, missing_symbols)
            
            if new_prices:
                logger.info(f"Successfully fetched {len(new_prices)} prices from API")
                formatted_new_price = {f"stock:price:{symbol}": price for symbol, price in new_prices.items()}
                await self.market_cache.set_prices(formatted_new_price)
                current_prices.update(new_prices)
            else:
                logger.error("Failed to fetch missing prices from API")

        alert_count = 0
        triggered_count = 0
        
        async for alert in self.alert_service.stream_active_alerts():
            alert_count += 1
            price = current_prices.get(alert.asset.symbol)
            
            if price is not None:
                if self.check_condition(alert, price):
                    logger.info(f"Triggering alert {alert.id} for {alert.asset.symbol} at price {price}")
                    await self.trigger_notification(alert, price)
                    triggered_count += 1
            else:
                logger.warning(f"Price not found for symbol: {alert.asset.symbol} (Alert ID: {alert.id})")
                
        logger.info(f"Worker iteration finished. Processed {alert_count} alerts, triggered {triggered_count} notifications.")

    def fetch_prices_from_api(self, symbols: list[str], chunk_size: int = 50) -> dict:
        all_prices = {}

        def get_chunks(lst: list[str], n: int):
            for i in range(0, len(lst), n):
                yield lst[i:i + n]

        for chunk in get_chunks(symbols, chunk_size):
            try:
                tickers = yf.Tickers(" ".join(chunk))
                data = tickers.history(period="1d", interval="1m", progress=False)
                
                if not data.empty and 'Close' in data.columns:
                    latest_data = data['Close'].iloc[-1]
                    batch_prices = latest_data.to_dict()
                    
                    for symbol, price in batch_prices.items():
                        if price is not None and not math.isnan(price):
                            all_prices[symbol] = round(float(price), 2)
                        else:
                            logger.warning(f"Invalid price for {symbol}: {price}")
                else:
                    logger.warning(f"No valid data returned for chunk: {chunk}")

            except Exception as e:
                logger.error(f"Error fetching batch {chunk}: {e}")
                continue
                
        return all_prices

    def check_condition(self, alert: Alert, current_price: float) -> bool:
        if alert.condition == ConditionEnum.ABOVE.value:
            return current_price >= alert.target_price
            
        elif alert.condition == ConditionEnum.BELOW.value:
            return current_price <= alert.target_price
            
        return False

    async def trigger_notification(self, alert: Alert, current_price: float) -> None:
        await self.notification_service.queue_notification(alert, current_price)
        await self.alert_service.update_alert_status(alert.id, AlertStatus.PENDING)
