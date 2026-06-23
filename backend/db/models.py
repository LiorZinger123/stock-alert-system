from datetime import datetime
from typing import List, Optional
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import ForeignKey, String, Float, DateTime, Enum, func
from core.database import Base
from helpers.enums import ConditionEnum, AlertStatus


class User(Base):
    __tablename__ = "users"
    
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    username: Mapped[str] = mapped_column(String, unique=True, index=True)
    email: Mapped[str] = mapped_column(String, unique=True, index=True)
    password: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    provider: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    provider_id: Mapped[Optional[str]] = mapped_column(String, nullable=True, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    alerts: Mapped[List["Alert"]] = relationship(back_populates="owner")


class Asset(Base):
    __tablename__ = "assets"
    
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    symbol: Mapped[str] = mapped_column(String, unique=True, index=True)
    name: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    sector: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    industry: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    exchange: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    price: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    last_updated: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), 
        onupdate=func.now(), 
        server_default=func.now()
    )


class Alert(Base):
    __tablename__ = "alerts"
    
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    target_price: Mapped[float] = mapped_column(Float)
    condition: Mapped[ConditionEnum] = mapped_column(Enum(ConditionEnum))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    status: Mapped[AlertStatus] = mapped_column(Enum(AlertStatus), default=AlertStatus.ACTIVE)
    triggered_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    triggered_price: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    asset_id: Mapped[int] = mapped_column(ForeignKey("assets.id"))
    
    owner: Mapped["User"] = relationship(back_populates="alerts")
    asset: Mapped["Asset"] = relationship()
