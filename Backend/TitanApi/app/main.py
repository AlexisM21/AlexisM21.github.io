import sqlite3
from fastapi import FastAPI, APIRouter, HTTPException
from routers import terms_router, courses_router, sections_router, meetings_router, csv_upload_router, scheduler_router
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()
app.include_router(terms_router.router)
app.include_router(courses_router.router)
app.include_router(sections_router.router)
app.include_router(meetings_router.router)
app.include_router(csv_upload_router.router)
app.include_router(scheduler_router.router)



app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # or specify your frontend domain
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get('/')
def root():
    return {"message" : "hello wRodl!"}