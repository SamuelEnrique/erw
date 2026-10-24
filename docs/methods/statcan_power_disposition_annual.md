# Canada's annual supply and disposition of electric power by province (Statistics Canada, table 25-10-0021-01)

Energy Research Warehouse (ERW), method note written in session 2443 (chain 117) for a table first written on 24 October 2026 (session 2441).

Tables: `statcan_power_disposition_annual`

## Publisher and address

Statistics Canada, table 25-10-0021-01, "Electric power, electric utilities and industry, annual supply and disposition" (`https://www150.statcan.gc.ca/t1/tbl1/en/tv.action?pid=2510002101`), read as the table's full CSV download, a zip: `https://www150.statcan.gc.ca/n1/tbl/csv/25100021-eng.zip`. Source id `statcan:25-10-0021-01`. Connector: `warehouse/connectors/statcan_power_disposition.py` (session 2441). The host's robots file disallows paths ending in `.csv` for every agent, not a `.zip`, and names no AI agent (read 726).

## Vintage and revision

2005 to 2025, written by run `20261024T114729Z` (the write under the lock, offline), which read the zip saved at 2026-10-24T11:45:47Z (`retrieved_at`). `vintage` is the zip's last-modified time, 2026-10-16T12:30:33Z. 85 rows carry StatCan's revision mark, kept in `x_revised`. Every run that is not `--offline` asks again and writes the table again.

## Shape and variables

Series, 3,909 rows, 14 entities (Canada and the thirteen provinces and territories), 21 components.

- `entity`: `statcan_pd:<area>` (`ca`, or a postal code in lower case).
- `variable`: StatCan's component as a slug.
  - supply: `total_generation_of_electricity`, imports from the United States (`total_`, `_purchased`, `_exchanged`), interprovincial receipts (`total_`, `_purchased`);
  - out: exports to the United States (`total_`, `_firm`, `_secondary`, `_exchanged`), interprovincial deliveries (`total_`, `_firm`, `_secondary`);
  - `total_electricity_available_for_use_within_specific_geographic_border`, `electricity_used_by_producers`, `unallocated_electricity`;
  - sales to ultimate customers (`total_`, and residential, mining and manufacturing, agriculture, other industries).
- `unit` MWh, as StatCan gives it. `ts_utc` the year's 1 January; `freq` P1Y; `geo` CA or CA-<province>.
- `node`: the area and component as StatCan names them; `x_component` StatCan's name; `x_vector` its vector.

72 values are 0. 43 are negative: unallocated electricity, StatCan's balancing residual (38), and exchanged exports to the United States (5, British Columbia's and Canada's among them). The totals hold their parts: a sum takes one level. Canada's exports to the United States, TWh: 73.0 in 2015, 47.8 in 2023, 31.9 in 2025.

## Reading the source

- The run stops, asking nothing, while `statcan_power_disposition` or the host is paused.
- One request a run (timeout 180 seconds, 2 seconds' pause); `--offline` reads the saved zip.
- Only the estimate "Electricity quantity" is taken. "Electricity value" (Canadian dollars, thousands; 2,153 rows) is not taken, a foreign currency's values being a standing question for the owner; its rows are counted in the header.
- A figure StatCan marks ".." (not available, 867) or "x" has no row and is counted. Nothing is filled.
- The run stops, and no file is written, for any of these:
  - a zip that does not hold 25100021.csv alone;
  - a quantity in a unit other than megawatt hours, or a scalar factor other than units;
  - an estimate, area or status not in the map;
  - a year that does not read;
  - a key given twice.

## License

Public: the Statistics Canada Open Licence, StatCan's verdict on record in `license_verdicts.csv`. The header names the source and says the table does not constitute an endorsement by Statistics Canada.

## Cross-checks (session 2441)

- **Within the table, Canada:** generation plus imports less exports equals the electricity available in every year but 2015 (1.0065).
- **Against `statcan_generation_class_annual`:** total generation equals its total of all classes and types in every year.
- **Against `statcan_electricity_trade_monthly`:** exports to the United States are 0.968 to 1.011 of its twelve-month sums of US deliveries, 2008 to 2025, except 1.087 in 2015.

## What it does not hold

- The dollar values; months (25-10-0016-01 holds the monthly trade); a line for losses (the table has none).
