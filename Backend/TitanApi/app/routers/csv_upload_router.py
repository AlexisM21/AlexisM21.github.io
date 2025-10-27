from fastapi import FastAPI, APIRouter, HTTPException, File, UploadFile
from services import csv_scraper_service
from crud import open_class_list_crud

router = APIRouter()


@router.post("/open/upload")
async def upload_csv(file: UploadFile = File(...)):
    # Check if CSV file
    if file.content_type != "text/csv":
        raise HTTPException(
            status_code=400,
            detail=f"Invalid file type: {file.content_type}. Only CSV files are allowed!"
        )

    try:
        contents = await file.read()

        results = csv_scraper_service.scrape_csv(contents)
        if results.get("status") == "error":
            raise HTTPException(status_code=400, detail=results.get("errors",["Unknown error"]))
        
        return {
            "message" : "CSV Update Completed.",
            "inserted" : results.get("inserted", []),
            "errors" : results.get("errors", []),
        }
    
    except HTTPException:
         raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Upload failed: {e}")


@router.get("/open")
def get_all_open_classes():
    return {"data": open_class_list_crud.get_open_class_list()}
