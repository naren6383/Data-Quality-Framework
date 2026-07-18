import pandas as pd

def check_duplicates(df: pd.DataFrame, key_column: str = "order_id") -> list[dict]:
    """
    Check for duplicate rows and duplicate values in a specific key column.
    
    1. Check fully duplicated rows using df.duplicated().sum()
       -> Pass if 0, Fail if any found
    2. Check duplicate values in the key_column (if it exists)
       -> Pass if 0, Fail if any found
       -> If key_column does not exist, skip sub-check gracefully.
       
    Args:
        df: The pandas DataFrame to check.
        key_column: The primary key column to validate uniqueness.
        
    Returns:
        A list of result dictionaries with validation status.
    """
    results = []
    
    # 1. Check fully duplicated rows
    num_full_duplicates = int(df.duplicated().sum())
    if num_full_duplicates == 0:
        results.append({
            "check": "Duplicate Rows",
            "column": "ALL",
            "status": "Pass",
            "details": "No fully duplicated rows found."
        })
    else:
        results.append({
            "check": "Duplicate Rows",
            "column": "ALL",
            "status": "Fail",
            "details": f"Found {num_full_duplicates} fully duplicated rows."
        })
        
    # 2. Check duplicate key column values
    if key_column and key_column in df.columns:
        # Ignore nulls or include them? Standard duplicated() will count nulls as duplicates
        # which is usually desired for unique IDs. We'll use the default pandas duplicates check.
        num_key_duplicates = int(df[key_column].duplicated().sum())
        if num_key_duplicates == 0:
            results.append({
                "check": "Duplicate Keys",
                "column": key_column,
                "status": "Pass",
                "details": f"All values in key column '{key_column}' are unique."
            })
        else:
            results.append({
                "check": "Duplicate Keys",
                "column": key_column,
                "status": "Fail",
                "details": f"Found {num_key_duplicates} duplicate values in key column '{key_column}'."
            })
    else:
        results.append({
            "check": "Duplicate Keys",
            "column": key_column or "N/A",
            "status": "Warning",
            "details": f"Key column '{key_column}' not found. Duplicate key validation skipped."
        })
        
    return results
