import sqlite3
from contextlib import contextmanager
from pathlib import Path
## HELPER FUNCTION TO OPEN DB FILE
## ALSO PROVIDES FRESH CONNECTION PER REQUEST with connection: .....
## ALSO US TO ACCESS DATA VIA DICTS row["term"] OR dict(row)
ROOT = Path(__file__).resolve().parents[1]
DB_PATH = ROOT / "openclasslist.db"

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