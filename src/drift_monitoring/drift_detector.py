"""
Drift Monitoring using EvidentlyAI
Monitors shifts in audience demographics and behavioral patterns
"""
import pandas as pd
import numpy as np
from typing import Dict, Any, List, Optional
from datetime import datetime
import json

try:
    from evidently.report import Report
    from evidently.metric_preset import DataDriftPreset, DataQualityPreset
    from evidently.metrics import DataDriftTable, DatasetDriftMetric
    EVIDENTLY_AVAILABLE = True
except ImportError:
    EVIDENTLY_AVAILABLE = False


class DriftMonitor:
    """
    Monitor data drift in ad event streams
    Detects shifts in user demographics, device types, etc.
    """
    
    def __init__(self, drift_threshold: float = 0.5):
        """
        Initialize drift monitor
        
        Args:
            drift_threshold: Threshold for drift detection (0-1)
        """
        self.drift_threshold = drift_threshold
        self.baseline_data = None
        self.baseline_stats = {}
        self.drift_alerts = []
        
    def set_baseline(self, data: pd.DataFrame):
        """
        Set baseline data for drift detection
        
        Args:
            data: DataFrame with baseline ad event data
        """
        self.baseline_data = data.copy()
        
        # Calculate baseline statistics
        self.baseline_stats = {
            'user_age': {
                'mean': data['user_age'].mean() if 'user_age' in data.columns else None,
                'std': data['user_age'].std() if 'user_age' in data.columns else None,
                'median': data['user_age'].median() if 'user_age' in data.columns else None
            },
            'device_type': {
                'distribution': data['device_type'].value_counts(normalize=True).to_dict() if 'device_type' in data.columns else {}
            },
            'region': {
                'distribution': data['region'].value_counts(normalize=True).to_dict() if 'region' in data.columns else {}
            },
            'bid_amount': {
                'mean': data['bid_amount'].mean() if 'bid_amount' in data.columns else None,
                'std': data['bid_amount'].std() if 'bid_amount' in data.columns else None
            },
            'timestamp': datetime.utcnow().isoformat(),
            'sample_size': len(data)
        }
        
    def detect_drift(self, current_data: pd.DataFrame) -> Dict[str, Any]:
        """
        Detect drift between baseline and current data
        
        Args:
            current_data: DataFrame with current ad event data
            
        Returns:
            Dictionary with drift detection results
        """
        if self.baseline_data is None or self.baseline_data.empty:
            return {
                "error": "No baseline data set. Call set_baseline() first.",
                "drift_detected": False
            }
        
        if current_data.empty:
            return {
                "error": "Current data is empty",
                "drift_detected": False
            }
        
        drift_results = {
            "drift_detected": False,
            "drifted_features": [],
            "drift_scores": {},
            "timestamp": datetime.utcnow().isoformat(),
            "current_sample_size": len(current_data),
            "baseline_sample_size": len(self.baseline_data)
        }
        
        # Use EvidentlyAI if available
        if EVIDENTLY_AVAILABLE:
            try:
                # Prepare data for Evidently
                common_columns = list(set(self.baseline_data.columns) & set(current_data.columns))
                
                # Select numeric and categorical columns
                numeric_cols = self.baseline_data[common_columns].select_dtypes(include=[np.number]).columns.tolist()
                categorical_cols = self.baseline_data[common_columns].select_dtypes(include=['object']).columns.tolist()
                
                # Remove timestamp columns
                numeric_cols = [c for c in numeric_cols if 'timestamp' not in c.lower()]
                categorical_cols = [c for c in categorical_cols if 'timestamp' not in c.lower()]
                
                if numeric_cols or categorical_cols:
                    # Create Evidently report
                    report = Report(metrics=[
                        DataDriftPreset(),
                    ])
                    
                    report.run(
                        reference_data=self.baseline_data[common_columns],
                        current_data=current_data[common_columns]
                    )
                    
                    # Extract results
                    report_dict = report.as_dict()
                    
                    # Parse drift results
                    if 'metrics' in report_dict:
                        for metric in report_dict['metrics']:
                            if metric.get('metric') == 'DatasetDriftMetric':
                                result = metric.get('result', {})
                                drift_results['drift_detected'] = result.get('dataset_drift', False)
                                drift_results['drift_share'] = result.get('drift_share', 0)
                                
                                # Get per-feature drift
                                if 'drift_by_columns' in result:
                                    for col, drift_info in result['drift_by_columns'].items():
                                        if drift_info.get('drift_detected', False):
                                            drift_results['drifted_features'].append(col)
                                            drift_results['drift_scores'][col] = drift_info.get('drift_score', 0)
                
            except Exception as e:
                drift_results['evidently_error'] = str(e)
        
        # Fallback: Manual drift detection using statistical tests
        drift_results.update(self._manual_drift_detection(current_data))
        
        # Create alert if drift detected
        if drift_results['drift_detected']:
            alert = {
                'alert_id': f"drift_{datetime.utcnow().timestamp()}",
                'timestamp': datetime.utcnow().isoformat(),
                'alert_type': 'data_drift',
                'severity': 'high' if len(drift_results['drifted_features']) > 3 else 'medium',
                'description': f"Data drift detected in {len(drift_results['drifted_features'])} features",
                'drifted_features': drift_results['drifted_features'],
                'drift_scores': drift_results['drift_scores']
            }
            self.drift_alerts.append(alert)
        
        return drift_results
    
    def _manual_drift_detection(self, current_data: pd.DataFrame) -> Dict[str, Any]:
        """
        Manual drift detection using statistical methods
        """
        results = {
            'manual_drift_checks': {}
        }
        
        # Check user age drift
        if 'user_age' in current_data.columns and self.baseline_stats['user_age']['mean'] is not None:
            current_age_mean = current_data['user_age'].mean()
            baseline_age_mean = self.baseline_stats['user_age']['mean']
            baseline_age_std = self.baseline_stats['user_age']['std']
            
            if baseline_age_std > 0:
                age_drift_score = abs(current_age_mean - baseline_age_mean) / baseline_age_std
                results['manual_drift_checks']['user_age'] = {
                    'drift_score': float(age_drift_score),
                    'current_mean': float(current_age_mean),
                    'baseline_mean': float(baseline_age_mean),
                    'drifted': age_drift_score > 2.0  # 2 sigma threshold
                }
                
                if age_drift_score > 2.0 and 'user_age' not in results.get('drifted_features', []):
                    if 'drifted_features' not in results:
                        results['drifted_features'] = []
                    results['drifted_features'].append('user_age')
                    results['drift_detected'] = True
        
        # Check device type distribution drift
        if 'device_type' in current_data.columns and self.baseline_stats['device_type']['distribution']:
            current_dist = current_data['device_type'].value_counts(normalize=True).to_dict()
            baseline_dist = self.baseline_stats['device_type']['distribution']
            
            # Calculate distribution shift
            shift_score = 0
            for device_type in set(list(current_dist.keys()) + list(baseline_dist.keys())):
                current_pct = current_dist.get(device_type, 0)
                baseline_pct = baseline_dist.get(device_type, 0)
                shift_score += abs(current_pct - baseline_pct)
            
            results['manual_drift_checks']['device_type'] = {
                'drift_score': float(shift_score),
                'current_distribution': current_dist,
                'baseline_distribution': baseline_dist,
                'drifted': shift_score > 0.3  # 30% distribution shift
            }
            
            if shift_score > 0.3 and 'device_type' not in results.get('drifted_features', []):
                if 'drifted_features' not in results:
                    results['drifted_features'] = []
                results['drifted_features'].append('device_type')
                results['drift_detected'] = True
        
        return results
    
    def get_drift_alerts(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Get recent drift alerts"""
        return self.drift_alerts[-limit:]
    
    def get_baseline_summary(self) -> Dict[str, Any]:
        """Get summary of baseline data"""
        return {
            "baseline_set": self.baseline_data is not None,
            "baseline_stats": self.baseline_stats,
            "total_alerts": len(self.drift_alerts)
        }
