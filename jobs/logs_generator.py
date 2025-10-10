import random
import uuid
from datetime import datetime, timedelta, timezone
from sqlalchemy import create_engine, MetaData, Table, Column, String, TIMESTAMP, JSON, insert
from sqlalchemy.exc import IntegrityError

# Your DB connection string
DATABASE_URL = "postgresql+psycopg2://pgrkam:root@localhost:5432/pgrkam"

engine = create_engine(DATABASE_URL)
metadata = MetaData()

# Define table schema
events_table = Table(
    'events', metadata,
    Column('event_id', String, primary_key=True),
    Column('event_type', String, nullable=False),
    Column('user_id', String),
    Column('session_id', String, nullable=False),
    Column('timestamp', TIMESTAMP, nullable=False),
    Column('properties', JSON),
)

# Create table if it doesn't exist
metadata.create_all(engine)

# Generate synthetic events
user_ids = [f"user_{i}" for i in range(1, 51)]
session_ids = [str(uuid.uuid4()) for _ in range(100)]
event_types = ["page_load", "button_click", "form_submit"]
pages = ["/home", "/jobs", "/profile", "/apply", "/dashboard"]
buttons = ["search", "apply", "submit", "cancel"]

def generate_event():
    event_id = str(uuid.uuid4())
    event_type = random.choice(event_types)
    user_id = random.choice(user_ids)
    session_id = random.choice(session_ids)
    timestamp = datetime.now(timezone.utc) - timedelta(minutes=random.randint(0, 120))
    if event_type == "page_load":
        properties = {"page": random.choice(pages)}
    elif event_type == "button_click":
        properties = {"button_id": random.choice(buttons)}
    else:
        properties = {"form_id": "application_form", "fields_filled": {"experience": "3 years"}}
    return {
        "event_id": event_id,
        "event_type": event_type,
        "user_id": user_id,
        "session_id": session_id,
        "timestamp": timestamp,
        "properties": properties,
    }

def main():
    events = [generate_event() for _ in range(500)]
    with engine.connect() as conn:
        for event in events:
            stmt = insert(events_table).values(**event)
            try:
                conn.execute(stmt)
            except IntegrityError:
                # Handle duplicate event_id if it occurs
                pass
        conn.commit()
    print("Synthetic events successfully inserted.")

if __name__ == "__main__":
    main()
