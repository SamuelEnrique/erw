# Session 892 report: the Stanford draft: the empty table mended, a second cap fault mended, chain 048's tables left for 906

23 October 2026, 05:22 to 05:27 UTC, on lab-desktop (the data machine), a session of `queue/done/048-night-23-october-data-utility-files-products.md`, run while the method notes of session 891 were being written. Model spend USD 0. Pulls: Redivis's API, 63 requests of 100 (and 1 to Supabase for the lock check in each upload).

## Read these first

- **`ercot_wind_solar_hsl_hourly` is whole again in the Stanford draft:** uploaded with the true replace and proved (8,760 rows). Session 880 had left it empty.
- **My fault, mended within the session: a request cap fell inside `erw_headers`' true replace.**
  - The first run (cap 12) stopped inside the table's own upload; its retry (cap 30) uploaded and proved the table, then stopped inside the header merge after its DELETE and POST. The draft's `erw_headers` was empty for about four minutes.
  - A merge would then have read the empty table and kept only one table's lines. So `erw_headers` was rebuilt in full from this machine's tables instead (`runs/c048/s892/headers_full.py`, the uploader's own steps for that one table, 15 requests): 2,958 header lines of 212 public tables, proved by count. Every table in the draft is on this machine (session 880's reconcile against this machine's output), so no line was lost.
  - The queue files' estimate of "about 5 requests a table" was wrong. A traced run took 31 requests for one small table and the header merge: setup 7, the table 6, listing polls 6, the merge 12. The memory and the release note now say so.
- **Reconcile:** 176 of 214 tables match. The 38 that differ are tables the daily run has grown since their upload (`weather_forecast_hourly`, `weather_obs_hourly` and the rest), and `erw_coverage` (316) and `erw_sources` (416) match.
- **Not uploaded:** chain 048's thirteen new or changed public tables (EIA-861's efficiency, operations, distribution systems and distributed generation; the petroleum exports; EIA-860's four schedules; EIA's international electricity; the CER's trade; the Board's G.17; USGS's solar facilities). After the mending, 37 requests were left, under the 50 or more two tables and the merge would take. Chain 049's session 906 uploads them ("any table chain 048 left out"). The four remote tests session 864 fixed were not run either.
- Nothing released.

## Decisions made without you

- The empty `erw_headers` rebuilt from disk rather than merged, for the reason above. The rebuild reads `docs/licenses.md` of the main checkout, so the header lines of this chain's new tables (not yet in the draft) are not in it; session 906's merge adds them with their tables.
- The session ran beside session 891's method notes (which three helper agents were writing), as the two touch different files.

## For Samuel's ruling

- None new. The release note's "click" list stands; the draft holds no empty table.

## Files

- Changed: `warehouse/metadata/redivis_uploads_stanford.csv` (the hourly table's row), `docs/reviews/redivis-v1-release-note-2026-10-23.md` (session 892's paragraph), this report.
- On the data machine only: `runs/c048/s892/` (the counted wrapper, `headers_full.py`, the request log and outputs, the reconcile file).
- Memory: the Redivis cap note corrected with the traced counts.
