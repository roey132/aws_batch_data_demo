import os
import json
import boto3
import pandas as pd
from datetime import datetime, timedelta, timezone

s3 = boto3.client("s3")
eventbridge = boto3.client("events")

BUCKET = "batch-data-demo-euc1"

def get_target_date():
    date_str = os.environ.get("TARGET_DATE")
    if date_str:
        return datetime.strptime(date_str, "%Y-%m-%d").date()
    else:
        # Default to YESTERDAY in UTC
        return (datetime.now(timezone.utc).date() - timedelta(days=1))

def lambda_handler(event=None, context=None):
    target_date = get_target_date()
    date_str = target_date.strftime("%Y-%m-%d")

    raw_key = f"raw/{date_str}.json"
    processed_key = f"processed/year={target_date.year}/month={target_date.month:02d}/day={target_date.day:02d}/data.json"

    try:
        response = s3.get_object(Bucket=BUCKET, Key=raw_key)
        raw_json = json.loads(response["Body"].read())
    except Exception as e:
        print(f"❌ Failed to read raw file: {e}")
        return {"statusCode": 404, "body": f"Raw file not found: {raw_key}"}

    df = pd.DataFrame(raw_json)

    # Format time_utc field to standard timestamp format (optional but cleaner)
    df["time_utc"] = pd.to_datetime(df["time_utc"], format="ISO8601", errors="coerce") \
                        .dt.strftime("%Y-%m-%d %H:%M:%S")

    try:
        # Convert to JSON array (standard JSON)
        body = json.dumps(df.to_dict(orient="records"), indent=2)

        s3.put_object(Bucket=BUCKET, Key=processed_key, Body=body)
        print(f"✅ JSON written to s3://{BUCKET}/{processed_key}")

        # Emit transform-complete event
        eventbridge.put_events(
            Entries=[
                {
                    'EventBusName': 'pipeline-events',
                    'Source': 'transform.pipeline',
                    'DetailType': 'transform-complete',
                    'Detail': json.dumps({"target_date": date_str})
                }
            ]
        )

        return {"statusCode": 200, "body": f"Success for {date_str}"}
    except Exception as e:
        print(f"❌ Failed to upload JSON: {e}")
        return {"statusCode": 500, "body": f"Error for {date_str}"}
