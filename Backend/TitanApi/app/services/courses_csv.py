import pandas as pd
import io
import sqlite3
from db import get_conn


def scrape_courses_csv(file_bytes: bytes, table_name : str):
    df = pd.read_csv(io.BytesIO(file_bytes)) # Converts bytes to a DataFrame

    #clean possible issues
    df = df.loc[:, ~df.columns.str.contains('^Unnamed')]
    df.columns = df.columns.str.strip().str.lower()

    with get_conn() as c:
        df.to_sql(table_name, c, if_exists="append",index=False)
        count = len(df)

    return count