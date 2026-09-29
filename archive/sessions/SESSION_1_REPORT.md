# Session 1 report

Energy Research Warehouse (ERW), session 1, run 2026-09-24/25 (UTC). Every task in SESSION_1_PROMPT.md was carried out. Nothing was pushed.

## What was built

| Task | Result | Commit |
|---|---|---|
| 1 | Shallow clone of the IRW at `../irw-reference`, commit `d76fb5cc74b2c41e63a27f9b2ce2dfaed7dfe42b`. All eight listed documents read. No IRW data copied, nothing committed from it | `16d90c7` |
| 2 | `CLAUDE.md`, `ARCHITECTURE.md`, `PRIORITIES.md`, `docs/datastandard.md` (ERW Data Standard v0), folders `warehouse/{connectors,output,validate}`, `docs`, `.claude/skills`, `.gitignore`; one paragraph appended to `README.md` | `fe1c461` |
| 3 | `warehouse/connectors/ercot_prices.py`, `requirements.txt`, `requirements-py314.txt`, two output CSVs, three run logs | `a4ba5c1` |
| 4 | `warehouse/validate/erw_validate.py`. Both ERCOT files PASS, exit 0 (output below) | `273208e` |
| 5 | This report | final commit |

Connector summary lines (run `20260925T041925Z`):

```
ercot_dam_hub_prices.csv: rows=3600 range=2026-08-25T05:00:00Z..2026-09-24T04:00:00Z hubs=HB_BUSAVG,HB_HOUSTON,HB_NORTH,HB_SOUTH,HB_WEST min=2.36 max=158.93 USD/MWh
ercot_rtm_hub_prices.csv: rows=14400 range=2026-08-25T05:00:00Z..2026-09-24T04:45:00Z hubs=HB_BUSAVG,HB_HOUSTON,HB_NORTH,HB_SOUTH,HB_WEST min=-72.18 max=795.33 USD/MWh
```

Sources: DAM from ERCOT NP4-190-CD (30 daily files). RTM from ERCOT NP6-785-ER, the 2026 yearly archive published 2026-09-20, for intervals up to 2026-09-20T04:45Z, then from 384 NP6-905-CD 15-minute files. In the 485 hub-intervals covered by both sources, every value matched (max abs diff 0.0000). Every row carries `source`, `source_url` (the exact ERCOT document), `retrieved_at` and `vintage` (publish time). The run log in `warehouse/output/logs/` names every document.

Validator output, exit 0:

```
warehouse/output/ercot_dam_hub_prices.csv
  ERW Data Standard v0, shape series: PASS (0 error(s), 0 warning(s))
  info  rows=3600 columns=13 header_comment_lines=8
  info  ts_utc 2026-08-25T05:00:00Z .. 2026-09-24T04:00:00Z
  info  value 2.36 .. 158.93
  info  entities=5 variables=1
warehouse/output/ercot_rtm_hub_prices.csv
  ERW Data Standard v0, shape series: PASS (0 error(s), 0 warning(s))
  info  rows=14400 columns=13 header_comment_lines=12
  info  ts_utc 2026-08-25T05:00:00Z .. 2026-09-24T04:45:00Z
  info  value -72.18 .. 795.33
  info  entities=5 variables=1
```

I also ran the validator on throwaway files outside the repo. A malformed file returned exit 1 with 8 errors. An empty file and a missing file each returned exit 2.

## Decisions

1. **Window** is the 30 complete ERCOT operating days (America/Chicago) before the run date, 2026-08-25 to 2026-09-23, the same for both markets. Today's partial day and tomorrow's DAM are excluded.
2. **RTM uses two ERCOT reports.** The live report NP6-905-CD only keeps about 8 days, so 30 days are not available from it alone. The NP6-785-ER archive wins where the two overlap. This is recorded per row and in the file header.
3. **Strict completeness.** A market's file is written only if all 5 hubs have every interval (720 hourly, 2,880 quarter-hourly). Otherwise nothing is written for that market. Files are written through a temporary file, so a crash cannot leave a partial file.
4. **Series conventions:** `ts_utc` is interval start in UTC. `entity` is `ercot:HB_NORTH`. Variables are `spp_dam` and `spp_rtm`. `freq` is an ISO 8601 duration. `geo` is `US-TX`. `vintage` is the ERCOT publish time of the source document.
5. **Standard v0** defines three shapes (series, entities, events), namespaced source ids, and file names `source_market_product` of 40 characters or fewer. The file's own "Decisions in v0" section has the reasoning and the deferred items.
6. **Provenance header** uses `#` lines before the CSV header. Readers skip them by count. `comment="#"` would cut URLs.
7. **Output CSVs and run logs are committed** so the validator results and provenance can be reproduced from the repo. The logs of the two failed runs are kept as the error record.
8. **Environment:** a project `.venv` (gitignored). gridstatus 0.36.0 is installed with `--no-deps`, with lxml 6.1.3 and numpy 2.3.5 (see errors 1 and 2).
9. **Git identity:** none was configured. I set a repo-local one copied from the existing initial commit's author (Samuel Enrique).
10. `SESSION_1_PROMPT.md` was committed in Task 2, because `git add -A` picked it up.

## Errors hit

1. `pip install gridstatus` failed: `Failed to build installable wheels ... lxml`. gridstatus 0.36.0 pins `lxml~=5.3`, which has no wheel for Python 3.14, the only Python installed. Workaround: install lxml 6.1.3, then gridstatus with `--no-deps`, then its other dependencies.
2. `import numpy` failed: `DLL load failed while importing _multiarray_umath: An Application Control policy has blocked this file`. Windows Smart App Control is On and blocked numpy 2.5.3. numpy 2.3.5 loads.
3. Runs 1 and 2 (`logs/ercot_prices_20260925T041353Z.log`, `...041605Z.log`): RTM failed with `ValueError: Cannot convert from timedelta64[ns] to timedelta64[h]`. This is a gridstatus bug. The current-year NP6-785-ER workbook has empty sheets for Oct to Dec, which makes the hour column dtype object. The connector now casts whole-number hours to int before gridstatus parses them. Values are unchanged. No RTM file was written by those runs.
4. My own bug in run 1: the DAM cross-check joined on mismatched index names and logged "18000 keys, max abs diff 53.86". The data was correct; the check was wrong. It is fixed, and a mismatch now fails the run. Run 1's DAM file was superseded by run 3.

## Rerun

```bash
python -m venv .venv
.venv/Scripts/python -m pip install --no-deps -r requirements-py314.txt   # Python 3.14
# or, on Python 3.10 to 3.13:  pip install -r requirements.txt
.venv/Scripts/python warehouse/connectors/ercot_prices.py
.venv/Scripts/python warehouse/validate/erw_validate.py warehouse/output/ercot_dam_hub_prices.csv warehouse/output/ercot_rtm_hub_prices.csv
```

(On macOS or Linux use `.venv/bin/python`.) A rerun moves the window to the new run date and overwrites both CSVs.

## Open questions for the human

1. ERCOT's `mirDownload?doclookupId=` URLs for NP6-905-CD expire after about 8 days, so `source_url` stops resolving for those rows. The document file name in the run log is the durable id. Should we archive the raw source files (for example on Redivis or object storage)?
2. Should the ERW keep price corrections and revisions (NP4-180-ER, RTM price corrections) as extra vintages, or only the latest value?
3. gridstatus 0.36.0 pins old lxml and has the parse bug above. Report both upstream, pin a Python 3.12 runtime for CI, or both?
4. Should DAM include the next operating day (published at about 13:00 CT), even though RTM cannot?
5. Should output CSVs stay in git as tables grow, or move to Redivis only with git holding the logs?
6. Who holds the Redivis write token, and under which account will ERW datasets live?
