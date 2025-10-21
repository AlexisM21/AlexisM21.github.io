from db import get_conn
import sqlite3

def get_courses(value: str | None = None):
    with get_conn() as c:
        row = c.execute("SELECT * FROM course WHERE course_id=?", (value,)).fetchone()
        return dict(row) if row else None
    
def get_all_courses():
    with get_conn() as c:
        table = c.execute("SELECT * FROM course")
        rows = table.fetchall()

        results = [dict(row) for row in rows]

        return results

    
    