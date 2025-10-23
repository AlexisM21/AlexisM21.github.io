from db import get_conn
import sqlite3
# Purpose of CRUD
# Low level operation with Database
# Executes Raw SQL and returns plain python dicts
# No validation, data type enforcement - Just whatever is on the SQLite DB


def get_sections(value: str | None = None):
    with get_conn() as c:
        row = c.execute("SELECT * FROM section WHERE crn=?", (value,)).fetchone()
        return dict(row) if row else None
    

def get_all_sections():
    with get_conn() as c:
        table = c.execute("SELECT * FROM section")
        rows = table.fetchall()

        results = [dict(row) for row in rows]

        return results