# Denmark's electricity supply, a month, the country and its two areas (the Danish Energy Agency's monthly statistics)

Energy Research Warehouse (ERW), method note written in session 2349 (chain 109) for a table first written on 24 October 2026 (session 2348).

Tables: `ens_denmark_electricity_monthly`

## Publisher and address

The Danish Energy Agency (Energistyrelsen), "Månedlig elstatistik", the monthly electricity supply statistics, linked from `https://ens.dk/en/analyses-and-statistics/annual-and-monthly-statistics`. The workbook is `https://ens.dk/media/8572/download`, an .xls file, one GET, no key. Source id `ens:monthly_electricity`. Connector: `warehouse/connectors/ens_denmark_electricity.py` (session 2348). ens.dk's robots file allows `Claude-User` by name and every reader but Drupal's own paths (read 597).

## Vintage and revision

January 2000 to August 2026, written by run `20261024T082622Z`, which read the workbook saved at 2026-10-24T08:23:21Z (`retrieved_at`). `vintage` is its Last-Modified, 2026-10-02T07:14:59Z. The statistics page called the latest version July 2026; the workbook held August's rows too. Every run that is not `--offline` asks for the workbook again and writes the table again (`write_snapshot`).

## Shape and variables

Series, 27,777 rows, 37 variables.

- `entity`: three, one a sheet: `ens:dk` ("Hele landet (Denmark)"), `ens:dk_west` ("Energinet.dk_Vest (West)") and `ens:dk_east` ("Energinet.dk_Øst (East)").
- `variable`: one a column.
- `node`: the column's English label as the agency writes it. `x_sheet`: the sheet.
- `unit`: MWh (GWh times 1,000).
- `ts_utc`: the month's first day. `freq` P1M, `geo` DK.

The 35 columns:
- `gross_production`, `own_use_in_generation`, `net_production`;
- the kinds: `central_power_stations`, `public_power_stations`, `industrial_autoproducers`, `wind` and `wind_offshore` (from 2016), `hydro`, `solar`;
- `net_exchange`, and on the national sheet `net_exchange_west` and `net_exchange_east`;
- on the area sheets, in those two columns, `flow_west_to_east` and `flow_east_to_west`;
- `imports`, `exports` and `net_exports` (exports less imports), in all and with Sweden, Norway, Germany, the Netherlands (from 2019) and England (from 2023);
- `domestic_supply_incl_losses`, `primary_transmission_losses`, `domestic_supply_excl_losses`, `distribution_losses` (from 2021).

Net exports and net exchange are negative in months of net import, as the agency gives them. Totals are the agency's.

Denmark, TWh a year (the twelve months summed here for this note):

| `variable` | 2000 | 2015 | 2025 |
|---|---|---|---|
| gross_production | 35.79 | 28.73 | 33.73 |
| net_production | 34.26 | 27.70 | 33.07 |
| central_power_stations | 21.17 | 9.21 | 4.82 |
| wind | 4.24 | 14.13 | 19.09 |
| solar | 0.00 | 0.60 | 4.51 |
| imports | 8.42 | 15.64 | 27.06 |
| exports | 7.75 | 9.73 | 19.65 |
| domestic_supply_incl_losses | 34.92 | 33.62 | 40.48 |

## Reading the source

- The run stops at once, asking nothing, while `ens_electricity` or the host ens.dk is paused.
- One request a run (timeout 120 seconds). HTTP 404 stops the run; any other failure is tried up to `RETRIES` (4) times (`iso_prices.fetch_raw`). `--offline` reads the saved workbook.
- Only the monthly block is taken: the rows from the first "Januar" on, a year row then its month names, to the footnotes. The workbook's annual, January to August and quarterly blocks are its own sums and are not taken.
- The run stops, and no file is written, for any of these:
  - a sheet missing;
  - a national column whose English label is not the one read in session 2348;
  - an area sheet whose labels differ from the national sheet's, but for case and for columns 13 and 14;
  - a month name not Danish;
  - a value that is not a number;
  - a month given twice.
- A blank cell has no row. Nothing is filled.

## License

Internal. The statistics page states no licence or terms (read 598), and no terms page was found in session 2348. `sources.csv` flags the source `internal` until a read settles it. The workbook names Energinet as the source of most of its data.

## Cross-checks (session 2348)

- Within the table, in every month:
  - gross production less own use is net production within 0.001 MWh;
  - net production plus imports less exports is domestic supply including losses within 9 MWh;
  - West and East sum to the nation's net production, wind and solar exactly.
- Against `eurostat_electricity_monthly` (Denmark), 2016 to 2025:
  - wind 0.999 to 1.002;
  - imports and exports 1.000 in six of the ten years, exports 0.923 in 2020 the widest;
  - net production 0.999 to 1.031.
- `energinet_dk_production_hourly` holds Energinet's hourly production, a separate table.

## What it does not hold

- Months before 2000; production by fuel (the agency's annual statistics); the workbook's figure sheets.
