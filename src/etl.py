import json
import os
from collections import Counter
from pathlib import Path
from datetime import datetime, timezone

import psycopg
from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]
SCHEMA = json.loads((ROOT / 'docs' / 'event.schema.json').read_text(encoding='utf-8-sig'))
VALIDATOR = Draft202012Validator(SCHEMA, format_checker=FormatChecker())
DSN = os.getenv('DATABASE_URL', 'postgresql://campusfix:local_dev_only@localhost:55433/usage_analytics')

DDL = '''
CREATE TABLE IF NOT EXISTS product_events (
 event_id UUID PRIMARY KEY,
 event_name TEXT NOT NULL,
 event_timestamp TIMESTAMPTZ NOT NULL,
 user_id TEXT NOT NULL,
 session_id TEXT NOT NULL,
 schema_version TEXT NOT NULL,
 properties JSONB NOT NULL,
 ingested_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE TABLE IF NOT EXISTS event_quarantine (
 fingerprint TEXT PRIMARY KEY,
 raw_event TEXT NOT NULL,
 reason TEXT NOT NULL,
 quarantined_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
'''

def validate(event):
    errors = sorted(VALIDATOR.iter_errors(event), key=lambda e: str(e.path))
    if errors:
        raise ValueError('; '.join(error.message for error in errors))
    # Require an explicit timezone; naive event timestamps cannot be ordered reliably.
    timestamp = datetime.fromisoformat(event['event_timestamp'].replace('Z', '+00:00'))
    if timestamp.tzinfo is None or timestamp.utcoffset() is None:
        raise ValueError('event_timestamp must include a timezone')
    return timestamp.astimezone(timezone.utc)

def load(path=ROOT / 'data' / 'events.jsonl'):
    import hashlib
    counts = Counter()
    with psycopg.connect(DSN, connect_timeout=5) as connection:
        with connection.cursor() as cursor:
            cursor.execute(DDL)
            for line in Path(path).read_text(encoding='utf-8-sig').splitlines():
                if not line.strip():
                    continue
                try:
                    event = json.loads(line)
                    timestamp = validate(event)
                except (ValueError, TypeError) as error:
                    fingerprint = hashlib.sha256(line.encode('utf-8')).hexdigest()
                    cursor.execute('''INSERT INTO event_quarantine (fingerprint, raw_event, reason)
                        VALUES (%s,%s,%s) ON CONFLICT (fingerprint) DO NOTHING''',
                        (fingerprint, line, str(error)))
                    counts['quarantined'] += 1
                    continue
                cursor.execute('''INSERT INTO product_events
                    (event_id,event_name,event_timestamp,user_id,session_id,schema_version,properties)
                    VALUES (%s,%s,%s,%s,%s,%s,%s)
                    ON CONFLICT (event_id) DO NOTHING RETURNING event_id''',
                    (event['event_id'], event['event_name'], timestamp,
                     event['user_id'], event['session_id'], event['schema_version'],
                     psycopg.types.json.Jsonb(event['properties'])))
                counts['inserted' if cursor.fetchone() else 'duplicate'] += 1
            cursor.execute('SELECT count(*) FROM product_events')
            total = cursor.fetchone()[0]
            cursor.execute('SELECT count(*) FROM event_quarantine')
            quarantine_total = cursor.fetchone()[0]
    print(f"Run: inserted={counts['inserted']} duplicate={counts['duplicate']} quarantined={counts['quarantined']}")
    print(f'Database: product_events={total} event_quarantine={quarantine_total}')
    return counts

if __name__ == '__main__':
    load()

