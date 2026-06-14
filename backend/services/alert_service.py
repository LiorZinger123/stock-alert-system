import logging
import yfinance as yf
from typing import Union
from sqlalchemy import select
from sqlalchemy.orm import joinedload
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from db.models import Alert, Asset
from .container import market_cache
from helpers.enums import AlertStatus
from .asset_service import AssetService
from api.schemas.alerts import AlertReadSchema, AlertCreateSchema, AlertUpdateSchema


logger = logging.getLogger(__name__)


class AlertService:
    def __init__(self, db: AsyncSession, asset_service: AssetService):
        self.db = db
        self.asset_service = asset_service

    async def get_price_with_fallback(self, asset_or_symbol: Union[Asset, str]) -> float | None:
        symbol = asset_or_symbol.symbol if isinstance(asset_or_symbol, Asset) else asset_or_symbol
        
        try:
            cached_price = await market_cache.get_price(symbol)
            if cached_price is not None:
                return float(cached_price)
        except Exception as e:
            logger.warning(f"Redis unavailable for {symbol}: {e}")

        if isinstance(asset_or_symbol, Asset):
            return asset_or_symbol.last_known_price
        else:
            return await self.asset_service.get_price_from_db_by_symbol(symbol)

    def validate_action_on_alert(self, alert: Alert) -> None:
        if alert.status == AlertStatus.SENT:
            raise HTTPException(status_code=403, detail=f"Alert {alert.id} is already sent.")
        if alert.status == AlertStatus.PENDING:
            raise HTTPException(status_code=409, detail=f"Alert {alert.id} is in process.")

    async def get_all_by_user(self, user_id: int) -> list[AlertReadSchema]:
        query = select(Alert).options(joinedload(Alert.asset)).where(Alert.user_id == user_id)
        result = await self.db.execute(query)
        alerts = result.scalars().all()

        active_alerts = [a for a in alerts if a.status == AlertStatus.ACTIVE]
        active_symbols = [a.asset.symbol for a in active_alerts]
        
        price_map = {}
        if active_symbols:
            prices = await market_cache.get_prices_bulk(active_symbols)
            for symbol, price in zip(active_symbols, prices):
                final_price = price if price is not None else await self.get_price_with_fallback(symbol)
                price_map[symbol] = final_price

        response_list: list[AlertReadSchema] = []
        for alert in alerts:
            alert_schema = AlertReadSchema.model_validate(alert)
            if alert.status == AlertStatus.ACTIVE:
                alert_schema.current_price = price_map.get(alert.asset.symbol)
            else:
                alert_schema.current_price = None
            response_list.append(alert_schema)
        
        return response_list

    async def get_or_create_asset(self, symbol: str) -> Asset:
        symbol = symbol.upper()
        
        result = await self.db.execute(select(Asset).where(Asset.symbol == symbol))
        asset = result.scalar_one_or_none()
        
        if asset:
            return asset

        ticker = yf.Ticker(symbol)
        info = ticker.info
        
        new_asset = Asset(
            symbol=symbol,
            name=info.get("longName"),
            sector=info.get("sector"),
            industry=info.get("industry"),
            exchange=info.get("exchange"),
        )
        
        self.db.add(new_asset)
        await self.db.commit()
        await self.db.refresh(new_asset)
        return new_asset

    async def create_new_alert(self, user_id: int, alert_data: AlertCreateSchema) -> AlertReadSchema:
        asset = await self.get_or_create_asset(alert_data.symbol)

        try:
            price = yf.Ticker(asset.symbol).fast_info.last_price
            if price:
                rounded_price = round(float(price), 2)
                await market_cache.set_price(asset.symbol, rounded_price)
                asset.last_known_price = rounded_price
        except Exception as e:
            logger.error(f"Could not fetch price: {e}")

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
        alert_schema.current_price = await self.get_price_with_fallback(new_alert.asset)
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
            alert_schema.current_price = await self.get_price_with_fallback(alert.asset)

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
