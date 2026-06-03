import logging
from sqlalchemy.sql import func
from typing import AsyncGenerator
from sqlalchemy.orm import joinedload
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from db.models import Alert, Asset
from helpers.enums import AlertStatus


logger = logging.getLogger(__name__)


class WorkerAlertService:
    def __init__(self, session_factory: AsyncSession):
        self.session_factory = session_factory

    async def get_active_symbols(self) -> list[int]:
        async with self.session_factory() as session:
            query = (
                select(Asset.symbol)
                .join(Alert, Alert.asset_id == Asset.id)
                .filter(Alert.status == AlertStatus.ACTIVE.value)
                .distinct()
            )
            result = await session.execute(query)
            return list(result.scalars().all())

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
                .values(status=new_status)
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
