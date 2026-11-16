import logging
from typing import Optional
from sqlalchemy import update, case
from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncSession
from db.models import Asset
from services.container import rabbitmq_publisher
from helpers.constants import ASSETS_PRICES_RETRY_QUEUE


logger = logging.getLogger(__name__)


class WorkerAssetService:
    def __init__(self, session_factory: async_sessionmaker[AsyncSession]):
        self.session_factory = session_factory

    async def bulk_update_prices(
        self,
        price_map: dict[str, float],
        send_event: Optional[bool] = None
    ) -> None:
        if not price_map:
            return

        price_cases = case(price_map, value=Asset.symbol)

        async with self.session_factory() as session:
            try:
                query = (
                    update(Asset)
                    .where(Asset.symbol.in_(price_map.keys()))
                    .values(price=price_cases)
                    .execution_options(synchronize_session=None)
                )
                
                await session.execute(query)
                await session.commit()
                
                logger.info(f"Successfully updated {len(price_map)} assets in DB.")
            except Exception as e:
                await session.rollback()
                logger.error(f"Failed to bulk update assets in DB: {e}")

                if send_event:
                    await rabbitmq_publisher.publish_to_queue(ASSETS_PRICES_RETRY_QUEUE, price_map)
