import json
import requests
import cache

## DELETE ##

def get_open_class_user(audit: dict):

    requirements = audit.get("requirements", [])

    open_data = cache.OPEN_CACHE["data"]

    def get_course_code(section):
        course = section.get("course_id")
        if course:
            return course.strip()
        return None

    sections_by_course = {}

    for sec in open_data:
        if not isinstance(sec, dict):
            continue

        code = get_course_code(sec)
        if not code:
            continue

        if code not in sections_by_course:
            sections_by_course[code] = []

        sections_by_course[code].append(sec)

    plan_requirements = []

    for req in requirements:
        courses_allowed = req.get("courses_allowed", []) or []
        matches = []

        for code in courses_allowed:
            normalized = code.strip()
            if normalized in sections_by_course:
                matches.extend(sections_by_course[normalized])

        plan_requirements.append({
            "requirement_id": req.get("requirement_id"),
            "name": req.get("name"),
            "type": req.get("type"),
            "total_units_required": req.get("total_units_required"),
            "total_units_completed": req.get("total_units_completed"),
            "courses_allowed": courses_allowed,
            "open_sections": matches,
        })


    plan = {
        "student_info": audit.get("student_info", {}),
        "summary": {
            "remaining_requirements": len(plan_requirements),
        },
        "requirements": plan_requirements,
    }
    return plan
