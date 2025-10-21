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

@router.delete("/terms", status_code=204)
def delete_terms(term_id: int | None = None, term: str | None = None):
    if (term_id is None) == (term is None): #If empty value is accepted, return error
         raise HTTPException(
              status_code = 400,
              detail="Provide exactly one of: term_id OR term"
         )
    ok = terms_crud.delete_terms(term_id=term_id, term=term)
    if not ok:
         raise HTTPException(status_code=404, detail="Term not found")
    return None

@router.post("/terms/{term}")
def create_term(term : str):
     c = terms_crud.create_terms(term)
     if c is None:
        raise HTTPException(status_code=409, detail="Term already exist")
     return c

@router.get("/terms")
def get_all_terms():
     return terms_crud.get_all_terms()
