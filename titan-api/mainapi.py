import sqlite3
from fastapi import FastAPI, HTTPException
from db import DB_PATH
import crud

app = FastAPI(title="Titan Scheduler API")

@app.get("/")
async def root():
    return {"message": "Hello World"}

@app.get("/debug/dbpath")
def debug_dbpath():
    return {"db_path" : str(DB_PATH)}

@app.get("/terms/{term}")
def read_term(term: str):
    print(term)
    doc = crud.get_term(term)
    print(doc)
    if doc is None:
        raise HTTPException(status_code=404, detail="Term not found")
    return doc    

@app.post("/terms", status_code=201)
def create_term(term: str):
    doc = crud.insert_term(term)
    if doc is None:
        # insert failed because term already exists
        raise HTTPException(status_code=409, detail="Term already exists")
    return doc

@app.delete("/terms", status_code=204)
def delete_term(term_id: int | None = None, term: str | None = None):
    if (term_id is None) == (term is None):
        raise HTTPException(
            status_code=400,
            detail="Provide exactly one of: term_id OR term"
        )
    ok = crud.delete_term(term_id=term_id, term=term)
    if not ok:
        raise HTTPException(status_code=404, detail="Term not found")
    return None

@app.get("/termstable")
def terms_table_endpoint():
    return crud.terms_table()