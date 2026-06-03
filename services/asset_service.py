import yfinance as yf
from typing import Any
from sqlalchemy import select
from async_lru import alru_cache
from sqlalchemy.ext.asyncio import AsyncSession
from db.models import Alert, Asset
from .container import market_cache
from helpers.enums import AlertStatus



class AssetService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_live_data(self, symbol: str) -> dict[str, Any]:
        price = await market_cache.get_price(symbol)
        if price is not None:
            return {"price": float(price), "name": "Cached Data"}
        
        ticker = yf.Ticker(symbol)
        price = ticker.fast_info.last_price
        
        if price is not None:
            rounded_price = round(float(price), 2)
            await market_cache.set_price(symbol, rounded_price)
            
            return {
                "price": rounded_price,
                "name": ticker.info.get("shortName", symbol)
            }
        
        return {
            "price": None,
            "name": ticker.info.get("shortName", symbol)
        }

    async def get_user_alert_for_asset(self, user_id: int, symbol: str) -> Alert | None:
        stmt = (
            select(Alert)
            .join(Asset)
            .where(Asset.symbol == symbol.upper())
            .where(Alert.user_id == user_id)
            .where(Alert.status == AlertStatus.ACTIVE.value)
        )
        result = await self.db.execute(stmt)
        return result.scalars().first()
    
    @alru_cache(maxsize=128)
    async def search_stocks(self, query: str) -> (list | list[dict[str, Any]]):
        if len(query) < 2:
            return []

        search_results = yf.Search(query)
        
        results = [
            {"symbol": item["symbol"], "name": item["longname"]} 
            for item in search_results.quotes
        ]
        
        return results
