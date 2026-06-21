import logging
from typing import Sequence
from sqlalchemy.sql import func
from typing import AsyncGenerator
from sqlalchemy.orm import joinedload
from sqlalchemy import select, update, Row
from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncSession
from db.models import Alert, Asset
from helpers.enums import AlertStatus


logger = logging.getLogger(__name__)


class WorkerAlertService:
    def __init__(self, session_factory: async_sessionmaker[AsyncSession]):
        self.session_factory = session_factory

    async def get_active_symbols(self) -> list[str]:
        async with self.session_factory() as session:
            query = (
                select(Asset.symbol)
                .join(Alert, Alert.asset_id == Asset.id)
                .filter(Alert.status == AlertStatus.ACTIVE.value)
                .distinct()
            )
            result = await session.execute(query)
            return [str(s) for s in result.scalars().all()]

    async def stream_active_alerts(self) -> AsyncGenerator[Alert, None]:
        async with self.session_factory() as session:
            query = (
                select(Alert)
                .options(
                    joinedload(Alert.asset),
                    joinedload(Alert.owner)
                )
                .where(Alert.status == AlertStatus.ACTIVE.value)
            )
            stream = await session.stream(query)
            async for row in stream:
                yield row[0]

    async def update_alert_status(self, alert_id: int, new_status: AlertStatus) -> None:
        async with self.session_factory() as session:
            query = (
                update(Alert)
                .where(Alert.id == alert_id)
                .values(status=new_status.value)
            )
            await session.execute(query)
            await session.commit()

    async def mark_alert_as_pending(self, alert_id: int, trigger_price: float) -> None:
        async with self.session_factory() as session:
            query = (
                update(Alert)
                .where(Alert.id == alert_id)
                .values(
                    status=AlertStatus.PENDING.value,
                    triggered_price=trigger_price,
                    triggered_at=func.now()
                )
            )
            await session.execute(query)
            await session.commit()

    async def fetch_active_alerts_by_symbols(self, changed_symbols: list[str]) -> Sequence[Row]:
        async with self.session_factory() as session:
            query = (
                select(Alert.user_id, Alert.id, Asset.symbol)
                .join(Asset, Alert.asset_id == Asset.id)
                .where(
                    Asset.symbol.in_(changed_symbols),
                    Alert.status == AlertStatus.ACTIVE.value
                )
            )
            result = await session.execute(query)
            return result.all()

    async def get_user_alert_price_map(
        self, 
        price_updates: dict[str, float]
    ) -> dict[int, dict[int, float]]:
        changed_symbols = list(price_updates.keys())
        alert_records = await self.fetch_active_alerts_by_symbols(changed_symbols)
        
        user_alert_map: dict[int, dict[int, float]] = {}
        
        for user_id, alert_id, symbol in alert_records:
            if user_id not in user_alert_map:
                user_alert_map[user_id] = {}
            
            user_alert_map[user_id][alert_id] = price_updates[symbol]
                    
        return user_alert_map
