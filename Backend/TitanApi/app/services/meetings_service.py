from schemas import MeetingIn
from crud import meetings_crud

def get_meetings(crn: str):
    raw = meetings_crud.get_meetings(crn) # This will either return a python dictionary with course data or None if it could not find matching data
    if not raw: # If raw is empty return None
        return None
        
    # Sends it to Pydantic model which Validates data fields, Converts types if needed, Ignores unknown fields, Builds Structured model with attirubtes we can acces
    meeting = MeetingIn(**raw) # Converts data from {"course_id" : "CPSC 120", "Subject" : "CPSC"...} -> (course_id = "CPSC 120", Subject= "CPSC")
    return meeting # Returns course Object

def get_all_meetings():
    rows = meetings_crud.get_all_meetings()

    return [MeetingIn(**r) for r in rows]
