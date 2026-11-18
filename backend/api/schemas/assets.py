from pydantic import BaseModel, ConfigDict
from helpers.enums import AlertStatus, ConditionEnum


class AssetSchema(BaseModel):
    symbol: str
    name: str | None = None
    sector: str | None = None
    industry: str | None = None
    exchange: str | None = None
    price: float | None = None

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
    user_alerts: list[AssetAlertPreview] | None = None

    model_config = ConfigDict(from_attributes=True)
