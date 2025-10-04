# events-service/main.py
from fastapi import FastAPI
from pydantic import BaseModel
import databases
import sqlalchemy
import datetime

DATABASE_URL = "postgresql://postgres:password@postgres:5432/pgrkam"
database = databases.Database(DATABASE_URL)
metadata = sqlalchemy.MetaData()

events = sqlalchemy.Table(
    "events",
    metadata,
    sqlalchemy.Column("id", sqlalchemy.Integer, primary_key=True),
    sqlalchemy.Column("user_id", sqlalchemy.String),
    sqlalchemy.Column("session_id", sqlalchemy.String),
    sqlalchemy.Column("event_type", sqlalchemy.String),
    sqlalchemy.Column("timestamp", sqlalchemy.DateTime),
    sqlalchemy.Column("metadata", sqlalchemy.JSON),
)

engine = sqlalchemy.create_engine(DATABASE_URL)
metadata.create_all(engine)

app = FastAPI()

class Event(BaseModel):
    user_id: str
    session_id: str
    event_type: str
    timestamp: datetime.datetime
    metadata: dict

@app.on_event("startup")
async def startup():
    await database.connect()

@app.on_event("shutdown")
async def shutdown():
    await database.disconnect()

@app.post("/events")
async def create_event(event: Event):
    query = events.insert().values(
        user_id=event.user_id,
        session_id=event.session_id,
        event_type=event.event_type,
        timestamp=event.timestamp,
        metadata=event.metadata,
    )
    await database.execute(query)
    return {"status": "stored"}
