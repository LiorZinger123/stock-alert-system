import math
import asyncio
import logging
import yfinance as yf
from services.cache_managers import MarketCache
from ..shared.worker_alert_service import WorkerAlertService
from ..shared.worker_asset_service import WorkerAssetService


logger = logging.getLogger(__name__)


class PriceMonitor:
    def __init__(
            self,
            market_cache: MarketCache,
            alert_service: WorkerAlertService,
            asset_service: WorkerAssetService,
        ):
        self.market_cache = market_cache
        self.alert_service = alert_service
        self.asset_service = asset_service

    async def run_loop(self, interval: int = 60) -> None:
        logger.info("PriceMonitor started...")
        while True:
            try:
                start_time = asyncio.get_event_loop().time()
                
                logger.debug("Starting worker iteration...")
                await self.run_worker()
                logger.debug("Worker iteration completed successfully.")
                
                elapsed = asyncio.get_event_loop().time() - start_time
                sleep_time = max(0, interval - elapsed)
                
                logger.debug(f"Worker took {elapsed:.2f}s, sleeping for {sleep_time:.2f}s")
                await asyncio.sleep(sleep_time)

            except asyncio.CancelledError:
                logger.info("PriceMonitor is shutting down...")
                break
            except Exception as e:
                logger.exception(f"Critical error in PriceMonitor: {e}")
                await asyncio.sleep(interval)

    async def run_worker(self) -> None:
        logger.info("Starting Worker iteration")
        loop = asyncio.get_running_loop()
        
        active_symbols = await self.alert_service.get_active_symbols()
        
        active_prices = await loop.run_in_executor(None, self.fetch_prices_from_api, active_symbols)
        cached_prices = await self.market_cache.get_prices(active_symbols)

        updates_needed = {}

        for symbol, new_price in active_prices.items():
            old_price = cached_prices.get(symbol)
            
            if old_price is None or float(old_price) != float(new_price):
                updates_needed[symbol] = new_price

        if updates_needed:
            logger.info(f"Detected {len(updates_needed)} price changes. Updating systems...")
            
            formatted_updates = {f"stock:price:{s}": p for s, p in updates_needed.items()}
            await self.market_cache.set_prices(formatted_updates)
            
            await self.asset_service.bulk_update_last_known_prices(updates_needed)
        else:
            logger.info("No price changes detected. Systems are up to date.")

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
