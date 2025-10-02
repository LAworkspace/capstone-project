from fastapi import FastAPI
from pydantic import BaseModel
from typing import Optional, Dict
import psycopg2
import json

app = FastAPI()

# Connect to PostgreSQL
conn = psycopg2.connect(
    dbname="pgrkam",
    user="lakshmianand",  # your DB user
    password="root",  # set your password
    host="localhost",
    port="5432"
)
conn.autocommit = True
cursor = conn.cursor()

# Event model
class Event(BaseModel):
    user_id: Optional[str] = None
    session_id: str
    event_type: str
    timestamp: str
    metadata: Optional[Dict] = None

@app.post("/api/logEvent")
async def log_event(event: Event):
    try:
        cursor.execute(
            """
            INSERT INTO events (user_id, session_id, event_type, timestamp, metadata)
            VALUES (%s, %s, %s, %s, %s)
            """,
            (event.user_id, event.session_id, event.event_type, event.timestamp, json.dumps(event.metadata))
        )
        return {"status": "ok"}
    except Exception as e:
        print("Error inserting event:", e)
        return {"status": "error", "message": str(e)}

@app.get("/")
def root():
    return {"message": "Backend running!"}
