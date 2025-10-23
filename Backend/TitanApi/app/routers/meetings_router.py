from fastapi import FastAPI, APIRouter, HTTPException, File, UploadFile
from services import meetings_csv, meetings_service
from crud import meetings_crud

router = APIRouter()

@router.post("/meetings/upload")
async def upload_meetings_csv(file: UploadFile = File(...)):
    # Check if CSV file
    if file.content_type != "text/csv":
        raise HTTPException(
            status_code=400,
            detail=f"Invalid file type: {file.content_type}. Only CSV files are allowed!"
        )

    contents = await file.read()

    rows_inserted = meetings_csv.scrape_meetings_csv(contents, table_name="meeting")
    if rows_inserted["status"] == "error":
        return rows_inserted
    else:
        rows_inserted.pop("status")
        return{"message": f"Inserted {rows_inserted} rows into the  'meeting' table."}
    


@router.get("/meetings")
def get_all_meetings():
    return meetings_service.get_all_meetings()

