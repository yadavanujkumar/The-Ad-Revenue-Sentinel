"""
FastAPI streaming endpoint for ad events
"""
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.responses import JSONResponse
from typing import List
import uvicorn
from datetime import datetime
import json

from src.models.ad_events import AdImpression, AdClick, AdConversion, ValidationAlert
from src.data_validation.validator import DataValidator

app = FastAPI(
    title="Ad Revenue Sentinel API",
    description="Real-time ad event ingestion and validation",
    version="1.0.0"
)

# Initialize data validator
validator = DataValidator(
    click_spike_threshold=3.0,
    time_window_seconds=60,
    min_samples=10
)

# In-memory storage for demo (use proper DB in production)
impressions_store = []
clicks_store = []
conversions_store = []
alerts_store = []


@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "Ad Revenue Sentinel",
        "timestamp": datetime.utcnow().isoformat()
    }


@app.post("/events/impression", response_model=dict)
async def ingest_impression(impression: AdImpression):
    """
    Ingest ad impression event
    """
    try:
        # Validate impression
        alerts = validator.validate_impression(impression)
        
        # Store impression
        impressions_store.append(impression.dict())
        
        # Store alerts if any
        if alerts:
            for alert in alerts:
                alerts_store.append(alert.dict())
        
        return {
            "status": "success",
            "event_id": impression.event_id,
            "alerts": [alert.dict() for alert in alerts],
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/events/click", response_model=dict)
async def ingest_click(click: AdClick):
    """
    Ingest ad click event
    """
    try:
        # Validate click
        alerts = validator.validate_click(click)
        
        # Store click
        clicks_store.append(click.dict())
        
        # Store alerts if any
        if alerts:
            for alert in alerts:
                alerts_store.append(alert.dict())
        
        return {
            "status": "success",
            "event_id": click.event_id,
            "alerts": [alert.dict() for alert in alerts],
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/events/conversion", response_model=dict)
async def ingest_conversion(conversion: AdConversion):
    """
    Ingest ad conversion event
    """
    try:
        # Validate conversion
        alerts = validator.validate_conversion(conversion)
        
        # Store conversion
        conversions_store.append(conversion.dict())
        
        # Store alerts if any
        if alerts:
            for alert in alerts:
                alerts_store.append(alert.dict())
        
        return {
            "status": "success",
            "event_id": conversion.event_id,
            "alerts": [alert.dict() for alert in alerts],
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/alerts", response_model=List[dict])
async def get_alerts(severity: str = None, limit: int = 100):
    """
    Get validation alerts
    """
    filtered_alerts = alerts_store
    
    if severity:
        filtered_alerts = [a for a in filtered_alerts if a.get('severity') == severity]
    
    return filtered_alerts[-limit:]


@app.get("/stats")
async def get_stats():
    """
    Get system statistics
    """
    return {
        "total_impressions": len(impressions_store),
        "total_clicks": len(clicks_store),
        "total_conversions": len(conversions_store),
        "total_alerts": len(alerts_store),
        "click_through_rate": len(clicks_store) / len(impressions_store) if impressions_store else 0,
        "conversion_rate": len(conversions_store) / len(clicks_store) if clicks_store else 0,
        "validation_summary": validator.get_validation_summary(),
        "timestamp": datetime.utcnow().isoformat()
    }


@app.get("/events/impressions")
async def get_impressions(limit: int = 100):
    """Get recent impressions"""
    return impressions_store[-limit:]


@app.get("/events/clicks")
async def get_clicks(limit: int = 100):
    """Get recent clicks"""
    return clicks_store[-limit:]


@app.get("/events/conversions")
async def get_conversions(limit: int = 100):
    """Get recent conversions"""
    return conversions_store[-limit:]


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
