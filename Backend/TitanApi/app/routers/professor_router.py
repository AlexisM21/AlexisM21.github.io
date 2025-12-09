from fastapi import APIRouter, HTTPException, Query
from typing import Optional

router = APIRouter()

# CalState Fullerton Rate My Professor ID
CSUF_RMP_ID = 166

try:
    # Try different possible import names
    try:
        from ratemyprof import RateMyProfScraper
    except ImportError:
        from ratemyprof_api import RateMyProfScraper
    
    rmp_scraper = RateMyProfScraper(CSUF_RMP_ID)
    RMP_AVAILABLE = True
except ImportError:
    RMP_AVAILABLE = False
    rmp_scraper = None
    print("Warning: ratemyprof library not installed. Professor ratings will not be available.")
    print("Install with: pip install ratemyprof-api")
except Exception as e:
    RMP_AVAILABLE = False
    rmp_scraper = None
    print(f"Warning: Error initializing Rate My Professor scraper: {e}")
    print("Install with: pip install ratemyprof-api")


@router.get("/professor/rating")
def get_professor_rating(professor_name: str = Query(..., description="Professor name to search")):
    """
    Get Rate My Professor rating for a professor.
    Searches by professor name and returns rating information.
    """
    if not RMP_AVAILABLE:
        raise HTTPException(
            status_code=503,
            detail="Rate My Professor API is not available. Please install ratemyprof-api library."
        )
    
    if not professor_name or not professor_name.strip():
        raise HTTPException(
            status_code=400,
            detail="Professor name is required"
        )
    
    try:
        # Search for the professor
        professor_info = rmp_scraper.SearchProfessor(professor_name.strip())
        
        if not professor_info:
            return {
                "professor_name": professor_name,
                "found": False,
                "overall_rating": None,
                "num_ratings": 0,
                "rating_class": None
            }
        
        return {
            "professor_name": professor_name,
            "found": True,
            "overall_rating": professor_info.get("overall_rating"),
            "num_ratings": professor_info.get("tNumRatings", 0),
            "rating_class": professor_info.get("rating_class"),
            "department": professor_info.get("tDept"),
            "first_name": professor_info.get("tFname"),
            "last_name": professor_info.get("tLname")
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error fetching professor rating: {str(e)}"
        )

