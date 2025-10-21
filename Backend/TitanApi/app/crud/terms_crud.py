from db import get_conn
import sqlite3

def get_terms(value : str):
    with get_conn() as c:
        if isinstance(value, str):
            row = c.execute("SELECT * FROM term WHERE term=?" , (value,)).fetchone()
        else:
            row = c.execute("SELECT * FROM term WHERE term_id=?",(value,)).fetchone()
        return dict(row) if row else None
    
def delete_terms(term_id: int | None = None, term: str | None = None) -> bool:
    with get_conn() as c:
        if term_id is not None:
            cur = c.execute("DELETE FROM term WHERE term_id=?", (term_id,))
        else:
            cur = c.execute("DELETE FROM term WHERE term=?", (term,))
        return cur.rowcount > 0
    
def create_terms(value: str):
    with get_conn() as c:
        try:
            cur = c.execute("INSERT INTO term(term) VALUES (?)", (value,))
        except sqlite3.IntegrityError:
            return None
        
        row = c.execute("SELECT term_id, term FROM term WHERE term_id = ?", (cur.lastrowid,)).fetchone() 
        return dict(row) 
    
def get_all_terms():
    with get_conn() as c:
        table = c.execute("SELECT * FROM term")
        rows = table.fetchall()

        results = [dict(row) for row in rows]

        return results
    
