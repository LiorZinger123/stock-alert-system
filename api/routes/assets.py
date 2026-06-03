import logging
from typing import Any
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import APIRouter, HTTPException, Depends, status
from core.database import get_db
from ..schemas.assets import AssetDetailSchema
from services.asset_service import AssetService
from helpers.security import get_current_user_id


router = APIRouter()
logger = logging.getLogger(__name__)


@router.get("/search")
async def search_stocks_route(query: str, db: AsyncSession = Depends(get_db)) -> dict:
    try:
        service = AssetService(db)
        results = await service.search_stocks(query)
        
        return {"results": results}
        
    except Exception as e:
        logger.error(f"Error searching stocks with query '{query}': {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error occurred while searching for stocks."
        )


@router.get("/{symbol}", response_model=AssetDetailSchema)
async def get_asset_details(
    symbol: str,
    db: AsyncSession = Depends(get_db),
    user_id: int = Depends(get_current_user_id)
) -> dict[str, Any]:
    try:
        service = AssetService(db)
        live_data = await service.get_live_data(symbol)
        user_alert = await service.get_user_alert_for_asset(user_id, symbol)
        price = live_data.get("price")

        return {
            "symbol": symbol,
            "name": live_data.get("name", symbol),
            "current_price": float(price) if price is not None else None,
            "user_alert": user_alert
        }
        
    except Exception as e:
        logger.error(f"Error fetching asset {symbol} for user {user_id}: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve asset details. Please try again later."
        )
