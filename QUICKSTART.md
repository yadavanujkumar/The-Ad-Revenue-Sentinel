# Quick Start Guide

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yadavanujkumar/The-Ad-Revenue-Sentinel.git
cd The-Ad-Revenue-Sentinel
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

## Running the Demo

To see all features in action:
```bash
python demo.py
```

This will demonstrate:
- Data validation with bot detection
- Causal counterfactual analysis
- Drift monitoring with alerts
- Natural language query processing

## Streamlit Dashboard

Launch the interactive dashboard:
```bash
streamlit run app.py
```

Then open your browser to `http://localhost:8501`

### Dashboard Features:

1. **Dashboard** - Real-time metrics and alerts
2. **Data Ingestion** - Add events manually
3. **Causal Analysis** - Run counterfactual analyses
4. **Drift Monitoring** - Detect distribution shifts
5. **NL Query Interface** - Ask questions in English
6. **Sample Data Generator** - Generate test data

## FastAPI Backend

Start the API server:
```bash
python src/data_ingestion/api.py
```

API will be available at `http://localhost:8000`

Interactive docs at `http://localhost:8000/docs`

### Example API Calls:

Add an impression:
```bash
curl -X POST http://localhost:8000/events/impression \
  -H "Content-Type: application/json" \
  -d '{
    "event_id": "imp_001",
    "ad_id": "ad_1",
    "campaign_id": "summer_campaign",
    "user_id": "user_123",
    "user_age": 30,
    "device_type": "mobile",
    "region": "Mumbai",
    "platform": "app",
    "bid_amount": 2.5
  }'
```

Get statistics:
```bash
curl http://localhost:8000/stats
```

Get alerts:
```bash
curl http://localhost:8000/alerts?severity=high
```

## Using the Platform

### 1. Generate Sample Data

In the Streamlit app:
1. Go to "Sample Data Generator"
2. Choose number of impressions (100-1000)
3. Click "Generate Sample Data"

### 2. Run Causal Analysis

1. Navigate to "Causal Analysis"
2. Select a region (e.g., Mumbai)
3. Click "Run Bid Analysis"
4. View counterfactual insights

### 3. Monitor Data Drift

1. Go to "Drift Monitoring"
2. Click "Set Current Data as Baseline"
3. Generate more data with different patterns
4. Click "Detect Drift"
5. View drift alerts and affected features

### 4. Natural Language Queries

Try these questions:
- "Show me revenue by region"
- "What is the click-through rate by device type?"
- "Show top performing campaigns"
- "What is the conversion rate?"

## Key Features

### Data Validation
- Automatically detects bot traffic
- Flags suspicious patterns
- Validates business rules
- Generates severity-based alerts

### Causal Analysis
- Counterfactual bid impact
- Creative effectiveness
- Campaign uplift vs baseline
- Statistical significance testing

### Drift Detection
- Distribution shift monitoring
- Demographic changes
- Behavioral pattern shifts
- Automated alerts

### Natural Language Queries
- Intent recognition
- SQL generation
- Automatic visualizations
- Plain English insights

## Troubleshooting

### ModuleNotFoundError
Install missing dependencies:
```bash
pip install -r requirements.txt
```

### Port Already in Use
Change the port for Streamlit:
```bash
streamlit run app.py --server.port 8502
```

Or for FastAPI:
```python
# In src/data_ingestion/api.py, change:
uvicorn.run(app, host="0.0.0.0", port=8001)
```

### Memory Issues
Reduce sample data size in the generator (use 50-100 impressions instead of 1000)

## Next Steps

1. Integrate with your real ad data sources
2. Connect to Kafka for real-time streaming
3. Add PostgreSQL/MongoDB for persistent storage
4. Deploy with Docker
5. Set up monitoring and alerting
6. Add authentication and authorization
