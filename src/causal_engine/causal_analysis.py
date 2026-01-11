"""
Causal Investigation Engine using EconML and DoWhy
Performs counterfactual analysis on ad revenue data
"""
import pandas as pd
import numpy as np
from typing import Dict, Any, Optional, List
from dowhy import CausalModel
from econml.dml import CausalForestDML
from econml.inference import BootstrapInference


class CausalEngine:
    """
    Causal inference engine for ad revenue analysis
    Answers questions like:
    - "If we hadn't increased the bid in Mumbai, what would revenue have been?"
    - "Did revenue drop because of the new creative or external factors?"
    """
    
    def __init__(self):
        self.model = None
        self.causal_model = None
        
    def prepare_data(self, 
                     impressions: List[Dict],
                     clicks: List[Dict],
                     conversions: List[Dict]) -> pd.DataFrame:
        """
        Prepare data for causal analysis by merging events
        """
        # Convert to DataFrames
        df_impressions = pd.DataFrame(impressions)
        df_clicks = pd.DataFrame(clicks)
        df_conversions = pd.DataFrame(conversions)
        
        # Merge impressions and clicks
        if not df_clicks.empty and not df_impressions.empty:
            df_impressions['clicked'] = df_impressions['event_id'].isin(
                df_clicks['impression_id']
            ).astype(int)
        else:
            df_impressions['clicked'] = 0
        
        # Merge with conversions to get revenue
        if not df_conversions.empty and not df_impressions.empty:
            conversion_revenue = df_conversions.groupby('impression_id')['revenue'].sum().reset_index()
            df_impressions = df_impressions.merge(
                conversion_revenue, 
                left_on='event_id',
                right_on='impression_id',
                how='left'
            )
        
        # Fill NaN revenue with 0
        if 'revenue' in df_impressions.columns:
            df_impressions['revenue'] = df_impressions['revenue'].fillna(0)
        else:
            df_impressions['revenue'] = 0
        
        return df_impressions
    
    def counterfactual_bid_analysis(self, 
                                    data: pd.DataFrame,
                                    region: str,
                                    treatment_column: str = 'bid_amount',
                                    outcome_column: str = 'revenue') -> Dict[str, Any]:
        """
        Perform counterfactual analysis on bid changes
        
        Args:
            data: DataFrame with ad event data
            region: Region to analyze (e.g., "Mumbai")
            treatment_column: Column representing treatment (e.g., bid_amount)
            outcome_column: Column representing outcome (e.g., revenue)
            
        Returns:
            Dictionary with causal effect estimates
        """
        if data.empty or len(data) < 10:
            return {
                "error": "Insufficient data for causal analysis",
                "samples": len(data)
            }
        
        # Filter for the region
        region_data = data[data['region'] == region].copy()
        
        if region_data.empty or len(region_data) < 10:
            return {
                "error": f"Insufficient data for region: {region}",
                "samples": len(region_data)
            }
        
        # Create binary treatment (high vs low bid)
        median_bid = region_data[treatment_column].median()
        region_data['treatment'] = (region_data[treatment_column] > median_bid).astype(int)
        
        # Prepare features for confounders
        feature_columns = []
        if 'user_age' in region_data.columns:
            region_data['user_age_filled'] = region_data['user_age'].fillna(region_data['user_age'].median())
            feature_columns.append('user_age_filled')
        
        # Device type encoding
        if 'device_type' in region_data.columns:
            region_data['device_mobile'] = (region_data['device_type'] == 'mobile').astype(int)
            region_data['device_desktop'] = (region_data['device_type'] == 'desktop').astype(int)
            feature_columns.extend(['device_mobile', 'device_desktop'])
        
        if not feature_columns:
            feature_columns = ['bid_amount']  # Fallback
        
        try:
            # Use DoWhy for causal analysis
            causal_model = CausalModel(
                data=region_data,
                treatment='treatment',
                outcome=outcome_column,
                common_causes=feature_columns
            )
            
            # Identify causal effect
            identified_estimand = causal_model.identify_effect(proceed_when_unidentifiable=True)
            
            # Estimate effect
            estimate = causal_model.estimate_effect(
                identified_estimand,
                method_name="backdoor.linear_regression"
            )
            
            # Calculate counterfactual
            treated_revenue = region_data[region_data['treatment'] == 1][outcome_column].mean()
            control_revenue = region_data[region_data['treatment'] == 0][outcome_column].mean()
            
            return {
                "region": region,
                "treatment": "High Bid",
                "control": "Low Bid",
                "causal_effect": float(estimate.value),
                "treated_avg_revenue": float(treated_revenue),
                "control_avg_revenue": float(control_revenue),
                "counterfactual_question": f"If we hadn't increased bids in {region}, revenue would have been approximately ${control_revenue:.2f} instead of ${treated_revenue:.2f}",
                "revenue_impact": float(treated_revenue - control_revenue),
                "sample_size": len(region_data),
                "treated_samples": int(region_data['treatment'].sum()),
                "control_samples": int((1 - region_data['treatment']).sum())
            }
            
        except Exception as e:
            return {
                "error": f"Causal analysis failed: {str(e)}",
                "region": region,
                "sample_size": len(region_data)
            }
    
    def creative_effect_analysis(self,
                                 data: pd.DataFrame,
                                 creative_column: str = 'ad_id',
                                 outcome_column: str = 'revenue') -> Dict[str, Any]:
        """
        Analyze if revenue drop was due to new creative or external factors
        
        Args:
            data: DataFrame with ad event data
            creative_column: Column identifying different creatives
            outcome_column: Outcome to analyze
            
        Returns:
            Dictionary with creative effect analysis
        """
        if data.empty or len(data) < 10:
            return {
                "error": "Insufficient data for creative analysis",
                "samples": len(data)
            }
        
        try:
            # Calculate revenue by creative
            creative_revenue = data.groupby(creative_column).agg({
                outcome_column: ['mean', 'sum', 'count']
            }).reset_index()
            
            creative_revenue.columns = ['creative_id', 'avg_revenue', 'total_revenue', 'impressions']
            creative_revenue = creative_revenue.sort_values('total_revenue', ascending=False)
            
            # Calculate overall statistics
            overall_avg = data[outcome_column].mean()
            
            results = {
                "overall_avg_revenue": float(overall_avg),
                "creatives": []
            }
            
            for _, row in creative_revenue.iterrows():
                creative_data = {
                    "creative_id": row['creative_id'],
                    "avg_revenue": float(row['avg_revenue']),
                    "total_revenue": float(row['total_revenue']),
                    "impressions": int(row['impressions']),
                    "performance_vs_baseline": float(row['avg_revenue'] - overall_avg),
                    "performance_pct": float((row['avg_revenue'] / overall_avg - 1) * 100) if overall_avg > 0 else 0
                }
                results["creatives"].append(creative_data)
            
            return results
            
        except Exception as e:
            return {
                "error": f"Creative analysis failed: {str(e)}",
                "sample_size": len(data)
            }
    
    def campaign_uplift_analysis(self,
                                 data: pd.DataFrame,
                                 campaign_id: str,
                                 baseline_campaign_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Calculate campaign uplift vs baseline
        
        Args:
            data: DataFrame with ad event data
            campaign_id: Campaign to analyze
            baseline_campaign_id: Baseline campaign for comparison
            
        Returns:
            Dictionary with uplift analysis
        """
        if data.empty:
            return {"error": "No data available"}
        
        try:
            campaign_data = data[data['campaign_id'] == campaign_id]
            
            if campaign_data.empty:
                return {"error": f"No data for campaign: {campaign_id}"}
            
            campaign_metrics = {
                "campaign_id": campaign_id,
                "total_impressions": len(campaign_data),
                "total_clicks": int(campaign_data['clicked'].sum()) if 'clicked' in campaign_data.columns else 0,
                "total_revenue": float(campaign_data['revenue'].sum()),
                "avg_revenue_per_impression": float(campaign_data['revenue'].mean()),
                "click_through_rate": float(campaign_data['clicked'].mean()) if 'clicked' in campaign_data.columns else 0
            }
            
            # Compare with baseline if provided
            if baseline_campaign_id:
                baseline_data = data[data['campaign_id'] == baseline_campaign_id]
                
                if not baseline_data.empty:
                    baseline_revenue = baseline_data['revenue'].mean()
                    campaign_revenue = campaign_data['revenue'].mean()
                    
                    campaign_metrics["baseline_campaign_id"] = baseline_campaign_id
                    campaign_metrics["baseline_avg_revenue"] = float(baseline_revenue)
                    campaign_metrics["uplift_absolute"] = float(campaign_revenue - baseline_revenue)
                    campaign_metrics["uplift_percentage"] = float((campaign_revenue / baseline_revenue - 1) * 100) if baseline_revenue > 0 else 0
                    campaign_metrics["uplift_interpretation"] = f"Campaign shows {campaign_metrics['uplift_percentage']:.2f}% uplift vs baseline"
            
            return campaign_metrics
            
        except Exception as e:
            return {
                "error": f"Campaign analysis failed: {str(e)}",
                "campaign_id": campaign_id
            }
