# Operating hybrid power plants (Berkeley Lab)

Energy Research Warehouse (ERW), method note written in session 987 (chain 055) for a table first written on 23 October 2026.

Tables: `lbnl_hybrid_plants`

## Publisher and address

Lawrence Berkeley National Laboratory (Berkeley Lab), "Hybrid Power Plants: Status of Operating and Proposed Plants, 2026 Data Update" (`https://eta-publications.lbl.gov/publications/hybrid-power-plants-status-4`), its data file `https://eta-publications.lbl.gov/sites/default/files/2026-09/lbnl_hybrid_data_file_thru2025.xlsx`, sheet "01. Operating Plants". Connector: `warehouse/connectors/lbnl_hybrid_plants.py` (session 979). eta-publications.lbl.gov's robots file disallows `/search/`, not `/publications` or `/sites/`.

## Vintage and revision

Plants operating through 2025 (the file last modified 29 September 2026). A snapshot (ceiling one request). LBNL publishes a data update each year at a new address.

## Shape and variables

Entities, 1,068 rows: 632 hybrid plants (86,263 MW of generators and storage: 436 PV+storage, 60 others by LBNL's final type, 40 fossil+PV, 28 fossil+storage, 26 fossil+hydro, 24 wind+storage, 12 wind+PV, 6 wind+PV+storage) and 436 storage-only plants LBNL lists beside them (type Storage, final type and total capacity empty, their storage MW, MWh and duration given). `entity_id` `lbnl_hybrid:<EIA plant id>`, or `lbnl_hybrid:none-<name>` for the 10 plants LBNL marks "missing"; `entity_type` `plant`; `geo` US-<state>; `lat`, `lon`; `capacity_mw` the generators' and storage's total; `status` and `status_date` empty. `x_*` LBNL's columns: region, final type and type, duration (hours), storage to generation ratio (percent), generator 1 to 3 and storage capacity (MW), storage energy (MWh), the battery's and generator 1's online dates, coupling, storage technology, the number of battery uses and each use as LBNL marks it.

## Reading the sheet

- The headings must be as read; an id given twice stops the run; a date is written as a day; a blank stays blank. Nothing is filled.
- The sheet "03. Hybrids in Queues" is LBNL's Queued Up data, held as `lbnl_interconnection_queue`, and is not taken again.

## License

**Held internal.** This file's notice is the Department of Energy's contract notice only (the U.S. Government's license to publish or reproduce the dataset "for U.S. Government purposes"), without the CC BY 4.0 statement of LBNL's other data files on which Berkeley Lab's verdict (read 14) rests. The license record shows the flag stricter than the verdict; the question is Samuel's (session 979).

## Cross-checks (sessions 979 and 987)

- Of `lbnl_solar_projects`' 160 PV+storage projects, 136 are PV+storage plants here by EIA id; of the 479 plants with both PV and battery generators in `eia860m_operating_generators`, 411 are LBNL's PV+storage plants.
- Session 987, against the code: `FIELDS` gives the x columns; the counts computed from the rows.

## What it does not hold

- The hybrids in the interconnection queues (`lbnl_interconnection_queue`), the PPA sample (`lbnl_hybrid_ppa_prices` holds the solar file's PV+battery PPAs), and the file's summary sheets.
