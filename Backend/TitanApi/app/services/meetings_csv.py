import pandas as pd
import io
import sqlite3
from db import get_conn
from schemas import MeetingIn
from pydantic import ValidationError
from typing import Any, Dict, List
## DELETE ##

REQUIRED_HEADERS = {"term","crn","day_of_week","start_min","end_min","room"}
ALL_COLLS = ["crn","day_of_week","start_min","end_min","room"]


def scrape_meetings_csv(file_bytes: bytes, table_name : str):

    df = pd.read_csv(io.BytesIO(file_bytes)) # Converts bytes to a DataFrame
    df.columns = df.columns.str.strip().str.lower() # Normalizes Data

    missing = [c for c in REQUIRED_HEADERS if c not in df.columns]
    if missing:
        return {"status": "error", "errors": [f"Missing columns: {missing}"]}
    
    keep = ["crn","day_of_week","start_min","end_min","room"]

    # Loops through the dataframe df and checks the colums. It will only keep what is matched in the keep list above
    valid_columns = []

    for c in keep:
        if c in df.columns:
            valid_columns.append(c)
    
    df.drop_duplicates(subset=["crn"], keep="last")

    valid: List[MeetingIn] = []
    errors: List[str] = []

    # Loops through all rows
    # Validates each variable to make sure it matches with the SectionIn Schema (Find it in Schema file)
    # if not record errors
    # If none were valid, stop and return error

    
    for i, row in df.iterrows():
        # 1) Convert NaN -> None
        cleaned_values = {}
        for k, v in row.items():
            cleaned_values[k] = None if pd.isna(v) else v

        # 2) Ensure expected keys exist (fill missing optional keys with None)
        for k in keep:
            cleaned_values.setdefault(k, None)

        # 3) Validate once with Pydantic
        try:
            model = MeetingIn(**cleaned_values)   # or SectionIn(**cleaned_values)
            valid.append(model)
        except ValidationError as e:
            for err in e.errors():
                field = ".".join(str(p) for p in err.get("loc", [])) or "<unknown>"
                msg = err.get("msg", "Invalid value")
                bad_val = cleaned_values.get(field, "<missing>")
                # +2 because CSV header is row 1, DataFrame index starts at 0
                errors.append(f"row {i+2} (field '{field}', value={bad_val!r}): {msg}")

        if not valid:
            return {"status": "error", "errors": errors or ["No valid rows."]}
        
    rows_inserted = 0
    try:
        with get_conn() as c:
            before = c.total_changes
            insert_query = """
                            INSERT OR IGNORE INTO meeting (crn, day_of_week, start_min, end_min, room)
                            VALUES (?,?,?,?,?)
                            """
            for m in valid:
                c.execute(
                    insert_query, 
                    (
                        m.crn,
                        m.day_of_week,
                        m.start_min,
                        m.end_min,
                        m.room,
                    )
                )
                rows_inserted = c.total_changes - before
    except Exception as e:
        return {"status" : "error", "errors": [f"DB error:: {e}"]}

    return {
        "status": "ok",
        "inserted": rows_inserted,
        "ignored": len(valid) - rows_inserted,
        "errors": errors, 
    }