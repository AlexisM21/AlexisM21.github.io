from fastapi import FastAPI, APIRouter, HTTPException, File, UploadFile
from typing import Optional, List, Dict, Any
from collections import OrderedDict
from services import csv_scraper_service
from crud import open_class_list_crud
from db import get_conn

router = APIRouter()


@router.post("/open/upload")
async def upload_csv(file: UploadFile = File(...)):
    # Check if CSV file
    if file.content_type != "text/csv":
        raise HTTPException(
            status_code=400,
            detail=f"Invalid file type: {file.content_type}. Only CSV files are allowed!"
        )

    try:
        contents = await file.read()

        results = csv_scraper_service.scrape_csv(contents)
        if results.get("status") == "error":
            raise HTTPException(status_code=400, detail=results.get("errors",["Unknown error"]))
        
        return {
            "message" : "CSV Update Completed.",
            "inserted" : results.get("inserted", []),
            "errors" : results.get("errors", []),
        }
    
    except HTTPException:
         raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Upload failed: {e}")


@router.get("/open")
def get_all_open_classes():
    return {"data": open_class_list_crud.get_open_class_list()}

def group_rows(rows: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    grouped = OrderedDict()
    for r in rows:
        key = (r["term"], str(r["crn"]))
        if key not in grouped:
            grouped[key] = {
                "term": r["term"],
                "crn": str(r["crn"]),
                "course_id": r.get("course_id"),
                "subject": r.get("subject"),
                "number": r.get("number"),
                "units": r.get("units"),
                "prereq": r.get("prereq"),
                "coreq": r.get("coreq"),
                "section": r.get("section"),
                "professor": r.get("professor"),
                "status": r.get("status"),
                "meetings": []
            }
        grouped[key]["meetings"].append({
            "day": r.get("day_of_week"),
            "start": r.get("start_min"),
            "end": r.get("end_min"),
            "room": r.get("room")
        })
    return list(grouped.values())


def normalize_days_param(days_raw: Optional[str]) -> List[str]:
    """Accept comma-separated 'Mon,Wed' or a single day string. Normalize to capitalized short names."""
    if not days_raw:
        return []
    parts = [p.strip() for p in days_raw.split(",") if p.strip()]
    # optional normalization map if you accept Monday -> Mon, etc.
    mapping = {
        "MONDAY": "Mon", "TUESDAY": "Tue", "WEDNESDAY": "Wed",
        "THURSDAY": "Thu", "FRIDAY": "Fri", "SATURDAY": "Sat", "SUNDAY": "Sun",
        "MON": "Mon", "TUE": "Tue", "WED": "Wed", "THU": "Thu", "FRI": "Fri", "SAT": "Sat", "SUN": "Sun"
    }
    out = []
    for p in parts:
        key = p.upper()
        out.append(mapping.get(key, p))  # if unknown, pass through
    return out

def overlaps_time_condition_sql(has_start_end: bool, has_start_only: bool, has_end_only: bool) -> str:
    """
    Returns SQL snippet for meeting time overlapping conditions using m.start_min/m.end_min.
    When both start and end provided: (m.end_min > ? AND m.start_min < ?)
    When only start_after provided: m.start_min >= ?
    When only end_before provided: m.end_min <= ?
    """
    if has_start_end:
        return "(m.end_min > ? AND m.start_min < ?)"
    if has_start_only:
        return "(m.start_min >= ?)"
    if has_end_only:
        return "(m.end_min <= ?)"
    return ""

@router.get("/open/query")
def openclasses_query(
    term: Optional[str] = None,
    subject: Optional[str] = None,   # e.g., "CPSC"
    course: Optional[str] = None,    # e.g., "CPSC 120A" (partial match supported)
    crn: Optional[str] = None,
    only_open: bool = True,
    # time filters (minutes since midnight). Examples:
    # 10:30 AM -> 10*60 + 30 -> 630
    time_start: Optional[int] = None,   # window start (inclusive) OR "start after" when time_end is None
    time_end: Optional[int] = None,     # window end (exclusive)
    # days: comma-separated short day names like "Mon,Wed" (or "Monday,Wednesday")
    days: Optional[str] = None,
    # days_mode: "any" (class has a meeting on at least one of the listed days)
    # or "all" (class has meetings on every listed day)
    days_mode: str = "any"
):
    """
    Query open_classes view with flexible filters:
      - subject (e.g., CPSC)
      - course (partial match on course_id)
      - term, crn, only_open
      - time_start/time_end (minutes from midnight): class matches if any meeting overlaps the window
      - days (csv): 'Mon,Wed'
      - days_mode: 'any' or 'all' (default 'any')
    Returns: list of objects grouped by (term,crn) with meetings array.
    """
    try:
        where_clauses = []
        params: List[Any] = []

        if term:
            where_clauses.append("UPPER(term) = UPPER(?)")
            params.append(term)

        if subject:
            # match subject column exactly or partial; normalize
            where_clauses.append("UPPER(subject) = UPPER(?)")
            params.append(subject)

        if course:
            where_clauses.append("UPPER(course_id) LIKE UPPER(?)")
            params.append(f"%{course}%")

        if crn:
            where_clauses.append("crn = ?")
            params.append(str(crn))

        if only_open:
            where_clauses.append("LOWER(status) LIKE 'open%'")

        # time filters: build SQL condition for meeting overlap when both time_start and time_end supplied,
        # or simple start_min >= time_start when only start provided, or end_min <= time_end when only end provided.
        has_start_end = (time_start is not None and time_end is not None)
        has_start_only = (time_start is not None and time_end is None)
        has_end_only = (time_end is not None and time_start is None)

        time_sql = overlaps_time_condition_sql(has_start_end, has_start_only, has_end_only)
        if time_sql:
            where_clauses.append(time_sql)
            # append params in the same order as SQL expects:
            if has_start_end:
                params.append(time_start)
                params.append(time_end)
            elif has_start_only:
                params.append(time_start)
            elif has_end_only:
                params.append(time_end)

        # days: we support two modes:
        #  - days_mode == "any": add SQL WHERE m.day_of_week IN (...) so DB filters rows that are on those days
        #  - days_mode == "all": do not filter rows in SQL (we'll check availability of all days after grouping)
        required_days = normalize_days_param(days)
        if required_days and days_mode.lower() == "any":
            # build a SQL IN clause with one placeholder per day
            placeholders = ",".join("?" for _ in required_days)
            where_clauses.append(f"m.day_of_week IN ({placeholders})")
            params.extend(required_days)

        where_sql = ("WHERE " + " AND ".join(where_clauses)) if where_clauses else ""

        sql = f"""
        SELECT term, crn, course_id, subject, number, units, prereq, coreq,
               section, professor, status, day_of_week, start_min, end_min, room
        FROM open_classes
        {where_sql}
        ORDER BY term, course_id, crn;
        """

        with get_conn() as conn:
            cur = conn.execute(sql, params)
            cols = [c[0] for c in cur.description]
            rows = [dict(zip(cols, row)) for row in cur.fetchall()]

        grouped = group_rows(rows)

        # If days_mode == 'all', filter groups to only those which include **all** required_days
        if required_days and days_mode.lower() == "all":
            required_set = set(required_days)
            filtered = []
            for g in grouped:
                meeting_days = set([m.get("day") for m in g.get("meetings", []) if m.get("day")])
                # require that meeting_days contains every required day
                if required_set.issubset(meeting_days):
                    filtered.append(g)
            grouped = filtered

        # If time filters were applied in SQL partly or not at all, ensure final safety: if time window present,
        # we keep only groups that have at least one meeting overlapping the requested window.
        if (has_start_end or has_start_only or has_end_only):
            def meeting_overlaps(meet):
                s = meet.get("start", -1) if meet.get("start") is not None else -1
                e = meet.get("end", -1) if meet.get("end") is not None else -1
                # treat TBA (-1) as match
                if s < 0 or e < 0:
                    return True
                if has_start_end:
                    return not (e <= time_start or s >= time_end)
                if has_start_only:
                    return s >= time_start
                if has_end_only:
                    return e <= time_end
                return True
            final = []
            for g in grouped:
                if any(meeting_overlaps(m) for m in g.get("meetings", [])):
                    final.append(g)
            grouped = final

        return grouped

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

