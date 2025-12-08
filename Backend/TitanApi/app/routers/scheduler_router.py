from fastapi import APIRouter, HTTPException
from services import scheduler_service
from pydantic import BaseModel
from typing import List, Optional

router = APIRouter()

class CompletedModel(BaseModel):
    completed: List[str] = []
    max_units: Optional[int] = 15

@router.post("/schedule/next-semester")
def generate_schedule(payload: CompletedModel):
    try:
        result = scheduler_service.generate_next_semester_schedule(
            payload.completed, 
            max_units=payload.max_units or 15
        )
        return {"data": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
