# Session 930 report: hydropower relicensing and license surrenders (ORNL)

23 October 2026, from 10:13 UTC, on lab-desktop (the data machine), a session of `queue/done/052-day-23-october-data-world-oil-reactors-stocks.md`, the second of its two sessions of a source of its own choosing. Model spend USD 0. Pulls: 3 requests of 20, 11 seconds apart (HydroSource's robots file, asked alone and read first; the dataset's page; its workbook).

## Read these first

- **Why this source:** chain 051 took the hydropower fleet (`ornl_eha_hydropower_plants`) and its pipeline; the licenses of that fleet are turning over, with capacity, operation and sometimes the dam itself at stake. ORNL's relicensing and surrender data is the national record of that turnover, from the same publisher under the same verdict (session 914).
- **One table written, validated, archived, in coverage (sector power, public), in the release package, both holds:** `ornl_hydropower_relicensing`, 559 records on 31 December 2025, an events table:
  - 407 relicensing cases: 198 relicenses issued, 160 pending, 40 notices of intent, 9 converted to exemptions; each with its process (219 traditional, 157 integrated, 22 alternative), dates, new mode, the new license's capacity, and whether it carries a settlement (57), construction or turbine-generator investment;
  - 152 surrenders and terminations: 82 surrenders issued, 31 pending, 9 notices, 15 license and 15 exemption terminations; 28 with the dam removed; each with its capacity and ORNL's reason.
  - 548 records name the plant in ORNL's fleet database (`entity_ids` `ornl_eha:<EHA_PtID>`).
- **The cross-checks, against `ornl_eha_hydropower_plants`:**
  - Of the 405 relicensing records that name a plant, 401 are in the fleet table, and 396 of those carry the same FERC docket there.
  - Of the 197 issued relicenses with an expiry, 193 give the same expiry as the fleet table's FERC expiry.
  - The new license's capacity equals the plant's capacity in the fleet table within 1 MW for 130 of 197 issued relicenses; the others are relicenses with changed capacity, the change the table records.
  - Of the 143 surrenders that name a plant, 46 are still in the fleet table, the others gone from the fleet as surrendered plants are.

## Decisions made without you

- **One events table for both sheets,** with `event_type` telling a relicense from a surrender and `x_record` the sheet.
- **The event's date is FERC's issuance where there is one, else the application's, else the notice of intent's,** with `x_date_kind` saying which.
- **The workbook taken by its public link,** as in sessions 911 and 916.
- **This source over another** for the session's free choice, as above.

## For Samuel's ruling

- None new (HydroSource's form stands with session 916's question).

## Files

- New: `warehouse/connectors/ornl_hydro_relicensing.py`, `tests/test_session930.py` (3 tests), this report.
- Changed: `build_coverage.py`, `release_v1.py`, `live_set.yaml`, `docs/coverage.md`, `coverage.csv`, `archive_manifest.csv`, `sources.csv`, `license_tables.csv`, `docs/licenses.md`, `docs/redivis/release-v1/`.
- On the data machine only: `runs/c052/s930/`, `runs/license_reads/s930/`, `runs/s930*`, `warehouse/raw/ornl_hydro_relicensing/`.
