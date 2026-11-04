# CampusFix Usage Analytics — Data Dictionary

## 1. Project overview

CampusFix Usage Analytics is a data engineering project that processes synthetic product-usage events modeled on CampusFix issue-management workflows.

The pipeline generates sample events, validates their structure, loads valid records into PostgreSQL, quarantines malformed records, and supports analytical queries in Google BigQuery.

The current dataset is synthetic. Live CampusFix application instrumentation is not yet implemented.

## 2. Event tracking plan

| Event name | Meaning | Example trigger |
|---|---|---|
| issue_created | A new campus issue is submitted | User submits an issue |
| issue_status_changed | An issue moves to another status | Coordinator or technician changes status |
| issue_reopened | A previously closed issue is reopened | User reopens an issue |
| issue_closed | An issue is marked closed | Authorized user closes an issue |
| user_login | A user signs in | Successful authentication |

These are modeled event definitions for the analytics dataset, not confirmation that the production application currently emits them.

## 3. Event schema

| Field | Type | Required | Description |
|---|---|---|---|
| event_id | UUID string | Yes | Unique identifier used for deduplication |
| event_name | String | Yes | One of the five supported event names |
| event_timestamp | ISO 8601 datetime | Yes | Event occurrence time, including timezone |
| user_id | String | Yes | Synthetic user identifier |
| session_id | String | Yes | Synthetic session identifier |
| schema_version | String | Yes | Event schema version, currently 1.0 |
| properties | JSON object | Yes | Additional event attributes |

The source JSON Schema is stored in docs/event.schema.json.

## 4. Event properties

The synthetic event generator includes:

| Property | Type | Description |
|---|---|---|
| issue_id | String | Synthetic issue identifier |
| source | String | Identifies the synthetic event generator |

Properties are not yet event-specific. A future version can define different required properties for each event type.

## 5. PostgreSQL tables

### product_events

Stores validated events.

| Column | Type | Purpose |
|---|---|---|
| event_id | UUID | Primary key; prevents duplicate IDs |
| event_name | TEXT | Event category |
| event_timestamp | TIMESTAMPTZ | Event occurrence time |
| user_id | TEXT | User identifier |
| session_id | TEXT | Session identifier |
| schema_version | TEXT | Schema version |
| properties | JSONB | Event attributes |
| ingested_at | TIMESTAMPTZ | Database ingestion time |

### event_quarantine

Stores malformed or schema-invalid records.

| Column | Type | Purpose |
|---|---|---|
| fingerprint | TEXT | SHA-256 fingerprint; primary key |
| raw_event | TEXT | Original rejected record |
| reason | TEXT | Validation failure |
| quarantined_at | TIMESTAMPTZ | Quarantine insertion time |

## 6. Data quality rules

1. Events must satisfy the JSON Schema.
2. Event timestamps must contain timezone information.
3. Duplicate event IDs are ignored using PostgreSQL ON CONFLICT.
4. Malformed JSON and invalid event records are quarantined.
5. Reprocessing the same valid input must not create duplicate database records.

## 7. Verified local results

The following results were observed during local execution on 4 November 2026:

- 11 automated tests passed.
- 1,000 generated synthetic events were initially ingested.
- Three invalid test records were quarantined.
- One additional valid test record was inserted.
- PostgreSQL contained 1,001 valid events and three quarantined records.
- Reprocessing the original dataset detected 1,000 duplicate events without reinserting them.
- Windows Task Scheduler successfully launched the ETL manually, returning result code 0.

## 8. BigQuery analytics

Project: named-messenger-468517-q2

Dataset: campusfix_analytics

Table: product_events

Region: asia-south1 (Mumbai)

A manually uploaded CSV was used to create the analytical table.

Verified BigQuery results:

- Total events: 1,001
- Distinct event IDs: 1,001
- Distinct event types: 5

The CSV upload is a separate manual step. The current Python ETL does not automatically synchronize PostgreSQL with BigQuery.

## 9. Orchestration

The pipeline uses Windows Task Scheduler with a daily trigger and a Python wrapper implementing retries and logging.

Task name: CampusFix Daily ETL

Scheduled time: 6:37 PM local time

A manually triggered task run completed successfully on 4 November 2026. The first unattended daily execution remains to be verified.

## 10. Known limitations

- Events are synthetic, not collected from live CampusFix users.
- BigQuery loading is manual.
- Late-arriving event handling has not been demonstrated.
- Automated failure notifications have not been verified.
- Windows Task Scheduler requires the local machine and PostgreSQL service to be available.
- No Apache Airflow orchestration has been implemented.
