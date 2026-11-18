from typing import Literal
from datetime import datetime
from pydantic import BaseModel, ConfigDict, field_validator, Field
from .assets import AssetSchema
from helpers.validators import round_price_helper
from helpers.enums import ConditionEnum, AlertStatus


class AlertReadSchema(BaseModel):
    id: int
    target_price: float
    condition: ConditionEnum
    status: AlertStatus
    created_at: datetime | None = None
    triggered_at: datetime | None = None
    triggered_price: float | None = Field(default=None, exclude=None)
    asset: AssetSchema      
    
    model_config = ConfigDict(from_attributes=True)

    @field_validator('target_price', mode='before')
    @classmethod
    def round_target_price(cls, v): 
        return round_price_helper(v)


class AlertCreateSchema(BaseModel):
    symbol: str
    name: str
    target_price: float = Field(gt=0)
    condition: ConditionEnum

    model_config = ConfigDict(extra='forbid')

    @field_validator('target_price', mode='before')
    @classmethod
    def round_target_price(cls, v): 
        return round_price_helper(v)


class AlertUpdateSchema(BaseModel):
    symbol: str
    target_price: float | None = Field(None, gt=0)
    condition: ConditionEnum | None = None
    status: Literal[AlertStatus.ACTIVE, AlertStatus.INACTIVE] | None = None

    model_config = ConfigDict(extra='forbid')

    @field_validator('target_price', mode='before')
    @classmethod
    def round_target_price(cls, v): 
        return round_price_helper(v)
