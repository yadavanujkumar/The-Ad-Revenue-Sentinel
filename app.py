"""
Streamlit UI for Ad Revenue Sentinel
Main dashboard integrating all components
"""
import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import uuid
import plotly.express as px
import plotly.graph_objects as go

# Import our modules
import sys
sys.path.append('/home/runner/work/The-Ad-Revenue-Sentinel/The-Ad-Revenue-Sentinel')

from src.models.ad_events import AdImpression, AdClick, AdConversion
from src.data_validation.validator import DataValidator
from src.causal_engine.causal_analysis import CausalEngine
from src.drift_monitoring.drift_detector import DriftMonitor
from src.nlp_query.query_engine import NLQueryEngine

# Page configuration
st.set_page_config(
    page_title="Ad Revenue Sentinel",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
.main-header {
    font-size: 2.5rem;
    font-weight: bold;
    color: #1f77b4;
    text-align: center;
    padding: 1rem;
}
.metric-card {
    background-color: #f0f2f6;
    padding: 1rem;
    border-radius: 0.5rem;
    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}
.alert-high {
    background-color: #ffebee;
    padding: 1rem;
    border-left: 4px solid #f44336;
    border-radius: 0.25rem;
    margin: 0.5rem 0;
}
.alert-medium {
    background-color: #fff3e0;
    padding: 1rem;
    border-left: 4px solid #ff9800;
    border-radius: 0.25rem;
    margin: 0.5rem 0;
}
.alert-low {
    background-color: #e8f5e9;
    padding: 1rem;
    border-left: 4px solid #4caf50;
    border-radius: 0.25rem;
    margin: 0.5rem 0;
}
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'impressions' not in st.session_state:
    st.session_state.impressions = []
if 'clicks' not in st.session_state:
    st.session_state.clicks = []
if 'conversions' not in st.session_state:
    st.session_state.conversions = []
if 'alerts' not in st.session_state:
    st.session_state.alerts = []
if 'validator' not in st.session_state:
    st.session_state.validator = DataValidator()
if 'drift_monitor' not in st.session_state:
    st.session_state.drift_monitor = DriftMonitor()
if 'causal_engine' not in st.session_state:
    st.session_state.causal_engine = CausalEngine()
if 'nl_query_engine' not in st.session_state:
    st.session_state.nl_query_engine = NLQueryEngine()
if 'baseline_set' not in st.session_state:
    st.session_state.baseline_set = False

# Header
st.markdown('<div class="main-header">📊 Ad Revenue Sentinel</div>', unsafe_allow_html=True)
st.markdown("**Real-Time Ad-Revenue Observability & Causal Analytics Platform**")

# Sidebar
st.sidebar.title("Navigation")
page = st.sidebar.radio(
    "Select Page",
    ["Dashboard", "Data Ingestion", "Causal Analysis", "Drift Monitoring", "NL Query Interface", "Sample Data Generator"]
)

# Helper function to generate sample data
def generate_sample_data(num_impressions=100):
    """Generate sample ad event data"""
    regions = ['Mumbai', 'Delhi', 'Bangalore', 'Chennai', 'Kolkata', 'Hyderabad']
    devices = ['mobile', 'desktop', 'tablet']
    campaigns = ['summer_campaign', 'winter_sale', 'festive_offer', 'baseline_campaign']
    ads = [f'ad_{i}' for i in range(1, 11)]
    
    impressions = []
    clicks = []
    conversions = []
    
    for i in range(num_impressions):
        # Generate impression
        event_id = str(uuid.uuid4())
        timestamp = datetime.utcnow() - timedelta(minutes=np.random.randint(0, 1440))
        
        impression = {
            'event_id': event_id,
            'timestamp': timestamp.isoformat(),
            'ad_id': np.random.choice(ads),
            'campaign_id': np.random.choice(campaigns),
            'user_id': f'user_{np.random.randint(1, 1000)}',
            'user_age': int(np.random.normal(35, 15)),
            'device_type': np.random.choice(devices, p=[0.6, 0.3, 0.1]),
            'region': np.random.choice(regions),
            'platform': np.random.choice(['web', 'app'], p=[0.4, 0.6]),
            'bid_amount': float(np.random.uniform(0.5, 5.0))
        }
        impressions.append(impression)
        
        # Generate click (30% CTR)
        if np.random.random() < 0.3:
            click_id = str(uuid.uuid4())
            click = {
                'event_id': click_id,
                'timestamp': (timestamp + timedelta(seconds=np.random.randint(1, 300))).isoformat(),
                'impression_id': event_id,
                'ad_id': impression['ad_id'],
                'campaign_id': impression['campaign_id'],
                'user_id': impression['user_id'],
                'user_age': impression['user_age'],
                'device_type': impression['device_type'],
                'region': impression['region'],
                'click_position': np.random.randint(1, 10)
            }
            clicks.append(click)
            
            # Generate conversion (10% of clicks)
            if np.random.random() < 0.1:
                conversion = {
                    'event_id': str(uuid.uuid4()),
                    'timestamp': (timestamp + timedelta(seconds=np.random.randint(300, 3600))).isoformat(),
                    'click_id': click_id,
                    'impression_id': event_id,
                    'ad_id': impression['ad_id'],
                    'campaign_id': impression['campaign_id'],
                    'user_id': impression['user_id'],
                    'revenue': float(np.random.uniform(10, 200)),
                    'conversion_type': np.random.choice(['purchase', 'signup', 'download'])
                }
                conversions.append(conversion)
    
    return impressions, clicks, conversions

# Dashboard Page
if page == "Dashboard":
    st.header("Real-Time Dashboard")
    
    # Metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Impressions", len(st.session_state.impressions))
    with col2:
        st.metric("Total Clicks", len(st.session_state.clicks))
    with col3:
        st.metric("Total Conversions", len(st.session_state.conversions))
    with col4:
        total_revenue = sum([c.get('revenue', 0) for c in st.session_state.conversions])
        st.metric("Total Revenue", f"${total_revenue:.2f}")
    
    # Rates
    col1, col2, col3 = st.columns(3)
    
    with col1:
        ctr = (len(st.session_state.clicks) / len(st.session_state.impressions) * 100) if st.session_state.impressions else 0
        st.metric("Click-Through Rate", f"{ctr:.2f}%")
    with col2:
        cvr = (len(st.session_state.conversions) / len(st.session_state.clicks) * 100) if st.session_state.clicks else 0
        st.metric("Conversion Rate", f"{cvr:.2f}%")
    with col3:
        rpi = total_revenue / len(st.session_state.impressions) if st.session_state.impressions else 0
        st.metric("Revenue per Impression", f"${rpi:.2f}")
    
    # Alerts Section
    st.subheader("⚠️ Validation Alerts")
    
    if st.session_state.alerts:
        high_alerts = [a for a in st.session_state.alerts if a.get('severity') == 'high']
        medium_alerts = [a for a in st.session_state.alerts if a.get('severity') == 'medium']
        low_alerts = [a for a in st.session_state.alerts if a.get('severity') == 'low']
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("High Severity", len(high_alerts))
        with col2:
            st.metric("Medium Severity", len(medium_alerts))
        with col3:
            st.metric("Low Severity", len(low_alerts))
        
        # Display recent alerts
        st.write("**Recent Alerts:**")
        for alert in st.session_state.alerts[-5:]:
            severity_class = f"alert-{alert.get('severity', 'low')}"
            st.markdown(f"""
            <div class="{severity_class}">
                <strong>{alert.get('alert_type', 'Unknown').upper()}</strong> - {alert.get('severity', 'low').upper()}<br>
                {alert.get('description', 'No description')}
            </div>
            """, unsafe_allow_html=True)
    else:
        st.info("No alerts yet. Generate some sample data to see alerts in action!")
    
    # Visualizations
    if st.session_state.impressions:
        st.subheader("📈 Performance Visualizations")
        
        df = pd.DataFrame(st.session_state.impressions)
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Revenue by Region
            if st.session_state.conversions:
                df_conv = pd.DataFrame(st.session_state.conversions)
                df_merged = df.merge(df_conv[['impression_id', 'revenue']], 
                                   left_on='event_id', right_on='impression_id', how='left')
                df_merged['revenue'] = df_merged['revenue'].fillna(0)
                
                revenue_by_region = df_merged.groupby('region')['revenue'].sum().reset_index()
                fig = px.bar(revenue_by_region, x='region', y='revenue', 
                           title='Revenue by Region', 
                           labels={'revenue': 'Total Revenue ($)', 'region': 'Region'})
                st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # Device Distribution
            device_dist = df['device_type'].value_counts().reset_index()
            device_dist.columns = ['device_type', 'count']
            fig = px.pie(device_dist, values='count', names='device_type', 
                        title='Impressions by Device Type')
            st.plotly_chart(fig, use_container_width=True)

# Data Ingestion Page
elif page == "Data Ingestion":
    st.header("Data Ingestion & Validation")
    
    tab1, tab2, tab3 = st.tabs(["Add Impression", "Add Click", "Add Conversion"])
    
    with tab1:
        st.subheader("Add Ad Impression")
        with st.form("impression_form"):
            col1, col2 = st.columns(2)
            with col1:
                ad_id = st.text_input("Ad ID", value=f"ad_{np.random.randint(1, 10)}")
                campaign_id = st.text_input("Campaign ID", value="summer_campaign")
                user_id = st.text_input("User ID", value=f"user_{np.random.randint(1, 1000)}")
                user_age = st.number_input("User Age", min_value=13, max_value=100, value=30)
            
            with col2:
                device_type = st.selectbox("Device Type", ["mobile", "desktop", "tablet"])
                region = st.text_input("Region", value="Mumbai")
                platform = st.selectbox("Platform", ["web", "app"])
                bid_amount = st.number_input("Bid Amount ($)", min_value=0.0, value=2.5, step=0.1)
            
            if st.form_submit_button("Add Impression"):
                try:
                    impression = AdImpression(
                        event_id=str(uuid.uuid4()),
                        timestamp=datetime.utcnow(),
                        ad_id=ad_id,
                        campaign_id=campaign_id,
                        user_id=user_id,
                        user_age=user_age,
                        device_type=device_type,
                        region=region,
                        platform=platform,
                        bid_amount=bid_amount
                    )
                    
                    # Validate
                    alerts = st.session_state.validator.validate_impression(impression)
                    
                    # Store
                    st.session_state.impressions.append(impression.model_dump())
                    st.session_state.alerts.extend([alert.model_dump() for alert in alerts])
                    
                    st.success(f"✅ Impression added! Event ID: {impression.event_id}")
                    if alerts:
                        st.warning(f"⚠️ {len(alerts)} validation alert(s) generated")
                except Exception as e:
                    st.error(f"Error: {str(e)}")
    
    with tab2:
        st.subheader("Add Ad Click")
        if not st.session_state.impressions:
            st.warning("Add impressions first before adding clicks")
        else:
            with st.form("click_form"):
                impression_ids = [imp['event_id'] for imp in st.session_state.impressions]
                selected_impression = st.selectbox("Select Impression ID", impression_ids[-10:])
                
                if st.form_submit_button("Add Click"):
                    try:
                        # Get impression details
                        impression = next(imp for imp in st.session_state.impressions 
                                        if imp['event_id'] == selected_impression)
                        
                        click = AdClick(
                            event_id=str(uuid.uuid4()),
                            timestamp=datetime.utcnow(),
                            impression_id=selected_impression,
                            ad_id=impression['ad_id'],
                            campaign_id=impression['campaign_id'],
                            user_id=impression['user_id'],
                            user_age=impression.get('user_age'),
                            device_type=impression['device_type'],
                            region=impression['region'],
                            click_position=np.random.randint(1, 10)
                        )
                        
                        # Validate
                        alerts = st.session_state.validator.validate_click(click)
                        
                        # Store
                        st.session_state.clicks.append(click.model_dump())
                        st.session_state.alerts.extend([alert.model_dump() for alert in alerts])
                        
                        st.success(f"✅ Click added! Event ID: {click.event_id}")
                        if alerts:
                            st.warning(f"⚠️ {len(alerts)} validation alert(s) generated")
                    except Exception as e:
                        st.error(f"Error: {str(e)}")
    
    with tab3:
        st.subheader("Add Ad Conversion")
        if not st.session_state.clicks:
            st.warning("Add clicks first before adding conversions")
        else:
            with st.form("conversion_form"):
                col1, col2 = st.columns(2)
                with col1:
                    click_ids = [clk['event_id'] for clk in st.session_state.clicks]
                    selected_click = st.selectbox("Select Click ID", click_ids[-10:])
                    revenue = st.number_input("Revenue ($)", min_value=0.0, value=50.0, step=1.0)
                
                with col2:
                    conversion_type = st.selectbox("Conversion Type", ["purchase", "signup", "download"])
                
                if st.form_submit_button("Add Conversion"):
                    try:
                        # Get click details
                        click = next(clk for clk in st.session_state.clicks 
                                   if clk['event_id'] == selected_click)
                        
                        conversion = AdConversion(
                            event_id=str(uuid.uuid4()),
                            timestamp=datetime.utcnow(),
                            click_id=selected_click,
                            impression_id=click['impression_id'],
                            ad_id=click['ad_id'],
                            campaign_id=click['campaign_id'],
                            user_id=click['user_id'],
                            revenue=revenue,
                            conversion_type=conversion_type
                        )
                        
                        # Validate
                        alerts = st.session_state.validator.validate_conversion(conversion)
                        
                        # Store
                        st.session_state.conversions.append(conversion.model_dump())
                        st.session_state.alerts.extend([alert.model_dump() for alert in alerts])
                        
                        st.success(f"✅ Conversion added! Event ID: {conversion.event_id}")
                        if alerts:
                            st.warning(f"⚠️ {len(alerts)} validation alert(s) generated")
                    except Exception as e:
                        st.error(f"Error: {str(e)}")

# Causal Analysis Page
elif page == "Causal Analysis":
    st.header("🔍 Causal Investigation Engine")
    
    if not st.session_state.impressions:
        st.warning("No data available. Please generate sample data or add events manually.")
    else:
        # Prepare data
        data = st.session_state.causal_engine.prepare_data(
            st.session_state.impressions,
            st.session_state.clicks,
            st.session_state.conversions
        )
        
        tab1, tab2, tab3 = st.tabs(["Bid Impact Analysis", "Creative Effect", "Campaign Uplift"])
        
        with tab1:
            st.subheader("Counterfactual Bid Analysis")
            st.write("*Answer: If we hadn't increased the bid in [region], what would the revenue have been?*")
            
            regions = data['region'].unique() if 'region' in data.columns else []
            selected_region = st.selectbox("Select Region", regions)
            
            if st.button("Run Bid Analysis"):
                with st.spinner("Performing causal analysis..."):
                    result = st.session_state.causal_engine.counterfactual_bid_analysis(
                        data, selected_region
                    )
                    
                    if 'error' in result:
                        st.error(result['error'])
                    else:
                        st.success("✅ Analysis Complete!")
                        
                        col1, col2, col3 = st.columns(3)
                        with col1:
                            st.metric("Treated Avg Revenue", f"${result['treated_avg_revenue']:.2f}")
                        with col2:
                            st.metric("Control Avg Revenue", f"${result['control_avg_revenue']:.2f}")
                        with col3:
                            st.metric("Causal Effect", f"${result['causal_effect']:.2f}")
                        
                        st.info(f"**Insight:** {result['counterfactual_question']}")
                        
                        st.json(result)
        
        with tab2:
            st.subheader("Creative Effect Analysis")
            st.write("*Answer: Did revenue drop because of the new creative or external factors?*")
            
            if st.button("Run Creative Analysis"):
                with st.spinner("Analyzing creative performance..."):
                    result = st.session_state.causal_engine.creative_effect_analysis(data)
                    
                    if 'error' in result:
                        st.error(result['error'])
                    else:
                        st.success("✅ Analysis Complete!")
                        st.metric("Overall Avg Revenue", f"${result['overall_avg_revenue']:.2f}")
                        
                        if result['creatives']:
                            df_creatives = pd.DataFrame(result['creatives'])
                            
                            fig = px.bar(df_creatives, x='creative_id', y='avg_revenue',
                                       title='Revenue by Creative',
                                       labels={'avg_revenue': 'Avg Revenue ($)', 'creative_id': 'Creative ID'})
                            st.plotly_chart(fig, use_container_width=True)
                            
                            st.dataframe(df_creatives)
        
        with tab3:
            st.subheader("Campaign Uplift Analysis")
            st.write("*Answer: Show me the uplift for [campaign] vs. the baseline*")
            
            campaigns = data['campaign_id'].unique() if 'campaign_id' in data.columns else []
            
            col1, col2 = st.columns(2)
            with col1:
                target_campaign = st.selectbox("Target Campaign", campaigns)
            with col2:
                baseline_campaign = st.selectbox("Baseline Campaign", campaigns, index=min(1, len(campaigns)-1))
            
            if st.button("Calculate Uplift"):
                with st.spinner("Calculating uplift..."):
                    result = st.session_state.causal_engine.campaign_uplift_analysis(
                        data, target_campaign, baseline_campaign
                    )
                    
                    if 'error' in result:
                        st.error(result['error'])
                    else:
                        st.success("✅ Uplift Calculated!")
                        
                        if 'uplift_percentage' in result:
                            col1, col2, col3 = st.columns(3)
                            with col1:
                                st.metric("Target Campaign Revenue", f"${result['avg_revenue_per_impression']:.2f}")
                            with col2:
                                st.metric("Baseline Campaign Revenue", f"${result['baseline_avg_revenue']:.2f}")
                            with col3:
                                st.metric("Uplift", f"{result['uplift_percentage']:.2f}%")
                            
                            st.info(f"**Insight:** {result['uplift_interpretation']}")
                        
                        st.json(result)

# Drift Monitoring Page
elif page == "Drift Monitoring":
    st.header("📉 Ad-Drift & Reliability Monitoring")
    
    if not st.session_state.impressions:
        st.warning("No data available. Please generate sample data first.")
    else:
        df = pd.DataFrame(st.session_state.impressions)
        
        # Prepare merged data
        data = st.session_state.causal_engine.prepare_data(
            st.session_state.impressions,
            st.session_state.clicks,
            st.session_state.conversions
        )
        
        col1, col2 = st.columns(2)
        
        with col1:
            if not st.session_state.baseline_set:
                if st.button("🔧 Set Current Data as Baseline"):
                    st.session_state.drift_monitor.set_baseline(data)
                    st.session_state.baseline_set = True
                    st.success("✅ Baseline set successfully!")
                    st.rerun()
            else:
                st.success("✅ Baseline is set")
                baseline_summary = st.session_state.drift_monitor.get_baseline_summary()
                st.json(baseline_summary['baseline_stats'])
        
        with col2:
            if st.session_state.baseline_set:
                if st.button("🔍 Detect Drift"):
                    with st.spinner("Detecting data drift..."):
                        drift_result = st.session_state.drift_monitor.detect_drift(data)
                        
                        if drift_result.get('drift_detected'):
                            st.error("🚨 **DRIFT DETECTED!**")
                            
                            st.metric("Drifted Features", len(drift_result.get('drifted_features', [])))
                            
                            if drift_result.get('drifted_features'):
                                st.write("**Drifted Features:**")
                                for feature in drift_result['drifted_features']:
                                    score = drift_result.get('drift_scores', {}).get(feature, 'N/A')
                                    st.write(f"- {feature}: {score}")
                        else:
                            st.success("✅ No drift detected")
                        
                        st.json(drift_result)
        
        # Display drift alerts
        st.subheader("Drift Alerts History")
        alerts = st.session_state.drift_monitor.get_drift_alerts()
        
        if alerts:
            for alert in alerts[-5:]:
                severity_class = f"alert-{alert.get('severity', 'low')}"
                st.markdown(f"""
                <div class="{severity_class}">
                    <strong>DRIFT ALERT</strong> - {alert.get('severity', 'low').upper()}<br>
                    {alert.get('description', 'No description')}<br>
                    <small>Features: {', '.join(alert.get('drifted_features', []))}</small>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("No drift alerts yet")

# NL Query Interface Page
elif page == "NL Query Interface":
    st.header("💬 Natural Language Query Interface")
    st.write("Ask questions in plain English!")
    
    if not st.session_state.impressions:
        st.warning("No data available. Please generate sample data first.")
    else:
        # Prepare data
        data = st.session_state.causal_engine.prepare_data(
            st.session_state.impressions,
            st.session_state.clicks,
            st.session_state.conversions
        )
        
        # Example queries
        st.subheader("Example Queries:")
        examples = [
            "Show me revenue by region",
            "What is the click-through rate by device type?",
            "Show top performing campaigns",
            "What is the conversion rate?",
            "Show me the uplift for campaigns",
            "Show revenue by device"
        ]
        
        cols = st.columns(3)
        for i, example in enumerate(examples):
            with cols[i % 3]:
                if st.button(example, key=f"example_{i}"):
                    st.session_state.current_query = example
        
        # Query input
        query = st.text_input(
            "Enter your question:",
            value=st.session_state.get('current_query', ''),
            placeholder="e.g., Show me revenue by region"
        )
        
        if st.button("🔍 Execute Query") or query:
            if query:
                with st.spinner("Processing query..."):
                    result = st.session_state.nl_query_engine.process_query(query, data)
                    
                    if 'error' in result:
                        st.error(f"❌ {result['error']}")
                        if 'suggestions' in result:
                            st.write("**Try these queries:**")
                            for suggestion in result['suggestions']:
                                st.write(f"- {suggestion}")
                    else:
                        st.success("✅ Query processed successfully!")
                        
                        # Show interpretation
                        if 'interpretation' in result:
                            st.info(f"**Insight:** {result['interpretation']}")
                        
                        # Show SQL query
                        if 'sql_query' in result:
                            with st.expander("🔍 View Generated SQL"):
                                st.code(result['sql_query'], language='sql')
                        
                        # Show results
                        if 'results' in result:
                            st.subheader("Results")
                            if isinstance(result['results'], list):
                                st.dataframe(pd.DataFrame(result['results']))
                            else:
                                st.json(result['results'])
                        
                        # Show visualization
                        if 'visualization' in result:
                            st.subheader("Visualization")
                            st.plotly_chart(result['visualization'], use_container_width=True)

# Sample Data Generator Page
elif page == "Sample Data Generator":
    st.header("🎲 Sample Data Generator")
    st.write("Generate realistic sample ad event data for testing")
    
    num_impressions = st.slider("Number of Impressions", 10, 1000, 100)
    
    if st.button("Generate Sample Data"):
        with st.spinner("Generating sample data..."):
            impressions, clicks, conversions = generate_sample_data(num_impressions)
            
            # Validate all events
            validator = st.session_state.validator
            all_alerts = []
            
            for imp in impressions:
                imp_obj = AdImpression(**imp)
                alerts = validator.validate_impression(imp_obj)
                all_alerts.extend([alert.model_dump() for alert in alerts])
            
            for clk in clicks:
                clk_obj = AdClick(**clk)
                alerts = validator.validate_click(clk_obj)
                all_alerts.extend([alert.model_dump() for alert in alerts])
            
            for conv in conversions:
                conv_obj = AdConversion(**conv)
                alerts = validator.validate_conversion(conv_obj)
                all_alerts.extend([alert.model_dump() for alert in alerts])
            
            # Store in session state
            st.session_state.impressions.extend(impressions)
            st.session_state.clicks.extend(clicks)
            st.session_state.conversions.extend(conversions)
            st.session_state.alerts.extend(all_alerts)
            
            st.success(f"✅ Generated:")
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Impressions", len(impressions))
            with col2:
                st.metric("Clicks", len(clicks))
            with col3:
                st.metric("Conversions", len(conversions))
            with col4:
                st.metric("Alerts", len(all_alerts))
    
    # Clear data
    if st.button("🗑️ Clear All Data"):
        st.session_state.impressions = []
        st.session_state.clicks = []
        st.session_state.conversions = []
        st.session_state.alerts = []
        st.session_state.baseline_set = False
        st.success("All data cleared!")
        st.rerun()
