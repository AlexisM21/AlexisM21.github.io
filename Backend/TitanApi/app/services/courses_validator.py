import pandas as pd
import io

#CSV VALIDATOR
def validate_df(df: pd.DataFrame, required_cols: dict) -> list[str]:
    """
    required_cols = {
    "course_id": "string",
    "subject" : "string",
    "number" : "string",
    "units": "float",
    }
    """

    errors =[]
    df.columns = df.columns.str.strip().str.lower()

    # Check for missing required columns
    missing = [c for c in required_cols if c not in df.columns]
    if missing:
        errors.append(f"Missing columns: {missing}")
        return errors
    
    # Check for nulls
    for col in required_cols:
        if df[col].isna().any():
            errors.append(f"Column '{col}' has missing values.")

    # Type check (will try to convert)
    for col, dtype in required_cols.items():
        try:
            if dtype == "string":
                df[col] = df[col].astype("string").str.strip()
            elif dtype == "float":
                pd.to_numeric(df[col], errors="raise")
            elif dtype == "int":
                pd.to_numeric(df[col], errors="raise", downcast="integer")
        except Exception:
            errors.append(f"Column '{col}' cannot be converted to {dtype}.")

    return errors