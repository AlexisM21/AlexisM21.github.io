from fastapi import FastAPI, APIRouter, HTTPException, File, UploadFile
from services import courses_csv, courses_service
from crud import courses_crud

router = APIRouter()


@router.post("/courses/upload")
async def upload_courses_csv(file: UploadFile = File(...)):
    # Check if CSV file
    if file.content_type != "text/csv":
        raise HTTPException(
            status_code=400,
            detail=f"Invalid file type: {file.content_type}. Only CSV files are allowed!"
        )

    contents = await file.read()

    rows_inserted = courses_csv.scrape_courses_csv(contents, table_name="course")
    if rows_inserted["status"] == "error":
        return rows_inserted
    else:
        rows_inserted.pop("status")
        return{"message": f"Inserted {rows_inserted} rows into the  'course' table."}


@router.post("/courses/{course_id}")
def get_courses(course_id: str):
    c = courses_service.get_course(course_id)
    if c is None:
        raise HTTPException(status_code=404, detail="Course not found!")
    return c


@router.get("/courses")
def get_all_courses():
    return courses_service.get_all_courses()


@router.delete("/courses/{course_id}")
def delete_courses(course_id):
    # empty value is accepted
    if course_id is None:
        raise HTTPException(
            status_code=400,
            detail="Please Enter Course_ID"
        )
    ok = courses_crud.delete_courses(course_id)
    
    if not ok: # Course_id NOT FOUNd
        raise HTTPException(
            status_code=404,
            detail="course_id Not Found"
        )
    return {f"Successfully Deleted {course_id}!"}