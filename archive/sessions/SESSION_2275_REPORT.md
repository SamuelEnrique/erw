# Session 2275 report: method notes for this chain's tables, and the Stanford draft

24 October 2026, from 04:33 UTC to 04:58 UTC, on lab-desktop (the data machine), chain 103, unattended. Model spend USD 0. Pulls: Redivis's API, 104 requests of 150 (7, 90 and 7), and 1 to Supabase.

## Read these first

- **Two method notes, each checked against its code and its table, read past the header lines:**
  - `docs/methods/statfi_finland_electricity_monthly.md`: 6,350 rows, 16 lines, 414 months, January 1992 to June 2026. Every row of the written table equals the trial's. In all 414 months:
    - the six sources sum to total generation within 2,000 MWh;
    - CHP's three kinds sum to CHP, and the four countries to net imports, within 1,000 MWh;
    - generation plus net imports equals consumption within 1,000 MWh.

    The figures are whole GWh, so these gaps are rounding.
  - `docs/methods/energy_charts_central_europe.md`: 1,419,805 rows, 43 series, the hourly rule for quarter-hour answers, each country's production types and the cross-checks.
- **Contradictions found and acted on:**
  1. Session 2272's report gave the table's load against Ember's demand as 0.821 for Austria and 0.914 for Czechia. Those are the 2023 figures only. Over 2023 to 2025 they are 0.781 to 0.821 and 0.914 to 0.921; the report and the note now say so.
  2. The table's `vintage` is blank in every row (the answers carry no date of their own). The note says so.
  3. The header's request list writes Austria's answers as "at 2023": the country code, not a time. The note says so; the code is unchanged.
  4. Czechia's answers are hourly for 2023 and 2024 and quarter-hourly from 2025, not quarter-hourly throughout. The note says so.
- **The branch merged with main** (chain 101 landed as `f6b4cede`, with queue files 104 and 105):
  - this chain's reads 404 to 420 renumbered 431 to 447, its three verdicts' reads with them (440, 442, 445), and the reports and notes shifted (`runs/c090/shift_reads.py`);
  - the add-only files joined; the license record, the release README (line 9 only) and the package and site records rebuilt;
  - no row doubled; `tests/test_session205.py` passes within its bound (406 later reads against 422), a comment added for this chain.
- **The Stanford draft (erw:b9wm), a plain upload under the data lock, nothing released.** It waited seven minutes for chain 102's session 2261, which held the lock for its own draft upload. Each table was proved by the draft's count:
  - new: `statfi_finland_electricity_monthly` (6,350);
  - replaced, as the release note asked, because session 2185's notes rewrote them after their upload: `bsee_offshore_incidents` (4,818), `nrc_rop_findings` (18,240), `statcan_electricity_generation_monthly` (58,361), `statcan_oil_gas_supply_monthly` (56,007) and `ntd_transit_energy_annual` (10,161);
  - refreshed: `erw_coverage` (472 rows), `erw_sources` (560) and `erw_headers` (4,475 lines).
- **Not uploaded:** `energy_charts_central_europe`. It is internal until chain 102's Energy-Charts verdict reaches main.
- **The reconciles:**
  - before: 354 tables, 308 match, 44 differ, 2 not yet uploaded;
  - after: 360 tables, 311 match, 47 differ (tables daily runs have grown since their upload), 2 not yet uploaded, none missing from the draft.
- **The release note extended** with this session's paragraph.

## Decisions made without you

- **The metadata refresh from this branch** (chain 101's landing merged in) drops chain 102's unlanded tables' rows from `erw_coverage` and `erw_sources` again, minutes after its session 2261 uploaded them. The same holds for any chain whose tables are not in the refreshing branch. The next refresh from a branch that holds them puts them back. Chain 102's agent is told.

## For Samuel's ruling

- **The draft is not ready for a release click** while chains 102 and 103 have not landed and refreshed the metadata tables from a branch that holds every table.

## Files

- New: `docs/methods/statfi_finland_electricity_monthly.md`, `docs/methods/energy_charts_central_europe.md`, this report.
- Changed: `docs/coverage.md` (two Method cells), `warehouse/metadata/redivis_uploads_stanford.csv`, `docs/reviews/redivis-v1-release-note-2026-10-23.md`, `tests/test_session205.py` (a comment), `archive/sessions/SESSION_2272_REPORT.md`, and the merge's files.
- On the data machine only: `runs/c103/s2275/`, `runs/c103/resolve1.py`, `runs/c103/readme_line.py`.
