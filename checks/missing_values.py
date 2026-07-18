import pandas as pd

def check_missing_values(df: pd.DataFrame) -> list[dict]:
    """
    Check for missing (null) values in each column of the DataFrame.
    
    Rules:
    - 0 nulls -> Pass
    - <10% of rows null -> Warning
    - >=10% of rows null -> Fail
    
    Args:
        df: The pandas DataFrame to check.
        
    Returns:
        A list of result dictionaries with validation status.
    """
    results = []
    total_rows = len(df)
    
    if total_rows == 0:
        for col in df.columns:
            results.append({
                "check": "Missing Values",
                "column": col,
                "status": "Pass",
                "details": "Dataset is empty. No values to check."
            })
        return results

    for col in df.columns:
        null_count = int(df[col].isnull().sum())
        null_rate = null_count / total_rows
        
        if null_count == 0:
            status = "Pass"
            details = "No missing values found."
        elif null_rate < 0.10:
            status = "Warning"
            details = f"Found {null_count} missing values ({null_rate:.1%})."
        else:
            status = "Fail"
            details = f"Found {null_count} missing values ({null_rate:.1%}). This meets or exceeds the 10% threshold."
            
        results.append({
            "check": "Missing Values",
            "column": col,
            "status": status,
            "details": details
        })
        
    return results
