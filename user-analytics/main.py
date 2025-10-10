# user-analytics/main.py
from fastapi import FastAPI, HTTPException
import sqlalchemy
import pandas as pd

DATABASE_URL = "postgresql+psycopg2://pgrkam:root@localhost:5432/pgrkam"

engine = sqlalchemy.create_engine(DATABASE_URL)

app = FastAPI()

@app.get("/users/{user_id}/features")
def get_user_features(user_id: str):
    query = f"SELECT * FROM events WHERE user_id = '{user_id}'"
    df = pd.read_sql(query, engine)

    if df.empty:
        raise HTTPException(status_code=404, detail="User not found or no events")

    total_clicks = df[df["event_type"] == "click"].shape[0]
    job_applies = df[df["event_type"] == "job_apply"].shape[0]
    video_watches = df[df["event_type"] == "video_watch"].shape[0]

    features = {
        "total_clicks": total_clicks,
        "job_applications": job_applies,
        "video_engagements": video_watches,
    }
    return features
