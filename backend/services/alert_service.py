import logging
from sqlalchemy.orm import joinedload
from sqlalchemy import select, desc, and_
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from db.models import Alert
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
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f"Alert {alert.id} is already sent.")
        if alert.status == AlertStatus.PENDING:
            raise HTTPException(status_code=status.HTTP_423_LOCKED, detail=f"Alert {alert.id} is in process.")

    async def get_all_by_user(self, user_id: int, offset: int = 0, limit: int = 20) -> list[AlertReadSchema]:
        query = (
            select(Alert)
            .options(joinedload(Alert.asset))
            .where(Alert.user_id == user_id)
            .order_by(desc(Alert.created_at))
            .limit(limit)
            .offset(offset)
        )
        result = await self.db.execute(query)
        alerts = result.scalars().all()
        
        return [AlertReadSchema.model_validate(a) for a in alerts]

    async def create_new_alert(self, user_id: int, alert_data: AlertCreateSchema) -> AlertReadSchema:
        asset = await self.asset_service.get_or_create_asset(alert_data.symbol, alert_data.name)

        query = select(Alert).where(
            and_(
                Alert.user_id == user_id,
                Alert.asset_id == asset.id,
                Alert.target_price == alert_data.target_price,
                Alert.condition == alert_data.condition
            )
        )
        result = await self.db.execute(query)

        if result.scalars().first():
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="You already have an identical alert set for this asset."
            )

        new_alert = Alert(
            user_id=user_id,
            asset_id=asset.id,
            target_price=alert_data.target_price,
            condition=alert_data.condition
        )
        
        self.db.add(new_alert)
        await self.db.commit()
        await self.db.refresh(new_alert, ["asset"])
        
        return AlertReadSchema.model_validate(new_alert)

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

            new_price = update_data.target_price if update_data.target_price is not None else alert.target_price
            new_condition = update_data.condition if update_data.condition is not None else alert.condition
            asset_id = alert.asset_id 

            conflict_query = select(Alert).where(
                and_(
                    Alert.user_id == user_id,
                    Alert.asset_id == asset_id,
                    Alert.target_price == new_price,
                    Alert.condition == new_condition,
                    Alert.id != alert_id
                )
            )
            conflict_result = await self.db.execute(conflict_query)
            if conflict_result.scalars().first():
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="An identical alert (same asset, price, and condition) already exists."
                )

            update_dict = update_data.model_dump(
                exclude={'id', 'symbol', 'name'}, 
                exclude_unset=True
            )
            
            for key, value in update_dict.items():
                setattr(alert, key, value)

            await self.db.commit()
            await self.db.refresh(alert, ["asset"])

            return AlertReadSchema.model_validate(alert)
        except HTTPException:
            raise
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
        except HTTPException:
            raise
        except Exception as e:
            await self.db.rollback()
            logger.error("Database error occurred during deletion.")
            raise e
