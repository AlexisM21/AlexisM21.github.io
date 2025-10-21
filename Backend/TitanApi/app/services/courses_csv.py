import pandas as pd
import io
import sqlite3
from services import courses_validator
from db import get_conn



REQUIRED = {
        "course_id": "string",
        "subject": "string",
        "number": "string",
        # "description": "string",
        "units": "float",
        # "prereq": "string",
        # "coreq": "string",
    }

def scrape_courses_csv(file_bytes: bytes, table_name : str):

    
    df = pd.read_csv(io.BytesIO(file_bytes)) # Converts bytes to a DataFrame

    # Seeing if Valid CSV
    errors = courses_validator.validate_df(df, REQUIRED)

    if errors != []:
        return {"status": "error", "errors": errors}
    
    #If duplicates
    df = df.drop_duplicates(subset=["course_id"], keep="last")

    #clean possible issues
    df = df.loc[:, ~df.columns.str.contains('^Unnamed')]
    df.columns = df.columns.str.strip().str.lower()



    with get_conn() as c:
        insert_query = """
                        INSERT OR IGNORE INTO course (course_id, subject, number, description, units, prereq, coreq)
                        VALUES (?,?,?,?,?,?,?)
                        """
        
        rows_inserted = 0
        before = c.total_changes
        for _, row in df.iterrows():
            c.execute(insert_query, tuple(row))
        rows_inserted = c.total_changes - before


        # df.to_sql(table_name, c, if_exists="append",index=False)
        # count = len(df)
        # return count
        return {"status": "OK", "inserted": rows_inserted, "skipped": len(df) - rows_inserted}