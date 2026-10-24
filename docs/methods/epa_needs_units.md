# Generating units of EPA's power sector model, a unit, the 2025 reference case (EPA, National Electric Energy Data System, NEEDS for the 2025 Reference Case)

Energy Research Warehouse (ERW), method note written in session 2185 (chain 097) for a table first written on 24 October 2026 (session 2183).

Tables: `epa_needs_units`

## Publisher and address

U.S. Environmental Protection Agency (EPA), National Electric Energy Data System (NEEDS), the inventory of generating units its Integrated Planning Model (IPM) starts from. The NEEDS page (`https://www.epa.gov/power-sector-modeling/national-electric-energy-data-system-needs`, read 376) links NEEDS for the 2025 reference case (December 2025) and each earlier version. One workbook, four of its sheets:

`https://www.epa.gov/system/files/documents/2025-12/needs-for-2025-reference-case.xlsx`

The User-Agent is "Mozilla/5.0 (compatible; ERW-connector/0.1; +https://github.com/SamuelEnrique/erw)". Source id `epa:needs_2025_reference_case`. Connector: `warehouse/connectors/epa_needs.py` (session 2183), its only table. www.epa.gov's robots file (read 375) disallows its admin, search, user, core and theme paths, not /power-sector-modeling/ or /system/files/.

The table is not scheduled: no line of `warehouse/run_daily.sh`, the other `warehouse/*.sh` scripts, `warehouse/scheduled.py`, `scripts/` or `.github/workflows/` names the connector (searched in session 2185), and `run_status.csv` holds no row for it. It was written once, by run `20261024T020406Z` on the data machine, offline from the saved workbook.

## Vintage and revision

One vintage: NEEDS for the 2025 reference case. The workbook (5,912,677 bytes) was retrieved at 2026-10-24T01:59:08Z by the session's probe, and the write read that copy. Its Last-Modified time, 2025-12-15T18:55:14Z, is every row's `vintage`. `coverage.csv` gives the same 38,030 rows, as a snapshot.

Each run writes the whole table again (`ip.write_snapshot`), and the workbook is asked again unless `--offline`. Its address names its version: a later reference case is a new address, which a later session reads from the page and sets in the code.

## Shape and variables

Entities, 38,030 rows, one a unit, at 17,380 ORIS plant codes. `entity_id` `epa_needs:<EPA's UniqueID_Final>` (the ORIS plant code, the unit kind and the unit id, as `10003_B_BLR1`); `entity_type` `generator` (36,919: EPA's kinds G, 36,918, and I, 1) or `equipment` (1,111: EPA's B, a boiler, Decision 54); `name` the plant name and the unit id; `geo` US-<state> (52 values: 50 states, DC and PR); `capacity_mw` EPA's Capacity (MW) (blank in 7 rows, below; one is 0); `status` `active` for the units of the NEEDS_Active sheet, else blank; `lat`, `lon`, `status_date`, `operator` empty.

| `x_needs_sheet` | EPA's sheet | Units | Generators | Boilers | MW |
|---|---|---|---|---|---|
| active | NEEDS_Active | 22,688 | 21,660 | 1,028 | 1,155,380 |
| retired_by_2028 | NEEDS_Retiredby2028 | 1,094 | 1,011 | 83 | 65,351 |
| hardwired_capacity | NEEDS_HardwiredCapMW | 2,755 | 2,755 | 0 | 117,400 |
| dropped_capacity | NEEDS_DroppedCapMW | 11,493 | 11,493 | 0 | 582,669 |

Units with boilers (coal steam 366 boilers, oil and gas steam 373, municipal solid waste 139, biomass 117 and others) carry their capacity on the boilers (`equipment`): of the active sheet's 1,155,380 MW, 220,467 MW is on boilers and 934,913 MW on generators.

The `x_` columns, as EPA writes them: `x_unique_id`, `x_oris`, `x_unit_kind` (G, B or I), `x_unit_id`, `x_camd_unit_id` (blank in 33,977), `x_plant_type` (22 types: Combustion Turbine 11,451 units, Solar PV 9,006, Hydro 4,455 and so on), `x_ct_ic`, `x_ipm_region` (67 regions; blank in 10,581 dropped units), `x_county`, `x_fips5` (blank in the same 10,581), `x_heat_rate_btu_kwh` (Btu/kWh; EPA writes 0 for 14,852 units and leaves 11,300 blank), `x_online_year` (1891 to 2031), `x_retirement_year` (EPA's 9999, no retirement, written blank; 385 active units carry a year from 2029 to 2103, and two dropped units carry 0), `x_firing`, `x_bottom`, `x_cogen`, `x_fuels`, `x_scrubber`, `x_nox_comb_control`, `x_nox_post_comb_control`, `x_pm_control`, `x_mercury_controls`, `x_so2_permit_rate` and `x_nox_rate_mode1` (lb/MMBtu), `x_ccs`, `x_c2g`, `x_bart`, `x_owner` and `x_owner_percent`, `x_holding_company` and `x_holding_company_percent`, `x_regulatory_status`, and `x_drop_reason` for the dropped sheet.

- The one unit of kind I is `epa_needs:0_I_1`, "IMPORT1 1", plant type IMPORT, 1,000 MW on the active sheet in California (IPM region WEC_SDGE), typed `generator`.
- All 1,339 units in Alaska, Hawaii and Puerto Rico are on the dropped sheet.
- The seven units with no capacity are all dropped: Turning Point Solar TPS51 and TPS52, K Road Calico Solar 01 and 02, Summit Lake Wind Energy Project 1, Harvest Wind Energy Project 1 and Haymaker Hybrid HBESS.
- The hardwired sheet's units came on line from 1972 to 2028, most of them in 2023 to 2025 (453, 711 and 661); 1,679 of its 2,755 are Solar PV.
- Dropped units' reasons: retired or planned to retire by June 2028 5,783; onsite, a net buyer of electricity in 2021, 1,878; canceled or postponed 1,417; in Alaska, Hawaii or Puerto Rico 1,339; planned, not meeting NEEDS criteria 784; status OS or RE for three years 174; lack of model plants 118.

No `entity_id` is given twice. The counts were computed in session 2185 from the rows, read past the 10 header lines with pandas (every column as text); the header's counts by sheet and its MW agree.

## Checks the connector makes

- Before any request, the connector and www.epa.gov are checked against `warehouse/metadata/paused_sources.csv`; a paused publisher stops the run with no request. It is not paused.
- The workbook must hold the four sheets, and each the 36 columns the connector reads (and the dropped sheet EPA's reasons), or the run stops. Rows blank in every column are passed over.
- A unit id blank or given twice, in one sheet or across sheets, stops the run; so does a unit kind not in the map (G, I and C as generators, B as equipment), a state name not in the map of 50 states, DC and PR, a state code unlike the name's FIPS code where a code is given, or a capacity that does not read as a number.
- A unit with no capacity is kept with `capacity_mw` blank and counted in the header (7). Nothing is filled.
- Ceiling: one request a run, a pause of 1 second after it.

## The cross-check

Session 2183 set NEEDS beside EIA-860M's operating generators (`eia860m_operating_generators`, net summer MW) in the states where NEEDS has active generators (48 states and DC) in `runs/c097/s2183/cross.py` (on the data machine, not in git), reading the trial copy of the table:

- NEEDS's 21,660 active generators hold 934,913 MW against EIA-860M's 27,608 operating generators and 1,312,452 MW. 10,892 of NEEDS's 11,061 plant codes are in EIA-860M, and 21,345 of the 21,660 generators match on plant code and generator id.
- By state, the active generators alone run from 0.15 to 1.25 of EIA-860M, median 0.716 (Texas 0.67, California 0.87), because the capacity of units with boilers sits on the boilers in NEEDS.
- The active and hardwired sheets together, every unit kind: 1,272,779 MW against 1,312,452, a ratio of 0.97. By state the median is 0.974, from 0.81 to 1.29: Texas 0.97, California 1.00, Florida 0.98, Pennsylvania 0.96, Illinois 0.89, New York 1.05, Arizona 0.93, Georgia 1.01; outside 0.8 to 1.2 only Rhode Island (1.29) and Wyoming (1.21).
- Active capacity by plant type: combined cycle 287,659 MW, onshore wind 153,575, combustion turbine 146,928, solar PV 114,448, nuclear 96,578, hydro 79,357.

## License

The header: "License: public (EPA; see license_verdicts.csv). Cite the U.S. Environmental Protection Agency, NEEDS for the 2025 Reference Case." `license_verdicts.csv` gives EPA "may be public", the same if the ERW sells anything (read 55, session 311): "Unless otherwise specified, geospatial data produced by the EPA is by default in the public domain and is not subject to domestic copyright protection under 17 U.S.C." Its note: EPA's documents may be freely distributed and used for non-commercial, scientific and educational purposes. `coverage.csv`: public.

## Found while writing this note

- The docstring gives `entity_type` generator for "EPA's G and I". The one I unit is an import, "IMPORT1 1", 1,000 MW in California, not a generating unit; it is typed `generator`, counted in the active sheet's 1,155,380 MW and in California's NEEDS capacity in the cross-check.
- The docstring says the four sheets must hold "the columns read on 24 October 2026 (the first 50 alike, the dropped sheet with EPA's reasons)". The code checks only that the 36 columns it reads (and the reasons on the dropped sheet) are present; it does not compare the first 50.
- The docstring's map of unit kinds names G, I and B; the code also maps C (a committed unit) to `generator`. No C unit is in this workbook.
- Session 2183's report says the cross-check compares "the same 49 states and DC". The active generators are in 49 `geo` values, which are 48 states and DC.
- The active and hardwired sum in the cross-check sets units EPA hard-wires into the model, some on line only in 2026 to 2028 (276 units), beside EIA-860M's operating generators.

Acted on in session 2185: the docstring names the import unit and the unit kind C, and says the 36 columns read are what is checked; session 2183's report is corrected (48 states and DC, the import, the hardwired units' dates). The table is unchanged.

## What it does not hold

- EPA's other sheets of the workbook, and earlier or later versions of NEEDS.
- Latitude and longitude: `lat` and `lon` are empty.
- IPM's results: NEEDS is the model's starting fleet, not its projections.
- Generation, fuel use or emissions: capacities, characteristics and permit or mode 1 rates only.
