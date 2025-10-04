import pandas as pd
from datetime import datetime
import os, json
from sqlalchemy import create_engine
from minio import Minio

from dotenv import load_dotenv
import os

load_dotenv()  # Load variables from .env

DB_URL = os.getenv("DATABASE_URL")
engine = create_engine(DB_URL)

minio_client = Minio(
    os.getenv("MINIO_ENDPOINT", "localhost:9000"),
    access_key=os.getenv("MINIO_ACCESS_KEY", "minio"),
    secret_key=os.getenv("MINIO_SECRET_KEY", "MINIO_ROOT_PASSWORD"),
    secure=False
)
bucket = "features"
if not minio_client.bucket_exists(bucket):
    minio_client.make_bucket(bucket)

# 1) read raw events
df = pd.read_sql("SELECT * FROM events", engine, parse_dates=["timestamp"])

# sessionization + aggregation
agg = df.groupby("session_id").agg(
    user_id=("user_id", lambda s: s.mode().iloc[0] if not s.mode().empty else None),
    first_ts=("timestamp", "min"),
    last_ts=("timestamp", "max"),
    total_events=("event_type", "count"),
    page_loads=("event_type", lambda s: (s=="page_load").sum()),
    clicks=("event_type", lambda s: (s=="click").sum()),
    job_applies=("event_type", lambda s: (s=="job_apply").sum()),
    forms=("event_type", lambda s: (s=="form_submit").sum()),
    videos=("event_type", lambda s: (s=="video_watch").sum()),
).reset_index()

agg["session_duration_s"] = (agg["last_ts"] - agg["first_ts"]).dt.total_seconds().fillna(0)
agg["avg_time_between_events"] = agg["session_duration_s"] / agg["total_events"].replace(0, 1)

# add weekday/hour features
agg["session_start_weekday"] = agg["first_ts"].dt.weekday
agg["session_start_hour"] = agg["first_ts"].dt.hour

# write Parquet & upload
ts = datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")
fname = f"features/session_features_{ts}.parquet"
agg.to_parquet(fname, index=False)
minio_client.fput_object(bucket, fname, fname)
print(f"Uploaded {fname} to minio://{bucket}")
