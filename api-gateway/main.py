# api-gateway/main.py
from fastapi import FastAPI
from pydantic import BaseModel
import httpx

app = FastAPI()

class Event(BaseModel):
    user_id: str
    session_id: str
    event_type: str
    timestamp: str
    metadata: dict

@app.post("/api/events")
async def relay_event(event: Event):
    async with httpx.AsyncClient() as client:
        await client.post("http://events-service:8001/events", json=event.dict())
    return {"status": "received"}
