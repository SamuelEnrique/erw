---
name: erw-add-connector
description: Use this skill when asked to add a new ISO, market, node set or other data source to the Energy Research Warehouse (ERW) price connector, for example "add PJM", "add ERCOT load zones", "add IESO prices", "pull another market", or "wire a new source into the daily refresh". Covers the function in warehouse/connectors/iso_prices.py, raw file saving, the completeness rule, table naming, the validator, coverage, the daily workflow and the session report, plus the mistakes earlier sessions made.
---

# ERW: add a connector

How to add a source to the Energy Research Warehouse (ERW) so that it arrives
the way everything else did: real data only, complete or not at all, traceable
per row, validated, and listed in coverage. Modeled on the IRW's skills
(github.com/ben-domingue/irw, `.claude/skills/`): this file orchestrates and
points at the files that own each rule; it does not restate them.

| Rule | Owner |
|---|---|
| Table shapes, columns, units, naming | `docs/datastandard.md` |
| Whether a table passes | `warehouse/validate/erw_validate.py` |
| How a price source is pulled and written | `warehouse/connectors/iso_prices.py` (module docstring) |
| What runs every day | `warehouse/run_daily.sh`, called by `.github/workflows/daily-prices.yml` |
| Non-negotiables | `CLAUDE.md` |

## When to use it, and when not

Use it for any new time-series price or load source that fits the `series`
shape: a new ISO, a new market at an existing ISO (load zones, ancillary
prices), or more nodes. For `entities` or `events` sources (plants, projects,
PPAs, filings) the shape exists in the standard but the validator has no checks
for it yet: build those checks first, as their own piece of work.

Stop and say so, rather than working around it, when:

- the source needs a key or login the ERW does not have (PJM Data Miner, for
  one). Do not scrape around an access control.
- the terms forbid redistribution. PRIORITIES.md puts licensed feeds in "not now".
- the only way to get 30 days is to invent, fill or interpolate anything.

## Steps

1. **Probe before writing code.** In the scratchpad, pull one day about 20 days
   back and yesterday, for every market, with gridstatus. Record: exact node
   names, the `Interval Start`/`Interval End` spacing, how far back history
   goes, whether yesterday is published yet, and the URL of each file fetched.
   One ISO at a time: CAISO OASIS resets connections under parallel load.

2. **Write `pull_<iso>(ctx)` in `iso_prices.py`**, following `pull_nyiso` or
   `pull_isone`:
   - a module-level node list (`<ISO>_HUBS` or `_ZONES`), native ids unchanged;
   - `ctx["data_url"]`: a regex matching the ISO's data files only, so helper
     requests (cookie pages, latest-interval lookups) are never cited as the
     source of a row;
   - `ctx["reports"]`: `source id -> (report name, report page)`;
   - one spec per market: `fetch(day)`, `nodes`, `source` (`iso:report`),
     `page`, `step`, `minutes` or `five_min` (or `irregular`), `forward=True` for
     day-ahead, `variable`, `freq`, `market`, `file`, `title`, `notes`;
   - register it in `ISOS` with its local operating-day time zone and `geo`.
   If one fetch can draw on two reports (MISO final or prelim), set a
   `_source` column per row.

3. **Raw files come for free, if you let them.** Every response that goes
   through `requests` or pandas' `read_csv(url)` is saved to
   `warehouse/raw/<iso>/<run_id>/` with a manifest. Anything fetched another
   way (a different HTTP client, a subprocess) is not captured: route it
   through `requests` instead.

4. **Completeness is strict and belongs to the ISO's own intervals.** A market
   is written only if every node has every interval of the window; otherwise
   nothing is written and the log says which intervals are missing. Never
   relax this to get a file out. 5-minute prices become time-weighted 15-minute
   means (`<variable>_15m_mean`). If the ISO's intervals are irregular, use
   `irregular=True` and check the result by hand against one raw file. When the
   ISO confirms data is absent (HTTP 404), raise `SourceGap`: it is not retried.

5. **Name the table** `source_market_product`, lowercase, 40 characters or
   fewer: `pjm_dam_hub_prices`, `ercot_rtm_zone_prices`. `erw_validate` checks it.

6. **Smoke test outside the repo:**
   `python warehouse/connectors/iso_prices.py <iso> --days 2 --out-dir <scratch>`.
   Then the real run: `--days 30`. Read the run log, not only the summary line.

7. **Validate:** `python warehouse/validate/erw_validate.py warehouse/output/*.csv`.
   If a real file exposes a gap in the standard, add a check that makes the
   validator stricter, record it under "Decisions in v0" in
   `docs/datastandard.md` with a one-line reason, and never weaken a check to
   make a file pass.

8. **Tests:** `python -m unittest discover -s tests -v`. Any new shared helper
   gets a test on a fixture of real rows copied from an output file.

9. **Coverage:** `python warehouse/metadata/build_coverage.py`. Never edit
   `docs/coverage.md` or `warehouse/metadata/coverage.csv` by hand.

10. **Daily refresh:** add the ISO to the default `ISOS` in
    `warehouse/run_daily.sh`, then run `bash warehouse/run_daily.sh` twice and
    confirm the second run adds no rows (the merge key is
    `entity, variable, ts_utc`).

11. **Report and commit.** Record every decision and error in the session's
    `SESSION_N_REPORT.md`, commit after each task, keep the run logs of failed
    runs, and do not push. Nothing goes to Redivis without a human.

## Mistakes already made: do not repeat them

- **Python 3.14 and gridstatus.** gridstatus 0.36.0 pins `lxml~=5.3`, which has
  no 3.14 wheel. Locally: `pip install --no-deps -r requirements-py314.txt`.
  CI uses 3.12 and `requirements.txt`. Windows Smart App Control blocked numpy
  2.5.3; 2.3.5 loads.
- **gridstatus bugs are real.** The current-year ERCOT NP6-785-ER workbook
  broke `parse_doc` (fixed in `TracedErcot`). gridstatus's ISO-NE 5-minute
  reader silently skips a 4-hour file that fails to load. Only the
  completeness check catches that.
- **A cross-check that cannot fail is worse than none.** Joining two frames
  whose index level names differ (`Location` versus `node`) fanned out 5x and
  logged a "max diff 53.86" that meant nothing. Assert the joined length.
- **Do not assume regular intervals.** NYISO's real-time file has extra
  intervals at irregular times (09:47:51) and late stamps (12:10:03). gridstatus
  labels them all as 5 minutes. Rebuild intervals from the stamps.
- **Recording every HTTP response twice.** `requests` re-enters
  `Session.send` on redirects. The capture records at the outermost call only;
  do not add a second hook.
- **Helper requests are not sources.** Without `data_url`, a cookie page or a
  "latest interval" lookup made each day look like two files, and rows cited
  the report page instead of the file.
- **Publication lags differ.** MISO's real-time prelim for yesterday may not
  exist yet; SPP's daily RTBM files lag several days and some interval files
  never appear; ISO-NE's prelim 5-minute files have gaps. These are reasons a
  market is not written, reported, not problems to work around.
- **Retrying a 404 wastes an hour.** SPP retried whole days of 288 interval
  files because one file was absent. Raise `SourceGap`.
- **Operating days are local.** MISO's market day is EST all year; CAISO's is
  Pacific. A run near midnight UTC shifts some windows by a day.
- **Headers.** Never read an output with `comment="#"`: it truncates URLs.
  Skip the leading `#` lines by count.
- **Em dashes** are banned in every file. Check new files before committing.
