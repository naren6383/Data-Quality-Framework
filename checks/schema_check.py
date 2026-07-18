import pandas as pd

def check_schema(df: pd.DataFrame, expected_columns: list[str]) -> list[dict]:
    """
    Compare df.columns against expected_columns.
    
    - Missing expected columns not found in df -> Fail
    - Extra columns in df not in expected_columns -> Warning
    - Exact match -> Pass
    
    Return one result dict summarizing schema status,
    plus individual dicts for each missing/extra column.
    
    Args:
        df: The pandas DataFrame to check.
        expected_columns: The list of columns expected in the DataFrame.
        
    Returns:
        A list of result dictionaries with validation status.
    """
    results = []
    
    # Standardize input lists by stripping whitespace
    expected_set = {col.strip() for col in expected_columns if col.strip()}
    df_cols_set = set(df.columns)
    
    missing_columns = expected_set - df_cols_set
    extra_columns = df_cols_set - expected_set
    
    # 1. Summary result
    if len(missing_columns) > 0:
        summary_status = "Fail"
        summary_details = f"Schema check failed: {len(missing_columns)} expected column(s) missing."
    elif len(extra_columns) > 0:
        summary_status = "Warning"
        summary_details = f"Schema mismatch: {len(extra_columns)} extra column(s) detected."
    else:
        summary_status = "Pass"
        summary_details = "All expected columns are present, and no extra columns are found."
        
    results.append({
        "check": "Schema Validation",
        "column": "ALL",
        "status": summary_status,
        "details": summary_details
    })
    
    # 2. Add individual records for missing columns
    for col in sorted(missing_columns):
        results.append({
            "check": "Missing Column",
            "column": col,
            "status": "Fail",
            "details": f"Expected column '{col}' was not found in the dataset."
        })
        
    # 3. Add individual records for extra columns
    for col in sorted(extra_columns):
        results.append({
            "check": "Extra Column",
            "column": col,
            "status": "Warning",
            "details": f"Column '{col}' was found in the dataset but is not in the expected schema."
        })
        
    return results
