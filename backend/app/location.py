from fastapi import APIRouter, HTTPException
import requests

router = APIRouter(prefix="/location", tags=["Location"])

RESTCOUNTRIES_URL = "https://restcountries.com/v3.1/name/"

@router.get("/{country_name}")
def get_country_info(country_name: str):
    """
    Fetch country info from REST Countries API (exact match).
    """
    try:
        # ✅ Use fullText=true for exact match
        response = requests.get(f"{RESTCOUNTRIES_URL}{country_name}?fullText=true")
        if response.status_code != 200:
            raise HTTPException(status_code=404, detail="Country not found")

        data = response.json()[0]  # take first match
        name = data.get("name", {}).get("common")
        capital = data.get("capital", [None])[0]
        flag = data.get("flags", {}).get("svg")
        
        currencies = data.get("currencies", {})
        currency = list(currencies.keys())[0] if currencies else None

        languages = list(data.get("languages", {}).values()) if data.get("languages") else []

        latlng = data.get("latlng", [None, None])

        return {
            "name": name,
            "capital": capital,
            "flag": flag,
            "currency": currency,
            "languages": languages,
            "latlng": latlng
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching country data: {str(e)}")
