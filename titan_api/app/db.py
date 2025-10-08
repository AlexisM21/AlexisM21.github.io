import sqlite3
from contextlib import contextmanager
from pathlib import Path

HERE = Path(__file__).resolve()
ROOT = HERE.parents[2]
DB_PATH = ROOT / "TitanSchedulerDatabase" / "openclasslist.db" 

@contextmanager
def get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()
    