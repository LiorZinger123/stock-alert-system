import logging
from collections.abc import Sequence
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import APIRouter,HTTPException, status, Depends
from db.models import Alert
from core.database import get_db
from services.alert_service import AlertService
from helpers.security import get_current_user_id
from api.schemas.alerts import AlertReadSchema, AlertBulkCreateSchema, AlertBulkUpdateSchema, AlertBultDeleteSchema


router = APIRouter()
logger = logging.getLogger(__name__)


@router.get("", response_model=list[AlertReadSchema])
async def get_user_alerts(
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
) -> Sequence[AlertReadSchema]:
    try:
        service = AlertService(db)
        return await service.get_all_by_user(user_id)
    except Exception as e:
        logger.error(f"Error fetching alerts: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve alerts."
        )


@router.post("/bulk", response_model=list[AlertReadSchema], status_code=status.HTTP_201_CREATED)
async def create_multiple_alerts(
    bulk_data: AlertBulkCreateSchema,
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
) -> list[Alert]:
    try:
        service = AlertService(db)
        return await service.bulk_create(user_id, bulk_data.alerts)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error creating alerts: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to save alerts."
        )


@router.put("/bulk", response_model=list[AlertReadSchema])
async def update_multiple_alerts(
    bulk_update: AlertBulkUpdateSchema,
    db: AsyncSession = Depends(get_db),
    user_id: int = Depends(get_current_user_id)
) -> list[Alert]:
    try:
        service = AlertService(db)
        return await service.bulk_update(user_id, bulk_update.alerts)
    except HTTPException:
        raise
    except PermissionError:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Unauthorized access to alert."
        )
    except Exception as e:
        logger.error(f"Error updating alerts: {e}")
        raise HTTPException(status_code=500, detail="Failed to update alerts.")


@router.delete("/bulk")
async def delete_multiple_alerts(
    payload: AlertBultDeleteSchema,
    db: AsyncSession = Depends(get_db),
    user_id: int = Depends(get_current_user_id)
) -> dict[str, str]:
    try:
        service = AlertService(db)
        count = await service.bulk_delete(user_id, payload.alerts_ids)
        return {"message": f"Successfully deleted {count} alerts"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Delete error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete alerts."
        )
