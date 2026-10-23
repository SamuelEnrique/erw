# Refined product spot prices, a trading day: gasoline, diesel, jet fuel, heating oil, propane (EIA)

Energy Research Warehouse (ERW), method note written in session 2018 (chain 057) for a table first written on 25 September 2026 (session 7).

Tables: `eia_product_spot_prices`

## Publisher and address

U.S. Energy Information Administration (EIA), Spot Prices for Crude Oil and Petroleum Products (`https://www.eia.gov/dnav/pet/pet_pri_spt_s1_d.htm`), through the EIA API v2 route `petroleum/pri/spt`: `https://api.eia.gov/v2/petroleum/pri/spt/data/?api_key=REDACTED&frequency=daily&data[0]=value&sort[0][column]=period&sort[0][direction]=asc&sort[1][column]=series&sort[1][direction]=asc&offset=0&length=5000` followed by one `facets[series][]=` for each of the nine series below (decoded here, as the rows keep it in `source_url`), pages of 5,000. Source id `eia:petroleum/pri/spt`, which `eia_fuel_spot_prices` shares. Connector: `warehouse/connectors/eia_series.py` (session 7), one of its thirteen tables. The key comes from `EIA_API_KEY` and is written `REDACTED` in the address each row keeps.

## Vintage and revision

2 June 1986 to 20 October 2026 in the file on the data machine. Its header: rebuilt from the ERW archive by `warehouse/restore_tables.py` as of run `20261022T152428Z-github`, from the connector's run `20261022T143537Z`; "Dates EIA lists without a value, omitted: 0". The rows' `retrieved_at` are 29 September 2026 (71,908 rows), 30 September (44), 8 October (46), 19 October (54) and 22 October 2026 (36). `coverage.csv` gives the same 72,088 rows and dates.

Each run asks for the full history and `ip.write_csv` merges it into the file on (entity, variable, ts_utc): a day EIA revises is replaced, and a row EIA stops giving is kept from an earlier run. The file's header line "every run replaces all of it" is the older wording; the code's header has said otherwise since session 865 (23 October 2026), after this file was written. A table whose newest date is more than 10 days old is not written.

## Shape and variables

Series, 72,088 rows: 9 series. `entity` `eia:<EIA series id>`; `variable` `spot_price`; `unit` USD/gal; `ts_utc` EIA's trading date at 00:00:00Z (no Saturday or Sunday in the table); `freq` P1D; `geo` US on every row; `market`, `node` and `vintage` empty (EIA's series names are in the header's "Series:" line). Every series ends on 20 October 2026.

| Series | EIA's name | Rows | From | 20 October 2026 |
|---|---|---|---|---|
| EER_EPMRU_PF4_Y35NY_DPG | New York Harbor Conventional Gasoline Regular Spot Price FOB | 10,157 | 1986-06-02 | 2.897 |
| EER_EPMRU_PF4_RGC_DPG | U.S. Gulf Coast Conventional Gasoline Regular Spot Price FOB | 10,154 | 1986-06-02 | 3.157 |
| EER_EPMRR_PF4_Y05LA_DPG | Los Angeles Reformulated RBOB Regular Gasoline Spot Price | 5,932 | 2003-03-11 | 3.477 |
| EER_EPD2DXL0_PF4_Y35NY_DPG | New York Harbor Ultra-Low Sulfur No 2 Diesel Spot Price | 5,118 | 2006-06-14 | 5.265 |
| EER_EPD2DXL0_PF4_RGC_DPG | U.S. Gulf Coast Ultra-Low Sulfur No 2 Diesel Spot Price | 5,118 | 2006-06-14 | 4.962 |
| EER_EPD2DC_PF4_Y05LA_DPG | Los Angeles, CA Ultra-Low Sulfur CARB Diesel Spot Price | 7,658 | 1996-04-17 | 5.365 |
| EER_EPJK_PF4_RGC_DPG | U.S. Gulf Coast Kerosene-Type Jet Fuel Spot Price FOB | 9,191 | 1990-04-02 | 4.632 |
| EER_EPD2F_PF4_Y35NY_DPG | New York Harbor No. 2 Heating Oil Spot Price FOB | 10,155 | 1986-06-02 | 4.832 |
| EER_EPLLPA_PF4_Y44MB_DPG | Mont Belvieu, TX Propane Spot Price FOB | 8,605 | 1992-07-09 | 1.133 |

Values run from 0.203 (propane, 23 March 2020) to 5.526 USD/gal (Los Angeles CARB diesel, 14 October 2026); none is 0 or negative.

## Reading the API

- The rows read must equal the total the API reports, or the table is not written; an empty answer stops it too.
- The nine series are asked by series id: if EIA returns nothing for one of them, the table stops.
- A unit not in the connector's map, or a (series, date) given twice, stops the table. Every row here is EIA's "$/GAL".
- A value that is not a number stops the table, except an empty value, "none" and "Not Available", which are omitted and counted (none here).
- The 10-day limit is read on the newest date of the whole table, not of each series.
- No ceiling is stated. A page is tried up to four times; pages are 0.5 seconds apart.

## License

The header: "License: public domain (EIA)"; `coverage.csv` says public, and `docs/licenses.md` gives the ERW verdict public (EIA, "may be public"). EIA's own notice on its daily spot prices of crude oil and products, quoted in `docs/methods/price_board_v4.md`, names another party as their source: "Sources: Refinitiv, an LSEG business". The prices are therefore Refinitiv's (LSEG's), republished by EIA. Session 127 (`archive/sessions/SESSION_127_REPORT.md`) held EIA's NYMEX futures back as internal on that kind of reading, left this table public, and asked a person to rule on it too. EIA's general terms are record 1 of `license_reads.csv`.

## Cross-checks (session 2018)

- The counts above were computed from the rows, read past the 12 header lines; no (entity, variable, ts_utc) is given twice, and no date is a weekend.
- Days a year: 246 to 250 for each series in 2024 and 2025, as for trading days.
- From 14 June 2006, when the two ULSD series begin, the table has 5,129 dates, and all nine series are priced on 5,091 of them.
- New York Harbor ULSD is at or above New York Harbor heating oil on 5,108 of the 5,116 days both are priced (on average 0.0999 USD/gal above).
- Dates against WTI's in `eia_fuel_spot_prices` from 2 June 1986: 10,174 dates here, 10,172 WTI dates; 23 dates here have no WTI row, and 21 WTI dates have no row here.
- The connector has no cross-check of its own beyond its reading rules.

## What it does not hold

- Crude oil: WTI and Brent by the day are `eia_fuel_spot_prices`, from the same route.
- Futures (`eia_all_futures_prices`), and retail prices: weekly retail gasoline and diesel are `eia_retail_fuel_prices` and `eia_regional_retail_fuel_prices`.
- Days without a trade.
