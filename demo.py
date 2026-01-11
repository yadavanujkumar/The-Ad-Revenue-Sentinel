"""
Example script demonstrating the Ad Revenue Sentinel platform
"""
import sys
sys.path.append('/home/runner/work/The-Ad-Revenue-Sentinel/The-Ad-Revenue-Sentinel')

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import uuid

from src.models.ad_events import AdImpression, AdClick, AdConversion
from src.data_validation.validator import DataValidator
from src.causal_engine.causal_analysis import CausalEngine
from src.drift_monitoring.drift_detector import DriftMonitor
from src.nlp_query.query_engine import NLQueryEngine


def generate_sample_events(num_impressions=200):
    """Generate sample ad events for demonstration"""
    print(f"Generating {num_impressions} sample impressions...")
    
    regions = ['Mumbai', 'Delhi', 'Bangalore', 'Chennai', 'Kolkata']
    devices = ['mobile', 'desktop', 'tablet']
    campaigns = ['summer_campaign', 'winter_sale', 'baseline_campaign']
    
    impressions = []
    clicks = []
    conversions = []
    
    for i in range(num_impressions):
        # Create impression
        event_id = str(uuid.uuid4())
        timestamp = datetime.utcnow() - timedelta(minutes=np.random.randint(0, 1440))
        
        impression = AdImpression(
            event_id=event_id,
            timestamp=timestamp,
            ad_id=f'ad_{np.random.randint(1, 10)}',
            campaign_id=np.random.choice(campaigns),
            user_id=f'user_{np.random.randint(1, 500)}',
            user_age=int(np.random.normal(35, 12)),
            device_type=np.random.choice(devices, p=[0.6, 0.3, 0.1]),
            region=np.random.choice(regions),
            platform=np.random.choice(['web', 'app'], p=[0.4, 0.6]),
            bid_amount=float(np.random.uniform(0.5, 5.0))
        )
        impressions.append(impression)
        
        # Generate click (25% CTR)
        if np.random.random() < 0.25:
            click = AdClick(
                event_id=str(uuid.uuid4()),
                timestamp=timestamp + timedelta(seconds=np.random.randint(1, 300)),
                impression_id=event_id,
                ad_id=impression.ad_id,
                campaign_id=impression.campaign_id,
                user_id=impression.user_id,
                user_age=impression.user_age,
                device_type=impression.device_type,
                region=impression.region,
                click_position=np.random.randint(1, 10)
            )
            clicks.append(click)
            
            # Generate conversion (8% of clicks)
            if np.random.random() < 0.08:
                conversion = AdConversion(
                    event_id=str(uuid.uuid4()),
                    timestamp=timestamp + timedelta(seconds=np.random.randint(300, 3600)),
                    click_id=click.event_id,
                    impression_id=event_id,
                    ad_id=impression.ad_id,
                    campaign_id=impression.campaign_id,
                    user_id=impression.user_id,
                    revenue=float(np.random.uniform(10, 150)),
                    conversion_type=np.random.choice(['purchase', 'signup'])
                )
                conversions.append(conversion)
    
    print(f"✓ Generated {len(impressions)} impressions, {len(clicks)} clicks, {len(conversions)} conversions")
    return impressions, clicks, conversions


def demo_validation(impressions, clicks, conversions):
    """Demonstrate data validation"""
    print("\n" + "="*60)
    print("DEMO 1: Data Validation")
    print("="*60)
    
    validator = DataValidator()
    all_alerts = []
    
    print("Validating impressions...")
    for imp in impressions:
        alerts = validator.validate_impression(imp)
        all_alerts.extend(alerts)
    
    print("Validating clicks...")
    for clk in clicks:
        alerts = validator.validate_click(clk)
        all_alerts.extend(alerts)
    
    print("Validating conversions...")
    for conv in conversions:
        alerts = validator.validate_conversion(conv)
        all_alerts.extend(alerts)
    
    print(f"\n✓ Total alerts generated: {len(all_alerts)}")
    
    # Show alert breakdown
    alert_types = {}
    for alert in all_alerts:
        alert_type = alert.alert_type
        alert_types[alert_type] = alert_types.get(alert_type, 0) + 1
    
    print("\nAlert breakdown:")
    for alert_type, count in alert_types.items():
        print(f"  - {alert_type}: {count}")
    
    # Show sample alerts
    if all_alerts:
        print("\nSample alert:")
        sample = all_alerts[0]
        print(f"  Type: {sample.alert_type}")
        print(f"  Severity: {sample.severity}")
        print(f"  Description: {sample.description}")
    
    return validator


def demo_causal_analysis(impressions, clicks, conversions):
    """Demonstrate causal analysis"""
    print("\n" + "="*60)
    print("DEMO 2: Causal Analysis")
    print("="*60)
    
    causal_engine = CausalEngine()
    
    # Prepare data
    print("Preparing data for causal analysis...")
    impressions_dict = [imp.model_dump() for imp in impressions]
    clicks_dict = [clk.model_dump() for clk in clicks]
    conversions_dict = [conv.model_dump() for conv in conversions]
    
    data = causal_engine.prepare_data(impressions_dict, clicks_dict, conversions_dict)
    print(f"✓ Prepared {len(data)} events")
    
    # Counterfactual bid analysis
    print("\n--- Counterfactual Bid Analysis ---")
    region = 'Mumbai'
    print(f"Question: If we hadn't increased bids in {region}, what would revenue have been?")
    
    result = causal_engine.counterfactual_bid_analysis(data, region)
    
    if 'error' not in result:
        print(f"\n✓ Analysis complete!")
        print(f"  Treated (High Bid) Avg Revenue: ${result['treated_avg_revenue']:.2f}")
        print(f"  Control (Low Bid) Avg Revenue: ${result['control_avg_revenue']:.2f}")
        print(f"  Causal Effect: ${result['causal_effect']:.2f}")
        print(f"  Sample Size: {result['sample_size']}")
        print(f"\n  Insight: {result['counterfactual_question']}")
    else:
        print(f"  {result['error']}")
    
    # Campaign uplift analysis
    print("\n--- Campaign Uplift Analysis ---")
    campaigns = data['campaign_id'].unique()
    if len(campaigns) >= 2:
        target = campaigns[0]
        baseline = campaigns[1]
        print(f"Calculating uplift: {target} vs {baseline}")
        
        result = causal_engine.campaign_uplift_analysis(data, target, baseline)
        
        if 'error' not in result:
            print(f"\n✓ Analysis complete!")
            print(f"  Target Campaign Avg Revenue: ${result['avg_revenue_per_impression']:.2f}")
            if 'uplift_percentage' in result:
                print(f"  Baseline Campaign Avg Revenue: ${result['baseline_avg_revenue']:.2f}")
                print(f"  Uplift: {result['uplift_percentage']:.2f}%")
                print(f"\n  Insight: {result['uplift_interpretation']}")
        else:
            print(f"  {result['error']}")


def demo_drift_monitoring(impressions, clicks, conversions):
    """Demonstrate drift monitoring"""
    print("\n" + "="*60)
    print("DEMO 3: Drift Monitoring")
    print("="*60)
    
    drift_monitor = DriftMonitor()
    causal_engine = CausalEngine()
    
    # Prepare data
    impressions_dict = [imp.model_dump() for imp in impressions]
    clicks_dict = [clk.model_dump() for clk in clicks]
    conversions_dict = [conv.model_dump() for conv in conversions]
    
    data = causal_engine.prepare_data(impressions_dict, clicks_dict, conversions_dict)
    
    # Split data into baseline and current
    split_point = int(len(data) * 0.6)
    baseline_data = data[:split_point].copy()
    current_data = data[split_point:].copy()
    
    print(f"Setting baseline with {len(baseline_data)} samples...")
    drift_monitor.set_baseline(baseline_data)
    print("✓ Baseline set")
    
    # Artificially introduce drift in current data (for demonstration)
    if 'device_type' in current_data.columns:
        # Change device distribution
        mask = current_data['device_type'] == 'mobile'
        current_data.loc[mask, 'device_type'] = np.random.choice(
            ['desktop', 'tablet'], size=mask.sum(), p=[0.7, 0.3]
        )
        print("\n(Artificially introduced device distribution drift for demo)")
    
    print(f"\nDetecting drift in {len(current_data)} current samples...")
    result = drift_monitor.detect_drift(current_data)
    
    if result.get('drift_detected'):
        print("\n🚨 DRIFT DETECTED!")
        print(f"  Drifted Features: {len(result.get('drifted_features', []))}")
        
        for feature in result.get('drifted_features', []):
            score = result.get('drift_scores', {}).get(feature, 'N/A')
            print(f"    - {feature}: {score}")
        
        # Show manual drift checks
        if 'manual_drift_checks' in result:
            print("\n  Manual Drift Checks:")
            for feature, check in result['manual_drift_checks'].items():
                if check.get('drifted'):
                    print(f"    - {feature}: drift_score={check.get('drift_score', 'N/A'):.3f}")
    else:
        print("\n✓ No drift detected")


def demo_nl_query(impressions, clicks, conversions):
    """Demonstrate natural language queries"""
    print("\n" + "="*60)
    print("DEMO 4: Natural Language Query Interface")
    print("="*60)
    
    query_engine = NLQueryEngine()
    causal_engine = CausalEngine()
    
    # Prepare data
    impressions_dict = [imp.model_dump() for imp in impressions]
    clicks_dict = [clk.model_dump() for clk in clicks]
    conversions_dict = [conv.model_dump() for conv in conversions]
    
    data = causal_engine.prepare_data(impressions_dict, clicks_dict, conversions_dict)
    
    # Example queries
    queries = [
        "Show me revenue by region",
        "What is the click-through rate by device type?",
        "Show top performing campaigns"
    ]
    
    for i, query in enumerate(queries, 1):
        print(f"\n--- Query {i} ---")
        print(f"User: '{query}'")
        
        result = query_engine.process_query(query, data)
        
        if 'error' in result:
            print(f"Error: {result['error']}")
        else:
            print(f"Intent: {result['intent']}")
            if 'interpretation' in result:
                print(f"Interpretation: {result['interpretation']}")
            if 'results' in result:
                print(f"Results: {len(result['results']) if isinstance(result['results'], list) else 1} record(s)")
            print(f"✓ Query processed successfully")


def main():
    """Main demo function"""
    print("="*60)
    print("AD REVENUE SENTINEL - PLATFORM DEMONSTRATION")
    print("="*60)
    print("\nThis demo showcases all core features of the platform:")
    print("1. Data Validation")
    print("2. Causal Analysis")
    print("3. Drift Monitoring")
    print("4. Natural Language Queries")
    print("\n" + "="*60 + "\n")
    
    # Generate sample data
    impressions, clicks, conversions = generate_sample_events(200)
    
    # Run demos
    demo_validation(impressions, clicks, conversions)
    demo_causal_analysis(impressions, clicks, conversions)
    demo_drift_monitoring(impressions, clicks, conversions)
    demo_nl_query(impressions, clicks, conversions)
    
    print("\n" + "="*60)
    print("DEMO COMPLETE!")
    print("="*60)
    print("\nTo explore the interactive dashboard, run:")
    print("  streamlit run app.py")
    print("\nTo start the FastAPI backend, run:")
    print("  python src/data_ingestion/api.py")
    print("\n" + "="*60 + "\n")


if __name__ == "__main__":
    main()
