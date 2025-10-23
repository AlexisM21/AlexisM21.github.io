from schemas import CourseOut
from crud import courses_crud

def get_course(course_id: str):
    raw = courses_crud.get_courses(course_id) # This will either return a python dictionary with course data or None if it could not find matching data
    if not raw: # If raw is empty return None
        return None
        
    # Sends it to Pydantic model which Validates data fields, Converts types if needed, Ignores unknown fields, Builds Structured model with attirubtes we can acces
    course = CourseOut(**raw) # Converts data from {"course_id" : "CPSC 120", "Subject" : "CPSC"...} -> (course_id = "CPSC 120", Subject= "CPSC")
    return course # Returns course Object

def get_all_courses():
    rows = courses_crud.get_all_courses()

    return [CourseOut(**r) for r in rows]
