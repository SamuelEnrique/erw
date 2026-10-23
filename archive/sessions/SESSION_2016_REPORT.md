# Session 2016 report: industry's energy (EIA's Manufacturing Energy Consumption Survey, 2022)

23 October 2026, from 18:27 UTC, on lab-desktop (the data machine), the third session of `queue/done/057-night-23-october-data-wholesale-solar-industry-buildings.md`. Model spend USD 0. Pulls: 7 requests of 15 (www.eia.gov's robots file, asked in a call of its own, unchanged since session 2014; the 2022 MECS data page; four tables through the connector's first trial, Tables 1.2, 3.2, 11.1 and 11.3; Table 3.2's PDF, for its footnotes). The write reused the saved tables (`--offline`).

## Read these first

- **One table written, validated, archived, in coverage (sectors power, gas, oil and coal, public), in the release package, both holds:** `eia_mecs_manufacturing`, 5,363 rows: the 2022 survey (released August 2025 to March 2026; the next is fielded in 2027) for 81 industries (NAICS three to six digits, and all manufacturing) in the nation and each census region (405 in all):
  - fuel consumption by source, TBtu (Table 3.2): total, net electricity, residual and distillate fuel oil, natural gas, HGL, coal, coke and breeze, hydrogen (national only) and other;
  - electricity's components of net demand, MWh (Table 11.1): purchases, transfers in, total onsite generation, sales and transfers offsite, net demand;
  - onsite generation's components, MWh (Table 11.3): cogeneration, renewables (excluding wood and other biomass), other. Table 11.3's total equals Table 11.1's in all 315 industries and regions where both are figures (the run stops otherwise), so it is kept once.
- **The codes:** a cell EIA writes as a code has no row; the header counts them: 1,307 "*" (an estimate less than 0.5), 356 "Q" (withheld, relative standard error above 50 percent), 30 "D" (withheld to avoid disclosure), 324 "NA" (hydrogen in the regions, where it is inside Other). Eleven figures EIA marks "h", "Revised data" (its footnote), carry `x_mark` h.
- **Manufacturing's 2022 totals:** 15,742 TBtu of fuel; 20,843 TBtu of first use (fuel and feedstock, Table 1.2); 807 TWh of electricity purchased, 151 TWh generated onsite (146 of it cogeneration), 30 TWh sold or transferred offsite, 933 TWh net demand; the West's net demand 108 TWh.

## The cross-check

MECS's national figures against the Monthly Energy Review's industrial sector for 2022 (`eia_sector_energy_consumption_monthly`, twelve months summed), `runs/c057/s2016/cross.py`:

| MECS (manufacturing) | MER (whole industrial sector) | Share |
|---|---|---|
| First use, all energy, 20,843 TBtu | Total primary energy (TNICBUS), 26,076 | 79.9% |
| Fuel consumption, 15,742 | the same, 26,076 | 60.4% |
| Natural gas as fuel, 7,087 | Natural gas (NNICBUS), 10,781 | 65.7% |
| Coal as fuel, 398 | Coal (CLICBUS), 987 | 40.3% |
| Electricity purchased, 2,754 TBtu at 3,412 Btu a kWh | Retail electricity (ESICBUS), 3,482 | 79.1% |

The MER's industrial sector holds agriculture, mining (with oil and gas extraction's lease and plant fuel) and construction as well as manufacturing, and counts feedstocks: manufacturing at 80 percent of the sector's energy and purchased electricity is EIA's usual proportion. MECS counts coal made into coke as a nonfuel input, so its coal as fuel is the smaller share.

## Errors

- **The first write was blocked by the validator:** the name `eia_mecs` has two parts, and a table's name must have at least three. Renamed `eia_mecs_manufacturing` (the connector stays `eia_mecs.py`). The blocked run had already added the source's row to the main checkout's `sources.csv` and left its table in `warehouse/output/`: the row was put back (`git checkout`) and the file removed before the second write.
- **That blocked write was run through a pipe** (`write_table.sh ... | grep -v`), which rule 7 forbids for a gate: its exit code was read through `PIPESTATUS`, and every later gate is run unpiped, its output in a file.
- **pandas read "n/a" as an empty cell,** as in session 2014: the reader now keeps text cells (`keep_default_na=False`), so text where a figure belongs stops the run, and EIA's "NA" is counted as a code. The trial was run again: the same 5,363 rows.
- **Table 11.3's "Renewable energy" heading sits four rows above the header's last row:** the header is read over four rows.

## Decisions made without you

- **Tables 3.2, 11.1 and 11.3 only;** Table 1.2 (first use) is read for the cross-check, not stored: it carries unlabelled marker columns ("m") its notes were not read for.
- **A code is no row,** counted in the header; nothing is set to zero or to half a unit.
- **Million kWh written as MWh** (times 1,000), the ERW's unit; TBtu kept as EIA's.
- **A negative net electricity kept as published** (All Other Petroleum and Coal Products, -1 TBtu: it sells more than it buys).

## For Samuel's ruling

- None new.

## Files

- New: `warehouse/connectors/eia_mecs.py`, `tests/test_session2016.py` (3 tests), this report.
- Changed: `build_coverage.py`, `release_v1.py`, `live_set.yaml`, `docs/coverage.md`, `coverage.csv`, `archive_manifest.csv`, `sources.csv`, `license_tables.csv`, `docs/licenses.md`, `docs/redivis/release-v1/`.
- On the data machine only: `runs/c057/s2016/`, `runs/license_reads/s2016/`, `runs/s2016*`, `warehouse/raw/eia_mecs/`, and `runs/c057/register.py` (a helper that writes a new table's sector rule and holds).
