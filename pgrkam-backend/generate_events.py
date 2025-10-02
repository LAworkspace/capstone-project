import psycopg2
import random
from datetime import datetime, timedelta
import json
import uuid

# Connect to PostgreSQL
conn = psycopg2.connect(
    dbname="pgrkam",
    user="lakshmianand",
    password="yourpassword",  # your actual password
    host="localhost",
    port="5432"
)
conn.autocommit = True
cursor = conn.cursor()

# Pages, event types, buttons
pages = ["home", "jobs", "profile", "training", "business_opportunities"]
event_types = ["page_load", "click", "form_submit", "job_apply", "video_watch"]
buttons = ["apply", "submit", "next", "watch", "learn_more"]

# Optional job IDs for job_apply events
job_ids = [f"job_{i}" for i in range(1, 101)]

def generate_events(num_users=1000, events_per_user=50):
    """Generate 50,000 events: 1000 users x 50 events each"""
    total_events = 0
    for user_id in range(1, num_users + 1):
        for _ in range(events_per_user):
            session_id = str(uuid.uuid4())
            event_type = random.choices(
                event_types, weights=[0.3, 0.3, 0.2, 0.1, 0.1], k=1
            )[0]
            timestamp = datetime.now() - timedelta(days=random.randint(0, 30),
                                                   minutes=random.randint(0, 1440))
            
            metadata = {"page": random.choice(pages),
                        "button": random.choice(buttons)}
            
            if event_type == "job_apply":
                metadata["job_id"] = random.choice(job_ids)
            elif event_type == "form_submit":
                metadata["form"] = random.choice(["profile_update", "training_signup", "job_application"])
            
            cursor.execute(
                """
                INSERT INTO events (user_id, session_id, event_type, timestamp, metadata)
                VALUES (%s, %s, %s, %s, %s)
                """,
                (str(user_id), session_id, event_type, timestamp, json.dumps(metadata))
            )
            total_events += 1

    print(f"{total_events} synthetic events inserted successfully!")

if __name__ == "__main__":
    generate_events()  # 1000 users x 50 events = 50,000 events
