from db import get_conn
import sqlite3


def if_helper(value : int | str) ->bool:
    if isinstance(value, int):
        return True
    else:
        return False

def get_terms(value : str):
    with get_conn() as c:
        if isinstance(value, str):
            row = c.execute("SELECT * FROM term WHERE term=?" , (value,)).fetchone()
        else:
            row = c.execute("SELECT * FROM term WHERE term_id=?",(value,)).fetchone()
        return dict(row) if row else None
    
def delete_terms(value: int | str) -> int:
    with get_conn() as c:
        # c = get_terms(value)
        if isinstance(value, int):
            print("in int")
            current = c.execute("DELETE FROM term WHERE term_id=?", (value,))
        if isinstance(value, str):
            print ("in string")
            current = c.execute("DELETE FROM term WHERE term=?", (value,))

        return current.rowcount > 0
    
def create_terms(value: str):
    with get_conn() as c:
        try:
            cur = c.execute("INSERT INTO term(term) VALUES (?)", (value,))
        except sqlite3.IntegrityError:
            return None
        
        row = c.execute("SELECT term_id, term FROM term WHERE term_id = ?", (cur.lastrowid,)).fetchone() 
        return dict(row) 
    
