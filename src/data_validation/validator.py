"""
Data Validator - Flags integrity issues in ad event data
"""
import uuid
from datetime import datetime, timedelta
from collections import defaultdict, deque
from typing import List, Dict, Any
import numpy as np
from src.models.ad_events import AdImpression, AdClick, AdConversion, ValidationAlert


class DataValidator:
    """
    Validates ad event data and flags integrity issues:
    - Bot-driven click spikes
    - Negative revenue entries
    - Anomalous patterns
    """
    
    def __init__(self, 
                 click_spike_threshold: float = 3.0,
                 time_window_seconds: int = 60,
                 min_samples: int = 10):
        """
        Initialize validator with configurable thresholds
        
        Args:
            click_spike_threshold: Standard deviations above mean to flag as spike
            time_window_seconds: Time window for tracking click rates
            min_samples: Minimum samples before flagging anomalies
        """
        self.click_spike_threshold = click_spike_threshold
        self.time_window_seconds = time_window_seconds
        self.min_samples = min_samples
        
        # Track clicks per user in time window
        self.user_clicks: Dict[str, deque] = defaultdict(lambda: deque())
        # Historical click rates for baseline
        self.historical_click_rates: List[float] = []
        
    def validate_impression(self, impression: AdImpression) -> List[ValidationAlert]:
        """Validate impression event"""
        alerts = []
        
        # Check for invalid bid amounts
        if impression.bid_amount <= 0:
            alerts.append(ValidationAlert(
                alert_id=str(uuid.uuid4()),
                alert_type="invalid_bid",
                severity="medium",
                description=f"Invalid bid amount: {impression.bid_amount}",
                affected_events=[impression.event_id],
                metadata={"bid_amount": impression.bid_amount}
            ))
        
        # Check for suspicious age values
        if impression.user_age is not None and (impression.user_age < 13 or impression.user_age > 100):
            alerts.append(ValidationAlert(
                alert_id=str(uuid.uuid4()),
                alert_type="suspicious_age",
                severity="low",
                description=f"Suspicious user age: {impression.user_age}",
                affected_events=[impression.event_id],
                metadata={"user_age": impression.user_age}
            ))
        
        return alerts
    
    def validate_click(self, click: AdClick) -> List[ValidationAlert]:
        """Validate click event and detect bot-driven click spikes"""
        alerts = []
        current_time = click.timestamp
        user_id = click.user_id
        
        # Add current click to user's history
        self.user_clicks[user_id].append(current_time)
        
        # Remove clicks outside time window
        cutoff_time = current_time - timedelta(seconds=self.time_window_seconds)
        while self.user_clicks[user_id] and self.user_clicks[user_id][0] < cutoff_time:
            self.user_clicks[user_id].popleft()
        
        # Check for bot-like behavior (too many clicks in short time)
        clicks_in_window = len(self.user_clicks[user_id])
        if clicks_in_window > 10:  # More than 10 clicks per minute is suspicious
            alerts.append(ValidationAlert(
                alert_id=str(uuid.uuid4()),
                alert_type="bot_traffic",
                severity="high",
                description=f"Possible bot traffic: {clicks_in_window} clicks in {self.time_window_seconds}s",
                affected_events=[click.event_id],
                metadata={
                    "user_id": user_id,
                    "clicks_in_window": clicks_in_window,
                    "time_window": self.time_window_seconds
                }
            ))
        
        # Track click rate for baseline
        self.historical_click_rates.append(clicks_in_window)
        
        # Detect click spikes if we have enough historical data
        if len(self.historical_click_rates) >= self.min_samples:
            mean_rate = np.mean(self.historical_click_rates[-100:])  # Last 100 samples
            std_rate = np.std(self.historical_click_rates[-100:])
            
            if std_rate > 0:
                z_score = (clicks_in_window - mean_rate) / std_rate
                if z_score > self.click_spike_threshold:
                    alerts.append(ValidationAlert(
                        alert_id=str(uuid.uuid4()),
                        alert_type="click_spike",
                        severity="medium",
                        description=f"Click rate spike detected: {z_score:.2f} std above mean",
                        affected_events=[click.event_id],
                        metadata={
                            "z_score": z_score,
                            "current_rate": clicks_in_window,
                            "mean_rate": mean_rate
                        }
                    ))
        
        return alerts
    
    def validate_conversion(self, conversion: AdConversion) -> List[ValidationAlert]:
        """Validate conversion event"""
        alerts = []
        
        # Check for negative revenue (should be caught by model validation)
        if conversion.revenue < 0:
            alerts.append(ValidationAlert(
                alert_id=str(uuid.uuid4()),
                alert_type="negative_revenue",
                severity="high",
                description=f"Negative revenue detected: {conversion.revenue}",
                affected_events=[conversion.event_id],
                metadata={"revenue": conversion.revenue}
            ))
        
        # Check for suspiciously high revenue (potential fraud)
        if conversion.revenue > 10000:  # $10k threshold
            alerts.append(ValidationAlert(
                alert_id=str(uuid.uuid4()),
                alert_type="high_revenue",
                severity="medium",
                description=f"Unusually high revenue: {conversion.revenue}",
                affected_events=[conversion.event_id],
                metadata={"revenue": conversion.revenue}
            ))
        
        return alerts
    
    def get_validation_summary(self) -> Dict[str, Any]:
        """Get summary of validation metrics"""
        return {
            "total_users_tracked": len(self.user_clicks),
            "historical_samples": len(self.historical_click_rates),
            "avg_click_rate": np.mean(self.historical_click_rates) if self.historical_click_rates else 0,
            "std_click_rate": np.std(self.historical_click_rates) if self.historical_click_rates else 0
        }
