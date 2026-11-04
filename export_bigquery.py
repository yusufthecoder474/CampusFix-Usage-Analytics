import csv
import json
from pathlib import Path

import psycopg
from src.etl import DSN

output = Path("data/bigquery_events.csv")
output.parent.mkdir(parents=True, exist_ok=True)

with psycopg.connect(DSN) as conn:
    with conn.cursor() as cursor:
        cursor.execute("""
            SELECT event_id, event_name, event_timestamp,
                   user_id, session_id, schema_version, properties
            FROM product_events
            ORDER BY event_timestamp, event_id
        """)
        rows = cursor.fetchall()

with output.open("w", newline="", encoding="utf-8") as file:
    writer = csv.writer(file)
    writer.writerow([
        "event_id", "event_name", "event_timestamp",
        "user_id", "session_id", "schema_version", "properties"
    ])
    for row in rows:
        writer.writerow([
            str(row[0]),
            row[1],
            row[2].isoformat(),
            row[3],
            row[4],
            row[5],
            json.dumps(row[6])
        ])

print(f"Exported {len(rows)} validated events")
print(f"CSV saved to: {output.resolve()}")
