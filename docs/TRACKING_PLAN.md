# CampusFix Product Usage Tracking Plan

## Purpose
Track product usage events for analytics.

## Events

| Event | Description |
|---|---|
| issue_created | A student creates an issue |
| issue_status_changed | Issue status changes |
| issue_reopened | A closed issue is reopened |
| issue_closed | An issue is closed |
| user_login | A user successfully logs in |

## Required fields
- event_id
- event_name
- event_timestamp
- user_id
- session_id
- schema_version
- properties

## Data quality
- Validate required fields
- Detect duplicate event IDs
- Validate timestamps
- Quarantine invalid events
- Support idempotent reprocessing

## Privacy
Do not collect passwords, email addresses, names, cookies or authentication tokens.

## Source
Initial events are synthetic, not collected from live CampusFix users.
