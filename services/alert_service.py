import logging
import yfinance as yf
from typing import Optional
from sqlalchemy import select
from fastapi import HTTPException
from collections.abc import Sequence
from sqlalchemy.orm import joinedload
from sqlalchemy.ext.asyncio import AsyncSession
from db.models import Alert, Asset
from .container import market_cache
from helpers.enums import AlertStatus
from api.schemas.alerts import AlertReadSchema


logger = logging.getLogger(__name__)


class AlertService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_price_with_fallback(self, asset: Asset) -> Optional[float]:
        try:
            cached_price = await market_cache.get_price(asset.symbol)
            if cached_price is not None:
                return float(cached_price)
        except Exception as e:
            logger.warning(f"Redis unavailable for {asset.symbol}: {e}")

        return asset.last_known_price

    def validate_action_on_alert(self, alert: Alert) -> None:
        if alert.status == AlertStatus.SENT:
            raise HTTPException(status_code=403, detail=f"Alert {alert.id} is already sent and cannot be modified.")
        
        if alert.status == AlertStatus.PENDING:
            raise HTTPException(status_code=409, detail=f"Alert {alert.id} is in process.")

    async def get_all_by_user(self, user_id: int) -> Sequence[AlertReadSchema]:
        query = select(Alert).options(joinedload(Alert.asset)).where(Alert.user_id == user_id)
        result = await self.db.execute(query)
        alerts = result.scalars().all()

        active_alerts = [a for a in alerts if a.status == AlertStatus.ACTIVE.value]
        active_symbols = [a.asset.symbol for a in active_alerts]
        
        price_map = {}
        if active_symbols:
            prices = await market_cache.get_prices_bulk(active_symbols)
            
            for symbol, price in zip(active_symbols, prices):
                final_price = price
                if final_price is None:
                    final_price = await self.asset_service.get_price_from_db_by_symbol(symbol)
                price_map[symbol] = final_price

        for alert in alerts:
            if alert.status == AlertStatus.ACTIVE.value:
                alert.asset.current_price = price_map.get(alert.asset.symbol)
            else:
                alert.asset.current_price = None
        
        return alerts

    async def get_or_create_assets(self, symbols: list[str]) -> dict:
        symbols = [s.upper() for s in symbols]
        
        result = await self.db.execute(select(Asset).where(Asset.symbol.in_(symbols)))
        existing = {a.symbol: a for a in result.scalars().all()}
        
        new_assets = []
        for symbol in symbols:
            if symbol not in existing:
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
                new_assets.append(new_asset)
                existing[symbol] = new_asset
        
        if new_assets:
            await self.db.commit()
            
        return existing

    async def bulk_create(self, user_id: int, alerts_data: list) -> list[Alert]:
        symbols = [a.symbol for a in alerts_data]
        assets = await self.get_or_create_assets(symbols)
        
        for symbol in symbols:
            try:
                ticker = yf.Ticker(symbol)
                price = ticker.fast_info.last_price
                
                if price is not None:
                    rounded_price = round(float(price), 2)
                    
                    await market_cache.set_price(symbol, rounded_price)
                    assets[symbol.upper()].last_known_price = rounded_price
            except Exception as e:
                logger.error(f"Could not fetch price for {symbol}: {e}")
        
        new_alerts = []
        for item in alerts_data:
            alert = Alert(
                user_id=user_id, 
                asset_id=assets[item.symbol.upper()].id, 
                target_price=item.target_price, 
                condition=item.condition
            )
            self.db.add(alert)
            new_alerts.append(alert)
        
        await self.db.commit()

        for a in new_alerts: 
            await self.db.refresh(a, ["asset"])
            price = await self.get_price_with_fallback(a.asset)
            a.asset.current_price = price
                
        return new_alerts

    async def bulk_update(self, user_id: int, updates: list) -> list[Alert]:
        try:
            alert_ids = [item.id for item in updates]
            query = select(Alert).options(joinedload(Alert.asset)).where(
                Alert.id.in_(alert_ids), 
                Alert.user_id == user_id
            )
            result = await self.db.execute(query)
            alerts_map = {alert.id: alert for alert in result.unique().scalars().all()}

            for item in updates:
                alert = alerts_map.get(item.id)
                if not alert:
                    raise PermissionError(f"Alert {item.id} not found or unauthorized.")
                
                update_data = item.model_dump(exclude={'id'}, exclude_unset=True)
                self.validate_action_on_alert(alert)

                for key, value in update_data.items():
                    setattr(alert, key, value)

            await self.db.commit()
            
            for alert in alerts_map.values():
                await self.db.refresh(alert, ["asset"])
                alert.asset.current_price = await self.get_price_with_fallback(alert.asset)
            
            return list(alerts_map.values())

        except Exception as e:
            await self.db.rollback()
            logger.error(f"Bulk update failed: {e}")
            raise e
        
    async def bulk_delete(self, user_id: int, alerts_ids: list[int]) -> int:
        try:
            query = select(Alert).where(Alert.id.in_(alerts_ids), Alert.user_id == user_id)
            result = await self.db.execute(query)
            alerts_to_delete = result.scalars().all()

            if not alerts_to_delete:
                return 0

            for alert in alerts_to_delete:
                self.validate_action_on_alert(alert)
                await self.db.delete(alert)
            
            await self.db.commit()
            return len(alerts_to_delete)
        except Exception as e:
            await self.db.rollback()
            raise e
