# Supply Chain Exception Intelligence Assistant

**Tagline:** Detect. Prioritize. Explain. Act.

---

## Table of Contents

1. [Project Overview](#project-overview)
2. [Problem Statement](#problem-statement)
3. [Objectives](#objectives)
4. [Features](#features)
5. [Architecture](#architecture)
6. [Workflow](#workflow)
7. [Technology Stack](#technology-stack)
8. [Dataset Description](#dataset-description)
9. [Exception Detection](#exception-detection)
10. [Isolation Forest](#isolation-forest)
11. [Risk Scoring](#risk-scoring)
12. [Recommendation Engine](#recommendation-engine)
13. [LLM Integration](#llm-integration)
14. [Streamlit Dashboard](#streamlit-dashboard)
15. [Installation](#installation)
16. [Environment Setup](#environment-setup)
17. [Running the Application](#running-the-application)
18. [Usage Guide](#usage-guide)
19. [Example Questions](#example-questions)
20. [Limitations](#limitations)
21. [Future Enhancements](#future-enhancements)
22. [Conclusion](#conclusion)

---

## Project Overview

The **Supply Chain Exception Intelligence Assistant** is an AI-powered supply chain analytics platform designed to detect, analyze, and resolve operational exceptions in real-time. It combines rule-based analysis, machine learning anomaly detection, and optional LLM integration to provide a comprehensive supply chain control tower.

The system processes shipment data, identifies risks, calculates transparent risk scores, and recommends corrective actions. It's designed for supply chain managers, operations teams, and logistics coordinators.

---

## Problem Statement

Modern supply chains generate massive amounts of data from multiple sources:
- Delivery tracking systems
- Inventory management systems
- Supplier performance data
- Transportation networks
- Weather and environmental factors

**Key Challenges:**
- Identifying critical exceptions amidst thousands of shipments
- Understanding root causes of delays and shortages
- Prioritizing actions based on business impact
- Making data-driven decisions quickly
- Integrating multiple data sources

**Without a system like this:**
- Delayed detection of critical issues
- Manual, time-consuming analysis
- Inconsistent prioritization
- Missed cost-saving opportunities
- Reactive instead of proactive management

---

## Objectives

1. **Automated Exception Detection:** Identify delivery delays, inventory shortages, supplier performance issues, and cost anomalies automatically
2. **Risk Prioritization:** Calculate transparent, explainable risk scores (0-100)
3. **Intelligent Insights:** Use ML (Isolation Forest) to detect unusual patterns
4. **Actionable Recommendations:** Provide specific, prioritized corrective actions
5. **LLM Explanation:** Augment analysis with natural language explanations (optional)
6. **Interactive Dashboard:** Provide a professional control tower interface
7. **Natural Language Interface:** Allow users to ask questions about their data
8. **Resilience:** Work without external APIs; gracefully handle missing data

---

## Features

### Core Features

✅ **Data Processing**
- Load supply chain data from CSV
- Validate and clean data
- Handle missing values intelligently
- Engineer features for analysis

✅ **Exception Detection**
- Delivery delay detection (with categories)
- Inventory shortage detection
- Supplier performance analysis
- Transportation cost anomaly detection
- Lead time deviation detection

✅ **Machine Learning**
- Isolation Forest for unsupervised anomaly detection
- Automated model training and prediction
- No manual labeling required

✅ **Risk Scoring**
- Transparent, weighted risk calculation
- Individual risk factor breakdown
- Risk level categorization (LOW, MEDIUM, HIGH, CRITICAL)

✅ **Recommendations**
- Deterministic, rule-based recommendations
- Priority-based action queuing
- Category-organized actions

✅ **Interactive Dashboard**
- Multiple views: Overview, Exceptions, Shipments, Inventory, Suppliers, Map, Analytics
- Real-time filtering and search
- Professional KPI cards and visualizations
- CSV export capabilities

✅ **Natural Language Assistant**
- Question answering about supply chain data
- LLM-powered explanations (optional)
- Fallback rule-based responses

✅ **API Key Optional**
- Application runs without OPENAI_API_KEY
- LLM features gracefully degrade

---

## Architecture

```
CSV
  ↓
Pandas Data Processing
  ↓
Feature Engineering
  ↓
Rule-Based Exception Detection
  ↓
Isolation Forest Anomaly Detection
  ↓
Risk Scoring (Weighted Components)
  ↓
Exception Prioritization
  ↓
Recommendation Engine
  ↓
LLM Explanation (Optional)
  ↓
Streamlit Dashboard
```

### Module Structure

```
supply-chain-intelligence/
├── app.py                          # Main Streamlit application
├── requirements.txt                # Python dependencies
├── .env.example                    # Environment variables template
├── README.md                       # This file
│
├── data/
│   └── supply_chain_data.csv       # Supply chain dataset (2500+ records)
│
├── models/
│   └── anomaly_model.py            # Isolation Forest implementation
│
├── modules/
│   ├── data_processing.py          # Data loading and preprocessing
│   ├── exception_detection.py      # Exception detection logic
│   ├── risk_scoring.py             # Risk score calculation
│   ├── recommendations.py          # Recommendation engine
│   └── llm_assistant.py            # LLM integration
│
├── utils/
│   └── helpers.py                  # Utility functions
│
└── assets/                         # Static assets (empty)
```

---

## Workflow

### 1. Data Ingestion
- Load CSV file with supply chain data
- Validate required columns
- Detect data quality issues

### 2. Data Preparation
- Parse dates
- Handle missing values
- Remove duplicates
- Normalize numerical values

### 3. Feature Engineering
- Calculate delivery delays
- Categorize delay severity
- Assess inventory status
- Compute cost deviations
- Calculate lead time deviations

### 4. Exception Detection
Five parallel detection processes:

**Delivery Exceptions:**
- On Time (0 days)
- Minor Delay (1-2 days)
- Major Delay (3-5 days)
- Critical Delay (>5 days)

**Inventory Exceptions:**
- Normal: inventory > reorder_point
- Low: inventory < reorder_point
- Critical: inventory < safety_stock

**Supplier Exceptions:**
- Analyze on-time percentage
- Identify poor performers (< 80% on-time)
- Flag unreliable suppliers

**Cost Exceptions:**
- Use IQR (Interquartile Range) analysis
- Flag anomalously high costs

**Lead Time Exceptions:**
- Compare actual vs. expected
- Calculate percentage deviation
- Flag unusual patterns

### 5. Machine Learning Anomaly Detection
- Isolation Forest with contamination=0.05
- Features: quantity, shipping_cost, distance_km, actual_lead_time, inventory_level, supplier_lead_time
- Output: Normal / Anomaly + anomaly score (0-1)

### 6. Risk Scoring
Calculate transparent risk score (0-100) using weighted components:
- Delivery Delay: 30 points
- Inventory Shortage: 25 points
- Supplier Risk: 20 points
- Transportation Cost: 10 points
- Lead Time Risk: 10 points
- ML Anomaly: 5 points

Risk Levels:
- 0-30: LOW (🟢)
- 31-60: MEDIUM (🟡)
- 61-80: HIGH (🟠)
- 81-100: CRITICAL (🔴)

### 7. Prioritization
- Sort by risk level and score
- Identify critical and high-risk shipments
- Flag urgent actions

### 8. Recommendations
Generate actionable recommendations based on:
- Delay category
- Inventory status
- Supplier performance
- Cost anomalies
- Lead time issues
- ML anomalies

### 9. Dashboard & Visualization
- Render interactive Streamlit interface
- Provide filtering and search
- Enable data export

---

## Technology Stack

### Backend
- **Python 3.8+** - Core language
- **Pandas 2.1+** - Data manipulation
- **NumPy 1.26+** - Numerical computing
- **Scikit-learn 1.3+** - Machine learning (Isolation Forest)
- **Python-dotenv 1.0+** - Environment management

### Frontend
- **Streamlit 1.28+** - Interactive dashboard
- **Plotly 5.17+** - Interactive visualizations

### Optional
- **OpenAI API** - LLM integration for explanations

### Development
- CSV format for data
- No database required
- No complex dependencies

---

## Dataset Description

### Synthetic Dataset
- **Records:** 2,500 shipments
- **Time Period:** Jan 2023 - Aug 2024
- **Distribution:** ~70% normal, ~30% with exceptions

### Columns

| Column | Type | Description |
|--------|------|-------------|
| shipment_id | String | Unique shipment identifier (S00001, S00002, ...) |
| order_id | String | Associated order |
| product_id | String | Product being shipped (Product_1 to Product_50) |
| supplier | String | Supplier name (SupplierA to SupplierJ) |
| warehouse | String | Origin warehouse (NY, LA, Chicago, TX, Seattle) |
| destination | String | Destination city |
| order_date | DateTime | Date order was placed |
| ship_date | DateTime | Date shipment was sent |
| expected_delivery | DateTime | Expected delivery date |
| actual_delivery | DateTime | Actual delivery date (or NULL for in-transit) |
| quantity | Integer | Units shipped |
| inventory_level | Integer | Current inventory in warehouse |
| reorder_point | Integer | Inventory threshold for reordering |
| safety_stock | Integer | Minimum safety inventory |
| supplier_lead_time | Integer | Expected days from supplier |
| actual_lead_time | Integer | Actual days taken |
| transport_mode | String | Ground, Air, Ocean, Rail |
| shipping_cost | Float | Cost in USD |
| distance_km | Float | Distance in kilometers |
| weather_condition | String | Weather at time of shipment |
| status | String | Delivered, In Transit, Pending |

### Feature Engineering Columns (Added by Pipeline)

| Column | Description |
|--------|-------------|
| delay_days | Number of days delayed from expected delivery |
| delivery_delay_category | On Time, Minor Delay, Major Delay, Critical Delay |
| inventory_status | Normal, Low, Critical |
| lead_time_deviation_pct | % deviation from expected lead time |
| cost_anomaly | Normal, High, Low |
| lead_time_category | Normal, Moderate Deviation, High Deviation |

---

## Exception Detection

### Delivery Delay Detection

```
On Time:       delay_days <= 0
Minor Delay:   1 <= delay_days <= 2
Major Delay:   3 <= delay_days <= 5
Critical Delay: delay_days > 5
```

### Inventory Shortage Detection

```
Normal:   inventory_level >= reorder_point
Low:      safety_stock <= inventory_level < reorder_point
Critical: inventory_level < safety_stock
```

### Supplier Performance Analysis

```
On-Time % >= 95%  → Excellent
On-Time % >= 90%  → Good
On-Time % >= 80%  → Acceptable
On-Time % >= 60%  → Poor
On-Time % < 60%   → Critical
```

### Transportation Cost Anomaly

Uses Interquartile Range (IQR) method:
```
Q1 = 25th percentile
Q3 = 75th percentile
IQR = Q3 - Q1
Upper Bound = Q3 + 1.5 × IQR
Lower Bound = Q1 - 1.5 × IQR

High Anomaly: cost > Upper Bound
Low Anomaly:  cost < Lower Bound
```

### Lead Time Deviation

```
Normal:              deviation <= 20%
Moderate Deviation:  20% < deviation <= 50%
High Deviation:      deviation > 50%
```

---

## Isolation Forest

### What is Isolation Forest?

Isolation Forest is an unsupervised machine learning algorithm that detects anomalies by isolating unusual observations in the dataset.

### How It Works

1. **Randomly select features and split values** - Creates decision trees
2. **Isolates anomalies quickly** - Anomalies require fewer splits
3. **Calculates anomaly score** - Based on tree depth
4. **No labeling required** - Unsupervised learning

### Configuration

```python
contamination = 0.05  # Expect ~5% anomalies
random_state = 42     # Reproducibility
n_estimators = 100    # Number of trees
```

### Features Used

- `quantity`: Unusual order quantities
- `shipping_cost`: Unusual costs
- `distance_km`: Unusual distances
- `actual_lead_time`: Unusual delivery times
- `inventory_level`: Unusual inventory levels
- `supplier_lead_time`: Unusual supplier patterns

### Output

- **-1:** Anomaly detected
- **1:** Normal observation
- **Anomaly Score:** 0-1 (lower = more anomalous)

### Example

```
Normal Shipment:        Score = 0.92 (Normal)
Extremely High Cost:    Score = 0.15 (Anomaly)
Unusual Quantity:       Score = 0.20 (Anomaly)
```

---

## Risk Scoring

### Risk Score Calculation

```
Total Risk = sum(weighted_factors)
           = delay_score (0-30)
           + inventory_score (0-25)
           + supplier_score (0-20)
           + cost_score (0-10)
           + lead_time_score (0-10)
           + anomaly_score (0-5)

Maximum = 100
Minimum = 0
```

### Transparent Breakdown

Every shipment includes:
- `delay_score`: Points from delivery delay
- `inventory_score`: Points from inventory status
- `supplier_score`: Points from supplier reliability
- `cost_score`: Points from cost anomalies
- `lead_time_score`: Points from lead time deviation
- `anomaly_score`: Points from ML anomaly detection
- `total_risk_score`: Final risk score
- `risk_level`: Categorized level

### Example Risk Breakdown

```
Shipment S00123:

Delay Score:         15 (Major Delay: 4 days)
Inventory Score:     10 (Low inventory)
Supplier Score:      15 (Supplier has 75% on-time rate)
Cost Score:           8 (Slightly high shipping)
Lead Time Score:      5 (20% deviation)
Anomaly Score:        3 (Slight anomaly detected)
─────────────────────────────
Total Risk Score:    56/100  → MEDIUM Risk
```

---

## Recommendation Engine

### Recommendation Categories

1. **Delivery Recommendations**
   - Minor Delay: "Monitor shipment status"
   - Major Delay: "Contact carrier to investigate"
   - Critical Delay: "Expedite shipment immediately"

2. **Inventory Recommendations**
   - Low Inventory: "Schedule replenishment"
   - Critical Inventory: "Emergency restock or transfer"

3. **Supplier Recommendations**
   - Poor Performance: "Review supplier performance"
   - Critical Issues: "Consider alternate suppliers"

4. **Cost Recommendations**
   - High Costs: "Review transportation routes"
   - Negotiate: "Renegotiate carrier rates"

5. **Lead Time Recommendations**
   - High Deviation: "Investigate supplier variability"
   - Pattern Issue: "Review supplier lead time trends"

6. **Anomaly Recommendations**
   - ML Anomaly: "Investigate unusual patterns"

### Priority Levels

- **URGENT** 🔴 - Requires immediate action
- **HIGH** 🟠 - Requires prompt attention
- **MEDIUM** 🟡 - Should be addressed soon
- **LOW** 🟢 - Monitor

---

## LLM Integration

### Optional LLM Features

When `OPENAI_API_KEY` is set:

1. **Shipment Explanations** - Why is a specific shipment risky?
2. **Question Answering** - Answer natural language questions
3. **Business Insights** - Generate strategic insights

### LLM Prompts

**Shipment Explanation:**
```
"Explain why this shipment is risky in 2-3 sentences given:
- Risk score: 75/100
- Delay: Major Delay (4 days)
- Inventory: Low
- Supplier: 70% on-time rate
- Recommended actions: [list]"
```

**Question Answering:**
```
"Based on supply chain data showing:
- 2,500 shipments
- 150 critical shipments
- 300 delayed shipments
- [other stats]

Answer: [User question]"
```

### Fallback Behavior

If LLM is unavailable:
- Rule-based explanations provided
- Application continues working
- User notified: "LLM unavailable - using rule-based analysis"

---

## Streamlit Dashboard

### Pages

1. **📊 Overview**
   - KPI cards (Total Shipments, Exceptions, Critical, Avg Delay, etc.)
   - Status distribution pie charts
   - Risk level distribution
   - Supplier performance trends

2. **🚨 Exceptions**
   - Filtered exception list
   - Multi-select filters (Risk, Delay, Supplier, Warehouse)
   - CSV export capability

3. **🚛 Shipments**
   - Detailed shipment view
   - Risk factor breakdown visualization
   - Delivery and inventory information
   - Recommended actions
   - AI analysis (if LLM available)

4. **📦 Inventory**
   - Inventory status metrics
   - Product-level inventory chart
   - Inventory detail table
   - CSV export

5. **🏭 Suppliers**
   - On-time performance metrics
   - Supplier performance chart
   - Detailed supplier table
   - CSV export

6. **🗺️ Map**
   - Route summary (warehouse → destination)
   - Top routes by volume
   - Risk visualization (future enhancement)

7. **🤖 AI Assistant**
   - Chat interface for natural language questions
   - Example questions
   - Rule-based and LLM-powered answers
   - Conversation history

8. **📈 Analytics**
   - Shipment volume trend
   - Delay trend over time
   - Cost distribution histogram
   - Transport mode performance analysis

---

## Installation

### Prerequisites

- Python 3.8 or higher
- pip package manager
- Git (optional)

### Steps

1. **Clone or download the project**
```bash
cd supply-chain-intelligence
```

2. **Create a virtual environment**
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Verify installation**
```bash
python -c "import pandas; import streamlit; print('✓ Dependencies installed successfully')"
```

---

## Environment Setup

### 1. Generate Dataset

The dataset is automatically generated when the app first runs. To regenerate:

```bash
python generate_dataset.py
```

This creates `data/supply_chain_data.csv` with 2,500 realistic records.

### 2. Optional: Configure LLM (OpenAI)

1. Get an API key from [OpenAI](https://platform.openai.com)

2. Create `.env` file in the project root:
```bash
cp .env.example .env
```

3. Add your API key:
```
OPENAI_API_KEY=sk-xxxxxxxxx...
```

4. The application will automatically detect and use the API key.

### 3. Verify Setup

```bash
# Test data processing
python -c "from modules.data_processing import clean_and_prepare_data; df = clean_and_prepare_data('data/supply_chain_data.csv'); print(f'✓ Data loaded: {len(df)} records')"
```

---

## Running the Application

### Start the Streamlit App

```bash
streamlit run app.py
```

### What Happens

1. Streamlit starts local server (http://localhost:8501)
2. App loads supply chain data
3. Data processing pipeline runs
4. Anomaly detection model trains
5. Risk scores calculated
6. Dashboard rendered

### Browser Access

- Open http://localhost:8501 in your browser
- Use sidebar to navigate pages
- Upload CSV or use default dataset

### Stop the App

Press `Ctrl+C` in the terminal running Streamlit.

---

## Usage Guide

### Basic Workflow

1. **Overview Page**
   - Check KPIs and current status
   - Identify high-risk shipments
   - Understand distribution of issues

2. **Exceptions Page**
   - Filter by risk level or supplier
   - Identify critical shipments
   - Review exception details
   - Export report for stakeholders

3. **Shipment Details**
   - Click on a shipment ID
   - See complete details
   - Understand risk breakdown
   - Review recommendations
   - Read AI analysis

4. **Supplier Performance**
   - Monitor supplier reliability
   - Identify worst performers
   - Make sourcing decisions

5. **Inventory Management**
   - Monitor stock levels
   - Identify replenishment needs
   - Prevent stock-outs

6. **AI Assistant**
   - Ask natural language questions
   - Get data-driven answers
   - Explore insights

### Advanced Features

**CSV Upload**
- Import custom datasets
- System validates columns
- Errors shown clearly

**Data Export**
- Download exception reports
- Export supplier performance
- Share inventory analysis
- CSV format for Excel/Sheets

**Real-time Filtering**
- Multi-select filters
- Live chart updates
- Instant results

---

## Example Questions for AI Assistant

1. **"Which shipments are critical?"**
   - Returns: List of critical shipments with risk scores

2. **"What's our average delay?"**
   - Returns: Calculated average delay in days

3. **"Which supplier has the worst performance?"**
   - Returns: Worst supplier with on-time percentage

4. **"Which products are at stock-out risk?"**
   - Returns: List of products with critical inventory

5. **"What are our biggest supply-chain problems?"**
   - Returns: Summary of major issues

6. **"Show me high-risk shipments"**
   - Returns: CRITICAL and HIGH risk shipments

7. **"Which warehouse has inventory issues?"**
   - Returns: Warehouses with critical stock

8. **"What's the transportation cost anomaly?"**
   - Returns: Unusually high shipping costs

9. **"Why is shipment S00123 critical?"**
   - Returns: Detailed explanation of risk factors

10. **"What action should we take for shipment S00456?"**
    - Returns: Prioritized recommendations

---

## Limitations

1. **Data Quality**
   - Assumes reasonably clean input data
   - Missing values handled with median imputation
   - Extreme outliers may need manual review

2. **Scalability**
   - Designed for datasets up to ~100K rows
   - For larger datasets, consider database backend
   - CSV loading is memory-based

3. **Real-time Processing**
   - Batch processing, not real-time streaming
   - Model retrains on app restart
   - Not suitable for millisecond-level latency

4. **Customization**
   - Weights in risk scoring are fixed
   - Thresholds for exception detection are hardcoded
   - Future: Configuration file for customization

5. **Geographic Visualization**
   - Basic route summary provided
   - Full map visualization requires geolocation data
   - Future: Plotly Mapbox integration

6. **LLM Integration**
   - Requires OpenAI API (paid)
   - Falls back gracefully without it
   - API costs scale with usage

7. **Data Privacy**
   - No encryption for sensitive data
   - Use only for authorized supply chain data
   - Future: Add role-based access control

---

## Future Enhancements

### Short Term
- [ ] Configuration file for thresholds and weights
- [ ] More transport modes and carriers
- [ ] Supplier contact information integration
- [ ] Automated alert notifications (email/SMS)

### Medium Term
- [ ] Database backend (PostgreSQL/MongoDB)
- [ ] Real-time data streaming (Kafka)
- [ ] Advanced geographic visualization
- [ ] Predictive delay forecasting
- [ ] Multi-model ensemble (Random Forest + XGBoost)
- [ ] Custom metrics and KPI definitions

### Long Term
- [ ] Multi-tenant SaaS platform
- [ ] Role-based access control
- [ ] Advanced ML: Deep Learning for pattern recognition
- [ ] Integration with ERP systems (SAP, Oracle)
- [ ] Mobile app
- [ ] API for third-party integrations
- [ ] Supply chain network optimization

---

## Conclusion

The Supply Chain Exception Intelligence Assistant transforms raw shipment data into actionable insights. By combining rule-based analysis, machine learning, and optional LLM integration, it provides a comprehensive solution for modern supply chain management.

### Key Takeaways

✅ **Automated Detection:** Identify issues before they escalate
✅ **Transparent Scoring:** Understand exactly why something is risky
✅ **Actionable Insights:** Get specific recommendations for every issue
✅ **Interactive Dashboard:** Professional control tower interface
✅ **Scalable Architecture:** Easy to customize and extend
✅ **Resilient Design:** Works without external dependencies

### Getting Started

1. Install dependencies: `pip install -r requirements.txt`
2. Generate dataset: `python generate_dataset.py`
3. Run app: `streamlit run app.py`
4. Open browser: http://localhost:8501

---

## Viva Explanation

### What This System Does (Beginner's Explanation)

Imagine you're managing thousands of shipments across your supply chain. You have:
- Shipments in transit
- Inventory in warehouses
- Different suppliers
- Various delivery routes

**The Problem:**
- Which shipments might be delayed?
- Which warehouses are running out of stock?
- Which suppliers are unreliable?
- Which shipments have unusual costs?

**The Solution:**
This intelligent assistant analyzes ALL your shipment data and:

1. **Detects Problems** - Finds delays, shortages, supplier issues, and cost anomalies
2. **Calculates Risk** - Scores each shipment 0-100 based on multiple factors
3. **Prioritizes** - Shows you the most critical issues first (CRITICAL 🔴 → HIGH 🟠 → MEDIUM 🟡 → LOW 🟢)
4. **Recommends Actions** - Tells you exactly what to do
5. **Explains with AI** - Uses AI to explain why something is risky (optional)
6. **Visualizes Everything** - Beautiful dashboard with charts and filters

**Example:**
```
Shipment S00123:
- Delayed by 5 days
- Supplier only 65% reliable
- Inventory running low
→ Risk Score: 68/100 (HIGH)
→ Action: "Expedite shipment and contact supplier"
```

### Why It's Valuable

- **Saves Time:** Automated analysis instead of manual spreadsheets
- **Reduces Costs:** Identify cost anomalies and optimize routes
- **Improves Reliability:** Prevent stock-outs and missed deliveries
- **Better Decisions:** Data-driven, not guesswork
- **Professional Dashboard:** Like having a supply chain command center

---

**Built with Python, Pandas, Scikit-learn, and Streamlit**

For questions or contributions, please refer to the project documentation.

