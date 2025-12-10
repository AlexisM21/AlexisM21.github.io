from db import get_conn
import pandas as pd
import numpy as np
import sqlite3

def convert_days_of_week(df: list[dict]):
    days = {
        1: "Mon",
        2: "Tue",
        3: "Wed",
        4: "Thur",
        5: "Fri",
        6: "Sat",
        7: "Sun",
        -1: "TBA"  
    }

    for row in df:
        value = row["day_of_week"]
        row["day_of_week"] = days.get(value, None)

    return df

def min_to_hour_help(input: int):
    hours = input // 60
    mins = input % 60

    time_str = f"{hours}:{mins:02d}"
    return time_str


def min_to_hour(df: list[dict]):
    for row in df:
        row["start_min"] = min_to_hour_help(row["start_min"])
        row["end_min"] = min_to_hour_help(row["end_min"])
    
    return df

def group_meetings(df: list[dict]):
    df = pd.DataFrame(df)

    # FAST vectorized tuple creation
    df["meeting"] = list(zip(
        df["day_of_week"].to_numpy(),
        df["start_min"].to_numpy(),
        df["end_min"].to_numpy(),
        df["room"].to_numpy()
    ))

    # Group by schedule key
    grouped = (
        df.groupby(
            ["term", "crn", "course_id", "title","section", "professor", "status"],
            sort=False,
            as_index=False
        ).agg(meetings=("meeting", list))
    )

    result = []
    append = result.append

    for row in grouped.itertuples(index=False):
        # Convert meeting tuples → dicts
        meeting_list = [
            {
                "day": int(d) if isinstance(d, (np.integer,)) else d,
                "start": int(s) if isinstance(s, (np.integer,)) else s,
                "end": int(e) if isinstance(e, (np.integer,)) else e,
                "room": r
            }
            for (d, s, e, r) in row.meetings
        ]

        append({
            "term": row.term,
            "crn": int(row.crn) if isinstance(row.crn, (np.integer,)) else row.crn,
            "course_id": row.course_id,
            "title" : row.title,
            "section": row.section,
            "professor": row.professor,
            "status": row.status,
            "meetings": meeting_list
        })

    return result

    # grouped = (
    #     df.groupby(["term","crn","course_id","section","professor","status","room"])
    #     .apply(lambda g:
    #         g.drop(columns=["term","crn","course_id","section","professor","status","room"])
    #         [["day_of_week","start_min","end_min"]]
    #         .rename(columns={"day_of_week":"day","start_min":"start","end_min":"end"})
    #         .to_dict(orient="records")
    #     )
    #     .reset_index(name="meetings")
    # )

    # records = grouped.to_dict(orient="records")
    # return records

def get_open_class_list():
    with get_conn() as c:
        rows = c.execute("SELECT * FROM open_classes").fetchall()
        if not rows:
            return{"data": [], "message": "No open classes found."}

        rows = [dict(row) for row in rows]
        rows = convert_days_of_week(rows)

        rows = group_meetings(rows)

        return rows
