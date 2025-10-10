import pandas as pd
from sqlalchemy import create_engine
from minio import Minio
import os

# PostgreSQL connection
DATABASE_URL = "postgresql+psycopg2://pgrkam:root@localhost:5432/pgrkam"
engine = create_engine(DATABASE_URL)

# MinIO connection settings
MINIO_ENDPOINT = "localhost:9000"
MINIO_ACCESS_KEY = "minioadmin"
MINIO_SECRET_KEY = "minioadmin"
MINIO_BUCKET = "ml-features"
MINIO_OBJECT = "features/session_features.csv"

minio_client = Minio(
    MINIO_ENDPOINT,
    access_key=MINIO_ACCESS_KEY,
    secret_key=MINIO_SECRET_KEY,
    secure=False,
)

def load_events():
    query = "SELECT * FROM events"
    df = pd.read_sql(query, engine)
    # Remove any timezone info (tz-naive)
    df['timestamp'] = pd.to_datetime(df['timestamp']).dt.tz_localize(None)
    return df

def engineer_features(df):
    # Basic session grouping and initial aggregates
    grouped = df.sort_values('timestamp').groupby('session_id')
    sessions = grouped.agg({
        'user_id': 'first',
        'timestamp': ['min', 'max', 'count'],
        'event_type': lambda x: list(x),
        'properties': lambda x: list(x)
    }).reset_index()
    sessions.columns = [
        'session_id',
        'user_id',
        'start_time',
        'end_time',
        'event_count',
        'event_types',
        'event_properties'
    ]

    # Session duration
    sessions['session_duration'] = (sessions['end_time'] - sessions['start_time']).dt.total_seconds()

    # Pivot table: count of each event_type per session
    event_counts = df.pivot_table(
        index='session_id',
        columns='event_type',
        values='event_id',
        aggfunc='count'
    ).fillna(0)
    sessions = sessions.merge(event_counts, on='session_id', how='left')

    # Session inactivity gaps - max, mean, std gap per session
    df['prev_timestamp'] = df.groupby('session_id')['timestamp'].shift(1)
    df['gap'] = (df['timestamp'] - df['prev_timestamp']).dt.total_seconds()
    gap_stats = df.groupby('session_id')['gap'].agg(['max', 'mean', 'std']).fillna(0)
    sessions = sessions.merge(gap_stats, on='session_id', how='left')

    # First and last event types
    first_event = df.groupby('session_id').first()['event_type']
    last_event = df.groupby('session_id').last()['event_type']
    sessions['first_event'] = sessions['session_id'].map(first_event)
    sessions['last_event'] = sessions['session_id'].map(last_event)

    return sessions

def save_to_minio(file_path):
    # Create bucket if not exists
    if not minio_client.bucket_exists(MINIO_BUCKET):
        minio_client.make_bucket(MINIO_BUCKET)
    # Upload file
    minio_client.fput_object(MINIO_BUCKET, MINIO_OBJECT, file_path)
    print(f"Uploaded {file_path} to MinIO bucket {MINIO_BUCKET}/{MINIO_OBJECT}")

def main():
    df = load_events()
    features = engineer_features(df)
    os.makedirs("data", exist_ok=True)
    file_path = "data/session_features.csv"
    features.to_csv(file_path, index=False)
    print("Feature engineering complete, file saved:", file_path)
    save_to_minio(file_path)

if __name__ == "__main__":
    main()
