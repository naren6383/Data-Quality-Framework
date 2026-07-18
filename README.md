# Data Quality Framework

An interactive, production-quality Data Quality validation dashboard built using Python and Streamlit.

## 🎯 Features
- **Data Quality Checks**:
  - **Missing Values Check**: Analyzes each column's null rate (Pass, Warning, or Fail thresholds).
  - **Duplicate Rows Check**: Validates row-level uniqueness and primary/key-column uniqueness.
  - **Schema Validation Check**: Checks if dataset columns match the user-defined expected structure.
  - **Data Types Validation**: Compares column data types against expected dtypes and checks for recoverability/coercion.
- **Reporting & Visualization Tabs**:
  - **📊 Executive Summary**: Displays interactive Plotly charts, validation KPI cards, and dynamic key insights.
  - **📋 Detailed Validation Table**: A complete filterable audit table with download options.
  - **🔍 Raw Data Preview**: View the raw dataset with highlighted null/missing cells and a clean CSV export tool.

## 📸 Screenshot
![screenshot](Screenshot%202026-07-18%20230118.png)

## 🚀 How to Run Locally

1. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Launch the app**:
   ```bash
   streamlit run app.py
   ```

## 🛠️ Tech Stack
- **Python**: Core logic
- **Streamlit**: Dashboard web interface
- **Pandas**: Data loading and processing
- **Plotly**: Dynamic charts and metrics

## 📂 Project Structure
```text
data-quality-framework/
├── app.py
├── checks/
│   ├── __init__.py
│   ├── missing_values.py
│   ├── duplicates.py
│   ├── schema_check.py
│   └── dtype_check.py
├── utils/
│   ├── __init__.py
│   ├── report_generator.py
│   └── styling.py
├── sample_data/
│   └── sample_sales_data.csv
├── requirements.txt
├── .gitignore
└── README.md
```

## 🔮 Future Improvements
- Support Excel (`.xlsx`) file uploads
- Integrate Great Expectations or Pandera for industry-standard validation
- Add automated data profiling (min/max/mean/distribution per column)
- Add anomaly/outlier detection
- Add scheduled validation runs with email/Slack alerts
- Support database connections (Postgres, Snowflake) as a data source instead of only CSV
