# app/routers/openclasses_router.py
import re
from fastapi import APIRouter, HTTPException, File, UploadFile
from typing import Optional, List, Dict, Any
from collections import OrderedDict

from services import csv_scraper_service
from crud import open_class_list_crud
from db import get_conn
from parser import PDF_parser

router = APIRouter()

# -----------------------
# Upload / simple get
# -----------------------
@router.post("/open/upload")
async def upload_csv(file: UploadFile = File(...)):
    if file.content_type != "text/csv":
        raise HTTPException(
            status_code=400,
            detail=f"Invalid file type: {file.content_type}. Only CSV files are allowed!"
        )
    try:
        contents = await file.read()
        results = csv_scraper_service.scrape_csv(contents)
        if results.get("status") == "error":
            raise HTTPException(status_code=400, detail=results.get("errors", ["Unknown error"]))
        return {
            "message": "CSV Update Completed.",
            "inserted": results.get("inserted", []),
            "errors": results.get("errors", []),
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Upload failed: {e}")


@router.get("/open")
def get_all_open_classes():
    return {"data": open_class_list_crud.get_open_class_list()}


# -----------------------
# Day helpers (DB stores days as numbers 1..7)
# -----------------------
DAY_NUM_TO_SHORT = {1: "Mon", 2: "Tue", 3: "Wed", 4: "Thu", 5: "Fri", 6: "Sat", 7: "Sun"}

# name/number -> int mapping
_DAY_NAME_TO_NUM = {
    "MONDAY": 1, "MON": 1, "MON.": 1, "1": 1,
    "TUESDAY": 2, "TUE": 2, "TUES": 2, "TUE.": 2, "2": 2,
    "WEDNESDAY": 3, "WED": 3, "WED.": 3, "3": 3,
    "THURSDAY": 4, "THU": 4, "THURS": 4, "THU.": 4, "4": 4,
    "FRIDAY": 5, "FRI": 5, "FRI.": 5, "5": 5,
    "SATURDAY": 6, "SAT": 6, "6": 6,
    "SUNDAY": 7, "SUN": 7, "7": 7
}

def normalize_single_day_token_to_num(tok: str) -> Optional[int]:
    if not tok:
        return None
    return _DAY_NAME_TO_NUM.get(tok.strip().upper())

def normalize_days_param(days_raw: Optional[str]) -> List[int]:
    """
    Accepts many formats and returns a sorted list of unique ints 1..7:
      - "Mon,Wed", "Monday Wednesday", "1,3", "1-3", "Mon-Thu"
    """
    if not days_raw:
        return []

    parts = re.split(r'[;,/]+|\s+(?![^-]*-)', days_raw.strip())
    result: List[int] = []
    seen = set()

    for p in parts:
        if not p:
            continue
        p = p.strip()
        # range like "1-3" or "Mon-Thu"
        if "-" in p:
            a, b = [x.strip() for x in p.split("-", 1)]
            a_num = normalize_single_day_token_to_num(a)
            b_num = normalize_single_day_token_to_num(b)
            if a_num is not None and b_num is not None:
                i, j = a_num, b_num
                if i <= j:
                    seq = list(range(i, j + 1))
                else:
                    seq = list(range(i, 8)) + list(range(1, j + 1))
                for d in seq:
                    if 1 <= d <= 7 and d not in seen:
                        result.append(d); seen.add(d)
                continue
            # fallthrough if range tokens not parseable

        n = normalize_single_day_token_to_num(p)
        if n is not None and 1 <= n <= 7 and n not in seen:
            result.append(n); seen.add(n)

    return sorted(result)


def normalize_db_meeting_day(raw_day: Any) -> str:
    """
    Convert DB numeric day (1..7 or numeric-string) to short label 'Mon'..'Sun'.
    Fallback to first-3-chars title-cased if unparseable.
    """
    if raw_day is None:
        return ""
    try:
        n = int(raw_day)
        return DAY_NUM_TO_SHORT.get(n, str(raw_day))
    except Exception:
        s = str(raw_day).strip()
        k = s.upper()
        n = _DAY_NAME_TO_NUM.get(k)
        if n:
            return DAY_NUM_TO_SHORT.get(n, s.title()[:3])
        return s.title()[:3]


# -----------------------
# Grouping & time helpers
# -----------------------
def group_rows(rows: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Group flat rows from open_classes view into objects keyed by (term, crn).
    Each meeting includes both 'day' (label) and 'day_num' (int or None).
    """
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

        raw_day = r.get("day_of_week")
        day_num = None
        try:
            if raw_day is not None:
                day_num = int(raw_day)
                if not (1 <= day_num <= 7):
                    day_num = None
        except Exception:
            day_num = None

        day_label = normalize_db_meeting_day(raw_day)

        grouped[key]["meetings"].append({
            "day": day_label,
            "day_num": day_num,
            "start": r.get("start_min"),
            "end": r.get("end_min"),
            "room": r.get("room")
        })
    return list(grouped.values())


def overlaps_time_condition_sql(has_start_end: bool, has_start_only: bool, has_end_only: bool) -> str:
    """
    SQL snippet using view columns start_min/end_min (no table alias).
    """
    if has_start_end:
        return "(end_min > ? AND start_min < ?)"
    if has_start_only:
        return "(start_min >= ?)"
    if has_end_only:
        return "(end_min <= ?)"
    return ""


# -----------------------
# Query endpoint (no pagination)
# -----------------------
@router.get("/open/query")
def openclasses_query(
    term: Optional[str] = None,
    subject: Optional[str] = None,
    course: Optional[str] = None,
    crn: Optional[str] = None,
    only_open: bool = True,
    # time filters (minutes since midnight)
    time_start: Optional[int] = None,
    time_end: Optional[int] = None,
    # days: accepts names, numbers, ranges; e.g., "Mon,Wed" or "1,3" or "Mon-Thu"
    days: Optional[str] = None,
    # days_mode: "any" or "all"
    days_mode: str = "any",
    # modality: "online", "inperson", "hybrid" (case-insensitive). None = no filter
    modality: Optional[str] = None,
):
    """
    Query open_classes and return all meetings for classes (term+crn) that match provided filters.
    New: modality can be 'online', 'inperson', or 'hybrid'.
    """
    try:
        outer_where: List[str] = []
        params: List[Any] = []

        # Basic outer filters (term/subject/course/crn/status)
        if term:
            outer_where.append("UPPER(term) = UPPER(?)")
            params.append(term)

        if subject:
            outer_where.append("UPPER(subject) = UPPER(?)")
            params.append(subject)

        if course:
            outer_where.append("UPPER(course_id) LIKE UPPER(?)")
            params.append(f"%{course}%")

        if crn:
            outer_where.append("crn = ?")
            params.append(str(crn))

        if only_open:
            outer_where.append("LOWER(status) LIKE 'open%'")

        # Modality handling (we add correlated EXISTS checks so that we still return ALL meetings for a matched CRN)
        mod = modality.strip().lower() if modality and isinstance(modality, str) else None
        if mod in ("online", "fully_online", "fully-online", "online-only"):
            # class must have at least one meeting whose room contains 'online'
            outer_where.append(
                "EXISTS (SELECT 1 FROM open_classes mmod WHERE mmod.term = open_classes.term AND mmod.crn = open_classes.crn AND UPPER(IFNULL(mmod.room,'')) LIKE '%ONLINE%')"
            )
        elif mod in ("inperson", "in-person", "in_person", "in_person_only"):
            # class must have at least one meeting whose room does NOT contain 'online' and is not empty/TBA
            outer_where.append(
                "EXISTS (SELECT 1 FROM open_classes mmod WHERE mmod.term = open_classes.term AND mmod.crn = open_classes.crn AND TRIM(IFNULL(mmod.room,'')) <> '' AND UPPER(IFNULL(mmod.room,'')) NOT LIKE '%ONLINE%' AND UPPER(TRIM(IFNULL(mmod.room,''))) NOT IN ('TBA'))"
            )
        elif mod in ("hybrid", "mixed"):
            # require both an online meeting and an in-person meeting
            outer_where.append(
                "EXISTS (SELECT 1 FROM open_classes mmod WHERE mmod.term = open_classes.term AND mmod.crn = open_classes.crn AND UPPER(IFNULL(mmod.room,'')) LIKE '%ONLINE%')"
            )
            outer_where.append(
                "EXISTS (SELECT 1 FROM open_classes mmod2 WHERE mmod2.term = open_classes.term AND mmod2.crn = open_classes.crn AND TRIM(IFNULL(mmod2.room,'')) <> '' AND UPPER(IFNULL(mmod2.room,'')) NOT LIKE '%ONLINE%' AND UPPER(TRIM(IFNULL(mmod2.room,''))) NOT IN ('TBA'))"
            )
        # else: no modality filter

        # Determine time filter flags
        has_start_end = (time_start is not None and time_end is not None)
        has_start_only = (time_start is not None and time_end is None)
        has_end_only = (time_end is not None and time_start is None)

        # Build time condition snippet for correlated subquery (operand uses view columns)
        oc2_time_cond = overlaps_time_condition_sql(has_start_end, has_start_only, has_end_only)
        # oc2_time_cond contains placeholders "?" if present; we'll append its params where needed.

        # Days normalization -> list[int]
        required_days = normalize_days_param(days)

        # Build correlated existence clauses (to ensure class has at least one meeting matching day/time when needed)
        existence_clauses: List[str] = []
        existence_params: List[Any] = []

        # days_mode == 'all' will be handled using aggregate EXISTS below
        if required_days and days_mode.lower() == "any":
            # oc2.day_of_week IN (?, ?, ?)
            ph = ",".join("?" for _ in required_days)
            existence_clauses.append(f"oc2.day_of_week IN ({ph})")
            existence_params.extend(required_days)

        # append time condition to existence clauses (if present)
        if oc2_time_cond:
            existence_clauses.append(oc2_time_cond)
            if has_start_end:
                existence_params.append(time_start); existence_params.append(time_end)
            elif has_start_only:
                existence_params.append(time_start)
            elif has_end_only:
                existence_params.append(time_end)

        # Compose correlated subqueries and attach to outer_where
        if required_days and days_mode.lower() == "all":
            # aggregated check: class must have (distinct) required days count >= n_required
            ph_days = ",".join("?" for _ in required_days)
            agg_sql = f"""
            EXISTS (
              SELECT 1 FROM (
                SELECT term, crn
                FROM open_classes
                WHERE day_of_week IN ({ph_days})
                GROUP BY term, crn
                HAVING COUNT(DISTINCT day_of_week) >= ?
              ) AS sub
              WHERE sub.term = open_classes.term AND sub.crn = open_classes.crn
            )
            """
            outer_where.append(agg_sql)
            params.extend(required_days)
            params.append(len(required_days))

            # if time constraints also present, require at least one meeting matching the time
            if oc2_time_cond:
                exists_time_sql = f"""
                EXISTS (
                  SELECT 1 FROM open_classes oc2
                  WHERE oc2.term = open_classes.term AND oc2.crn = open_classes.crn
                    AND {oc2_time_cond}
                )
                """
                outer_where.append(exists_time_sql)
                params.extend([time_start, time_end] if has_start_end else ([time_start] if has_start_only else ([time_end] if has_end_only else [])))
        else:
            # days_mode == 'any' or no days: combine existence_clauses into one correlated EXISTS
            if existence_clauses:
                exists_sql = "EXISTS (SELECT 1 FROM open_classes oc2 WHERE oc2.term = open_classes.term AND oc2.crn = open_classes.crn AND " + " AND ".join(existence_clauses) + ")"
                outer_where.append(exists_sql)
                params.extend(existence_params)

        # Final WHERE
        where_sql = ("WHERE " + " AND ".join(outer_where)) if outer_where else ""

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

        # Note: for days_mode=='all' we enforced via aggregated EXISTS above.
        # As a safety double-check (optional), you could post-filter by numeric day_num or time overlap here.

        # Final safety for time window if not already enforced in EXISTS (rare)
        if (has_start_end or has_start_only or has_end_only) and not oc2_time_cond:
            def meeting_overlaps(meet):
                s = meet.get("start", -1) if meet.get("start") is not None else -1
                e = meet.get("end", -1) if meet.get("end") is not None else -1
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

@router.post("/tda/upload")
async def prase_tda(file: UploadFile = File(...)):
    if file.content_type not in ["application/pdf", "application/octet-stream"]:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid file type: {file.content_type}. Only PDF files are allowed!"
        )
    try:
        contents = await file.read()
        results = PDF_parser.parse_tda(contents, file.filename)
        if results.get("status") == "error":
            raise HTTPException(status_code=400, detail=results.get("errors", ["Unknown error"]))
        return {
            "parsed_data": results
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Upload failed: {e}")