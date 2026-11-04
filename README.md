# CampusFix Usage Analytics

A Python-based product event analytics pipeline that validates synthetic CampusFix-style usage events, stores clean records in PostgreSQL, quarantines invalid data, and makes validated events available for analysis in Google BigQuery.

## Architecture

```mermaid
flowchart TD
    A["Synthetic CampusFix event generator"] --> B["JSONL event file"]
    B --> C["Python ETL and JSON Schema validation"]
    C -->|Valid| D["PostgreSQL product_events"]
    C -->|Invalid| E["PostgreSQL event_quarantine"]
    D --> F["CSV export"]
    F --> G["Manual upload to BigQuery"]
    G --> H["SQL usage analytics"]
    I["Windows Task Scheduler"] --> J["Retry and logging wrapper"]
    J --> C
