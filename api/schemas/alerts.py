from typing import Optional
from datetime import datetime
from pydantic import BaseModel, ConfigDict, field_validator
from .assets import AssetSchema
from helpers.enums import ConditionEnum, AlertStatus


class AlertReadSchema(BaseModel):
    id: int
    target_price: float
    condition: ConditionEnum
    status: AlertStatus
    created_at: Optional[datetime] = None
    triggered_at: Optional[datetime] = None
    asset: AssetSchema      
    
    model_config = ConfigDict(from_attributes=True)

    @field_validator('target_price', mode='before')
    @classmethod
    def round_price(cls, v):
        return round(float(v), 2)


class AlertCreateSchema(BaseModel):
    symbol: str
    target_price: float
    condition: ConditionEnum

    @field_validator('target_price', mode='before')
    @classmethod
    def round_price(cls, v):
        return round(float(v), 2)


class AlertBulkCreateSchema(BaseModel):
    alerts: list[AlertCreateSchema]


class AlertUpdateSchema(BaseModel):
    id: int
    target_price: Optional[float] = None
    condition: Optional[ConditionEnum] = None
    status: Optional[AlertStatus] = None

    @field_validator('target_price', mode='before')
    @classmethod
    def round_price(cls, v):
        return round(float(v), 2) if v is not None else v


class AlertBulkUpdateSchema(BaseModel):
    alerts: list[AlertUpdateSchema]


class AlertBultDeleteSchema(BaseModel):
    alerts_ids: list[int]