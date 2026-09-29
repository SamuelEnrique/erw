# Session 9 report

Energy Research Warehouse (ERW), session 9, run 2026-09-26 (UTC). Every task in SESSION_9_PROMPT.md was carried out, under the human ruling that the warehouse data leaves git. Nothing was pushed. No key was used this session.

## What was built

| Task | Result | Commit |
|---|---|---|
| 1 | Output tables out of git. `.gitignore` ignores `warehouse/output/*.csv` except an allowlist; the other 77 CSVs are untracked with `git rm --cached` and remain on disk. `warehouse/output/README.md` says where the data lives and how to regenerate it. The workflow commits only metadata, docs and digests | `b5006bf` |
| 2 | `docs/methods/ercot_peak_premium.md` defines the thesis metrics. `warehouse/derived/ercot_peak_premium.py` writes `ercot_peak_premium_annual` (2,016 rows) and `ercot_peak_premium_monthly` (23,688 rows) for all six ERCOT hubs, 2015 to 2026. There is a derived license rule (Decision 23) and a new unit, `ratio`. The script is in `run_daily.sh`. All eight thesis values are reproduced exactly | `5c4f209` |
| 3 | All 81 tables pass the validator. Coverage has a `derived` column, and derived licenses are checked against their inputs. The package reads the derived tables. 357 package tests (up from 346) and 11 repo tests pass | `7ed78a7` |
| 4 | This report | final commit |

## Task 1: tables leave git

- **Allowlist:**
  - `news_index.csv`, named by the prompt;
  - `news_stories.csv`: 674 KB, and the only output file a tracked doc links to (the digests, `docs/digest/*.md`, cite it on line 89).
  No other output CSV is linked from a doc. `docs/datastandard.md` uses `ercot_dam_hub_prices.csv` as a naming example, but that is not a link, and the file is 1.04 MB.
- **Untracked:** 77 CSVs were removed from the index (`git rm --cached`). Before and after: 79 CSVs on disk. After the commit, `git status` is clean, and `git status --ignored` lists the 77 as ignored. They are still recoverable from git history, for example with `git show bfed5a2:warehouse/output/<table>.csv`.
- **Run logs:** also ignored from now on (`warehouse/output/logs/`), because they describe the tables and belong with them. The logs committed before session 9 stay tracked.
- **Workflow:** `.github/workflows/daily-prices.yml` now stages only `docs/coverage.md`, `docs/digest`, `warehouse/metadata/coverage.csv`, `run_status.csv` and `sources.csv`. Its commit message and header comment say so.
- **README:** `warehouse/output/README.md` covers:
  - where the data lives now: this working tree, until the Postgres store exists;
  - what stays in git;
  - how to recover earlier tables from git history;
  - every rerun command from the session reports, grouped by connector.

Consequences to know before the Postgres store exists:
1. **The scheduled workflow starts from a fresh checkout without the tables.** Each day it rebuilds only what the connectors fetch: 3 days of ISO prices, full-history EIA, FRED, carbon and PortWatch series, and the entities snapshots. It validates them and commits metadata. The coverage it commits then describes the runner's tables, not this machine's: for example, 3-day ISO windows, and no ERCOT history.
2. **`ercot_peak_premium.py` fails loudly on the runner**, because the yearly ERCOT history tables are not in git. After three scheduled runs, the streak rule will open an issue for it. That failure is real, and it will clear once the tables live in Postgres.
3. **News:** `news_stories.csv` is still tracked but no longer committed by the workflow. The runner therefore starts each day from the committed copy, and re-ingests and may re-score up to two days of stories (on the order of USD 0.5 a day at the session 6 rates).

## Task 2: the ERCOT peak premium

**Method** (`docs/methods/ercot_peak_premium.md`):
- **Blocks** by the local (America/Chicago) hour `h` of each interval's start:
  - overnight: 21:00 to 12:00 the next day, `h >= 21 or h < 12`;
  - midday: `12 <= h < 16`;
  - peak: `16 <= h < 21`.
- **Periods:** the ERCOT operating year, and the calendar month in local time.
- **Percentiles:** numpy default, linear interpolation.
- **No cap, floor or exclusion.**
- **DST:** interval starts are stored in UTC and converted to local time. The spring-forward day's overnight block has 56 intervals and the fall-back day's has 64; midday and peak are never affected. A full year has 21,900 overnight, 5,840 midday and 7,300 peak intervals, and this was checked on 2015 and 2025.
- **Completeness:** a past year or month must hold every quarter hour, or nothing is written. The current year and month are partial, and `n_intervals` shows it.

**Tables:**
- The annual table has one variable per metric (28 in all) per hub, `ts_utc` `YYYY-01-01T00:00:00Z`, freq `P1Y`.
- The monthly table has the same metrics per local calendar month, freq `P1M`.
- `entity` is `ercot:<hub>` and `source` is `erw:ercot_peak_premium`, with `source_url` linking the method doc. The header's `Derived from:` line names all 13 input tables (`ercot_rtm_hub_prices_2015` to `_2026` and `ercot_rtm_hub_prices`).
- License: public, the most restrictive license of the inputs (ERCOT NP6-785-ER and NP6-905-CD, both public).
- `run_daily.sh` runs the script right after the ISO price connectors.

**Thesis reproduction: every value matches, and nothing was adjusted.**

| HB_HUBAVG | Thesis 2015 | ERW 2015 | Thesis 2025 | ERW 2025 | Match |
|---|---|---|---|---|---|
| median (all intervals) | 20.49 | 20.49 | 25.68 | 25.68 | yes, yes |
| 99.9th percentile | 583.96 | 583.96 | 311.80 | 311.80 | yes, yes |
| peak-block IQR | 7.64 | 7.64 | 34.12 | 34.12 | yes, yes |
| midday minimum | -3.98 | -3.98 | -18.25 | -18.25 | yes, yes |

## HB_HUBAVG, 2015 versus 2025: all metrics

Real-time 15-minute settlement point prices, ERCOT operating year, 35,040 intervals each. USD/MWh unless noted.

| Metric | 2015 | 2025 |
|---|---|---|
| **All intervals:** min | -11.58 | -31.88 |
| Q1 | 17.99 | 19.37 |
| median | 20.49 | 25.68 |
| Q3 | 24.52 | 36.44 |
| max | 1,538.66 | 3,553.10 |
| 99.9th percentile | 583.96 | 311.80 |
| IQR | 6.53 | 17.07 |
| worst-interval multiple (p99.9 / median, ratio) | 28.50 | 12.14 |
| **Overnight (21:00 to 12:00):** min | -11.58 | -31.88 |
| Q1 | 17.32 | 19.21 |
| median | 19.10 | 24.79 |
| Q3 | 21.72 | 32.74 |
| max | 849.44 | 3,553.10 |
| **Midday (12:00 to 16:00):** min | -3.98 | -18.25 |
| Q1 | 20.38 | 15.18 |
| median | 24.28 | 22.52 |
| Q3 | 29.71 | 29.52 |
| max | 1,207.89 | 330.35 |
| **Peak (16:00 to 21:00):** min | 7.57 | -16.13 |
| Q1 | 20.85 | 24.91 |
| median | 24.12 | 37.03 |
| Q3 | 28.49 | 59.03 |
| max | 1,538.66 | 2,350.31 |
| peak-block IQR | 7.64 | 34.12 |
| peak minus midday median | -0.16 | 14.52 |
| intervals at or above 1,000 (count) | 5 | 9 |
| intervals at or below 0 (count) | 297 | 959 |

Read plainly: from 2015 to 2025 the typical price rose modestly, and the extreme tail (the 99.9th percentile) fell. Meanwhile the peak block widened sharply:
- its IQR rose from 7.64 to 34.12, 4.5 times;
- its median moved from 16 cents below the midday median to 14.52 above it;
- midday prices fell;
- zero-or-negative intervals tripled, from 297 to 959.

The annual table holds the same metrics for all six hubs and every year from 2015 to 2026. The 2026 row is partial, to 2026-09-25.

## Task 3: validation, coverage, package, tests

- `erw_validate` passes all 81 tables: 70 series, 9 entities, 2 events.
- **Coverage:**
  - `coverage.csv` and `docs/coverage.md` have a `derived` column: `yes` for the two peak-premium tables, `no` for the rest;
  - `build_coverage.py` reads each derived table's `Derived from:` line, recomputes the license from the input tables, and fails if the header disagrees;
  - the sector for both tables is `power`.
- **Package:**
  - `erw.fetch` reads the derived tables as ordinary series;
  - `erw.filter(market="ercot_rtm")` returns the live, yearly and derived ERCOT real-time tables;
  - `erw.cite` names the ERW (derived) as publisher, from the registry.
- **New tests:**
  - the derived flag, the inputs and the license rule;
  - the eight thesis values, to the cent;
  - complete-year counts (35,040, or 35,136 in a leap year);
  - the metric identities: multiple = p99.9 / median, peak IQR = Q3 - Q1, and monthly interval counts summing to the year.

## Decisions

1. **Allowlist:** `news_index.csv` plus `news_stories.csv`, because the digests link it and it is under 1 MB. It is internal (outlets' text), but it was already in git, and the prompt's rule is literal.
2. **Run logs join the ignored outputs.** The workflow's "never outputs" rule covers them, and they describe tables that are no longer in git.
3. **Blocks use the local hour of the interval's start.** Overnight is written as "h >= 21 or h < 12" so that the block spanning midnight is explicit.
4. **The annual `ts_utc` is `YYYY-01-01T00:00:00Z`**, a label, because the series standard puts P1Y rows at 00:00Z. The period itself is the local ERCOT year, which starts at 06:00Z; the header and the method doc say so.
5. **Derived tables are ordinary series tables** with `source` `erw:<method>`, a `Derived from:` header line and a coverage flag (Decision 23). New unit: `ratio`.
6. **The derived tables carry market `ercot_rtm`**, since they are ERCOT real-time metrics. So a market filter returns them with the price tables.

## Errors hit

None that changed data. One test expectation (`filter(market="ercot_rtm")`) had to include the derived tables. A cite-test helper was corrected before its first run.

## Rerun

```bash
.venv/Scripts/python warehouse/derived/ercot_peak_premium.py      # needs the ERCOT history tables on disk
PYTHON=.venv/Scripts/python bash warehouse/run_daily.sh
.venv/Scripts/python -m pytest package/tests -q
```
Every other rerun command is in `warehouse/output/README.md`.

## Open questions for the human

1. **Until Postgres exists, the only full copy of the tables is this working tree.** Should it be backed up somewhere (for example, a release asset or cloud storage) before the next session?
2. **CI now runs without the history**, so `ercot_peak_premium` will fail there daily and open a streak issue after three runs. Should the workflow skip derived scripts until the Postgres store is live?
3. **News continuity in CI:** should the workflow keep committing `news_stories.csv`, the one allowlisted table it changes, so it doesn't re-score stories? Or should that wait for Postgres?
4. **Carried over:** the ERCOT peak premium for day-ahead prices (not asked for); a PJM key; a Tiingo key; the eval sample.
