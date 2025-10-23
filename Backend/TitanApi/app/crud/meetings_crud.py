from db import get_conn
import sqlite3
# Purpose of CRUD
# Low level operation with Database
# Executes Raw SQL and returns plain python dicts
# No validation, data type enforcement - Just whatever is on the SQLite DB


def get_meetings(value: str | None = None):
    with get_conn() as c:
        row = c.execute("SELECT * FROM meeting WHERE crn=?", (value,)).fetchall()
        return [dict(r) for r in row] if row else []
    

def get_all_meetings():
    with get_conn() as c:
        table = c.execute("SELECT * FROM meeting")
        rows = table.fetchall()

        results = [dict(row) for row in rows]

        return results