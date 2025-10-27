from pydantic import BaseModel, field_validator
from typing import Optional, List

def _coerce_int(v, field):
    if v is None or v == "" or str(v).lower() in {"nan", "none"}:
        raise ValueError(f"{field} is required and must be an integer")
    # Handle floats/strings like "510.0"
    try:
        return int(float(v))
    except Exception:
        raise ValueError(f"{field} must be an integer, got {v!r}")

class CourseOut(BaseModel):
    course_id: str
    subject: str
    number: str
    description: Optional[str] = None
    units: float
    prereq: Optional[str] = None
    coreq: Optional[str] = None

class CourseIn(BaseModel):
    course_id: str
    subject: str
    number: str
    description: Optional[str] = None
    units: float
    prereq: Optional[str] = None
    coreq: Optional[str] = None
    
    @field_validator("number", mode="before")
    def to_str(cls, v):
        if v is None:
            raise ValueError("number is a required field")
        return str(v).strip()

class UploadSummary(BaseModel):
    processed: int
    inserted: int
    updated: int
    ignored: int
    errors: List[str] = []

class SectionIn(BaseModel):
    crn: str
    course_id: str
    term_id: int
    section: str
    instruction_mode: str
    professor: Optional[str] = "TBA"
    status: str

    @field_validator("crn", "section", mode="before")
    def to_str_fields(cls, v, info):
        if v is None:
            raise ValueError(f"{info.field_name} is a required field!")
        return str(v).strip()
    
    @field_validator("term_id", mode="before")
    def to_int_term_id(cls, v):
        return _coerce_int(v, "term_id")
    
class MeetingIn(BaseModel):
    # meeting_id : int
    term_id: int
    crn: str
    day_of_week: int
    start_min: int
    end_min: int
    room: str

    @field_validator("crn",mode="before")
    def to_str(cls, v):
        if v is None:
            raise ValueError("crn is a required field!")
        return str(v).strip()
    @field_validator("term_id", "day_of_week", "start_min", "end_min", mode="before")
    def to_int_fields(cls, v, info):
        return _coerce_int(v, info.field_name)
    
    # @field_validator("section",mode="before")
    # def to_str(cls, v):
    #     if v is None:
    #         raise ValueError("section is a required field!")
    #     return str(v).strip()
