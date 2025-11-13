from fastapi import APIRouter, HTTPException
import requests
import os

router = APIRouter(prefix="/images", tags=["Images"])

UNSPLASH_ACCESS_KEY = os.getenv("UNSPLASH_ACCESS_KEY", "your_access_key")
UNSPLASH_URL = "https://api.unsplash.com/search/photos"

@router.get("/{query}")
def get_images(query: str, per_page: int = 4):
    """
    Fetch 4–6 images from Unsplash for the given query
    """
    try:
        headers = {"Authorization": f"Client-ID {UNSPLASH_ACCESS_KEY}"}
        params = {"query": query, "per_page": per_page}
        response = requests.get(UNSPLASH_URL, headers=headers, params=params)
        if response.status_code != 200:
            raise HTTPException(status_code=500, detail="Error fetching images from Unsplash")
        data = response.json()
        image_urls = [item["urls"]["regular"] for item in data.get("results", [])]
        return {"query": query, "images": image_urls}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")
