from db import get_conn
import pandas as pd
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

    # Build a list of meeting dicts directly from each row
    df["meeting"] = df[["day_of_week", "start_min", "end_min"]] \
        .rename(columns={"day_of_week": "day", "start_min": "start", "end_min": "end"}) \
        .to_dict(orient="records")

    # Group and collect those meeting dicts into lists
    grouped = (
        df.groupby(["term","crn","course_id","section","professor","status","room"], as_index=False)
          .agg(meetings=("meeting", list))
    )

    # Convert back to Python list of dicts
    return grouped.to_dict(orient="records")
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
        rows = [dict(row) for row in rows]
        rows = convert_days_of_week(rows)
        rows = group_meetings(rows)
        return rows