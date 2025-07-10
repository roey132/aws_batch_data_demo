from datetime import datetime, timedelta, timezone
import requests
import json
import boto3

def get_yesterday_utc_range():
    today = datetime.now(timezone.utc).date()
    yesterday = today - timedelta(days=1)
    return yesterday.strftime("%Y-%m-%d"), today.strftime("%Y-%m-%d")

def fetch_earthquake_data(start_date: str, end_date: str) -> list:
    url = (
        "https://earthquake.usgs.gov/fdsnws/event/1/query"
        f"?format=geojson&starttime={start_date}&endtime={end_date}"
    )
    response = requests.get(url)
    response.raise_for_status()
    data = response.json()

    records = []
    for feature in data.get("features", []):
        props = feature.get("properties", {})
        coords = feature.get("geometry", {}).get("coordinates", [None, None, None])
        quake_time = props.get("time")

        records.append({
            "id": feature.get("id"),
            "magnitude": props.get("mag"),
            "place": props.get("place"),
            "time_utc": datetime.utcfromtimestamp(quake_time / 1000).isoformat() if quake_time else None,
            "longitude": coords[0],
            "latitude": coords[1],
            "depth_km": coords[2],
            "status": props.get("status"),
            "type": props.get("type"),
            "tsunami": props.get("tsunami"),
            "alert": props.get("alert"),
        })

    return records

def lambda_handler(event=None, context=None):
    BUCKET = "batch-data-demo-euc1" 
    s3 = boto3.client("s3")

    start_date, end_date = get_yesterday_utc_range()
    records = fetch_earthquake_data(start_date, end_date)

    file_name = f"{start_date}.json"
    s3_key = f"raw/{file_name}"
    s3.put_object(Bucket=BUCKET, Key=s3_key, Body=json.dumps(records))
    print(f"✅ Saved {len(records)} records to s3://{BUCKET}/{s3_key}")
    return {"statusCode": 200, "body": f"Fetched {start_date} data"}
