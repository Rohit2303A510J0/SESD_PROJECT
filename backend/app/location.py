from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
import requests

router = APIRouter(prefix="/location", tags=["Location"])

RESTCOUNTRIES_URL = "https://restcountries.com/v3.1/name/"

@router.get("/{country_name}")
def get_country_info(country_name: str):
    """
    Fetch detailed country info from REST Countries API (exact match).
    """
    try:
        # Normalize input (capitalize first letter, handle special cases)
        country_name = country_name.strip()
        if not country_name:
            raise HTTPException(status_code=400, detail="Country name is required")

        # ✅ Use fullText=true for exact match
        response = requests.get(f"{RESTCOUNTRIES_URL}{country_name}?fullText=true")

        if response.status_code != 200:
            raise HTTPException(status_code=404, detail="Country not found")

        data = response.json()[0]
        name = data.get("name", {}).get("common")
        capital = data.get("capital", [None])[0]
        flag = data.get("flags", {}).get("svg")
        currencies = data.get("currencies", {})
        currency = list(currencies.keys())[0] if currencies else None
        languages = list(data.get("languages", {}).values()) if data.get("languages") else []
        latlng = data.get("latlng", [None, None])
        region = data.get("region", "Unknown")
        population = data.get("population", "N/A")

        return JSONResponse({
            "name": name,
            "capital": capital,
            "flag": flag,
            "currency": currency,
            "languages": languages,
            "latlng": latlng,
            "region": region,
            "population": population
        })

    except requests.exceptions.RequestException:
        raise HTTPException(status_code=500, detail="External API request failed")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching country data: {str(e)}")
