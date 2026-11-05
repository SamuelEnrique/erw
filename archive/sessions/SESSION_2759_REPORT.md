# Session 2759 report: method notes for chain 139's four tables, and the Stanford draft of all four

25 October 2026, about 22:37 to 22:52 UTC, on lab-desktop (the data machine), chain 139, unattended. Run after session 2762, so that its table is described and uploaded with the chain's others. Precheck passed (`runs/c139/pre2759.out`). Model spend USD 0. Pulls: 90 Redivis requests of 150, and 1 to Supabase; none to a publisher.

## Read these first

- **Three errors of mine, found by the check and corrected before the commit:**
  - **WAPA's peak year:** report 2751 named FY 2012 (40,857,445 MWh) as the peak of WAPA's sales. The peak is FY 2011 (42,428,128).
  - **Parker-Davis's fixed sales:** report 2751 said they were near 1.42 TWh every year. That holds from FY 2011; FY 2008 was 1,343,545 MWh.
  - **Denmark's production:** report 2756 read it as net of the plants' own use, from a gap below Eurostat's gross production. The gap is below in 31 of 35 years (0.4 to 7.6 per cent), but above in 2011, 2012, 2013 and 2017 (1.0 to 6.6 per cent). The reading is withdrawn; the note says neither file defines it.

  Reports 2751 and 2756 are corrected in place, each correction marked.
- **Method notes** for the chain's four tables, each checked against its table by code (`runs/c139/s2759_check.py`). All 109 figures the notes name match: counts, retrieval times, and both sides of each cross-check. Each note has its Method cell (`runs/c139/cells.py`):
  - `docs/methods/wapa_energy_sales_annual.md` (WAPA's energy sold and power rate; the fiscal year stamped on 1 October);
  - `docs/methods/dst_dk_electricity_supply_annual.md` (Denmark's supply, production and imports from 1966);
  - `docs/methods/eurostat_electricity_consumption_annual.md` (consumption by sector; FC includes the energy sector);
  - `docs/methods/eurostat_renewable_shares_annual.md` (the directive's shares; above 100 kept).
- **With these, every held table outside the unlanded chains' eight has a note** (`runs/c139/undescribed.py`: 603 tables, 8 without).
- **The Stanford draft:** four public tables uploaded, each proved by the draft's count:
  - `wapa_energy_sales_annual` (307 rows);
  - `dst_dk_electricity_supply_annual` (360);
  - `eurostat_electricity_consumption_annual` (15,667);
  - `eurostat_renewable_shares_annual` (3,095).

  How it ran:
  - A plain upload under the data lock (cap 130), the main checkout pulled first, from this branch merged with main (main's queue file 140 only): `runs/c139/s2759.sh`, copied from chain 138's.
  - The metadata tables were proved whole: `erw_headers` 5,335 lines, `erw_coverage` 603 rows, `erw_sources` 693 rows.
  - Reconciles: before, 443 tables, 379 match, 60 differ, 4 not yet uploaded; after, 385 match, 58 differ (tables the daily runs have grown since their upload), none missing.
  - Requests: 8, 75 (74 to Redivis, 1 to Supabase) and 8. **Nothing released.**
- **The upload record** (`warehouse/metadata/redivis_uploads_stanford.csv`, four rows) and the release note's paragraph go in with this report.

## Decisions made without you

- **Session 2762 run before this one,** so that its table is in the notes and the upload.

## For Samuel's ruling

- **Releasing the draft,** as before: a person's click after the diff.

## Files

- New: four method notes; this report.
- Changed: `docs/coverage.md` (four Method cells), `docs/reviews/redivis-v1-release-note-2026-10-23.md`, `warehouse/metadata/redivis_uploads_stanford.csv`, reports 2751 and 2756 (the corrections).
- On the data machine only: `runs/c139/s2759.sh`, `runs/c139/s2759/`, `runs/c139/s2759_check.py`, `runs/c139/s2759_note.py`, `runs/c139/cells.py`.
