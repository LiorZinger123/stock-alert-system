from typing import Optional
from pydantic import BaseModel, ConfigDict, Field
from helpers.enums import AlertStatus, ConditionEnum


class AssetSchema(BaseModel):
    symbol: str
    name: Optional[str] = None
    sector: Optional[str] = None
    industry: Optional[str] = None
    exchange: Optional[str] = None
    price: Optional[float] = None

    model_config = ConfigDict(from_attributes=True)


class AssetMetadata(BaseModel):
    name: str | None = None


class AssetAlertPreview(BaseModel):
    id: int
    target_price: float
    condition: ConditionEnum
    status: AlertStatus

    model_config = ConfigDict(from_attributes=True)


class AssetDetails(AssetSchema):
    user_alerts: Optional[list[AssetAlertPreview]] = None

    model_config = ConfigDict(from_attributes=True)
