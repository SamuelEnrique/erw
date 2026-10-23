# Crude oil prices by stream and area, a month: first purchase prices, landed and F.O.B. costs of imports, refiners' acquisition cost (EIA)

Energy Research Warehouse (ERW), method note written in session 2018 (chain 057) for a table first written on 6 October 2026 (session 132).

Tables: `eia_crude_stream_prices`

## Publisher and address

U.S. Energy Information Administration (EIA), four routes of the EIA API v2, each asked with no facet (every series the route gives) from January 2019, sorted by period and series, pages of 5,000:

| Route | EIA's report and page | Source id | Variable |
|---|---|---|---|
| `petroleum/pri/dfp2` | Domestic Crude Oil First Purchase Prices for Selected Crude Streams, `https://www.eia.gov/dnav/pet/pet_pri_dfp2_k_m.htm` | `eia:petroleum/pri/dfp2:streams` | `first_purchase_price` |
| `petroleum/pri/land2` | Landed Costs of Imported Crude for Selected Crude Streams, `https://www.eia.gov/dnav/pet/pet_pri_land2_k_m.htm` | `eia:petroleum/pri/land2` | `landed_cost` |
| `petroleum/pri/imc2` | F.O.B. Costs of Imported Crude Oil for Selected Crude Streams, `https://www.eia.gov/dnav/pet/pet_pri_imc2_k_m.htm` | `eia:petroleum/pri/imc2` | `fob_cost` |
| `petroleum/pri/rac2` | Refiner Acquisition Cost of Crude Oil, `https://www.eia.gov/dnav/pet/pet_pri_rac2_dcu_nus_m.htm` | `eia:petroleum/pri/rac2` | `refiner_acquisition_cost` |

The address of the first page of each, as the rows keep it (decoded here): `https://api.eia.gov/v2/petroleum/pri/dfp2/data/?frequency=monthly&data[0]=value&start=2019-01&sort[0][column]=period&sort[0][direction]=asc&sort[1][column]=series&sort[1][direction]=asc&offset=0&length=5000`, and the same for the other three routes. The `:streams` suffix keeps the registry row of `eia_crude_first_purchase_prices`, which reads the same route, as it is. Connector: `warehouse/connectors/eia_board.py` (session 132), one of its three tables. The key from `EIA_API_KEY` is sent apart from the address, so the address kept in `source_url` and in the raw files has none.

## Vintage and revision

January 2019 to August 2026 in the file on the data machine, read by run `20261010T151001Z` (10 October 2026) and restored from the Redivis draft by `scripts/sync.py`, as its header says; every row's `retrieved_at` is 10 October 2026. Header: "Series: 41, newest date 2026-08-01. petroleum/pri/dfp2: 819 rows returned, 728 values; petroleum/pri/land2: 792 rows returned, 467 values; petroleum/pri/imc2: 246 rows returned, 146 values; petroleum/pri/rac2: 1,641 rows returned, 1,641 values", and 516 dates with no value not written. `coverage.csv` gives the same 2,982 rows and dates, and 38 nodes.

Each run reads the whole history from January 2019, deletes the file and writes the table again, so EIA's revisions are taken and a row EIA no longer gives leaves the table. A table whose newest month is more than 150 days old is not written.

## Shape and variables

Series, 2,982 rows: 41 series, each one entity with one variable. `entity` `eia:<EIA series id>`; `unit` USD/bbl on every row; `ts_utc` the month's first day; `freq` P1M; `node` the stream or area, from EIA's description (38 names: three streams have both a landed and an F.O.B. series); `market` and `vintage` empty. These are averages of the month, not spot prices.

| Variable | Rows | Series | Streams or areas | `geo` |
|---|---|---|---|---|
| `first_purchase_price` | 728 | 9 | West Texas Intermediate, West Texas Sour, Light Louisiana Sweet, Heavy Louisiana Sweet, Mars Blend, Wyoming Sweet, California Kern River (to March 2020), California Midway-Sunset (to September 2025), Alaska North Slope | the state: US-TX, US-LA, US-WY, US-CA, US-AK |
| `landed_cost` | 467 | 11 | Canadian Light Sour Blend, Canadian Bow River Heavy, Mexican Mayan, Ecuadorian Oriente, Ecuadorian Napo, Saudi Arabian Light, Saudi Arabian Medium, Saudi Arabian Berri, Iraqi Basrah Light, Venezuelan Merey, Algerian Saharan Blend | empty |
| `fob_cost` | 146 | 3 | Canadian Light Sour Blend, Mexican Mayan, Iraqi Basrah Light | empty |
| `refiner_acquisition_cost` | 1,641 | 18 | composite, domestic and imported, for the U.S. and each of the five PADDs | US for the three U.S. series, empty for the PADDs |

Only the three U.S. refiner series reach August 2026 (92 months); every other series ends in July 2026 or earlier. The import streams are thin: Algerian Saharan Blend and Iraqi Basrah Light's F.O.B. cost have one month each, and Saudi Arabian Berri 5 of the 45 months of its span. Values run from 9.34 (Canadian Bow River Heavy, landed, April 2020) to 121.23 (PADD 1 domestic acquisition cost, June 2022).

## Reading the API

- The rows read must equal the total the API reports, or the table is not written; a table with no value at all stops.
- A unit other than "$/BBL" stops the table; an (entity, variable, ts_utc) given twice stops it.
- A value that is empty, "W", "NA", "--", "null" or "None" is not written and is counted (516 here); any other value that is not a number stops the table.
- `geo` is read from EIA's area code: the US, a state (also as S plus the state's code), else empty.
- Ceiling: 1,500,000 rows returned in a run, counted from session 132's 1,300 rows of probes; past it the run stops. A page is tried up to four times; pages are 0.4 seconds apart.

## License

Public: a work of the U.S. government (record 1 of `license_reads.csv`). The header: "License: public. U.S. government publications are in the public domain (EIA, Copyrights and Reuse); these are EIA's own surveys"; `coverage.csv`: public.

## Cross-checks (session 2018)

- The counts above were computed from the rows, read past the 18 header lines; 819 plus 792 plus 246 plus 1,641 rows returned, less the 516 not written, is the 2,982 held.
- The composite acquisition cost lies between the domestic and the imported cost in every month: the U.S. in all 92 months, each PADD in all 91 (July 2026, U.S.: 83.65 between 81.24 imported and 84.93 domestic).
- Landed cost is at or above F.O.B. cost for Canadian Light Sour Blend in 65 of 67 shared months (median 2.56 USD/bbl above) and for Mexican Mayan in 76 of 78 (median 0.99 above).
- Mars Blend (F003075793) equals `eia_crude_first_purchase_prices`'s in all 91 months.
- West Texas Intermediate's first purchase price is on average 0.93 USD/bbl below the month's mean of WTI Cushing's daily spot price in `eia_fuel_spot_prices` (91 months).
- The connector has no cross-check of its own beyond its reading rules.

## What it does not hold

- Months before 2019, and the months EIA lists with no value (withheld or not yet reported).
- Daily crude prices: WTI and Brent by the day are `eia_fuel_spot_prices`. The longer first purchase histories of Mars and North Dakota are `eia_crude_first_purchase_prices`.
- Volumes: the streams' prices only.
- The header's words on "a weekly value's is EIA's survey Monday" are the connector's text for all its tables; they do not concern this one.
