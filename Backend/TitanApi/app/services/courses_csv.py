import pandas as pd
import io
import sqlite3
from db import get_conn
from schemas import CourseIn
from pydantic import ValidationError
from typing import Any, Dict, List


REQUIRED_HEADERS = {"course_id", "subject", "number", "units"}
ALL_COLS = ["course_id", "subject", "number", "description", "units", "prereq", "coreq"]






def scrape_courses_csv(file_bytes: bytes, table_name : str):

    
    df = pd.read_csv(io.BytesIO(file_bytes)) # Converts bytes to a DataFrame
    df.columns = df.columns.str.strip().str.lower() # Normalizes Data

    # Check for missing required columns from CSV
    missing = [c for c in REQUIRED_HEADERS if c not in df.columns]
    if missing:
        return {"status": "error", "errors": [f"Missing columns: {missing}"]}
    
    # Keeps only the following columns from CSV
    keep = ["course_id", "subject", "number", "description", "units", "prereq", "coreq"]

    # Loops through the dataframe df and checks the colums. It will only keep what is matched in the keep list above
    valid_columns = []

    for c in keep:
        if c in df.columns:
            valid_columns.append(c)

    # Drop duplucates 
    df.drop_duplicates(subset=["course_id"], keep="last")

    valid: List[CourseIn] = []
    errors: List[str] = []

    # Loops through all rows
    # Validates each variable to make sure it matches with the CourseIn Schema (Find it in Schema file)
    # if not record errors
    # If none were valid, stop and return error

    for i, row in df.iterrows():
        try: 
            cleaned_values = {} # Empty Dictionary
            # We have to convert Pandas' NaN to Python None
            # Loops through each row item. If NaN exist key that value into the cleaned_values dict and set it = None
            # else Store it normally
            for k, v in row.items():
                if pd.isna(v): 
                    cleaned_values[k] = None
                else:
                    cleaned_values[k] = v
            # Make sure every key we NEED is in dict
            # Loops through keep which we stored our needed columns and checks them
            for k in keep:
                cleaned_values.setdefault(k, None)

            # Creates Pydantic object of our Cleaned/Validated Data into the value valid
            valid.append(CourseIn(**cleaned_values))
        except ValidationError as e:
            errors.append(F"row {i + 2}: {e.errors()[0]['msg']}")

        if not valid:
            return {"status": "error", "errors": errors or ["No valid rows."]}

    # Seeing if Valid CSV
    # errors = courses_validator.validate_df(df, REQUIRED)

    # if errors != []:
    #     return {"status": "error", "errors": errors}
    
    # #If duplicates
    # df = df.drop_duplicates(subset=["course_id"], keep="last")

    # #clean possible issues
    # df = df.loc[:, ~df.columns.str.contains('^Unnamed')]
    # df.columns = df.columns.str.strip().str.lower()


    rows_inserted = 0
    try:
        with get_conn() as c:
            before = c.total_changes
            insert_query = """
                            INSERT OR IGNORE INTO course (course_id, subject, number, description, units, prereq, coreq)
                            VALUES (?,?,?,?,?,?,?)
                            """
            for m in valid:
                c.execute(
                    insert_query, 
                    (
                        m.course_id,
                        m.subject,
                        m.number,
                        m.description,
                        m.units,
                        m.prereq,
                        m.coreq
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
        
    #     before = c.total_changes
    #     for _, row in df.iterrows():
    #         c.execute(insert_query, tuple(row))
    #     rows_inserted = c.total_changes - before


    #     # df.to_sql(table_name, c, if_exists="append",index=False)
    #     # count = len(df)
    #     # return count
    #     return {"status": "OK", "inserted": rows_inserted, "skipped": len(df) - rows_inserted}