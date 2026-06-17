import logging
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import APIRouter, HTTPException, Depends, status
from core.database import get_db
from services.asset_service import AssetService
from helpers.security import get_current_user_id
from ..schemas.assets import AssetDetails, AssetMetadata


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


@router.post("/{symbol}", response_model=AssetDetails)
async def get_asset_details(
    symbol: str,
    metadata: AssetMetadata,
    db: AsyncSession = Depends(get_db),
    user_id: int = Depends(get_current_user_id)
) -> AssetDetails:
    try:
        service = AssetService(db)
        return await service.get_asset_details(symbol, metadata.name, user_id)
    except Exception as e:
        logger.error(f"Error fetching asset {symbol}: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve asset details. Please try again later."
        )
