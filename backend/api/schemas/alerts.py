from datetime import datetime
from typing import Optional, Literal
from pydantic import BaseModel, ConfigDict, field_validator, Field
from .assets import AssetSchema
from helpers.validators import round_price_helper
from helpers.enums import ConditionEnum, AlertStatus


class AlertReadSchema(BaseModel):
    id: int
    target_price: float
    condition: ConditionEnum
    status: AlertStatus
    created_at: Optional[datetime] = None
    triggered_at: Optional[datetime] = None
    triggered_price: Optional[float] = Field(default=None, exclude=None)
    current_price: Optional[float] = None
    asset: AssetSchema      
    
    model_config = ConfigDict(from_attributes=True)

    @field_validator('target_price', mode='before')
    @classmethod
    def round_target_price(cls, v): 
        return round_price_helper(v)


class AlertCreateSchema(BaseModel):
    symbol: str
    target_price: float = Field(gt=0)
    condition: ConditionEnum

    model_config = ConfigDict(extra='forbid')

    @field_validator('target_price', mode='before')
    @classmethod
    def round_target_price(cls, v): 
        return round_price_helper(v)


class AlertUpdateSchema(BaseModel):
    target_price: Optional[float] = Field(None, gt=0)
    condition: Optional[ConditionEnum] = None
    status: Optional[Literal[AlertStatus.ACTIVE, AlertStatus.INACTIVE]] = None

    model_config = ConfigDict(extra='forbid')

    @field_validator('target_price', mode='before')
    @classmethod
    def round_target_price(cls, v): 
        return round_price_helper(v)
