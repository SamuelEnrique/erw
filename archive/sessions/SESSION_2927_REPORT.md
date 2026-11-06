# Session 2927 report: the daily run's seven days

6 November 2026, about 06:00 to 06:12 UTC, on lab-desktop (the data machine), chain 153, unattended. Model spend USD 0. Pulls: none from GitHub's API. `erw_health` was read from Supabase with this machine's keys (`runs/c147/seven_days.py`, read only).

## Read these first

- **The seven days** (`runs/c153/seven_days.out`):

  | Day | Rows | Failed | Jobs failed for the whole day |
  |---|---|---|---|
  | 2026-10-30 | 700 | 10 | none |
  | 2026-10-31 | 675 | 2 | daily prices (merge tests) |
  | 2026-11-01 | 665 | 3 | daily prices (merge tests) |
  | 2026-11-02 | 683 | 3 | daily prices (merge tests) |
  | 2026-11-03 | 671 | 3 | daily prices (merge tests) |
  | 2026-11-04 | 658 | 3 | daily prices (merge tests) |
  | 2026-11-05 | 687 | 7 | none |
  | 2026-11-06 | 182 | 1 | none |

- **"Stale on main": none.** The daily run's commit is within 1 day, the Roundup's within 8 days, and the hourly network's last ok step within 3 hours.
- **Each failed step, opened:**
  - **30 October, the model steps** (news score, policy score, deals, datacenters, news brief, and their 3-run streaks): "You have reached your specified API usage limits". This was the account's spending limit (chain 147's note), and the key works today (session 2918).
  - **31 October to 5 November, merge tests:** "Warning: The 'generic' unit for NumPy timedelta is deprecated". Repaired by chain 147 (session 2884); there is no merge tests failure since the catch-up run of 5 November.
  - **1 to 5 November, `dm_test_findings`** (the data machine's own run): for session 2928.
  - **5 November 23:03, EIA-930 `eia930_ciso_demand`:** "demand_forecast_mw: 143 of 168 hours (25 missing ...; first missing 2026-11-01T07:00:00Z)". These are EIA's 25 unpublished forecast hours at the clock change, and the completeness rule refused the file, as it must. Not this repository's fault.
  - **5 November 23:18, PortWatch:** "PortWatch error {'code': 400, 'message': 'Invalid URL'}" for chokepoint6. The connector's query does not depend on the window, and it passed on every other day of the week. This is the service's answer, not this code.
  - **5 November 23:47, `ercot_as_prices`:** HTTP 503 at `/misapp`. This falls under chain 147's `/misapp` ruling question; nothing was changed. The rollup failed after it for want of its input.
  - **6 November 01:41, package tests:** `test_derived_tables_flag_license_and_inputs` failed on `ercot_wind_solar_hsl_monthly`'s citation. Session 2884 fixed it after that run (`1bd5d70c0`, its source registered as the ERW's derived table). The test passes here, and the citation reads "Energy Research Warehouse (ERW), derived. ERW derived table: ERCOT output below HSL by month".
- **The page files the runner rebuilds:** main's `site/data/mix/`, `site/data/curtailment_profile.json`, `site/data/board.json` and `site/public/board/` are identical to the build before the runner's thinning (`e2794ff06^`). Session 2885 put those 164 files back. Nothing is thinner on main now.
- **The runner's builder fixed so it does not commit a thinner file again** (chain 151's item 8, before the run of 3 December): `warehouse/run_monthly.sh` now runs tests 94, 98, 133 and 144_page right after its builders. If they fail, `site/data/mix/` and `site/data/curtailment_profile.json` are put back as committed, a `monthly_page_tests` failure is recorded, and the run goes on. This is session 2913's board guard, for the monthly files.
  - **Proved on the runner's own thinned files of 6 November** (8 files from `e2794ff06`, put in place for the run, then restored): the four tests give 3 failures and 1 error, so the guard would have put them back.
  - Commit `4027dc594`. Test `tests/test_session2927.py` (4), with 2913's and 114's: 35 passed.

## Decisions made without you

- **The guard put in `run_monthly.sh`,** not in `run_daily.sh`, so a run by hand on the data machine is held too.
- **No change for PortWatch or the CISO forecast:** each failure was the publisher's.

## For Samuel's ruling

- None new (`/misapp` stays chain 147's question).
