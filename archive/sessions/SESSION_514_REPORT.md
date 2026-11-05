# Session 514 report: FERC Form 714's respondents

21 October 2026, from 19:41 UTC, on lab-desktop (the data machine), the fifth session of `queue/done/026-night-21-october-sources.md`. Model spend USD 0.

## Read these first

- **`warehouse/connectors/ferc714_respondents.py`: FERC Form 714's 219 respondents** as the entities table `ferc714_respondents`, from PUDL's `core_ferc714__respondent_id` (stable release).
  - `entity_id` is `ferc714:<PUDL's respondent id>`, the entity of `ferc714_area_demand_<year>`, so the demand tables can now be read by name.
  - It keeps FERC's id of the CSV years (to 2020), its id of the XBRL years (2021 on), and the respondent's EIA utility code. All 219 respondents carry an EIA code.
- **0 requests**: the file session 484's connector saved in `warehouse/raw/ferc714_demand/` was reused.
- **A fault found by the test, fixed before the write**: PUDL's whole-number ids with a blank beside them came out as "200.0". The columns are now read as text first, so they come out as "200".
- **Cross-checks** (`runs/s514/crosscheck.py` on the data machine):
  - Every entity of `ferc714_area_demand_2006`, `_2015` and `_2025` (175, 101 and 89 respondents) is in the table.
  - **The link to EIA-930's balancing authorities**, through `eia861_utility_sales` (2025), which names a balancing authority for each utility and state:
    - 111 respondents' EIA codes are named there with a BA;
    - 109 of them link to one or more of the 71 balancing authorities of `eia930_daily_demand`, and 108 to exactly one (Alabama Power to SOCO, Allete to MISO).
    - **Not every link is the respondent's own area**: Arizona Electric Power Cooperative links to CISO, because EIA-861 names the BA a utility sells in.
    - So the link was left out of the table and stays a cross-check. A column built from another ERW table would mix two sources.
- **License internal**, as `ferc714_area_demand_*`, until you rule on FERC 714 (the note's item). The table is not in `/data`'s public list or in Redivis v1, so it needs no hold.
- Written under the data lock (19:43 UTC); the validator, coverage and archive exited 0. Sector rule (`power`). Tests: `tests/test_session514.py`, 3.

## Pulls against their ceilings

| Host | Requests | What |
|---|---|---|
| s3.us-west-2.amazonaws.com | 0 of 2 | PUDL's file reused |

## Decisions made without you

1. The balancing-authority link is a cross-check, not a column.

## Files

- New: `warehouse/connectors/ferc714_respondents.py`, `tests/test_session514.py`, this report. Changed: `warehouse/metadata/build_coverage.py`, `docs/coverage.md`, `docs/licenses.md`, `warehouse/metadata/{coverage,archive_manifest,sources,license_tables}.csv`.
