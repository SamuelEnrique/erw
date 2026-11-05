# Session 492 report: EPA's Greenhouse Gas Reporting Program, power plants

21 October 2026, from 17:42 UTC, on lab-desktop (the data machine), the fourth session of `queue/done/022-evening-21-october-sources.md`. Model spend USD 0.

## Read these first

- **Robots and terms**: EPA's, as in session 486 (`www.epa.gov/robots.txt`; record 55). The GHGRP data-sets page links the newest data summary, `2023_data_summary_spreadsheets.zip` (28.4 MB, October 2024: one workbook a reporting year, 2010 to 2023), and EPA's own GHGRP-to-ORIS crosswalk.
- **CO2 only, as CO2.** The summary gives totals, methane and nitrous oxide in metric tons of CO2 equivalent (AR4 GWPs), which is not a unit of the standard: CO2e is not CO2. The non-biogenic and biogenic CO2 columns are CO2 itself, in metric tons, and those are taken (`tCO2`). The rest is left out and the header says so.
- **`warehouse/connectors/ghgrp_power.py`**:
  - one series table `epa_ghgrp_power_co2`: entity `ghgrp:<facility id>`; variables `co2_non_biogenic` and `co2_biogenic`; one row a facility and year, for the facilities reporting under subpart D (electricity generation) that year;
  - `x_oris` the ORIS codes from EPA's crosswalk, `;`-joined where a facility has several;
  - the sector rule (`power;carbon`) and `tests/test_session492.py` (4 tests).
- **Trial**: 17,035 rows, 1,443 facilities, 2010 to 2023; the validator passes.
- **Cross-check against eGRID2023** (session 486, its CO2 in short tons converted to metric), for the 1,033 plants with one ORIS code and more than 1,000 t:
  - median ratio 1.000, and 84.7% within 5%;
  - GHGRP's total is 1,397.2 Mt against eGRID's 1,346.7 Mt: a facility reports all its combustion, not only generation.

## To finish (session 489's part, when the lock is free)

`python warehouse/connectors/ghgrp_power.py` (the files are reused; one request, the page), the validator, `build_coverage.py --only '^epa_ghgrp_power_co2$'`, `archive.py write --tables '^epa_ghgrp_power_co2$'`.

## Pulls against their ceilings

| Host | Requests | What |
|---|---|---|
| www.epa.gov | 4 | the data-sets page twice, the zip, the crosswalk |

## For Samuel's ruling

- `tCO2e` in the unit vocabulary, for GHGRP's totals, methane and nitrous oxide (and AEO's emissions, session 490).

## Files

- New: `warehouse/connectors/ghgrp_power.py`, `tests/test_session492.py`, this report. Changed: `warehouse/metadata/build_coverage.py`.
