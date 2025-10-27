import pandas as pd
import io
import sqlite3
from db import get_conn
from schemas import SectionIn
from pydantic import ValidationError
from typing import Any, Dict, List

## DELETE ##
REQUIRED_HEADERS = {"crn","course_id","term_id","instruction_mode","status"}
ALL_COLS = ["crn","course_id","term_id","section","instruction_mode","professor","status"]


def scrape_sections_csv(file_bytes: bytes, table_name : str):

    df = pd.read_csv(io.BytesIO(file_bytes)) # Converts bytes to a DataFrame
    df.columns = df.columns.str.strip().str.lower() # Normalizes Data

    missing = [c for c in REQUIRED_HEADERS if c not in df.columns]
    if missing:
        return {"status": "error", "errors": [f"Missing columns: {missing}"]}
    
    keep = ["crn","course_id","term_id","section","instruction_mode","professor","status"]

    # Loops through the dataframe df and checks the colums. It will only keep what is matched in the keep list above
    valid_columns = []

    for c in keep:
        if c in df.columns:
            valid_columns.append(c)
    
    df.drop_duplicates(subset=["crn"], keep="last")

    valid: List[SectionIn] = []
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
            model = SectionIn(**cleaned_values)   # or SectionIn(**cleaned_values)
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
                            INSERT OR IGNORE INTO section (crn, course_id, term_id, section, instruction_mode, professor, status)
                            VALUES (?,?,?,?,?,?,?)
                            """
            for m in valid:
                c.execute(
                    insert_query, 
                    (
                        m.crn,
                        m.course_id,
                        m.term_id,
                        m.section,
                        m.instruction_mode,
                        m.professor,
                        m.status
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