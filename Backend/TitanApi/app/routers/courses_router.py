from fastapi import FastAPI, APIRouter, HTTPException, File, UploadFile
from services import courses_csv
from crud import courses_crud

router = APIRouter()

@router.post("/courses/upload")
async def upload_courses_csv(file: UploadFile = File(...)):
    contents = await file.read()

    rows_inserted = courses_csv.scrape_courses_csv(contents, table_name="course")

    return{"message": f"Inserted {rows_inserted} rows into the  'course' table."}

@router.post("/courses/{course_id}")
def get_courses(course_id: str):
    c = courses_crud.get_courses(course_id)
    if c is None:
        raise HTTPException(status_code=404, detail="Course not found!")
    return c

@router.post("/courses")
def get_all_courses():
    return courses_crud.get_all_courses()