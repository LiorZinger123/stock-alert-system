import logging
import yfinance as yf
from sqlalchemy import select
from async_lru import alru_cache
from sqlalchemy.orm import joinedload
from typing import Any, Union, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from db.models import Asset, Alert
from .container import market_cache
from helpers.enums import AlertStatus
from api.schemas.assets import AssetDetails, AssetAlertPreview


logger = logging.getLogger(__name__)


class AssetService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_or_create_asset(self, symbol: str, name: Optional[str] = None) -> Asset:
        symbol = symbol.upper()
        result = await self.db.execute(select(Asset).where(Asset.symbol == symbol))
        asset = result.scalar_one_or_none()
        if asset:
            return asset

        ticker = yf.Ticker(symbol)
        info = ticker.info
        raw_price = ticker.fast_info.last_price
        rounded_price = round(float(raw_price), 2) if raw_price is not None else None

        new_asset = Asset(
            symbol=symbol,
            name=name,
            sector=info.get("sector"),
            industry=info.get("industry"),
            exchange=info.get("exchange"),
            price=rounded_price
        )
        self.db.add(new_asset)
        await self.db.commit()
        await self.db.refresh(new_asset)

        if rounded_price:
            await market_cache.set_price(symbol, rounded_price)

        return new_asset

    async def get_asset_details(self, symbol: str, name: str | None, user_id: int) -> AssetDetails:
        asset = await self.get_or_create_asset(symbol, name)
        user_alerts = await self.get_user_alert_for_asset(user_id, symbol)
        
        return AssetDetails(
            symbol=asset.symbol,
            name=asset.name,
            sector=asset.sector,
            industry=asset.industry,
            exchange=asset.exchange,
            price=asset.price,
            user_alerts=[AssetAlertPreview.model_validate(alert) for alert in user_alerts]
        )
    
    @alru_cache(maxsize=128)
    async def search_stocks(self, query: str) -> list[dict[str, Any]]:
        if len(query) < 2:
            return []

        search_results = yf.Search(query)
        results = []
        
        for item in search_results.quotes:
            symbol = item.get("symbol")
            if not symbol:
                continue

            results.append({
                "symbol": symbol,
                "name": item.get("longname")
                        or item.get("shortname")
                        or symbol
            })
        
        return results

    async def get_price_from_db_by_symbol(self, symbol: str) -> float | None:
        stmt = select(Asset.price).where(Asset.symbol == symbol.upper())
        result = await self.db.execute(stmt)
        price = result.scalar_one_or_none()
        return float(price) if price is not None else None

    async def get_price_with_fallback(self, asset_or_symbol: Union[Asset, str]) -> float | None:
        symbol = asset_or_symbol.symbol if isinstance(asset_or_symbol, Asset) else asset_or_symbol
        
        try:
            cached_price = await market_cache.get_price(symbol)
            if cached_price is not None:
                return float(cached_price)
        except Exception as e:
            logger.warning(f"Redis unavailable for {symbol}: {e}")

        if isinstance(asset_or_symbol, Asset):
            return asset_or_symbol.price
        else:
            return await self.get_price_from_db_by_symbol(symbol)
        
    async def get_user_alert_for_asset(self, user_id: int, symbol: str) -> list[AssetAlertPreview]:
        query = (
            select(Alert)
            .options(joinedload(Alert.asset))
            .join(Asset)
            .where(Asset.symbol == symbol.upper())
            .where(Alert.user_id == user_id)
            .where(Alert.status == AlertStatus.ACTIVE.value)
        )
        result = await self.db.execute(query)
        alerts = result.scalars().all()
        
        return [AssetAlertPreview.model_validate(a) for a in alerts]
