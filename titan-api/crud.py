#crud.py
import sqlite3
from db import get_conn


def get_term(given: str):
    with get_conn() as conn:
        row = conn.execute("SELECT * FROM term WHERE term=:term",
                     {'term' : given}).fetchone()
        return dict(row) if row else None

def insert_term(given: str):
    with get_conn() as conn:
        try:
            cur = conn.execute("INSERT INTO term (term) VALUES (:term)",
                        {'term' : given.strip()})
        except sqlite3.IntegrityError:
            return None # Term already EXITST (unique constraint)
        
        row = conn.execute("SELECT term_id, term FROM term WHERE term_id = ?", (cur.lastrowid,)).fetchone() 
        return dict(row)
    
def delete_term(term_id: int | None = None, term: str | None = None) -> bool:
    with get_conn() as conn:
            if term_id is not None:
                cur = conn.execute("DELETE FROM term WHERE term_id=?", (term_id,))
            else:
                cur = conn.execute("DELETE FROM term WHERE term=?",(term,))
            return cur.rowcount > 0

def terms_table():
    with get_conn() as conn:
        rows = conn.execute("SELECT term_id, term FROM term ORDER BY term_id").fetchall()
        return [dict(r) for r in rows]








# import sqlite3
# from .db import get_conn

# def list_terms(limit: int = 100, offset: int = 0):
#     with get_conn() as conn:
#         rows = conn.execute(
#             "SELECT term_id, term, start_date, end_date FROM term ORDER BY term_id LIMIT ? OFFSET ?",
#             (limit, offset)
#         ).fetchall()
#         return [dict(r) for r in rows]

# def add_term(term: str, start_date: str | None = None, end_date: str | None = None):
#     with get_conn() as conn:
#         try:
#             cur = conn.execute(
#                 "INSERT INTO term(term, start_date, end_date) VALUES (?,?,?)",
#                 (term.strip(), start_date, end_date)
#             )
#         except sqlite3.IntegrityError as e:
#             # e.g., UNIQUE constraint failed
#             raise
#         new_row = conn.execute(
#             "SELECT term_id, term, start_date, end_date FROM term WHERE term_id = ?",
#             (cur.lastrowid,)
#         ).fetchone()
#         return dict(new_row)