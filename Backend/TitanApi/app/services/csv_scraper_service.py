import pandas as pd
import io
import sqlite3
from db import get_conn
from schemas import SectionIn, MeetingIn, CourseIn
from pydantic import ValidationError
from typing import Any, Dict, List

# Helper function to convert term -> term_id (create if missing)
def get_or_create_term_id(term_input: str) -> int:
    with get_conn() as c:
        row = c.execute(
            "SELECT term_id FROM term WHERE term = ?",
            (term_input,)
        ).fetchone()

        if row:
            return row[0]

        c.execute("INSERT INTO term (term) VALUES (?)", (term_input,))
        return c.lastrowid


REQUIRED_HEADERS = {
    "term", "course_id", "crn", "section",
    "day_of_week", "start_min", "end_min",
    "room", "instruction_mode", "professor", "status"
}


def scrape_csv(file_bytes: bytes):
    # 1) Load file into df and normalize
    df = pd.read_csv(
        io.BytesIO(file_bytes),
        dtype={
            "term": "string",
            "course_id": "string",
            "crn": "string",
            "section": "string",
            "instruction_mode": "string",
            "professor": "string",
            "status": "string",
            "room": "string",
        },
        converters={
            # Safely parse numeric meeting fields if present; keep missing as NA
            "day_of_week": lambda x: None if x == "" or pd.isna(x) else int(float(x)),
            "start_min":   lambda x: None if x == "" or pd.isna(x) else int(float(x)),
            "end_min":     lambda x: None if x == "" or pd.isna(x) else int(float(x)),
        },
        keep_default_na=True,  # keep NaN for truly missing
    )

    # Normalize column names
    df.columns = df.columns.str.strip().str.lower()

    # 2) Validate headers
    missing = [c for c in REQUIRED_HEADERS if c not in df.columns]
    if missing:
        return {"status": "error", "errors": [f"Missing columns: {missing}"]}

    # NaN -> None
    df = df.where(pd.notna(df), None)

    terms_table = ["term"]
    meetings_table = ["term", "crn", "day_of_week", "start_min", "end_min", "room"]
    sections_table = ["crn", "course_id", "term", "section", "instruction_mode", "professor", "status"]

    # Insert terms
    term_status = scrape_term(df, terms_table)
    if term_status.get("status") == "error":
        return term_status

    # Insert sections (may skip some)
    section_status = scrape_sections(df, sections_table)
    if section_status.get("status") == "error":
        return section_status

    # Insert meetings (may skip some)
    meeting_status = scrape_meetings(df, meetings_table)
    if meeting_status.get("status") == "error":
        return meeting_status

    return {
        "status": "ok",
        "inserted": {
            "terms": term_status.get("inserted_terms", 0),
            "sections": section_status.get("inserted", 0),
            "meetings": meeting_status.get("inserted", 0),
        },
        "errors": section_status.get("errors", []) + meeting_status.get("errors", []),
    }


def scrape_term(df: pd.DataFrame, keep_terms):
    # Only unique terms
    df = df.drop_duplicates(subset=["term"], keep="last")

    insert_query = """
        INSERT OR IGNORE INTO term (term) VALUES (?)
    """
    inserted_count = 0
    with get_conn() as c:
        before = c.total_changes
        for term in df["term"].dropna():
            c.execute(insert_query, (str(term),))
        inserted_count = c.total_changes - before  # new rows

    return {"status": "ok", "inserted_terms": inserted_count}


def scrape_sections(df: pd.DataFrame, keep_sections: List[str]):
    # One section per (crn, term)
    df = df.drop_duplicates(subset=["crn", "term"], keep="last")

    valid: List[SectionIn] = []
    errors: List[str] = []

    # Cache: term_name -> term_id
    term_cache: dict[str, int] = {}
    for term_name in df["term"].dropna().unique():
        term_cache[term_name] = get_or_create_term_id(term_name)

    # Cache: existing course_ids (so we can skip unknown courses)
    with get_conn() as c:
        rows = c.execute("SELECT course_id FROM course").fetchall()
    existing_course_ids = {row[0] for row in rows}

    # Build and validate section models
    for i, row in df.iterrows():
        cleaned_values = dict(row)

        # Ensure expected keys exist
        for k in keep_sections:
            cleaned_values.setdefault(k, None)

        # Convert term -> term_id
        term_name = cleaned_values.pop("term", None)
        if term_name is not None:
            tid = term_cache.get(term_name)
            if tid is None:
                tid = get_or_create_term_id(term_name)
                term_cache[term_name] = tid
            cleaned_values["term_id"] = tid
        else:
            cleaned_values["term_id"] = None

        # Skip rows whose course_id is not in the course table
        course_id = cleaned_values.get("course_id")
        if course_id is None or course_id not in existing_course_ids:
            errors.append(
                f"row {i+2}: Skipped section because course_id '{course_id}' does not exist in course table."
            )
            continue

        # Validate with Pydantic
        try:
            model = SectionIn(**cleaned_values)
            valid.append(model)
        except ValidationError as e:
            for err in e.errors():
                field = ".".join(str(p) for p in err.get("loc", [])) or "<unknown>"
                msg = err.get("msg", "Invalid value")
                bad_val = cleaned_values.get(field, "<missing>")
                errors.append(f"row {i+2} (field '{field}', value={bad_val!r}): {msg}")

    if not valid:
        return {"status": "error", "errors": errors or ["No valid section rows."]}

    # Insert into DB
    rows_inserted = 0
    try:
        with get_conn() as c:
            before = c.total_changes
            insert_query = """
                INSERT OR IGNORE INTO section (
                    crn, course_id, term_id, section,
                    instruction_mode, professor, status
                )
                VALUES (?,?,?,?,?,?,?)
            """
            for m in valid:
                c.execute(
                    insert_query,
                    (
                        m.crn,
                        m.course_id,
                        m.term_id,
                        m.section,
                        m.instruction_mode,
                        m.professor,
                        m.status,
                    ),
                )
            rows_inserted = c.total_changes - before
    except Exception as e:
        return {"status": "error", "errors": [f"DB error:: {e}"]}

    return {
        "status": "ok",
        "inserted": rows_inserted,
        "ignored": len(valid) - rows_inserted,
        "errors": errors,
    }


def scrape_meetings(df: pd.DataFrame, keep_meetings: List[str]):
    valid: List[MeetingIn] = []
    errors: List[str] = []

    # Cache: term_name -> term_id
    term_cache: dict[str, int] = {}
    for term_name in df["term"].dropna().unique():
        term_cache[term_name] = get_or_create_term_id(term_name)

    # Cache: existing (term_id, crn) pairs from section
    with get_conn() as c:
        rows = c.execute("SELECT term_id, crn FROM section").fetchall()
    existing_sections = {(row[0], row[1]) for row in rows}

    # Build and validate meeting models
    for i, row in df.iterrows():
        cleaned_values = dict(row)

        # Ensure expected keys exist
        for k in keep_meetings:
            cleaned_values.setdefault(k, None)

        # Convert term -> term_id
        term_name = cleaned_values.pop("term", None)
        if term_name is not None:
            tid = term_cache.get(term_name)
            if tid is None:
                tid = get_or_create_term_id(term_name)
                term_cache[term_name] = tid
            cleaned_values["term_id"] = tid
        else:
            cleaned_values["term_id"] = None

        term_id = cleaned_values.get("term_id")
        crn = cleaned_values.get("crn")

        # Skip meetings whose section does not exist
        if term_id is None or crn is None or (term_id, crn) not in existing_sections:
            errors.append(
                f"row {i+2}: Skipped meeting because section (term_id={term_id}, crn='{crn}') does not exist."
            )
            continue

        # Validate with Pydantic
        try:
            model = MeetingIn(**cleaned_values)
            valid.append(model)
        except ValidationError as e:
            for err in e.errors():
                field = ".".join(str(p) for p in err.get("loc", [])) or "<unknown>"
                msg = err.get("msg", "Invalid value")
                bad_val = cleaned_values.get(field, "<missing>")
                errors.append(f"row {i+2} (field '{field}', value={bad_val!r}): {msg}")

    if not valid:
        return {"status": "error", "errors": errors or ["No valid rows."]}

    # Insert into DB
    rows_inserted = 0
    try:
        with get_conn() as c:
            before = c.total_changes
            insert_query = """
                INSERT INTO meeting (
                    term_id, crn, day_of_week, start_min, end_min, room
                )
                VALUES (?,?,?,?,?,?)
                ON CONFLICT(term_id, crn, day_of_week) DO NOTHING;
            """
            for m in valid:
                c.execute(
                    insert_query,
                    (
                        m.term_id,
                        m.crn,
                        m.day_of_week,
                        m.start_min,
                        m.end_min,
                        m.room,
                    ),
                )
            rows_inserted = c.total_changes - before
    except Exception as e:
        return {"status": "error", "errors": [f"DB error:: {e}"]}

    return {
        "status": "ok",
        "inserted": rows_inserted,
        "ignored": len(valid) - rows_inserted,
        "errors": errors,
    }
