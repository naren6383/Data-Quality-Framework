import pandas as pd
import numpy as np

def check_dtypes(df: pd.DataFrame, expected_dtypes: dict[str, str]) -> list[dict]:
    """
    Validate columns in DataFrame against expected data types.
    
    Expected types: 'int', 'float', 'string', 'date'
    
    Rules:
    - Exact Match -> Pass
    - Mismatched but convertible/coercible with low error rate (<= 10% new nulls) -> Warning
    - Mismatched and not coercible (or high error rate > 10% new nulls) -> Fail
    
    Args:
        df: The pandas DataFrame to check.
        expected_dtypes: A dictionary mapping column names to expected types.
        
    Returns:
        A list of result dictionaries with validation status.
    """
    results = []
    total_rows = len(df)
    
    for col, expected in expected_dtypes.items():
        if col not in df.columns:
            results.append({
                "check": "Data Type Validation",
                "column": col,
                "status": "Fail",
                "details": f"Expected column '{col}' is missing from the dataset."
            })
            continue
            
        actual_dtype = df[col].dtype
        
        # Check for matching types
        is_match = False
        if expected == "int":
            is_match = pd.api.types.is_integer_dtype(actual_dtype)
        elif expected == "float":
            is_match = pd.api.types.is_float_dtype(actual_dtype)
        elif expected == "string":
            # In pandas, string columns are usually loaded as object or string type
            is_match = (
                pd.api.types.is_string_dtype(actual_dtype) or 
                pd.api.types.is_object_dtype(actual_dtype) or 
                isinstance(actual_dtype, pd.CategoricalDtype)
            )
        elif expected == "date":
            is_match = pd.api.types.is_datetime64_any_dtype(actual_dtype)
            
        if is_match:
            results.append({
                "check": "Data Type Validation",
                "column": col,
                "status": "Pass",
                "details": f"Column matches expected type '{expected}' (actual: {actual_dtype})."
            })
            continue
            
        # If no match, check if values can be coerced
        coercion_possible = False
        coerced_series = None
        original_null_count = int(df[col].isnull().sum())
        
        try:
            if expected == "int":
                coerced_series = pd.to_numeric(df[col], errors='coerce')
                if coerced_series.notnull().any():
                    # Check if numeric values are integer-like
                    non_nulls = coerced_series.dropna()
                    if (non_nulls % 1 == 0).all():
                        coercion_possible = True
            elif expected == "float":
                coerced_series = pd.to_numeric(df[col], errors='coerce')
                if coerced_series.notnull().any():
                    coercion_possible = True
            elif expected == "date":
                coerced_series = pd.to_datetime(df[col], errors='coerce')
                if coerced_series.notnull().any():
                    coercion_possible = True
            elif expected == "string":
                # Any column can be converted to string, so coercion is always possible
                coercion_possible = True
        except Exception:
            coercion_possible = False
            
        if coercion_possible:
            if coerced_series is not None:
                new_nulls = int(coerced_series.isnull().sum()) - original_null_count
                new_null_rate = new_nulls / total_rows if total_rows > 0 else 0.0
            else:
                new_nulls = 0
                new_null_rate = 0.0
                
            # Allow coercion warning only if new null rate is under 10%
            if new_null_rate <= 0.10:
                status = "Warning"
                details = (
                    f"Type mismatch: expected '{expected}', actual was {actual_dtype}. "
                    f"Values are coercible (introduced {new_nulls} new null(s), {new_null_rate:.1%})."
                )
            else:
                status = "Fail"
                details = (
                    f"Type mismatch: expected '{expected}', actual was {actual_dtype}. "
                    f"Coercion would discard too many values (introduced {new_nulls} null(s), {new_null_rate:.1%})."
                )
        else:
            status = "Fail"
            details = f"Type mismatch: expected '{expected}', actual was {actual_dtype}. Values cannot be coerced."
            
        results.append({
            "check": "Data Type Validation",
            "column": col,
            "status": status,
            "details": details
        })
        
    return results
