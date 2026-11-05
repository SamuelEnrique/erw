# Session 2353 report: method notes for this chain's tables, and the Stanford draft

24 October 2026, from 06:53 UTC, on lab-desktop (the data machine), a session of `queue/done/105-day-8-november-data-mexico-india-peru-korea.md`, there numbered 2303 (renumbered: session 2350's report). Model spend USD 0. Pulls: Redivis's API, 113 requests of 150 (two reconciles of 7, an upload of 99), and Supabase once for the uploader.

## Read these first

- **Four method notes for this chain's five tables,** linked from the Method column. Two helpers drafted them from the connectors, the raw files and the tables, with no request. I read each and acted on every contradiction.
  - `docs/methods/cea_india_psp_annual.md`: all 777 rows equal the six PDFs.
  - `docs/methods/kpx_korea.md` (both KPX tables): all rows equal the saved EPSIS pages. January 2026's daily peaks average 80,230.35 MW, against the table's 80,230.
  - `docs/methods/statnett_norway_daily.md`: the placement is confirmed by a weekly-cycle test. Sunday is the low day in every stretch between autumn slots, and the lowest day in 205 of 352 weeks, against 4 when every day is shifted one earlier.
  - `docs/methods/svk_sweden_production_hourly.md`: every value, time and publication time equals the raw files.
- **Corrected, with the tables written again offline** (each under the data lock, its rows put in by key, `runs/c105/s2353/rewrite_all.sh`):
  - **CEA, `node`:** CEA's footnote marks (`#`, `*`, `(*)`, `(**)`) are now taken off, so "Tripura *" and "Tripura (*)" are one name and Andaman-Nicobar's double space is gone.
  - **CEA, `x_kind`:**
    - 2025-26's "Others" have their own kind, `other_entities`: CEA's note calls them "other miscellaneous entities drawing power directly from ISTS".
    - Andaman-Nicobar, also marked # and outside its region, is named beside Lakshadweep.
  - **CEA, the gaps line:** every gap of a region marked ## is now named, the North-Eastern Region's 8 and 9 MU included. The ## reports are those of 2022-23 to 2024-25, not "until 2024-25".
  - **CEA and KPX, the license lines:** they state session 2299's verdicts (needs written permission).
  - **Statnett:** the shortfall against Statistics Norway is seasonal, in consumption as in production. It is within 0.3 percent from November to March and about 3.4 percent at June's median, so missing wind cannot be the whole cause.
  - **Sweden:**
    - hydro in 2020 is 1.2 percent over Eurostat, and 2021 and 2022 agree within 0.05 percent ("exactly" withdrawn);
    - the solar wording is now "centred at 12:00 on the label clock";
    - both halves of Mimer's 18 March sentence are quoted (that day is on Mimer and on eSett);
    - the header says why `vintage` is empty: 68 percent of hours were published more than a week after the hour, some months later again, and only the newest publication is shown.
  - **Reports corrected, each correction saying so:** 2295, 2297 (KPX is within 0.004 percent of Ember from 2000 to 2020, not "equal to the MWh"; 2021 is 0.96 percent below, 2022 0.32 percent above), 2350 and 2351.
- **The Stanford draft** (`runs/c105/s2353/stanford.sh`, under the data lock, from the main checkout pulled, with the branch's records):
  - **No table of this chain went:** all five are internal, and the Stanford target takes only public ones.
  - **Eight public tables uploaded, each proved by the draft's count:**
    - C30, written again: 82,760 rows replacing 88,376;
    - the QSS table, `census_cbp_hosting_annual` and `usdm_drought_state_weekly`, never uploaded before;
    - chain 101's REE table and three EIA tables, written again after its upload.
  - **The metadata tables refreshed:** `erw_coverage` 491, `erw_sources` 579, `erw_headers` 4,565.
  - **Reconciles:** before, 324 of 374 match; after, 330 match and 44 differ (tables daily runs have grown); none missing.
  - **The release note is extended.** Nothing is released.

## Recorded, not acted on

- **The write runs' "Retrieved:" line names the writing run.** The line already gives the probe's download times beside it. Every connector of this chain writes it this way, as the shared writer does.
- **No `run_status.csv` row, and one status file for KPX's two tables.** This chain's runs wrote `runs/status/<connector>.json` only, as `ip.write_status` does for every connector. KPX's second run's status replaced the first's.
- **`docs/licenses.md`'s "If the ERW sells anything" column reads "may be public"** for publishers whose terms were never read (Statnett, Svenska kraftnät). That is `licenses.py`'s rule for every unread publisher, not this chain's.
- **RTE not replaced** (1,448,927 rows; the draft holds that count). It is left for a run of its own, under the cap.
- **The upload record lacks rows for many tables the draft holds** (chains 101, 103 and 104's). It lost them in a merge; the release note says so.

## Errors

- None.

## Decisions made without you

- **The five tables written again**, so their headers carry the corrections at once.
- **RTE left for the next draft session**, so a cap is not reached inside it.

## For Samuel's ruling

- None new.

## Files

- New:
  - `docs/methods/cea_india_psp_annual.md`, `kpx_korea.md`, `statnett_norway_daily.md` and `svk_sweden_production_hourly.md`;
  - this report.
- Changed:
  - `warehouse/connectors/cea_india_psp.py`, `kpx_korea.py`, `statnett_norway.py` and `svk_sweden.py`;
  - `tests/test_session2295.py`;
  - reports 2295, 2297, 2350 and 2351;
  - `docs/coverage.md`, `coverage.csv`, `archive_manifest.csv` and `sources.csv` (the rewrites and the Method cells);
  - `warehouse/metadata/redivis_uploads_stanford.csv`;
  - `docs/reviews/redivis-v1-release-note-2026-10-23.md`.
- On the data machine only: `runs/c105/s2353/`, `runs/s2353*`.
