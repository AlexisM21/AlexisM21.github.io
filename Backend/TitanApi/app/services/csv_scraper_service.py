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
        row = c.execute("SELECT term_id FROM term WHERE term = ?",(term_input,)).fetchone()

        if row:
            return row[0]
        c.execute("INSERT INTO term (term) VALUES (?)", (term_input,))
        return c.lastrowid
    



REQUIRED_HEADERS = {"term", "course_id", "crn", "section", "day_of_week", "start_min","end_min","room","instruction_mode","professor","status"}

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
    # df = pd.read_csv(io.BytesIO(file_bytes)) # Converts bytes to a DataFrame
    df.columns = df.columns.str.strip().str.lower() # Normalizes Data

    # 2) Validate headers
    missing = [c for c in REQUIRED_HEADERS if c not in df.columns]
    if missing:
        return {"status": "error", "errors": [f"Missing columns: {missing}"]}
    
    # turns NaN -> None
    df = df.where(pd.notna(df), None)

    terms_table = ["term"]
    meetings_table = ["term", "crn", "day_of_week", "start_min", "end_min", "room"]
    sections_table = ["crn","course_id","term","section","instruction_mode","professor","status"]

    # returns error if something is wrong
    # for terms table
    term_status = scrape_term(df, terms_table)
    if(term_status.get("status") == "error"):
        return term_status
    # for sections table
    section_status = scrape_sections(df, sections_table)
    if(section_status.get("status") == "error"):
        return section_status
    # for meetings table
    meeting_status = scrape_meetings(df, meetings_table)
    if(meeting_status.get("status") == "error"):
        return meeting_status
    
    return {
        "status" : "ok",
        "inserted": {
            "terms" : term_status.get("inserted_terms", 0),
            "sections" : section_status.get("inserted", 0),
            "meetings" : meeting_status.get("inserted",0),
        },
        "errors" : (section_status.get("errors",[]) + meeting_status.get("errors",[])),
    }


def scrape_term(df: pd.DataFrame, keep_terms):
    df = df.drop_duplicates(subset=["term"],keep="last")

    insert_query = """
                    INSERT OR IGNORE INTO term (term) VALUES (?)
                    """
    inserted_count = 0
    with get_conn() as c:
        before = c.total_changes
        for term in df["term"].dropna():
            c.execute(insert_query, (str(term),))
        inserted_count = c.total_changes - before # counts new insertions

    return {"status" : "ok", "inserted_terms" : inserted_count}




def scrape_sections(df: pd.DataFrame, keep_sections: list[str]):

    df = df.drop_duplicates(subset=["crn", "term"], keep="last")

    valid: List[SectionIn] = []
    errors: List[str] = []

    # Creates Cache to store term mappings
    # Loops through term column in df
    term_cache: dict[str, int] = {}
    for term_name in df["term"].dropna().unique():
        term_cache[term_name] = get_or_create_term_id(term_name)

    # Loops through all rows
    # Validates each variable to make sure it matches with the SectionIn Schema (Find it in Schema file)
    # if not record errors
    # If none were valid, stop and return error

    
    for i, row in df.iterrows():

        cleaned_values = dict(row)

        # 2) Ensure expected keys exist (fill missing optional keys with None)
        for k in keep_sections:
            cleaned_values.setdefault(k, None)

        # 3) Convert term to term_id
        term_name = cleaned_values.pop("term", None) # remove "term" (string)
        if term_name is not None:
            tid = term_cache.get(term_name)
            if tid is None:
                # In case it was not in the list originally
                tid = get_or_create_term_id(term_name)
                term_cache[term_name] = tid
            cleaned_values["term_id"] = tid
        else:
            cleaned_values["term_id"] = None

        # 3) Validate once with Pydantic
        try:
            model = SectionIn(**cleaned_values)   # or SectionIn(**cleaned_values)
            valid.append(model)
        except ValidationError as e:
            for err in e.errors():
                field = ".".join(str(p) for p in err.get("loc", [])) or "<unknown>"
                msg = err.get("msg", "Invalid value")
                bad_val = cleaned_values.get(field, "<missing>")
                # +2 because CSV header is row 1, DataFrame index starts at 0
                errors.append(f"row {i+2} (field '{field}', value={bad_val!r}): {msg}")

    if not valid:
        return {"status": "error", "errors": errors or ["No valid section rows."]}
    
    # 5) Insert into DB    
    rows_inserted = 0

    try:
        with get_conn() as c:
            before = c.total_changes
            insert_query = """
                            INSERT OR IGNORE INTO section (crn, course_id, term_id, section, instruction_mode, professor, status)
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
                        m.status
                    )
                )
                rows_inserted = c.total_changes - before
    except Exception as e:
        return {"status" : "error", "errors": [f"DB error:: {e}"]}

    return {
        "status": "ok",
        "inserted": rows_inserted,
        "ignored": len(valid) - rows_inserted,
        "errors": errors, 
    }


def scrape_meetings(df: pd.DataFrame, keep_meetings: list[str]):

    valid: List[MeetingIn] = []
    errors: List[str] = []

    # Creates Cache to store term mappings
    # Loops through term column in df
    term_cache: dict[str, int] = {}
    for term_name in df["term"].dropna().unique():
        term_cache[term_name] = get_or_create_term_id(term_name)

    # Loops through all rows
    # Validates each variable to make sure it matches with the SectionIn Schema (Find it in Schema file)
    # if not record errors
    # If none were valid, stop and return error

    
    for i, row in df.iterrows():
        # 1) Convert NaN -> None
        cleaned_values = dict(row)

        # 2) Ensure expected keys exist (fill missing optional keys with None)
        for k in keep_meetings:
            cleaned_values.setdefault(k, None)

        # 3) Convert term to term_id
        term_name = cleaned_values.pop("term", None) # remove "term" (string)
        if term_name is not None:
            tid = term_cache.get(term_name)
            if tid is None:
                # In case it was not in the list originally
                tid = get_or_create_term_id(term_name)
                term_cache[term_name] = tid
            cleaned_values["term_id"] = tid
        else:
            cleaned_values["term_id"] = None

        # 3) Validate once with Pydantic
        try:
            model = MeetingIn(**cleaned_values)   # or SectionIn(**cleaned_values)
            valid.append(model)
        except ValidationError as e:
            for err in e.errors():
                field = ".".join(str(p) for p in err.get("loc", [])) or "<unknown>"
                msg = err.get("msg", "Invalid value")
                bad_val = cleaned_values.get(field, "<missing>")
                # +2 because CSV header is row 1, DataFrame index starts at 0
                errors.append(f"row {i+2} (field '{field}', value={bad_val!r}): {msg}")

    if not valid:
        return {"status": "error", "errors": errors or ["No valid rows."]}
    
    # 5) Insert into DB    
    rows_inserted = 0
    try:
        with get_conn() as c:
            before = c.total_changes
            insert_query = """
                            INSERT INTO meeting (term_id, crn, day_of_week, start_min, end_min, room)
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
                    )
                )
                rows_inserted = c.total_changes - before
    except Exception as e:
        return {"status" : "error", "errors": [f"DB error:: {e}"]}

    return {
        "status": "ok",
        "inserted": rows_inserted,
        "ignored": len(valid) - rows_inserted,
        "errors": errors, 
    }

