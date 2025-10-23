from fastapi import FastAPI, APIRouter, HTTPException, File, UploadFile
from services import sections_csv, sections_service
from crud import sections_crud

router = APIRouter()

@router.post("/sections/upload")
async def upload_sections_csv(file: UploadFile = File(...)):
    # Check if CSV file
    if file.content_type != "text/csv":
        raise HTTPException(
            status_code=400,
            detail=f"Invalid file type: {file.content_type}. Only CSV files are allowed!"
        )

    contents = await file.read()

    rows_inserted = sections_csv.scrape_sections_csv(contents, table_name="section")
    if rows_inserted["status"] == "error":
        return rows_inserted
    else:
        rows_inserted.pop("status")
        return{"message": f"Inserted {rows_inserted} rows into the  'section' table."}
    


@router.get("/sections")
def get_all_sections():
    return sections_service.get_all_sections()

