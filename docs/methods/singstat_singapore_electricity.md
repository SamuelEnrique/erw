# Singapore's electricity generation and consumption (SingStat Table Builder M890831 and M890841)

Energy Research Warehouse (ERW), method note written in session 2317 (chain 106) for a table first written on 24 October 2026 (session 2308).

Tables: `singstat_singapore_electricity`

## Publisher and address

The Singapore Department of Statistics (SingStat), Table Builder, two tables whose data source is the Energy Market Authority (each answer's `datasource`, "ENERGY MARKET AUTHORITY"):

    https://tablebuilder.singstat.gov.sg/api/table/tabledata/M890831   "Electricity Generation, Monthly"
    https://tablebuilder.singstat.gov.sg/api/table/tabledata/M890841   "Electricity Generation And Consumption, Annual"

One GET a table, no key. Source id `singstat:M890831_M890841`. Connector: `warehouse/connectors/singstat_electricity.py` (session 2308).

The Energy Market Authority's own site answered an Incapsula bot challenge (read 501), so it was not used. tablebuilder.singstat.gov.sg's robots file allows every path (read 504). www.singstat.gov.sg's allows every path with a crawl delay of 2 seconds (read 505). Neither names an AI agent.

## Vintage and revision

M890831 runs from January 1975 to June 2026. M890841 gives generation for 1975 to 2025 and consumption for 2005 to 2024. Written by run `20261024T060753Z`, which read the two answers saved at 2026-10-24T06:06:34Z and 06:06:37Z (`retrieved_at`). `vintage` is each table's "dataLastUpdated": 2026-10-14 for M890831 and 2026-06-23 for M890841, written at 00:00Z. Every run that is not `--offline` asks for both tables again and writes the table again (`write_snapshot`).

## Shape and variables

Series, 1,009 rows, 19 series.

- `entity`: `singstat:sg`.
- `variable`: the table's code in lower case, then the row's name in snake case (`m890831_electricity_generation`, `m890841_households`, ...).
- `node`: the row as SingStat writes it. `x_table`: the table. `x_series`: SingStat's series number (1, 2, 2.1, 2.1.1, ...).
- `unit` MWh: the tables' GWh, which SingStat writes "Gigawatt Hours", times 1,000.
- `ts_utc`: the month's or year's first day. `freq`: P1M (M890831) or P1Y (M890841). `geo` SG.

M890841's lines:
- generation (1);
- consumption (2), split into industrial-related (2.1: manufacturing, construction, utilities, other), commerce and service-related (2.2: seven activities), transport-related (2.3), households (2.4) and others (2.5).

TWh a year (the rows summed here for this note):

| `variable` | 2005 | 2015 | 2024 |
|---|---|---|---|
| m890841_electricity_generation | 38.21 | 50.27 | 59.62 |
| m890841_electricity_consumption | 35.49 | 47.51 | 57.64 |
| m890841_industrial_related | 14.51 | 20.09 | 22.70 |
| m890841_commerce_and_service_related | 13.08 | 17.48 | 23.20 |
| m890841_information_and_communications | 0.67 | 1.43 | 6.07 |
| m890841_households | 6.09 | 7.22 | 8.42 |
| m890841_transport_related | 1.20 | 2.44 | 3.20 |

Generation was 60.41 TWh in 2025. January to June 2026: 30.00 TWh (M890831). No value is negative.

## Reading the source

- The run stops at once, asking nothing, while `singstat_electricity` or the host tablebuilder.singstat.gov.sg is paused.
- Two requests a run, each fetched fresh (timeout 120 seconds, 2 seconds' pause after it). HTTP 404 stops the run; any other failure is tried up to `RETRIES` (4) times (`iso_prices.fetch_raw`). `--offline` reads the saved answers.
- The run stops, and no file is written, for any of these:
  - a table answered without rows;
  - a unit other than GWh or "Gigawatt Hours";
  - a monthly column key not of the form "YYYY Mon", or an annual one not a year;
  - a value that is not a number (commas are removed first);
  - a row and period given twice.
- A cell that is blank, "na", "-", "n.a.", ".." or "x" has no row. Nothing is filled.

## License

Internal. SingStat's terms of use page draws its text with scripts, so its HTML holds no sentence (read 506). No verdict is recorded; `sources.csv` flags the source `internal`. A read of the terms (another route to their text) would settle it.

## Cross-checks (session 2308)

- The twelve months of M890831 sum to M890841's annual generation (1.0000) in every year 2015 to 2025.
- Annual generation over `owid_ember_electricity_annual`'s demand for Singapore: 0.999 to 1.000, 2015 to 2025.
- In every year, the five consumption lines sum to the total within 200 MWh, and the four industrial parts sum to their line within 100 MWh: the tables' rounding.

## What it does not hold

- Generation by fuel or by producer; tariffs (M890991 and M891001, prices, not taken); the Energy Market Authority's own statistics, which its site keeps behind a bot challenge.
