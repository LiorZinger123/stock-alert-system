from typing import Optional
from pydantic import BaseModel, ConfigDict, Field
from helpers.enums import AlertStatus


class AssetSchema(BaseModel):
    symbol: str
    name: Optional[str] = None
    sector: Optional[str] = None
    industry: Optional[str] = None
    exchange: Optional[str] = None
    current_price: Optional[float] = Field(default=None, exclude_none=True)

    model_config = ConfigDict(from_attributes=True)


class AssetAlertPreview(BaseModel):
    id: int
    target_price: float
    condition: str
    status: AlertStatus


class AssetDetailSchema(BaseModel):
    symbol: str
    name: str
    current_price: Optional[float] = Field(default=None, exclude_none=True)
    user_alert: Optional[AssetAlertPreview] = None

    model_config = ConfigDict(from_attributes=True)
