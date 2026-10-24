# The UK's renewable electricity capacity and generation by technology, a quarter, from 2010 (DESNZ Energy Trends table 6.1)

Energy Research Warehouse (ERW), method note written in session 2214 (chain 098) for a table first written on 24 October 2026 (session 2174 of chain 094, `archive/sessions/SESSION_2174_REPORT.md`).

Tables: `desnz_uk_renewables_quarterly`

## Publisher and address

UK Department for Energy Security and Net Zero (DESNZ), Energy Trends section 6: renewables, table ET 6.1, sheet "Quarter". The page `https://www.gov.uk/government/statistics/energy-trends-section-6-renewables` links the workbook, here `https://assets.publishing.service.gov.uk/media/6aba724dfceb6fb3a65012d2/ET_6.1_SEP_26.xlsx` (September 2026 issue, 477,750 bytes). Source id `desnz:energy_trends_6_1`. Files saved under `warehouse/raw/desnz_renewables/`.

Connector: `warehouse/connectors/desnz_renewables.py` (session 2174): `[--offline] [--out-dir DIR]`, two requests (the page, fresh unless offline, and the workbook). Two of the sheet's four blocks are taken: CUMULATIVE INSTALLED CAPACITY (MW) as `capacity`, and ELECTRICITY GENERATED (GWh) as `generated` (times 1,000, MWh); load factors and shares are not. **No schedule runs it**: no step of `warehouse/run_daily.sh`, `warehouse/run_data_machine.sh`, `warehouse/run_data_machine_tables.sh`, `warehouse/run_monthly.sh`, `warehouse/refresh_supply.sh`, `warehouse/scheduled.py` or `.github/workflows/` names it.

## Vintage and revision

One run, `20261024T005702Z`, from the workbook retrieved at 2026-10-24T00:55:17Z; `vintage` 2026-09-28T13:57:33Z in every row. A later issue revises earlier quarters; a run merges by (entity, variable, ts_utc). No column of this issue is marked provisional (`x_provisional` no on all 1,982 rows), though table 5.1 of the same month marks the second quarter of 2026 provisional.

## Shape and variables

Series, 1,982 rows (capacity 1,024, generated 958), 20 technology entities, `entity` `desnz_et61:<technology>`, `freq` P3M, `geo` GB (the United Kingdom), `node` and `x_technology` DESNZ's words. The two blocks name their rows differently:

- capacity (16 entities): anaerobic_digestion, animal_biomass_non_ad, co_firing, energy_from_waste, landfill_gas, large_scale_hydro, liquid_biofuels, offshore_wind_floating, offshore_wind_seabed, onshore_wind, plant_biomass, sewage_sludge_digestion, shoreline_wave_tidal, small_scale_hydro, solar_photovoltaics, total;
- generated (15): the same where they match, but hydro (one row), offshore_wind (one row), co_firing_with_fossil_fuels, and non_biodegradable_wastes.

Every series holds all 66 quarters, 2010 Q1 to 2026 Q2, except liquid_biofuels (34 quarters in each block). Total capacity: 8,609 MW (2010 Q1) to 66,286.26 MW (2026 Q2), falling in one quarter. Total generated a year: 26.2 TWh (2010), 53.2 (2013), 83.0 (2016), 119.7 (2019), 135.2 (2022), 153.0 (2025): against table 5.1's total generated (`desnz_uk_electricity_quarterly`), 6.9 percent in 2010, 24.6 in 2015, 43.1 in 2020, 52.1 in 2025.

## Placing values in time, and what is filled

`ts_utc` is the quarter's first day at 00:00:00Z (the column header "<year> <n>th quarter"); capacity is at the quarter's end (DESNZ's note 1). "[x]" has no row; nothing is filled. Generated is DESNZ's actual figure where it has one, otherwise its estimate from a typical load factor (its note 8).

## License

Header: "License: public. Contains public sector information licensed under the Open Government Licence v3.0." `docs/licenses.md`: "may be public", flag public, ERW verdict public.

## Checks (session 2214)

The figures in this note were computed from the rows of `warehouse/output/desnz_uk_renewables_quarterly.csv`, read past its 10 header lines (scripts in `runs/c098/s2214/`).

- 1,982 rows, `ts_utc` from 2010-01-01T00:00:00Z to 2026-04-01T00:00:00Z, as the header states; no (entity, variable, ts_utc) twice.
- Session 2174's cross-check (`runs/c094/s2174/cross.py`), run again: its output is identical to the saved `cross.out`. The technologies (co_firing and non_biodegradable_wastes left out with TOTAL) sum to TOTAL exactly for capacity and within 0.0003 percent for generation in all 66 quarters; 6.1's onshore plus offshore wind is 1.0000 to 1.0001 of 5.1's total wind generated in 66 quarters; year-end capacity against IRENA (`irena_capacity_annual`): 2020 wind 24,458 / 24,458 and solar 13,772 / 13,772; 2022 wind 28,688 / 28,688 and solar 14,813 / 14,813; 2024 wind 32,339 / 32,082 and solar 19,430 / 18,953; 2025 wind 33,080 / 33,088 and solar 21,915 / 21,736.
- Leaving out TOTAL alone, as the header instructs, the sum exceeds TOTAL by up to 3.695 percent for capacity and by 2.201 to 4.792 percent for generation.

## Where the description and the data disagree

1. **What a sum must leave out.** The header and docstring say "a sum over the technologies must leave TOTAL out". It must also leave out co_firing (capacity) and non_biodegradable_wastes (generation), which DESNZ prints beside TOTAL; with TOTAL alone left out the sum runs up to 3.695 percent (capacity) and 4.792 percent (generation) above it. The cross-check leaves all three out.
2. **Two vocabularies.** The docstring describes one technology entity per row; capacity and generation name five technologies differently (offshore wind seabed and floating against offshore wind, large and small scale hydro against hydro, co_firing against co_firing_with_fossil_fuels), so the header's "20 technology rows" is the union of 16 and 15, and a join of capacity to generation by entity misses them.

Acted on in session 2214: the connector's docstring and header now say that a sum leaves out all three rows, and that the two blocks name five technologies differently, with each block's count; the table was written again offline from the saved workbook (no request, the same 1,982 rows, the archive unchanged), so its header says so.

## The session report against the table

Every figure of `SESSION_2174_REPORT.md` checked against the table, the saved workbook and the rerun cross-check holds (1,982 rows, 20 technology rows, 2010 Q1 to 2026 Q2, 66,286 MW at the end of June 2026, the sums in all 66 quarters, the wind comparison within 0.01 percent, wind and solar equal to IRENA's in 2020 and 2022, the 478 KB workbook, 3 requests), except:

- "for 2024 and 2025 within 2.5% (... solar 19,430 against 18,953 MW in 2024)": the 2024 solar gap is 2.517 percent of IRENA's figure (2.455 percent of DESNZ's), so "within 2.5%" holds only against DESNZ's figure. The report's reason (DESNZ having revised the years) is not testable from the table. Session 2214's report records the correction.

## What it does not hold

- Load factors, shares, renewables' fuel use, and DESNZ's annual tables.
