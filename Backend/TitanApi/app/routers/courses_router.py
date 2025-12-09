from fastapi import FastAPI, APIRouter, HTTPException, File, UploadFile
from services import courses_csv
from crud import courses_crud

router = APIRouter()


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