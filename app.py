import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px

# Adjust page settings first
st.set_page_config(page_title="Data Quality Framework", page_icon="🛡️", layout="wide")

# Import custom modules
from utils.styling import inject_custom_css, render_kpi_card, highlight_null_cells
from utils.report_generator import summarize, generate_summary_text, get_key_findings

# Inject premium styling
inject_custom_css()

# Custom Header
st.markdown('<div class="app-title">🛡️ Data Quality Framework</div>', unsafe_allow_html=True)
st.markdown('<div class="app-subtitle">Interactive Validator Dashboard</div>', unsafe_allow_html=True)
st.markdown('<div class="accent-divider"></div>', unsafe_allow_html=True)

# Helper function to infer type mapping
def infer_dtype_string(series: pd.Series) -> str:
    if pd.api.types.is_integer_dtype(series):
        return "int"
    elif pd.api.types.is_float_dtype(series):
        return "float"
    elif pd.api.types.is_datetime64_any_dtype(series):
        return "date"
    else:
        return "string"

# ----------------- SIDEBAR: DATA SOURCE SELECTION -----------------
st.sidebar.markdown("### 📁 Data Source Selection")

uploaded_file = st.sidebar.file_uploader(
    "Upload CSV file", 
    type=["csv"], 
    help="Limit 200MB per file • CSV format"
)

# Load dataframe
df = None
filename = ""

if uploaded_file is not None:
    filename = uploaded_file.name
    try:
        # Check if the file is empty before reading
        if uploaded_file.size == 0:
            st.sidebar.error("Uploaded file is empty. Please upload a valid CSV file.")
            st.stop()
            
        df = pd.read_csv(uploaded_file)
        if df.empty:
            st.sidebar.error("The uploaded CSV contains headers but no rows. Please upload a valid CSV.")
            st.stop()
            
        st.sidebar.success(f"Uploaded: {filename}")
    except Exception as e:
        st.sidebar.error(f"Error reading CSV file: {e}")
        st.stop()
else:
    filename = "sample_sales_data.csv"
    try:
        df = pd.read_csv("sample_data/sample_sales_data.csv")
        st.sidebar.info("Using default sample dataset.")
    except Exception as e:
        st.sidebar.error(f"Error loading default sample dataset: {e}")
        st.stop()

# Force session state refresh on file change
if st.session_state.get("current_loaded_filename") != filename:
    st.session_state.current_loaded_filename = filename
    # Clear previous run results to avoid displaying mismatching data
    if "results" in st.session_state:
        del st.session_state.results

# ----------------- SIDEBAR: CONFIGURE CHECKS -----------------
st.sidebar.markdown("### ⚙️ Configure Checks")

chk_missing = st.sidebar.checkbox("Missing Values Check", value=True)
chk_duplicates = st.sidebar.checkbox("Duplicate Rows Check", value=True)
chk_schema = st.sidebar.checkbox("Schema Validation Check", value=True)
chk_dtypes = st.sidebar.checkbox("Data Types Validation", value=True)

# Conditional Inputs
expected_cols_input = ""
if chk_schema:
    # Pre-fill expected columns with actual loaded columns
    default_cols = ", ".join(df.columns.tolist())
    expected_cols_input = st.sidebar.text_input(
        "Expected Columns (comma-separated)",
        value=default_cols,
        help="Specify the column names you expect to see in the uploaded dataset."
    )

expected_dtypes = {}
if chk_dtypes:
    st.sidebar.markdown("**Expected Column Types**")
    dtype_options = ["int", "float", "string", "date"]
    
    with st.sidebar.expander("📋 Edit Column Types"):
        for col in df.columns:
            inferred = infer_dtype_string(df[col])
            default_index = dtype_options.index(inferred)
            selected = st.selectbox(
                f"Column: {col}",
                options=dtype_options,
                index=default_index,
                key=f"dtype_{col}"
            )
            expected_dtypes[col] = selected

run_checks = st.sidebar.button("Run Validation Checks", type="primary")

# Run logic
any_check_enabled = chk_missing or chk_duplicates or chk_schema or chk_dtypes

if not any_check_enabled:
    st.warning("⚠️ Please enable at least one validation check in the sidebar to view metrics.")
    st.stop()

# Check validation execution
if "results" not in st.session_state or run_checks:
    results = []
    
    # 1. Missing Values check
    if chk_missing:
        from checks.missing_values import check_missing_values
        results.extend(check_missing_values(df))
        
    # 2. Duplicates check
    if chk_duplicates:
        from checks.duplicates import check_duplicates
        # Default key column is 'order_id', but if missing, use the first column dynamically
        key_col = "order_id" if "order_id" in df.columns else (df.columns[0] if len(df.columns) > 0 else None)
        results.extend(check_duplicates(df, key_column=key_col))
        
    # 3. Schema check
    if chk_schema:
        from checks.schema_check import check_schema
        expected_cols = [c.strip() for c in expected_cols_input.split(",") if c.strip()]
        results.extend(check_schema(df, expected_cols))
        
    # 4. Data Types check
    if chk_dtypes:
        from checks.dtype_check import check_dtypes
        results.extend(check_dtypes(df, expected_dtypes))
        
    # Cache in session state
    st.session_state.results = results
    st.session_state.summary = summarize(results)
    st.session_state.summary_text = generate_summary_text(st.session_state.summary)
    st.session_state.key_findings = get_key_findings(results)

# Retrieve results from cache
results = st.session_state.results
summary = st.session_state.summary
summary_text = st.session_state.summary_text
key_findings = st.session_state.key_findings

# ----------------- KPI METRIC CARDS -----------------
col1, col2, col3, col4, col5 = st.columns(5)
pass_rate = summary["pass_rate"]
pass_rate_status = "pass" if pass_rate >= 90.0 else ("warning" if pass_rate >= 70.0 else "fail")

with col1:
    st.markdown(render_kpi_card("Total Checks", str(summary["total"])), unsafe_allow_html=True)
with col2:
    st.markdown(render_kpi_card("Passed Checks", str(summary["passed"]), "pass"), unsafe_allow_html=True)
with col3:
    st.markdown(render_kpi_card("Warnings Raised", str(summary["warnings"]), "warning"), unsafe_allow_html=True)
with col4:
    st.markdown(render_kpi_card("Failures Detected", str(summary["failed"]), "fail"), unsafe_allow_html=True)
with col5:
    st.markdown(render_kpi_card("Overall Pass Rate", f"{pass_rate}%", pass_rate_status), unsafe_allow_html=True)

st.divider()

# Create tabs
tab_exec, tab_details, tab_raw = st.tabs(["📊 Executive Summary", "📋 Detailed Validation Table", "🔍 Raw Data Preview"])

# ----------------- TAB 1: EXECUTIVE SUMMARY -----------------
with tab_exec:
    st.markdown(f"### Health Summary")
    st.markdown(summary_text)
    
    chart_col1, chart_col2 = st.columns(2)
    
    with chart_col1:
        # Donut Chart
        labels = ['Pass', 'Warning', 'Fail']
        values = [summary['passed'], summary['warnings'], summary['failed']]
        colors = ['#10b981', '#f59e0b', '#ef4444']
        
        donut_fig = go.Figure(data=[go.Pie(
            labels=labels, 
            values=values, 
            hole=.5, 
            marker=dict(colors=colors),
            textinfo='percent+value'
        )])
        donut_fig.update_layout(
            title=dict(text="Proportion of Check Results", x=0.5, font=dict(size=16)),
            showlegend=True,
            legend=dict(orientation="h", yanchor="bottom", y=-0.15, xanchor="center", x=0.5),
            margin=dict(t=40, b=40, l=10, r=10),
            height=300
        )
        st.plotly_chart(donut_fig, use_container_width=True)
        
    with chart_col2:
        # Bar Chart
        res_df = pd.DataFrame(results)
        
        def normalize_check_name(name):
            if "Missing Values" in name:
                return "Missing Values"
            elif "Duplicate" in name:
                return "Duplicates"
            elif "Schema" in name or "Column" in name:
                return "Schema"
            elif "Data Type" in name:
                return "Data Types"
            return "Other"
            
        res_df['Normalized Check'] = res_df['check'].apply(normalize_check_name)
        bar_data = res_df.groupby(['Normalized Check', 'status']).size().reset_index(name='count')
        
        # Plotly stacked bar chart
        bar_fig = px.bar(
            bar_data,
            x='Normalized Check',
            y='count',
            color='status',
            color_discrete_map={'Pass': '#10b981', 'Warning': '#f59e0b', 'Fail': '#ef4444'},
            barmode='stack',
            labels={"status": "Status", "Normalized Check": "Check Category", "count": "Count"}
        )
        bar_fig.update_layout(
            title=dict(text="Checks Run by Type and Status", x=0.5, font=dict(size=16)),
            xaxis_title="Check Category",
            yaxis_title="Count of Sub-Checks",
            legend=dict(orientation="h", yanchor="bottom", y=-0.15, xanchor="center", x=0.5),
            margin=dict(t=40, b=40, l=10, r=10),
            height=300
        )
        st.plotly_chart(bar_fig, use_container_width=True)
        
    st.divider()
    st.markdown("### 💡 Key Findings")
    for finding in key_findings:
        st.markdown(f"- {finding}")

# ----------------- TAB 2: DETAILED VALIDATION TABLE -----------------
with tab_details:
    st.markdown("### Detailed Audit Logs")
    
    # Filtering inputs
    filt_col1, filt_col2 = st.columns([1, 2])
    
    with filt_col1:
        status_filter = st.selectbox("Filter by Status", ["All", "Pass", "Warning", "Fail"])
    with filt_col2:
        search_query = st.text_input("Search by Column Name", "", placeholder="Enter column name...")
        
    # Apply filtering
    filtered_results = results
    if status_filter != "All":
        filtered_results = [r for r in filtered_results if r["status"] == status_filter]
    if search_query:
        filtered_results = [r for r in filtered_results if search_query.lower() in r["column"].lower()]
        
    # Create stylized dataframe rows
    table_rows = []
    for r in filtered_results:
        status_emoji = "✅ Pass" if r["status"] == "Pass" else ("⚠️ Warning" if r["status"] == "Warning" else "❌ Fail")
        table_rows.append({
            "Check Category": r["check"],
            "Column Affected": r["column"],
            "Status": status_emoji,
            "Details": r["details"]
        })
        
    report_df = pd.DataFrame(table_rows)
    if report_df.empty:
        report_df = pd.DataFrame(columns=["Check Category", "Column Affected", "Status", "Details"])
        
    # Draw table
    st.dataframe(report_df, use_container_width=True, hide_index=True)
    
    # Download Button
    csv_data = report_df.to_csv(index=False)
    st.download_button(
        label="📥 Download Detailed Report (CSV)",
        data=csv_data,
        file_name="data_quality_detailed_report.csv",
        mime="text/csv"
    )

# ----------------- TAB 3: RAW DATA PREVIEW -----------------
with tab_raw:
    rows, cols = df.shape
    st.markdown(f"### Dataset Preview")
    st.markdown(f"**Dimensions:** `{rows}` rows, `{cols}` columns")
    
    # Stylized view highlighting nulls
    st.dataframe(highlight_null_cells(df), use_container_width=True)
    
    # Export Cleaned Data
    st.markdown("---")
    st.markdown("### Export Cleaned Data")
    st.markdown(
        "Dropping fully duplicated rows from the dataset and replacing null values. "
        "Ideal for downstream workflows."
    )
    
    cleaned_df = df.drop_duplicates()
    
    dl_col1, dl_col2 = st.columns([1, 3])
    with dl_col1:
        cleaned_csv = cleaned_df.to_csv(index=False)
        st.download_button(
            label="📥 Download Cleaned Data (CSV)",
            data=cleaned_csv,
            file_name=f"cleaned_{filename}",
            mime="text/csv"
        )
    with dl_col2:
        st.caption(
            f"Original dataset: {rows} rows. Cleaned dataset: {len(cleaned_df)} rows "
            f"({rows - len(cleaned_df)} duplicate rows removed)."
        )
