# Screenshot checklist

These are **instructions**, not screenshots. Capture them from your own working environment and save as PNG in `docs/screenshots/`.

1. `bigquery-summary.png`: Open BigQuery, run the `COUNT(*)`, `COUNT(DISTINCT event_id)`, and `COUNT(DISTINCT event_name)` summary. Show the query and result row (1,001 / 1,001 / 5).
2. `bigquery-event-types.png`: Run the event-name breakdown query from the README. Show all five rows.
3. `github-actions.png`: Open GitHub → Actions → successful **Python Tests** run. Show the green check and run name.
4. `local-tests.png`: In PowerShell, run `python -m pytest -q`; capture the final result (11 passed in the observed run).
5. `scheduled-etl.png`: Show `Get-ScheduledTaskInfo -TaskName "CampusFix Daily ETL"` and the last few lines of `logs/etl.log` with successful completion. Do not present a manually triggered run as an unattended run.

Before uploading, crop browser tabs and terminal history to exclude email addresses, account identifiers, passwords, tokens, and personal file paths. If results differ from those recorded on 4 November 2026, update the README to reflect the new run.

Once images are saved, open README.md and remove the HTML comment markers around the screenshot image links. GitHub will then render them.
