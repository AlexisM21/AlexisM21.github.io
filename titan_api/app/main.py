import sqlite3
from fastapi import FastAPI, APIRouter, HTTPException
from routers import terms_router

app = FastAPI()
app.include_router(terms_router.router)

@app.get('/')
def root():
    return {"message" : "hello wRodl!"}