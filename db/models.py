from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from sqlalchemy import Column, Integer, String, Float, ForeignKey, Boolean, DateTime, Enum
from core.database import Base
from helpers.enums import ConditionEnum, AlertStatus


class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    password = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    alerts = relationship("Alert", back_populates="owner")


class Asset(Base):
    __tablename__ = "assets"
    
    id = Column(Integer, primary_key=True, index=True)
    symbol = Column(String, unique=True, index=True, nullable=False)
    name = Column(String, nullable=True)
    sector = Column(String, nullable=True)
    industry = Column(String, nullable=True)
    exchange = Column(String, nullable=True)
    last_updated = Column(DateTime(timezone=True), onupdate=func.now(), server_default=func.now())


class Alert(Base):
    __tablename__ = "alerts"
    
    id = Column(Integer, primary_key=True, index=True)
    target_price = Column(Float, nullable=False)
    condition = Column(Enum(ConditionEnum), nullable=False)
    created_at = Column(DateTime(timezone=True), default=func.now(), server_default=func.now())
    status = Column(Enum(AlertStatus), default=AlertStatus.ACTIVE)
    last_triggered_at = Column(DateTime, nullable=True)
    
    user_id = Column(Integer, ForeignKey("users.id"))
    asset_id = Column(Integer, ForeignKey("assets.id"))
    
    owner = relationship("User", back_populates="alerts")
    asset = relationship("Asset")
