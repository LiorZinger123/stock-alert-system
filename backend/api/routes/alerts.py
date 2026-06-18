import logging
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import APIRouter,HTTPException, status, Depends, HTTPException
from core.database import get_db
from services.alert_service import AlertService
from services.asset_service import AssetService
from helpers.security import get_current_user_id
from api.schemas.alerts import AlertReadSchema, AlertCreateSchema, AlertUpdateSchema


router = APIRouter()
logger = logging.getLogger(__name__)


@router.get("", response_model=list[AlertReadSchema])
async def get_user_alerts(
    offset: int,
    limit: int,
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
) -> list[AlertReadSchema]:
    try:
        asset_service = AssetService(db)
        alert_service = AlertService(db, asset_service)
        return await alert_service.get_all_by_user(user_id, offset, limit)
    except Exception as e:
        logger.error(f"Error fetching alerts: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve alerts."
        )


@router.post("", response_model=AlertReadSchema, status_code=status.HTTP_201_CREATED)
async def create_alert(
    new_alert: AlertCreateSchema,
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
) -> AlertReadSchema:
    try:
        asset_service = AssetService(db)
        alert_service = AlertService(db, asset_service)
        return await alert_service.create_new_alert(user_id, new_alert)
    except HTTPException:
        raise
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


@router.put("/{alert_id}", response_model=AlertReadSchema)
async def update_alert(
    alert_id: int,
    update_data: AlertUpdateSchema,
    db: AsyncSession = Depends(get_db),
    user_id: int = Depends(get_current_user_id)
) -> AlertReadSchema:
    try:
        asset_service = AssetService(db)
        alert_service = AlertService(db, asset_service)
        return await alert_service.update_alert(user_id, alert_id, update_data)
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


@router.delete("/{alert_id}")
async def delete_alert(
    alert_id: str,
    db: AsyncSession = Depends(get_db),
    user_id: int = Depends(get_current_user_id)
) -> dict[str, str]:
    try:
        try:
            alert_id_int = int(alert_id)
        except ValueError:
            raise HTTPException(status_code=400, detail="Alert ID must be an integer.")

        asset_service = AssetService(db)
        alert_service = AlertService(db, asset_service)
        await alert_service.delete_alert(user_id, alert_id_int)
        return {"message": "Successfully deleted alert"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Delete error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete alert."
        )
