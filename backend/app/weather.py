from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import JSONResponse
import requests

router = APIRouter(prefix="/weather", tags=["Weather"])

OPEN_METEO_URL = "https://api.open-meteo.com/v1/forecast"


@router.get("/")
def get_weather(
    lat: float = Query(..., description="Latitude of the location"),
    lng: float = Query(..., description="Longitude of the location")
):
    """
    Fetch current weather for given latitude and longitude.
    """
    try:
        if lat is None or lng is None:
            raise HTTPException(status_code=400, detail="Latitude and longitude are required")

        params = {
            "latitude": lat,
            "longitude": lng,
            "current_weather": True,
        }

        response = requests.get(OPEN_METEO_URL, params=params)
        if response.status_code != 200:
            raise HTTPException(status_code=500, detail="Error fetching weather data from API")

        data = response.json()
        current = data.get("current_weather", {})

        if not current:
            raise HTTPException(status_code=404, detail="Weather data not found")

        weather_data = {
            "latitude": lat,
            "longitude": lng,
            "temperature": current.get("temperature"),
            "windspeed": current.get("windspeed"),
            "winddirection": current.get("winddirection"),
            "time": current.get("time"),
            "weathercode": current.get("weathercode"),
        }

        return JSONResponse({"weather": weather_data})

    except requests.exceptions.RequestException:
        raise HTTPException(status_code=500, detail="External API request failed")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")
