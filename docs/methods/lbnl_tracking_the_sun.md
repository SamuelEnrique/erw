# Distributed solar systems by state, customer segment and year of installation (Berkeley Lab's Tracking the Sun)

Energy Research Warehouse (ERW), method note written in session 2023 (chain 057) for a table first written on 23 October 2026 (session 2020, with the connector of session 2015).

Tables: `lbnl_tracking_the_sun`

## Publisher and address

Lawrence Berkeley National Laboratory (Berkeley Lab), Tracking the Sun, public data file, on the Open Energy Data Initiative (OEDI submission 3, `https://data.openei.org/submissions/3`). The 2024 edition's files are read from the OEDI data lake: the listing `https://oedi-data-lake.s3.amazonaws.com/?list-type=2&prefix=tracking-the-sun/2024/` and one Parquet file a state, `https://oedi-data-lake.s3.amazonaws.com/tracking-the-sun/2024/state=<ST>/part-....snappy.parquet` (27 files). Source id `lbnl:tracking_the_sun`. Connector: `warehouse/connectors/lbnl_tracking_the_sun.py` (session 2015; the 1980 floor, session 2020).

## Vintage and revision

The 2024 edition, its files last modified 28 February 2025 (17:44:25 to 17:44:41 UTC). Session 2015 fetched eight states' files and session 2020 the other nineteen (`--fetch-only --states`), retrieved 23 October 2026 18:22:00 to 18:50:50 UTC; run `20261023T185321Z` wrote the table from the saved files (`--offline`).

The listing and the files are taken from the saved files whenever a run has saved them, so a run without `--offline` asks only for what is not yet on the machine; another edition is read with `--edition`. The table is written whole each time. The edition holds systems installed to 2023; its 2024 rows are a partial year (15,138 systems).

## Shape and variables

Series, 8,762 rows: 135 state segments (`entity` `tts:<st>_<segment>`) in 27 states (AR, AZ, CA, CO, CT, DC, DE, FL, IL, MA, MD, ME, MN, NH, NJ, NM, NY, OH, OR, PA, RI, TX, UT, VA, VT, WA, WI), 1,891 segment-years from 1983 to 2024. `ts_utc` 1 January of the year of installation; `freq` P1Y; `geo` US-<ST>; `market` empty; `node` and `x_segment` the customer segment as the file writes it, "unknown" for its -1.

| Variable | Unit | Rows | What it is |
|---|---|---|---|
| systems | count | 1,891 | systems with an installation year |
| systems_priced | count | 1,891 | systems whose price and DC size are both above zero |
| systems_battery | count | 1,891 | systems whose battery_rated_capacity_kwh is above zero |
| capacity_dc | MW | 1,872 | the sum of the systems' DC size (the file's kW over 1,000) |
| price_median | USD/kW | 1,217 | the median of total installed price over DC size, priced systems only, unscreened |

| Segment | State segments | Systems | MW DC |
|---|---|---|---|
| RES | 27 | 3,132,657 | 25,228.6 |
| COM | 16 | 47,383 | 8,829.8 |
| NON-RES | 20 | 27,310 | 6,226.7 |
| GOV | 20 | 6,216 | 1,459.9 |
| NON-PROFIT | 17 | 4,842 | 324.0 |
| SCHOOL | 17 | 4,636 | 1,128.9 |
| unknown | 18 | 184,260 | 3,559.6 |

In all 3,407,304 systems with a year, 46,757.6 MW DC, 2,533,285 priced and 107,764 with a battery. California holds 1,920,989 of the systems and 18,003.5 MW. The states' years differ: Pennsylvania ends in 2014, Virginia and Washington in 2019, and Arkansas holds 105 systems from 2009 to 2011.

## Reading the files

- A listing marked truncated, one with no file, or one naming a state twice stops the run. A file without any of the five columns read (installation_date, pv_system_size_dc, total_installed_price, customer_segment, battery_rated_capacity_kwh) stops it, and so does a file whose date is unknown (no Last-Modified and no retrieval time).
- A system has no year, and no row, when its installation date does not read, is before 1 January 1980, or is after its file's own Last-Modified day. Such systems are counted in the run log by state and in the header in all: 19,162.
- A size or price of zero or less (the file writes -1 for missing) is missing: the system counts in systems, not in capacity_dc or the price. A segment-year with no size has no capacity_dc row, and one with no priced system no price_median row.
- An (entity, variable, ts_utc) given twice stops the run. Values are rounded to six decimals. Nothing is filled.
- Requests: the listing and one file a state, 28 for the 2024 edition, fetched under sessions 2015 and 2020's own ceilings (8 and 19 files). The data lake's host and data.openei.org have no robots file (HTTP 404).

## License

Public: CC BY 4.0, cite Berkeley Lab, Tracking the Sun. The table's header: "License: CC BY 4.0, as the OEDI submission states; cite Berkeley Lab, Tracking the Sun." `license_tables.csv` maps the table by hand to its own verdict, "Berkeley Lab, Tracking the Sun on OEDI" (`license_verdicts.csv`, read 176, the submission's record `"license": "https://creativecommons.org/licenses/by/4.0/"` and OEDI's footer), may be public.

## Cross-checks (sessions 2015, 2020 and 2023)

- Session 2015, on its eight states: California 1,920,989 systems and 18,004 MW DC, and Colorado 108,882, both as the table holds them; California's residential median from about USD 4,045 a kW in 2018 to 4,150 in 2023, as the table holds them (4,044.78 and 4,150.00).
- Session 2020, the DC capacity installed to the end of 2019 against EIA-861's net-metered (`eia_net_metering_state_annual`) and other distributed photovoltaic capacity (`eia861_distributed_generation`) at the end of 2019: 25,297 MW DC against 20,609 and 945 MW in the 27 states (117 percent), residential 13,732 against 12,381, California 10,259 against 9,128 and 169 (110 percent), the states' figures correlating at 0.98; Minnesota, Utah and Vermont well above EIA's, Maryland, Florida, Pennsylvania and Arkansas well below. Session 2023 computed the same 25,297, 13,732 and 10,259 MW from the rows.
- Session 2023: the systems with a year (3,407,304) and the header's systems without one (19,162) sum to the header's 3,426,466 systems; the segments' systems sum to the same 3,407,304.
- systems_priced and systems_battery are at most systems in all 1,891 segment-years, and price_median is present exactly where systems_priced is above zero (1,217).
- The price is unscreened, and it shows: five segment-years have a median below USD 500 a kW, the lowest USD 0.000025 (Massachusetts government systems, 2014, 55 priced); eight are above USD 15,000, all of them from 1998 to 2008.

## What it does not hold

- The systems themselves (one row a system in the file: zip codes, installers, equipment, third-party ownership and the rest): a summary only.
- Berkeley Lab's screened prices and its report's figures.
- Editions before 2024, and states the edition has no file for.
- Installations in 2024 in full: the edition holds a few.
