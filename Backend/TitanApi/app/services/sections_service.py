from schemas import SectionIn
from crud import sections_crud

def get_sections(crn: str):
    raw = sections_crud.get_sections(crn) # This will either return a python dictionary with course data or None if it could not find matching data
    if not raw: # If raw is empty return None
        return None
        
    # Sends it to Pydantic model which Validates data fields, Converts types if needed, Ignores unknown fields, Builds Structured model with attirubtes we can acces
    section = SectionIn(**raw) # Converts data from {"course_id" : "CPSC 120", "Subject" : "CPSC"...} -> (course_id = "CPSC 120", Subject= "CPSC")
    return section # Returns course Object

def get_all_sections():
    rows = sections_crud.get_all_sections()

    return [SectionIn(**r) for r in rows]
