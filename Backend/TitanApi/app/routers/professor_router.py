from fastapi import APIRouter, HTTPException, Query
from typing import Optional
import time

router = APIRouter()

CSUF_RMP_ID = 166

# --------------- RMP Scraper Loading ----------------
try:
    try:
        from ratemyprof import RateMyProfScraper
    except ImportError:
        from ratemyprof_api import RateMyProfScraper

    rmp_scraper = RateMyProfScraper(CSUF_RMP_ID)
    RMP_AVAILABLE = True
except Exception as e:
    print(f"[RMP] Failed to initialize scraper: {e}")
    RMP_AVAILABLE = False
    rmp_scraper = None

# --------------- MEMORY CACHE ----------------
# Cache for 1 hour per professor
RMP_CACHE = {}
CACHE_TTL = 3600  # seconds


@router.get("/professor/rating")
def get_professor_rating(professor_name: str = Query(..., description="Professor name to search")):
    """
    Get Rate My Professor rating with 1-hour caching.
    Prevents 100 simultaneous scrapes.
    """

    # Check installation
    if not RMP_AVAILABLE:
        raise HTTPException(status_code=503, detail="Rate My Professor scraper not available.")

    if not professor_name or not professor_name.strip():
        raise HTTPException(status_code=400, detail="Professor name is required")

    name = professor_name.strip()

    # --------------- RETURN FROM CACHE ---------------
    now = time.time()
    if name in RMP_CACHE:
        cached = RMP_CACHE[name]
        # Check TTL
        if now - cached["timestamp"] < CACHE_TTL:
            return cached["data"]

    # --------------- SCRAPE LIVE ---------------
    try:
        professor_info = rmp_scraper.SearchProfessor(name)

        if not professor_info:
            data = {
                "professor_name": name,
                "found": False,
                "overall_rating": None,
                "num_ratings": 0,
                "rating_class": None
            }
        else:
            data = {
                "professor_name": name,
                "found": True,
                "overall_rating": professor_info.get("overall_rating"),
                "num_ratings": professor_info.get("tNumRatings", 0),
                "rating_class": professor_info.get("rating_class"),
                "department": professor_info.get("tDept"),
                "first_name": professor_info.get("tFname"),
                "last_name": professor_info.get("tLname")
            }

        # --------------- UPDATE CACHE ---------------
        RMP_CACHE[name] = {
            "timestamp": now,
            "data": data
        }

        return data

    except Exception as e:
        # Gracefully fallback to "not found" instead of crashing
        data = {
            "professor_name": name,
            "found": False,
            "overall_rating": None,
            "num_ratings": 0,
            "rating_class": None
        }

        # Cache the failure for a short time (5 minutes) to prevent retry spam
        RMP_CACHE[name] = {
            "timestamp": now,
            "data": data
        }

        return data
