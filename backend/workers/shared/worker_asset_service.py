import logging
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncSession
from db.models import Asset
from services.container import market_cache


logger = logging.getLogger(__name__)


class WorkerAssetService:
    def __init__(self, session_factory: async_sessionmaker[AsyncSession]):
        self.session_factory = session_factory

    async def get_latest_prices(self, symbols: list[str]) -> dict[str, float]:
        prices = await market_cache.get_prices(symbols) 
        
        for symbol, price in prices.items():
            if price is None:
                prices[symbol] = await self.get_price_from_db_by_symbol(symbol)
        
        return prices

    async def get_price_from_db_by_symbol(self, symbol: str) -> float | None:
        async with self.session_factory() as session:
            query = select(Asset.last_known_price).where(Asset.symbol == symbol)
            result = await session.execute(query)
            return result.scalar_one_or_none()

    async def bulk_update_last_known_prices(self, price_map: dict[str, float]) -> None:
        async with self.session_factory() as session:
            try:
                for symbol, price in price_map.items():
                    query = (
                        update(Asset)
                        .where(Asset.symbol == symbol)
                        .values(last_known_price=price)
                    )
                    await session.execute(query)
                
                await session.commit()
                logger.info(f"Successfully updated {len(price_map)} assets in DB.")
            except Exception as e:
                await session.rollback()
                logger.error(f"Failed to bulk update assets in DB: {e}")
                raise e

    async def get_all_symbols(self) -> list[str]:
        async with self.session_factory() as session:
            query = select(Asset.symbol)
            result = await session.execute(query)
            return list(result.scalars().all())
