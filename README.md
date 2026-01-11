# The Ad-Revenue Sentinel 📊

**Real-Time Ad-Revenue Observability & Causal Analytics Platform**

A comprehensive platform for high-velocity digital advertising environments that provides real-time data streaming, causal inference, drift detection, and natural language query capabilities.

## 🌟 Features

### 1. Real-Time Data Streaming & Validation
- **FastAPI-based ingestion pipeline** for ad impressions, clicks, and conversion events
- **Data Validator** that automatically flags integrity issues:
  - Bot-driven click spikes detection
  - Negative revenue entries
  - Suspicious behavioral patterns
  - Anomaly detection with statistical thresholds

### 2. Causal Investigation Engine
- **Counterfactual Analysis** using Microsoft's DoWhy and EconML
- Answer critical business questions:
  - *"If we hadn't increased the bid in Mumbai, what would the revenue have been?"*
  - *"Did the revenue drop because of the new creative or an external factor?"*
  - *"What's the true uplift of the summer campaign vs. baseline?"*
- Move beyond correlation to understand true causal relationships

### 3. Ad-Drift & Reliability Monitoring
- **Data Drift Detection** using EvidentlyAI
- Monitor shifts in:
  - Audience demographics (age, location)
  - Device type distributions
  - Behavioral patterns
- Automatic **Reliability Alerts** when distributions deviate from training baseline

### 4. Natural Language Query Interface
- **Text-to-Insight** feature powered by intelligent query parsing
- Ask questions in plain English:
  - *"Show me the uplift for the summer campaign vs. the baseline"*
  - *"What's the revenue by region?"*
  - *"Show click-through rate by device type"*
- Automatically generates:
  - SQL queries
  - Plotly visualizations
  - Natural language interpretations

### 5. Interactive Streamlit Dashboard
- Real-time metrics visualization
- Multi-page interface for different analytics workflows
- Sample data generator for testing
- Alert management and monitoring

## 🚀 Quick Start

### Prerequisites
- Python 3.8 or higher
- pip package manager

### Installation

1. **Clone the repository:**
```bash
git clone https://github.com/yadavanujkumar/The-Ad-Revenue-Sentinel.git
cd The-Ad-Revenue-Sentinel
```

2. **Install dependencies:**
```bash
pip install -r requirements.txt
```

### Running the Application

#### Option 1: Streamlit Dashboard (Recommended)
```bash
streamlit run app.py
```

The dashboard will open in your browser at `http://localhost:8501`

#### Option 2: FastAPI Backend
```bash
python src/data_ingestion/api.py
```

The API will be available at `http://localhost:8000`

API Documentation: `http://localhost:8000/docs`

## 📖 Usage Guide

### 1. Generate Sample Data
- Navigate to the **"Sample Data Generator"** page
- Select the number of impressions to generate
- Click **"Generate Sample Data"**
- Sample data includes impressions, clicks, conversions, and validation alerts

### 2. Real-Time Data Ingestion
- Go to **"Data Ingestion"** page
- Add impressions, clicks, and conversions manually
- View real-time validation alerts for data quality issues

### 3. Causal Analysis
- Navigate to **"Causal Analysis"** page
- Run counterfactual analyses:
  - **Bid Impact Analysis**: Understand revenue impact of bid changes
  - **Creative Effect**: Determine if creative changes affected revenue
  - **Campaign Uplift**: Calculate true uplift vs. baseline campaigns

### 4. Drift Monitoring
- Go to **"Drift Monitoring"** page
- Set baseline data distribution
- Run drift detection to identify distribution shifts
- View reliability alerts for significant changes

### 5. Natural Language Queries
- Navigate to **"NL Query Interface"** page
- Type questions in plain English
- View generated SQL queries, results, and visualizations

## 🏗️ Architecture

```
The-Ad-Revenue-Sentinel/
├── src/
│   ├── models/
│   │   └── ad_events.py           # Pydantic models for ad events
│   ├── data_ingestion/
│   │   └── api.py                 # FastAPI streaming endpoints
│   ├── data_validation/
│   │   └── validator.py           # Data quality validator
│   ├── causal_engine/
│   │   └── causal_analysis.py     # Causal inference engine
│   ├── drift_monitoring/
│   │   └── drift_detector.py      # Drift detection module
│   └── nlp_query/
│       └── query_engine.py        # NL query processor
├── app.py                          # Streamlit dashboard
├── requirements.txt                # Python dependencies
└── README.md                       # Documentation
```

## 🔧 Tech Stack

- **Web Framework**: FastAPI, Uvicorn
- **Data Processing**: Pandas, NumPy
- **Causal Inference**: EconML, DoWhy
- **Drift Detection**: EvidentlyAI
- **Visualization**: Plotly, Matplotlib, Seaborn
- **UI**: Streamlit
- **Streaming**: Kafka-Python (optional)
- **Database**: SQLAlchemy, SQLite
- **Validation**: Pydantic

## 📊 API Endpoints

### Health Check
```
GET /
```

### Event Ingestion
```
POST /events/impression
POST /events/click
POST /events/conversion
```

### Data Retrieval
```
GET /events/impressions?limit=100
GET /events/clicks?limit=100
GET /events/conversions?limit=100
GET /alerts?severity=high&limit=100
GET /stats
```

## 🎯 Example Use Cases

### Use Case 1: Detect Bot Traffic
The validator automatically flags suspicious patterns:
- More than 10 clicks per user per minute
- Click rates exceeding 3 standard deviations above baseline
- Generates high-severity alerts for investigation

### Use Case 2: Counterfactual Bid Analysis
```python
# Question: "What would revenue be without bid increase in Mumbai?"
result = causal_engine.counterfactual_bid_analysis(data, region="Mumbai")
# Returns: Causal effect estimate and counterfactual scenario
```

### Use Case 3: Drift Detection
```python
# Set baseline during normal operation
drift_monitor.set_baseline(baseline_data)

# Monitor for distribution shifts
drift_result = drift_monitor.detect_drift(current_data)
# Alerts if user demographics or device distributions change significantly
```

### Use Case 4: Natural Language Analytics
```
User: "Show me the uplift for the summer campaign vs. baseline"
System: 
- Generates SQL query
- Calculates uplift percentage
- Creates visualization
- Returns: "Summer campaign shows 23.5% uplift vs baseline"
```

## 🔒 Data Quality & Validation

The platform includes comprehensive validation:
- ✅ Schema validation with Pydantic
- ✅ Business rule validation (no negative revenue, valid age ranges)
- ✅ Statistical anomaly detection
- ✅ Bot traffic detection
- ✅ Data drift monitoring

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 👤 Author

**Yadav Anuj Kumar**

## 🙏 Acknowledgments

- Microsoft's EconML and DoWhy for causal inference capabilities
- EvidentlyAI for drift detection
- The Plotly team for excellent visualization tools
- Streamlit for the amazing UI framework