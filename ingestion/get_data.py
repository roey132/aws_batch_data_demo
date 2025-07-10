import requests
import boto3
import json
from datetime import datetime, timezone

def fetch_today_earthquake_data() -> list:
    url = "https://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/all_day.geojson"
    response = requests.get(url)
    response.raise_for_status()

    data = response.json()
    features = data.get("features", [])
    today_utc = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
    today_timestamp_ms = int(today_utc.timestamp() * 1000)

    records = []

    for feature in features:
        props = feature.get("properties", {})
        coords = feature.get("geometry", {}).get("coordinates", [None, None, None])
        quake_time = props.get("time")

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

    return records

def save_to_s3(records: list, bucket: str):
    s3 = boto3.client("s3")
    today_str = datetime.utcnow().strftime("%Y-%m-%d")
    key = f"raw/{today_str}.json"
    body = json.dumps(records)

    s3.put_object(Bucket=bucket, Key=key, Body=body)
    print(f"✅ Saved {len(records)} records to s3://{bucket}/{key}")

def lambda_handler(event=None, context=None):
    BUCKET = "your-bucket-name"
    s3 = boto3.client("s3")

    records = fetch_today_earthquake_data()
    today_str = datetime.utcnow().strftime("%Y-%m-%d")
    key = f"raw/{today_str}.json"
    body = json.dumps(records)

    s3.put_object(Bucket=BUCKET, Key=key, Body=body)
    print(f"✅ Saved {len(records)} records to s3://{BUCKET}/{key}")
    return {
        "statusCode": 200,
        "body": f"{len(records)} records saved to {key}"
    }
