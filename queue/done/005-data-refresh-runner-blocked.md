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

## Report (session 216, 13 October 2026)

Moved to done without a run (the owner's ruling of 12 October 2026, session 216, point 4): session 206 did what this task asks for CARB. Its pull of CARB's auction summary (336 rows, newest auction 1 August 2026) and LCFS credit workbook (1,124 rows, newest 14 September 2026) from the data machine, each with its validator, coverage row, archive and Redivis draft, is in `archive/sessions/SESSION_206_REPORT.md` (step 6), and `warehouse/run_data_machine.sh` now asks CARB every day (`dm_carb_auction`, `dm_carb_lcfs`). NYISO's queue workbook is not pulled: NYISO's terms ask for written permission (`docs/licenses.md`; `nyiso_interconnection_queue` is "license needed" from 20 October 2026 in `warehouse/metadata/license_status.csv`), so it stays held until its license is answered. Issue #3 (CARB) can be closed by a person; issue #4 (NYISO) stays open.
