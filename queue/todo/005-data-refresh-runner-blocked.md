---
role: data
spend_cap_usd: 1.5
timeout_minutes: 120
permission_mode: auto
---
# Refresh the two tables GitHub's runners cannot download

Source: PRIORITIES.md layer 1, order 1 (the warehouse is serving something stale); warehouse/metadata/known_gaps.csv; open issues #3 and #4.

CARB's auction summary PDF (`carb_auction_allowance_prices`) and NYISO's interconnection queue workbook (`nyiso_interconnection_queue`) answer GitHub's runners with HTTP 202 and no body, so the daily job cannot refresh them. They download from a residential connection, which is why this is a data-machine task.

Do this, under the data lock the worker already holds (do not take or release it yourself):

1. Run `python scripts/sync.py` first. Then follow docs/runbook.md, sections "CARB auction prices" and "NYISO interconnection queue", exactly:
   - run each connector as the runbook says;
   - read its run log, not only the summary line;
   - validate the two files with `python warehouse/validate/erw_validate.py`.
2. If a source answers HTTP 202 here too, or anything fails:
   - do not retry more than the connector already does;
   - write nothing partial;
   - record the exact error.
3. For each table that refreshed:
   - rebuild coverage (`python warehouse/metadata/build_coverage.py`);
   - upload it as a Redivis draft the way the daily job does (never release a version: releasing is always Samuel's click);
   - load Supabase if the table is in `warehouse/supabase/live_set.yaml`.
4. Commit after each unit of work with a clear message. If a table is newer than its issue's latest failure, add one line to the final report saying issue #3 or #4 can be closed (do not close it yourself).

Ceiling: two downloads per source. No model calls besides this session. Real data only; no em dashes in any file.
