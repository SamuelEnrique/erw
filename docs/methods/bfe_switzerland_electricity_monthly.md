# Switzerland's electricity balance, a month (SFOE, ENSTAT on opendata.swiss)

Energy Research Warehouse (ERW), method note written in session 2345 (chain 109) for a table first written on 24 October 2026 (session 2343).

Tables: `bfe_switzerland_electricity_monthly`

## Publisher and address

The Swiss Federal Office of Energy (SFOE, BFE), "ENSTAT: Elektrizitätsbilanz der Schweiz - Monatswerte-CSV", listed on opendata.swiss (`https://opendata.swiss/en/dataset/enstat-elektrizitatsbilanz-der-schweiz-monatswerte-csv`). The file is `https://www.bfe-ogd.ch/ogd35/ogd35_schweizerische_elektrizitaetsbilanz_monatswerte.csv`, one GET, no key. Source id `bfe:ogd35`. Connector: `warehouse/connectors/bfe_switzerland_electricity.py` (session 2343). opendata.swiss and www.bfe-ogd.ch have no robots file (reads 593 and 595).

## Vintage and revision

January 2000 to August 2026, written by run `20261024T075439Z`, which read the file saved at 2026-10-24T07:53:13Z (`retrieved_at`). `vintage` is the file's Last-Modified, 2026-10-07T07:18:58Z. The months of 2026 are provisional (`x_final` 0, SFOE's "Definitiv"); every earlier month is final. Every run that is not `--offline` asks for the file again and writes the table again (`write_snapshot`), so SFOE's revisions replace the rows held.

## Shape and variables

Series, 4,000 rows, 15 variables.

- `entity`: `bfe:ch`.
- `variable`: one a column, in English.
- `node`: SFOE's German column name.
- `unit`: MWh (the file's GWh times 1,000).
- `ts_utc`: the month's first day. `freq` P1M, `geo` CH.
- `x_final`: 1 final, 0 provisional.

| `variable` | SFOE's column | From |
|---|---|---|
| run_of_river_generation | Erzeugung_Laufwerk_GWh | 2000-01 |
| storage_hydro_generation | Erzeugung_Speicherwerk_GWh | 2000-01 |
| nuclear_generation | Erzeugung_Kernkraftwerk_GWh | 2000-01 |
| other_generation | Erzeugung_andere_GWh | 2000-01 to 2019-12 |
| thermal_generation | Erzeugung_Thermische_GWh | 2020-01 |
| wind_generation | Erzeugung_Windkraft_GWh | 2020-01 |
| solar_generation | Erzeugung_Photovoltaik_GWh | 2020-01 |
| national_generation | Landeserzeugung_GWh | 2000-01 |
| pumped_storage_consumption | Verbrauch_Speicherpumpen_GWh | 2000-01 |
| net_generation | Erzeugung_netto_GWh | 2000-01 |
| imports | Einfuhr_GWh | 2000-01 |
| exports | Ausfuhr_GWh | 2000-01 |
| national_consumption | Landesverbrauch_GWh | 2000-01 |
| losses | Verluste_GWh | 2000-01 |
| final_consumption | Endverbrauch_GWh | 2000-01 |

From 2020, SFOE splits "other" into thermal, wind and solar. A cell it writes NULL has no row.

TWh a year (the twelve months summed here for this note):

| `variable` | 2000 | 2015 | 2025 |
|---|---|---|---|
| national_generation | 65.35 | 65.96 | 67.52 |
| nuclear_generation | 24.95 | 22.10 | 18.38 |
| storage_hydro_generation | 20.28 | 22.89 | 21.16 |
| run_of_river_generation | 17.57 | 16.60 | 16.33 |
| solar_generation | | | 7.95 |
| imports | 24.33 | 34.03 | 30.72 |
| exports | 31.40 | 35.07 | 30.70 |
| national_consumption | 56.30 | 62.63 | 62.33 |
| final_consumption | 52.37 | 58.25 | 57.97 |

## Reading the source

- The run stops at once, asking nothing, while `bfe_electricity` or the host www.bfe-ogd.ch is paused.
- One request a run (timeout 60 seconds). HTTP 404 stops the run; any other failure is tried up to `RETRIES` (4) times (`iso_prices.fetch_raw`). `--offline` reads the saved file.
- The run stops, and no file is written, for any of these:
  - a header other than the 18 columns read in session 2343;
  - a month outside 1 to 12;
  - a "Definitiv" other than 0 or 1;
  - a value that is not a number;
  - a month given twice.
- Nothing is filled.

## License

Public. `license_verdicts.csv` records the Swiss Federal Office of Energy (SFOE), read 594 (session 2343): "may be public", sold or not. The dataset's resource names opendata.swiss's term "Open use. Must provide the source": "You may use this dataset for commercial purposes. You must provide the source (author, title and link to the dataset)". The header gives all three.

## Cross-checks (session 2343)

- Within the table, exactly (0 MWh) in every month:
  - the kinds of generation sum to national generation;
  - national generation less pumping is net generation;
  - net generation plus imports less exports is national consumption;
  - national consumption less losses is final consumption.
- Against `energy_charts_central_europe` (Switzerland, 2023 to 2025): nuclear, solar and run-of-river are 1.000 of SFOE's every year.
- National consumption over `owid_ember_electricity_annual`'s demand: 0.956 to 0.967, 2016 to 2025.

## What it does not hold

- Months before 2000; SFOE's annual and weekly balances (the two other data sets the catalogue lists); the cantons; prices.
