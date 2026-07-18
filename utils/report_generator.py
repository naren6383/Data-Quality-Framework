import pandas as pd

def summarize(results: list[dict]) -> dict:
    """
    Aggregate all check results into:
    - total: total number of individual checks run
    - passed: count of status == 'Pass'
    - warnings: count of status == 'Warning'
    - failed: count of status == 'Fail'
    - pass_rate: round(passed / total * 100, 1) if total > 0 else 0
    
    Args:
        results: List of validation result dictionaries.
        
    Returns:
        Dictionary of aggregated stats.
    """
    total = len(results)
    passed = sum(1 for r in results if r["status"] == "Pass")
    warnings = sum(1 for r in results if r["status"] == "Warning")
    failed = sum(1 for r in results if r["status"] == "Fail")
    
    pass_rate = round((passed / total) * 100, 1) if total > 0 else 0.0
    
    return {
        "total": total,
        "passed": passed,
        "warnings": warnings,
        "failed": failed,
        "pass_rate": pass_rate
    }

def generate_summary_text(summary: dict) -> str:
    """
    Return a natural-language one-liner.
    
    Adjust tone based on pass_rate:
    - >=90%: positive/reassuring tone
    - 70-89%: neutral, "generally good but review these items"
    - <70%: cautionary, "significant data quality issues detected"
    
    Args:
        summary: Aggregated check statistics.
        
    Returns:
        Natural language string describing the quality summary.
    """
    pass_rate = summary["pass_rate"]
    failed = summary["failed"]
    warnings = summary["warnings"]
    
    base_msg = (
        f"Your dataset passed {pass_rate}% of quality checks. "
        f"{failed} critical issue(s) need attention and {warnings} warning(s) should be reviewed."
    )
    
    if pass_rate >= 90.0:
        return f"✨ **Reassuring:** {base_msg} The overall data health is excellent."
    elif pass_rate >= 70.0:
        return f"ℹ️ **Neutral:** {base_msg} The dataset is generally in good shape but has a few issues to review."
    else:
        return f"🚨 **Cautionary:** {base_msg} Significant data quality issues were detected. Review and clean the raw data."

def get_key_findings(results: list[dict]) -> list[str]:
    """
    Analyze the results list and extract 2-3 key findings.
    
    Args:
        results: List of validation result dictionaries.
        
    Returns:
        List of key findings string bullets.
    """
    findings = []
    
    # 1. Missing values findings
    missing_issues = [r for r in results if r["check"] == "Missing Values" and r["status"] in ("Warning", "Fail")]
    # Sort them by amount of missing values if we could, but let's list the failed ones first
    for r in missing_issues:
        severity_label = "critical missing values" if r["status"] == "Fail" else "missing values"
        findings.append(f"Column **{r['column']}** has {severity_label}: {r['details']}")

    # 2. Duplicates findings
    dup_issues = [r for r in results if r["check"] in ("Duplicate Rows", "Duplicate Keys") and r["status"] == "Fail"]
    for r in dup_issues:
        findings.append(f"**Uniqueness issue** detected: {r['details']}")

    # 3. Data type mismatch findings
    dtype_issues = [r for r in results if r["check"] == "Data Type Validation" and r["status"] in ("Warning", "Fail")]
    for r in dtype_issues:
        findings.append(f"Column **{r['column']}** has data type mismatch: {r['details']}")

    # 4. Schema mismatch findings
    schema_issues = [r for r in results if r["check"] == "Schema Validation" and r["status"] in ("Warning", "Fail")]
    for r in schema_issues:
        findings.append(f"**Schema validation discrepancy**: {r['details']}")

    # If no warnings or failures
    if not findings:
        findings.append("No critical issues or warnings found in the dataset. All parameters met the expected criteria!")

    # Return top 3 findings
    return findings[:3]
