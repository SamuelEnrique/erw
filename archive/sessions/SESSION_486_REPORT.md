# Session 486 report: EPA eGRID plants

21 October 2026, from 17:00 UTC, on lab-desktop (the data machine), at the owner's instruction of 21 October. Model spend USD 0.

## Read these first

- **Robots and terms**: `www.epa.gov/robots.txt` allows the eGRID download page and `/system/files/`. EPA's terms are in the record (record 55, session 311: "data produced by the EPA is by default in the public domain"). License public.
- **The newest data year is eGRID2023**, revision 2 (`egrid2023_data_rev2.xlsx`, 21.2 MB, 16 June 2025), in short tons; the `_metric` workbook is the same data. The table is from the plant sheet, PLNT23.
- **`warehouse/connectors/egrid.py`**:
  - an entities table `egrid_power_plants`, one row a plant:
    - entity_id `egrid:<ORISPL>` (the DOE/EIA plant code, the number `eia860` uses);
    - entity_type `plant`; capacity_mw the nameplate;
    - status empty (eGRID gives none);
    - operator the utility;
  - 46 of eGRID's own fields under named columns with their units (heat input, net generation, NOx, SO2, CO2, CH4, N2O, CO2e, mercury, their rates, generation by fuel), with eGRID's codes listed in the header;
  - eGRID's figures are EPA's, measured or estimated by EPA as its documentation says; a blank stays blank;
  - the sector rule (`power;carbon`) and `tests/test_session486.py` (4 tests); landed as `ffc3b0c0`.
- **Trial**: 12,612 plants, 1,303,569 MW of nameplate; the validator passes.
- **Cross-checks**:
  - net generation 4,191.0 TWh (EIA's 2023 figure is about 4,178);
  - CO2 1,607.7 million short tons (about 1,458 million metric, EPA's own scale);
  - 97.5% of eGRID's plant codes are in `eia860m_operating_generators`.

## To finish (session 489)

`python warehouse/connectors/egrid.py` (the workbook is reused), the validator, `build_coverage.py --only '^egrid_power_plants$'`, `archive.py write --tables '^egrid_power_plants$'`, `licenses.py tables` and `write`, and land.

## Pulls against their ceilings

| Host | Requests | What |
|---|---|---|
| www.epa.gov | 4 | robots file, the page twice, the workbook once |

## Decisions made without you

1. An entities table (one row a plant), not series: the plant sheet is one year's snapshot of each plant.
2. 46 fields chosen of eGRID's 150: the unit-level counts, the `*_SRC` source flags and the CHP adjustments are left in eGRID.

## Files

- New: `warehouse/connectors/egrid.py`, `tests/test_session486.py`, this report. Changed: `warehouse/metadata/build_coverage.py`.
- On this machine (not in git): `warehouse/raw/egrid/`, `runs/s486/`.
