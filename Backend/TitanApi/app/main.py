import sqlite3
from fastapi import FastAPI, APIRouter, HTTPException
from routers import terms_router, courses_router, sections_router, meetings_router, csv_upload_router, scheduler_router
from fastapi.middleware.cors import CORSMiddleware
from crud import open_class_list_crud
import cache


app = FastAPI()


@app.on_event("startup")
def load_open_cache():
    """
    Runs when FastAPI starts.
    Loads the open classes *once* into memory for instant response.
    """
    # global OPEN_CACHE
    print("Loading open class list into memory...")
    cache.OPEN_CACHE.clear()
    cache.OPEN_CACHE.update({
        "data" : open_class_list_crud.get_open_class_list()
    })

    print(f"Loaded {len(cache.OPEN_CACHE)} open class rows into memory.")



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
    print("Main sees:", len(cache.OPEN_CACHE))
    return {"message" : "hello wRodl!"}