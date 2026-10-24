# Austria's monthly electricity statistics (E-Control, el_dataset_mn)

Energy Research Warehouse (ERW), method note written in session 2394 (chain 113) for a table first written on 24 October 2026 (session 2391).

Tables: `econtrol_austria_electricity_monthly`

## Publisher and address

E-Control (Energie-Control Austria, the regulator), its electricity statistics download area (`https://www.e-control.at/statistik/e-statistik/data`), the file of monthly time series ("Zeitreihen mit monatlichen Daten"): `https://www.e-control.at/documents/1785851/8165594/el_dataset_mn.csv`. One GET, no key. Source id `econtrol:el_dataset_mn`. Connector: `warehouse/connectors/econtrol_austria_electricity.py` (session 2391). E-Control's robots file closes its services, login and `/home` paths only (read 682).

## Vintage and revision

January 2010 to August 2026, written by run `20261024T093144Z` (the write under the lock, offline), which read the file saved at 2026-10-24T09:27:50Z (`retrieved_at`). `vintage` is the file's last modified time, 2026-09-29T05:19:28Z, in every row. Every run that is not `--offline` asks for the file again and writes the table again (`write_snapshot`).

## Shape and variables

Series, 12,472 rows, 63 series, every one beginning in January 2010: 53 have all 200 months to August 2026, nine have 192 and `arbeitsvermogen` 144.

- `entity`: `econtrol:at:<TS_ID>` (E-Control's series code without its "#"); `x_ts_id` the same code.
- `variable`: the component (KOMP) in snake case, 18 of them. Among them:
  - `brutto_stromerzeugung` (gross generation, 26 series: in all, by the public grid, and by kind: hydro by run of river and storage and by size, combustibles by fuel, wind, solar, geothermal), with `brutto_stromerzeugung_stat_differenz`, E-Control's statistical difference;
  - `importe` and `exporte` (9 series each: in all, the public grid's, and with Czechia, Switzerland, Germany, Hungary, Italy, Liechtenstein and Slovenia);
  - `inlandstromverbrauch`, `brutto_stromverbrauch`, `endverbrauch`, `stromverbrauch`, `abgabe_an_endverbraucher`, `netzabgabe` (consumption in its several definitions);
  - `netzverluste` (grid losses), `eigenbedarf` and the power plants' own use, `verbrauch_fur_pumpspeicherung_psp` (pumping);
  - `energieinhalt_speicher` and `nennenergieinhalt` (the storage plants' energy content and its nominal value) and `arbeitsvermogen` (144 rows), each in MWh.
- `node`: the component, its breakdowns (Gliederung1 to 3) and its scope, as E-Control writes them, for example "Importe | DE | Ges".
- `x_breakdown` the breakdowns joined; `x_scope` N, `Ges` (all) or `Oef` (the public grid); `x_category` KAT.
- `unit` MWh for every series taken. `ts_utc` the month's first day; `freq` P1M; `geo` AT.

281 values are 0; none is negative. Gross generation in all ("Brutto-Stromerzeugung | Ges"), TWh a year: 2010 71.08, 2015 65.11, 2020 72.41, 2024 81.92, 2025 73.13, January to August 2026 48.01. Totals and parts are E-Control's: a sum takes one level.

## Reading the source

- The run stops at once, asking nothing, while `econtrol_electricity` or www.e-control.at is paused.
- One request a run (timeout 120 seconds); `--offline` reads the saved file.
- The file is wide: metadata rows (TS_ID, ZA, KOMP, Gliederung1 to 3, VO, REG, N, EHB, KAT, UNIT), then one row a month, semicolon-separated with decimal commas. It is read as UTF-8, else as Windows-1252, the encoding E-Control served in session 2391.
- A series in a unit other than MWh or MW is not taken and is counted in the header: the generation coefficient (unit "[1]") and two series in kW. A series the file gives twice (two columns with one TS_ID) is kept once when its columns are equal (2 such); unequal, the run stops.
- The run stops, and no file is written, for any of these:
  - a metadata row missing;
  - a row neither metadata nor a month;
  - a month out of range;
  - a value that is not a number;
  - a file with no value;
  - a series and month given twice.
- A blank cell has no row. Nothing is filled.

## License

Internal. The site carries "Copyright 2026 © E-Control" and the impressum grants no reuse (read 683, session 2391); `license_verdicts.csv` holds no verdict for E-Control yet. The table is held from the Redivis storage and the live set until a ruling or a reuse statement is read.

## Cross-checks (session 2391, against `eurostat_electricity_monthly`'s Austria, 2016 to 2025)

- Imports and exports in all: 1.000 (1.001 in 2016).
- Wind: 1.008 to 1.032.
- Gross generation: 1.024 to 1.070 times Eurostat's net production.
- Inland consumption: 0.943 to 0.988 of `owid_ember_electricity_annual`'s demand.
- Within the table, hydro, combustibles and wind, solar and geothermal sum to gross generation within 27.5 GWh a month.

## What it does not hold

- The download area's other four CSV files of time series (not read here); prices; the generation coefficient and the series in kW.
