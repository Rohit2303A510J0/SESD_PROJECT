from fastapi import APIRouter, HTTPException
import requests

router = APIRouter(prefix="/weather", tags=["Weather"])

OPEN_METEO_URL = "https://api.open-meteo.com/v1/forecast"

@router.get("/")
def get_weather(lat: float, lng: float):
    """
    Fetch current weather for given latitude and longitude
    """
    try:
        params = {
            "latitude": lat,
            "longitude": lng,
            "current_weather": True
        }
        response = requests.get(OPEN_METEO_URL, params=params)
        if response.status_code != 200:
            raise HTTPException(status_code=500, detail="Error fetching weather data")
        data = response.json()
        return {"latitude": lat, "longitude": lng, "weather": data.get("current_weather", {})}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")
