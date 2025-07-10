import os
import json
import boto3
import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq
from datetime import datetime, timezone
import io

s3 = boto3.client("s3")
BUCKET = "your-bucket-name"  # TODO: replace with your actual bucket name

def get_target_date():
    date_str = os.environ.get("TARGET_DATE")
    if date_str:
        return datetime.strptime(date_str, "%Y-%m-%d").date()
    else:
        return datetime.now(timezone.utc).date()

def lambda_handler(event=None, context=None):
    target_date = get_target_date()
    date_str = target_date.strftime("%Y-%m-%d")

    # Define S3 paths
    raw_key = f"raw/{date_str}.json"
    processed_key = f"processed/year={target_date.year}/month={target_date.month:02d}/day={target_date.day:02d}/data.parquet"

    # Download raw data
    try:
        response = s3.get_object(Bucket=BUCKET, Key=raw_key)
        raw_json = json.loads(response["Body"].read())
    except Exception as e:
        print(f"Failed to read raw JSON: {e}")
        return {"statusCode": 404, "body": f"Raw file not found: {raw_key}"}

    # Load into DataFrame
    df = pd.DataFrame(raw_json)

    # Convert to Parquet in memory
    table = pa.Table.from_pandas(df)
    buf = io.BytesIO()
    pq.write_table(table, buf)

    # Upload to processed/
    try:
        s3.put_object(Bucket=BUCKET, Key=processed_key, Body=buf.getvalue())
        print(f"Wrote Parquet to s3://{BUCKET}/{processed_key}")
        return {"statusCode": 200, "body": f"Success for {date_str}"}
    except Exception as e:
        print(f"Failed to write Parquet: {e}")
        return {"statusCode": 500, "body": f"Failed to write for {date_str}"}
