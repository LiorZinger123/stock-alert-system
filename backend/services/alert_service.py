import logging
from sqlalchemy import select, desc
from sqlalchemy.orm import joinedload
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from db.models import Alert
from .container import market_cache
from helpers.enums import AlertStatus
from .asset_service import AssetService
from api.schemas.alerts import AlertReadSchema, AlertCreateSchema, AlertUpdateSchema


logger = logging.getLogger(__name__)


class AlertService:
    def __init__(self, db: AsyncSession, asset_service: AssetService):
        self.db = db
        self.asset_service = asset_service

    def validate_action_on_alert(self, alert: Alert) -> None:
        if alert.status == AlertStatus.SENT:
            raise HTTPException(status_code=403, detail=f"Alert {alert.id} is already sent.")
        if alert.status == AlertStatus.PENDING:
            raise HTTPException(status_code=409, detail=f"Alert {alert.id} is in process.")

    async def get_all_by_user(self, user_id: int) -> list[AlertReadSchema]:
        query = (
            select(Alert)
            .options(joinedload(Alert.asset))
            .where(Alert.user_id == user_id)
            .order_by(desc(Alert.created_at))
        )
        result = await self.db.execute(query)
        alerts = result.scalars().all()

        active_symbols = [a.asset.symbol for a in alerts if a.status == AlertStatus.ACTIVE]
        
        price_map = {}
        if active_symbols:
            prices = await market_cache.get_prices_bulk(active_symbols)
            price_map = dict(zip(active_symbols, prices))

        response_list: list[AlertReadSchema] = []
        for alert in alerts:
            alert_schema = AlertReadSchema.model_validate(alert)
            if alert.status == AlertStatus.ACTIVE:
                alert_schema.current_price = price_map.get(alert.asset.symbol) or alert.asset.price
            else:
                alert_schema.current_price = None
            response_list.append(alert_schema)
        
        return response_list

    async def create_new_alert(self, user_id: int, alert_data: AlertCreateSchema) -> AlertReadSchema:
        asset = await self.asset_service.get_or_create_asset(alert_data.symbol)

        new_alert = Alert(
            user_id=user_id,
            asset_id=asset.id,
            target_price=alert_data.target_price,
            condition=alert_data.condition
        )
        
        self.db.add(new_alert)
        await self.db.commit()
        await self.db.refresh(new_alert, ["asset"])
        
        alert_schema = AlertReadSchema.model_validate(new_alert)
        alert_schema.current_price = await self.asset_service.get_price_with_fallback(new_alert.asset)
        
        return alert_schema

    async def update_alert(self, user_id: int, alert_id: int, update_data: AlertUpdateSchema) -> AlertReadSchema:
        try:
            query = select(Alert).options(joinedload(Alert.asset)).where(
                Alert.id == alert_id, 
                Alert.user_id == user_id
            )
            result = await self.db.execute(query)
            alert = result.scalar_one_or_none()

            if not alert:
                raise HTTPException(status_code=404, detail="Alert not found.")

            self.validate_action_on_alert(alert)
            
            update_dict = update_data.model_dump(exclude={'id'}, exclude_unset=True)
            for key, value in update_dict.items():
                setattr(alert, key, value)

            await self.db.commit()
            await self.db.refresh(alert, ["asset"])

            alert_schema = AlertReadSchema.model_validate(alert)
            alert_schema.current_price = await self.asset_service.get_price_with_fallback(alert.asset)

            return alert_schema

        except Exception as e:
            await self.db.rollback()
            logger.error(f"Update failed for alert {alert_id}: {e}")
            raise e
        
    async def delete_alert(self, user_id: int, alert_id: int) -> None:
        query = select(Alert).where(Alert.id == alert_id, Alert.user_id == user_id)
        result = await self.db.execute(query)
        alert_to_delete = result.scalars().one_or_none()

        if not alert_to_delete:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, 
                detail=f"Alert with ID {alert_id} not found."
            )

        try:
            self.validate_action_on_alert(alert_to_delete)
            await self.db.delete(alert_to_delete)
            await self.db.commit()
        except:
            await self.db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
                detail="Database error occurred during deletion."
            )
