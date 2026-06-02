import logging
import yfinance as yf
from sqlalchemy import select
from sqlalchemy.orm import joinedload
from sqlalchemy.ext.asyncio import AsyncSession
from db.models import Alert, Asset
from .container import market_cache


logger = logging.getLogger(__name__)


class AlertService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_all_by_user(self, user_id: int):
        query = select(Alert).options(joinedload(Alert.asset)).where(Alert.user_id == user_id)
        result = await self.db.execute(query)
        alerts = result.scalars().all()

        for alert in alerts:
            price = await market_cache.get_price(alert.asset.symbol)
            alert.asset.current_price = price if price is not None else 0.0
        
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
                data = ticker.fast_info 
                price = data.last_price
                
                if price:
                    rounded_price = round(float(price), 2)
                    await market_cache.set_price(symbol, rounded_price)
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
            price = await market_cache.get_price(a.asset.symbol)
            a.asset.current_price = price or 0.0
            
        return new_alerts

    async def bulk_update(self, user_id: int, updates: list) -> list[Alert]:
        try:
            alert_ids = [item.id for item in updates]
            query = select(Alert).where(Alert.id.in_(alert_ids), Alert.user_id == user_id)
            result = await self.db.execute(query)
            alerts_map = {alert.id: alert for alert in result.scalars().all()}

            for item in updates:
                if item.id not in alerts_map:
                    raise PermissionError(f"Alert {item.id} not found or unauthorized.")

                alert = alerts_map[item.id]
                update_data = item.dict(exclude={'id'}, exclude_unset=True)
                for key, value in update_data.items():
                    setattr(alert, key, value)

            await self.db.commit()
            
            for alert in alerts_map.values():
                await self.db.refresh(alert, ["asset"])
                price = await market_cache.get_price(alert.asset.symbol)
                alert.asset.current_price = float(price) if price else 0.0
            
            return list(alerts_map.values())

        except Exception as e:
            await self.db.rollback()
            raise e

    async def bulk_delete(self, user_id: int, alerts_ids: list[int]) -> int:
        try:
            query = select(Alert).where(Alert.id.in_(alerts_ids), Alert.user_id == user_id)
            result = await self.db.execute(query)
            alerts_to_delete = result.scalars().all()

            if not alerts_to_delete:
                return 0

            for alert in alerts_to_delete:
                await self.db.delete(alert)
            
            await self.db.commit()
            return len(alerts_to_delete)
        except Exception as e:
            await self.db.rollback()
            raise e
