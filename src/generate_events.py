import json
import random
import uuid
from datetime import datetime, timezone, timedelta
from pathlib import Path

random.seed(42)

EVENT_NAMES = [
    "issue_created",
    "issue_status_changed",
    "issue_reopened",
    "issue_closed",
    "user_login",
]

def generate_events(count=1000):
    events = []
    now = datetime.now(timezone.utc)

    for index in range(count):
        event = {
            "event_id": str(uuid.uuid4()),
            "event_name": random.choice(EVENT_NAMES),
            "event_timestamp": (
                now - timedelta(minutes=random.randint(0, 1440))
            ).isoformat(),
            "user_id": f"user_{random.randint(1, 100)}",
            "session_id": f"session_{random.randint(1, 200)}",
            "schema_version": "1.0",
            "properties": {
                "issue_id": f"ISSUE-{random.randint(1, 500)}",
                "source": "synthetic_campusfix"
            }
        }
        events.append(event)

    return events

def main():
    output = Path("data/events.jsonl")
    output.parent.mkdir(parents=True, exist_ok=True)

    events = generate_events()

    with output.open("w", encoding="utf-8") as file:
        for event in events:
            file.write(json.dumps(event) + "\n")

    print(f"Generated {len(events)} synthetic events")
    print(f"Saved to {output.resolve()}")

if __name__ == "__main__":
    main()
