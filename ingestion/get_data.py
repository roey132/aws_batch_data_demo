import requests
import pandas as pd
from datetime import datetime, timezone
import time

def reverse_geocode(lat, lon):
    """Get country from latitude and longitude using Nominatim."""
    url = "https://nominatim.openstreetmap.org/reverse"
    params = {
        "lat": lat,
        "lon": lon,
        "format": "json",
        "zoom": 3,  # country level
        "addressdetails": 1
    }
    headers = {
        "User-Agent": "EarthquakePipeline/1.0"
    }
    try:
        response = requests.get(url, params=params, headers=headers)
        if response.status_code == 200:
            data = response.json()
            return data.get("address", {}).get("country")
    except Exception:
        pass
    return None

def fetch_earthquake_data_with_country(limit: int = None) -> pd.DataFrame:
    url = "https://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/all_day.geojson"
    response = requests.get(url)
    response.raise_for_status()

    data = response.json()
    records = []

    features = data.get("features", [])
    if limit:
        features = features[:limit]  # for testing, limit requests

    for i, feature in enumerate(features):
        props = feature.get("properties", {})
        coords = feature.get("geometry", {}).get("coordinates", [None, None, None])
        lon, lat, depth = coords

        country = reverse_geocode(lat, lon)
        time.sleep(1)  # avoid hitting rate limit

        records.append({
            "id": feature.get("id"),
            "magnitude": props.get("mag"),
            "country": country,
            "time_utc": datetime.fromtimestamp(props.get("time") / 1000, tz=timezone.utc).isoformat() if props.get("time") else None,
            "longitude": lon,
            "latitude": lat,
            "depth_km": depth,
            "status": props.get("status"),
            "type": props.get("type"),
            "tsunami": props.get("tsunami"),
            "alert": props.get("alert"),
        })

    return pd.DataFrame(records)

if __name__ == "__main__":
    df = fetch_earthquake_data_with_country(limit=10)  # Fetch limited data for testing
    print(df.head())