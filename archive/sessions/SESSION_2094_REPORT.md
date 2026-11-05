# Session 2094 report: method notes for this chain's tables, and the Stanford draft

23 October 2026, from 21:43 UTC, on lab-desktop (the data machine), the eleventh session of `queue/done/068-day-26-october-data-mexico-renewables-loans-credits-pipelines.md`, unattended. Model spend USD 0. Pulls: Redivis's API, 79 requests of 150 (7, 65 and 7), and 1 to Supabase for the lock. The session was paused from 21:53 to 22:22 UTC (the agent's usage limit) between the upload and the last reconcile.

## Read these first

- **Four method notes, one for each of this chain's tables,** each count recomputed by this session from the tables read past their header lines:
  - `docs/methods/irena_capacity_annual.md` (20,662 rows, 224 countries and areas, 1,962 series, 2015 to 2025; IRENA's totals equal their parts: the non-renewable total with pumped hydro, the renewable total with mixed and pure hydropower)
  - `docs/methods/irs_soi_energy_credits_annual.md` (1,074 rows, 54 places, 2015 to 2023; Puerto Rico from 2018)
  - `docs/methods/eia_state_to_state_capacity.md` (19,311 rows, 686 crossings, 33 years from 1990, 1991 to 1993 absent; `value` is `x_capacity_mmcfd` over 1,000 on every row)
  - `docs/methods/noaa_cpc_oni_monthly.md` (1,840 rows, 920 months a variable, January 1950 to August 2026, none missing; the index from -2.04, NDJ 1973, to +2.59, NDJ 2015)
  Their Method cells are filled; the rows' other cells are kept as the branch had them.
- **Contradictions found, each corrected:**
  - `eia_state_to_state.py` said geo is empty for Canada and Mexico; it is also empty on the 289 rows whose state to is the Gulf of America. The docstring and the header now say so.
  - `irs_soi_energy.py` named the places without Puerto Rico, which the table holds from 2018 (14 rows) and SOI's national row includes. Corrected.
  - Session 2087's report said the returns sum to the national row within 50; it is within 70 (2021). Corrected.
  - Session 2085's report gave gas and coal ratios for four years as for 2018 to 2024; over every year they are 1.003 to 1.006 and 1.008 to 1.012. Corrected.
- **The Stanford draft (`datapages.erw:b9wm`):** a first reconcile (7 requests): 257 of 303 tables match, none missing; chain 067's tables are in the draft by its own upload. Then one plain upload under the data lock, with the branch's coverage, sources, license record, licenses document and validator (the unit `degC`) copied into the main checkout for the one run and main's put back: the three public tables (`irs_soi_energy_credits_annual` 1,074 rows, `eia_state_to_state_capacity` 19,311, `noaa_cpc_oni_monthly` 1,840) sent with the true replace and proved by the draft's count, and `erw_coverage` (413 rows), `erw_sources` (499) and `erw_headers` (3,930 lines) refreshed (65 Redivis requests, cap 136). `irena_capacity_annual` is internal and the target does not take it. The last reconcile (7): 257 of 303 match, 46 differ, every one a table a daily run has grown; none missing. Nothing released.
- **The release note extended** (session 2094's paragraph).

## Decisions made without you

- **The notes drafted by a helper agent in the chain's worktree and checked by this session**, as sessions 2004, 2032, 2038 and 2088 did; the helper was told not to cite this chain's read numbers, which the merges were renumbering.
- **The branch merged with chain 066's landing before the upload,** so `erw_coverage` holds chain 066's tables with this chain's.

## For Samuel's ruling

- None new. The Redivis click covers every public table of chains 048 to 059 and 066 to 068 in the draft.

## Files

- New: the four notes above, this report.
- Changed: `warehouse/connectors/eia_state_to_state.py`, `irs_soi_energy.py` (descriptions); `archive/sessions/SESSION_2085_REPORT.md`, `SESSION_2087_REPORT.md`; `docs/coverage.md` (the Method cells); `warehouse/metadata/redivis_uploads_stanford.csv`; `docs/reviews/redivis-v1-release-note-2026-10-23.md`.
- On the data machine only: `runs/c068/s2094/`.
