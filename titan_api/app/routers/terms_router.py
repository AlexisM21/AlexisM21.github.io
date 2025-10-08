## terms_router.python
from fastapi import FastAPI, APIRouter, HTTPException
from crud import terms_crud

router = APIRouter()

@router.get("/terms/{term}")
def get_terms(term: int | str):
        c = terms_crud.get_terms(term)
        if c is None:
            raise HTTPException(status_code=404, detail="Term not found!")
        return c

@router.delete("/terms/{term}")
def delete_terms(term: int | str):
    c = terms_crud.delete_terms(term)
    if c is False:
         raise HTTPException(status_code=404, detail="Term not found")
    else:
         print("Successfully deleted:", term, "!")
    return c

@router.post("/terms/{term}")
def create_term(term : str):
     c = terms_crud.create_terms(term)
     if c is None:
        raise HTTPException(status_code=409, detail="Term already exist")
     return c
