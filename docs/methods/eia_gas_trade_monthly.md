# Natural gas trade, a month: pipeline flows with Canada and Mexico, LNG exports in all and by point of exit, LNG imports (EIA)

Energy Research Warehouse (ERW), method note written in session 2018 (chain 057) for a table first written on 6 October 2026 (session 134).

Tables: `eia_gas_trade_monthly`

## Publisher and address

U.S. Energy Information Administration (EIA), two routes of the EIA API v2, from January 2015, sorted by period and series, pages of 5,000:

- `natural-gas/move/poe2`, U.S. Natural Gas Exports and Re-Exports by Point of Exit (`https://www.eia.gov/dnav/ng/ng_move_poe2_a_EPG0_ENP_Mmcf_m.htm`), source id `eia:natural-gas/move/poe2:supply`, asked with no facet: `https://api.eia.gov/v2/natural-gas/move/poe2/data/?frequency=monthly&data[0]=value&start=2015-01&sort[0][column]=period&sort[0][direction]=asc&sort[1][column]=series&sort[1][direction]=asc&offset=0&length=5000`. Of every series the route gives, the connector keeps N9132MX2, N9132CN2 and N9133US2 and the series whose id matches `NGM_EPG0_ENG_Y<letters>-Z00_MMCF`, the LNG exports of one point of exit to all countries.
- `natural-gas/move/poe1`, U.S. Natural Gas Imports by Point of Entry (`https://www.eia.gov/dnav/ng/ng_move_poe1_a_EPG0_IRP_Mmcf_m.htm`), source id `eia:natural-gas/move/poe1:supply`, asked for three series by facet: N9102CN2, N9102MX2 and N9103US2.

Connector: `warehouse/connectors/eia_supply.py` (session 134), one of its four tables. The key from `EIA_API_KEY` is sent apart from the address, so the address kept in `source_url` and in the raw files has none.

## Vintage and revision

January 2015 to July 2026 in the file on the data machine, read by run `20261010T145819Z` (10 October 2026) and restored from the Redivis draft by `scripts/sync.py`, as its header says; every row's `retrieved_at` is 10 October 2026. Header: "Series: 36, newest date 2026-07-01. natural-gas/move/poe2: 36,246 rows returned, 1,562 values; natural-gas/move/poe1: 417 rows returned, 417 values. Dates EIA lists with no value, not written: 0." `coverage.csv` gives the same 1,979 rows and dates.

Each run reads the whole history from January 2015, deletes the file and writes the table again, so EIA's revisions are taken and a row EIA no longer gives leaves the table. A table whose newest month is more than 150 days old is not written.

## Shape and variables

Series, 1,979 rows: 36 series. `entity` `eia:<EIA series id>`; `unit` MMcf (million cubic feet in the month, whole numbers as EIA publishes them); `ts_utc` the month's first day; `freq` P1M; `geo` US on every row; `node` EIA's series name without its unit; `market` and `vintage` empty.

| Variable | Series | Rows | Months |
|---|---|---|---|
| `import_volume` | N9102CN2 pipeline imports from Canada, N9102MX2 pipeline imports from Mexico, N9103US2 LNG imports | 417 | all 139, 2015-01 to 2026-07 |
| `export_volume` | N9132CN2 pipeline exports to Canada, N9132MX2 pipeline exports to Mexico, N9133US2 LNG exports, all points | 417 | all 139 |
| `export_volume` | 30 points of exit, `NGM_EPG0_ENG_Y<point>-Z00_MMCF` | 1,145 | 1 to 126 months each |

The points of exit, as EIA names them: Sabine Pass, Corpus Christi, Cameron, Cameron (Calcasieu Pass), Freeport, Plaquemines, Cove Point, Elba Island and Golden Pass (from April 2026); points on the Canadian and Mexican borders (Laredo, Nogales, Otay Mesa, Calexico, El Paso, San Luis, Sweetgrass, Crosby, Portal, Noonan-Estevan, Calais, Niagara Falls); points in Florida (Fort Lauderdale, Miami, Jacksonville, West Palm Beach, Doral); Kenai (Alaska), Newark, Savannah, and Altamira, Tamaulipas. Many hold a few months: Newark, Noonan-Estevan, San Luis and Savannah one each. Inside their spans many months have no row (Miami 45 rows over 124 months, Freeport 80 over 139). Two rows are 0, as EIA lists them: LNG imports in September 2019 and Laredo in November 2015.

July 2026: LNG exports 518,777 MMcf, pipeline exports to Mexico 227,569 and to Canada 80,758, pipeline imports from Canada 244,017.

## Reading the API

- The rows read must equal the total the API reports, or the table is not written; a table with no value at all stops.
- A row of `poe2` outside the kept series is passed over before its unit is read, and is not counted (36,246 rows returned, 1,562 written). The shaping function's docstring said such a row is counted; the code does not count it, and session 2018 corrected the docstring.
- A unit not in the connector's map stops the table (every row here is EIA's MMCF); an (entity, variable, ts_utc) given twice stops it.
- A value that is empty, "W", "NA", "--", "null" or "None" is not written and is counted (none here); any other value that is not a number stops the table.
- The connector does not check that each series it keeps or asks for came back.
- Ceiling: 1,200,000 rows returned in a run, counted from session 134's 6,000 rows of probes; past it the run stops. A page is tried up to four times; pages are 0.4 seconds apart.

## License

Public: a work of the U.S. government (record 1 of `license_reads.csv`). The header: "License: public. U.S. government publications are in the public domain (EIA, Copyrights and Reuse)"; `coverage.csv`: public.

## Cross-checks (session 2018)

- The counts above were computed from the rows, read past the 14 header lines; the six national series hold every one of the 139 months.
- The 30 points of exit sum to N9133US2, the LNG exports in all, within 1 MMcf in 118 of 139 months and within 3 MMcf in 128. Eleven months differ by more, the largest July 2026 (515,454 against 518,777, 3,323 short) and February 2016 (1,291 over).
- The point series equal `eia_lng_exports_monthly`'s, which reads the same route by series id, in all 634 rows the two tables share (9 terminals).
- The connector has no cross-check of its own beyond its reading rules.

## What it does not hold

- Prices: LNG export prices by terminal are `eia_lng_exports_monthly`; trade by country, with prices, is `eia_gas_trade_country_monthly`.
- Pipeline flows by point of entry or exit, and every other series of the two routes: the connector keeps the six national series and the LNG exports by point of exit only.
- Months before 2015.
- The header's line on "the Outlook's crude" is the connector's text for all its tables; it does not concern this one.
