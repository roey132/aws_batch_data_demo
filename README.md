# 🌍 Earthquake Data Batch Pipeline (AWS Athena + S3 + Lambda)

This project demonstrates a cloud-native batch data pipeline that ingests, processes, and queries daily earthquake data using the following stack:

- **AWS Lambda**: event-driven ingestion and transformation
- **Amazon S3**: data lake with partitioned storage (raw + processed)
- **AWS EventBridge**: orchestration of daily batch steps
- **AWS Glue**: partition discovery via crawler
- **AWS Athena**: SQL querying over processed JSON data
- **GitHub Actions**: CI/CD pipeline for Lambda deployment

---

## 📦 Features

- Scheduled ingestion of daily [USGS earthquake data](https://earthquake.usgs.gov/)
- Data is stored in `raw/` as JSON and transformed to partitioned `processed/` files
- Athena-ready data layout:  
  `s3://<bucket>/processed/year=YYYY/month=MM/day=DD/data.json`
- Timezone-aware, backfill-capable transformation (via `TARGET_DATE` env var)
- Custom EventBridge event triggers Glue crawler on transform success
- Built to be fully CI/CD-compatible via GitHub Actions

---

## 📁 Folder Structure

- `ingestion/get_data.py` – Lambda function to ingest raw data from USGS API
- `ingestion/transform.py` – Lambda function to process raw data to partitioned JSON
- `.github/workflows/` – GitHub Actions for CI/CD of Lambda functions
- `README.md` – Project documentation
- `requirements.txt` – Dependencies for local dev and Lambda packaging


---

## 🚀 Setup

1. **Install requirements**  
   `pip install -r requirements.txt`

2. **Deploy Lambda functions**  
   Uses GitHub Actions + AWS Secrets Manager

3. **Set up Athena**  
   Create external table + run `MSCK REPAIR TABLE`

4. **Set up Glue Crawler**
   Create a glue crawler for the athena table to run when needed

5. **Set up Eventbridge flows**
   Create a flow that runs the lambda functions and crawler
   one after the other on success.

---

## 🔍 Sample Athena Query

```sql
SELECT place, time_utc, magnitude
FROM batch_data_demo.earthquakes
WHERE year = '2025' AND month = '07'
ORDER BY time_utc DESC
LIMIT 10;
```

Python Version: 3.12
Author: Roey Aharonov
Date: 2025-07-12
