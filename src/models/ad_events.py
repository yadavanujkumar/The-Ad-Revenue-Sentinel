"""
Data models for ad events
"""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, validator


class AdImpression(BaseModel):
    """Model for ad impression events"""
    event_id: str = Field(..., description="Unique event identifier")
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    ad_id: str = Field(..., description="Ad identifier")
    campaign_id: str = Field(..., description="Campaign identifier")
    user_id: str = Field(..., description="User identifier")
    user_age: Optional[int] = Field(None, ge=0, le=120)
    device_type: str = Field(..., description="Device type (mobile, desktop, tablet)")
    region: str = Field(..., description="Geographic region")
    platform: str = Field(..., description="Platform (web, app)")
    bid_amount: float = Field(..., ge=0, description="Bid amount in USD")
    
    @validator('device_type')
    def validate_device_type(cls, v):
        allowed = ['mobile', 'desktop', 'tablet']
        if v.lower() not in allowed:
            raise ValueError(f"Device type must be one of {allowed}")
        return v.lower()


class AdClick(BaseModel):
    """Model for ad click events"""
    event_id: str = Field(..., description="Unique event identifier")
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    impression_id: str = Field(..., description="Related impression ID")
    ad_id: str = Field(..., description="Ad identifier")
    campaign_id: str = Field(..., description="Campaign identifier")
    user_id: str = Field(..., description="User identifier")
    user_age: Optional[int] = Field(None, ge=0, le=120)
    device_type: str = Field(..., description="Device type")
    region: str = Field(..., description="Geographic region")
    click_position: Optional[int] = Field(None, description="Click position")
    
    @validator('device_type')
    def validate_device_type(cls, v):
        allowed = ['mobile', 'desktop', 'tablet']
        if v.lower() not in allowed:
            raise ValueError(f"Device type must be one of {allowed}")
        return v.lower()


class AdConversion(BaseModel):
    """Model for ad conversion events"""
    event_id: str = Field(..., description="Unique event identifier")
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    click_id: str = Field(..., description="Related click ID")
    impression_id: str = Field(..., description="Related impression ID")
    ad_id: str = Field(..., description="Ad identifier")
    campaign_id: str = Field(..., description="Campaign identifier")
    user_id: str = Field(..., description="User identifier")
    revenue: float = Field(..., description="Revenue generated in USD")
    conversion_type: str = Field(..., description="Type of conversion (purchase, signup, etc.)")
    
    @validator('revenue')
    def validate_revenue(cls, v):
        if v < 0:
            raise ValueError("Revenue cannot be negative")
        return v


class ValidationAlert(BaseModel):
    """Model for data validation alerts"""
    alert_id: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    alert_type: str  # "bot_traffic", "negative_revenue", "anomaly"
    severity: str  # "low", "medium", "high"
    description: str
    affected_events: list[str]
    metadata: dict = {}
