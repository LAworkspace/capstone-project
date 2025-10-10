from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional, Dict, Any
from datetime import datetime
from sqlalchemy import create_engine, Table, Column, String, DateTime, JSON, MetaData
from sqlalchemy.dialects.postgresql import insert

DATABASE_URL = "postgresql+psycopg2://pgrkam:root@localhost:5432/pgrkam"

engine = create_engine(DATABASE_URL)
metadata = MetaData()

events_table = Table(
    "events",
    metadata,
    Column("event_id", String, primary_key=True),
    Column("event_type", String, nullable=False),
    Column("user_id", String, nullable=True),
    Column("session_id", String, nullable=False),
    Column("timestamp", DateTime, nullable=False),
    Column("properties", JSON),
)

metadata.create_all(engine)

app = FastAPI()

class Event(BaseModel):
    event_id: str
    event_type: str
    user_id: Optional[str] = None
    session_id: str
    timestamp: datetime
    properties: Optional[Dict[str, Any]] = None

@app.post("/events")
def ingest_event(event: Event):
    stmt = insert(events_table).values(
        event_id=event.event_id,
        event_type=event.event_type,
        user_id=event.user_id,
        session_id=event.session_id,
        timestamp=event.timestamp,
        properties=event.properties,
    ).on_conflict_do_nothing(index_elements=['event_id'])  # avoid duplicates by event_id

    with engine.connect() as conn:
        try:
            conn.execute(stmt)
            conn.commit()
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to insert event: {str(e)}")

    return {"status": "success"}
