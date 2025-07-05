import requests
import pandas as pd
from datetime import datetime, timezone

def fetch_today_earthquake_data() -> pd.DataFrame:
    url = "https://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/all_day.geojson"
    response = requests.get(url)
    response.raise_for_status()

    data = response.json()
    records = []

    # Get today's UTC midnight timestamp
    today_utc = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
    today_timestamp_ms = int(today_utc.timestamp() * 1000)

    for feature in data.get("features", []):
        props = feature.get("properties", {})
        coords = feature.get("geometry", {}).get("coordinates", [None, None, None])
        quake_time = props.get("time")

        # Only include if time is today (in UTC)
        if quake_time and quake_time >= today_timestamp_ms:
            records.append({
                "id": feature.get("id"),
                "magnitude": props.get("mag"),
                "place": props.get("place"),
                "time_utc": datetime.fromtimestamp(quake_time / 1000, tz=timezone.utc).isoformat(),
                "longitude": coords[0],
                "latitude": coords[1],
                "depth_km": coords[2],
                "status": props.get("status"),
                "type": props.get("type"),
                "tsunami": props.get("tsunami"),
                "alert": props.get("alert"),
            })

    return pd.DataFrame(records)


if __name__ == "__main__":
    df = fetch_today_earthquake_data()  # Fetch limited data for testing
    print(df.head())