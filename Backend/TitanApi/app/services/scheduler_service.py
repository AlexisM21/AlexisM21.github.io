import json
from pathlib import Path
from typing import List, Dict

BASE_DIR = Path(__file__).resolve().parent
REQ_FILE = BASE_DIR / "cs_requirements.json"

# A tiny set of time slots we will use to build a weekly calendar.
TIME_SLOTS = [
    {"days":["Mon","Wed","Fri"], "time":"09:00-10:00"},
    {"days":["Mon","Wed","Fri"], "time":"10:00-11:00"},
    {"days":["Tue","Thu"], "time":"09:30-11:00"},
    {"days":["Mon","Wed","Fri"], "time":"13:00-14:00"},
    {"days":["Tue","Thu"], "time":"13:30-15:00"},
    {"days":["Mon","Wed","Fri"], "time":"15:00-16:00"},
]

def load_requirements() -> List[Dict]:
    try:
        with open(REQ_FILE) as f:
            return json.load(f)
    except FileNotFoundError:
        raise FileNotFoundError(f"Requirements file not found: {REQ_FILE}. Please create cs_requirements.json in the services directory.")
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON in requirements file {REQ_FILE}: {e}")
    except Exception as e:
        raise RuntimeError(f"Error loading requirements file {REQ_FILE}: {e}")

def can_take(course: Dict, completed: List[str]) -> bool:
    """Return True if all prereqs for this course are in completed list."""
    for p in course.get("prereqs", []):
        if p not in completed:
            return False
    return True

def generate_next_semester_schedule(completed: List[str], max_units: int = 15) -> Dict:
    """
    Generate a naive schedule for the next semester.

    Parameters:
    - completed: list of course_id strings the student has already finished
    - max_units: maximum units to schedule for the semester (default 15)

    Returns a dict with:
    - planned_courses: list of courses scheduled (course_id, title, units, meeting pattern)
    - remaining_needed: courses still needed after this semester
    """
    reqs = load_requirements()
    completed_set = set(completed or [])

    # Determine needed courses (those in reqs but not completed)
    needed = [c for c in reqs if c["course_id"] not in completed_set]

    planned = []
    total_units = 0
    slot_index = 0

    for course in needed:
        # don't exceed units
        if total_units + course.get("units", 3) > max_units:
            continue
        # only take course if prereqs satisfied by completed courses
        if not can_take(course, completed):
            continue
        # assign a time slot (wrap around if more courses than slots)
        slot = TIME_SLOTS[slot_index % len(TIME_SLOTS)]
        slot_index += 1
        planned.append({
            "course_id": course["course_id"],
            "title": course.get("title", ""),
            "units": course.get("units", 3),
            "meeting": {
                "days": slot["days"],
                "time": slot["time"]
            }
        })
        total_units += course.get("units", 3)

    remaining_after = [c["course_id"] for c in reqs if c["course_id"] not in completed_set and c["course_id"] not in [p["course_id"] for p in planned]]

    return {
        "planned_units": total_units,
        "planned_courses": planned,
        "remaining_needed": remaining_after
    }
