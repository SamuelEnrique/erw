# Crude oil and marketed natural gas production by producing region, a month, history only (EIA's Short-Term Energy Outlook)

Energy Research Warehouse (ERW), method note written in session 2004 (chain 056) for a table first written on 6 October 2026 (session 134).

Tables: `eia_basin_production_monthly`

## Publisher and address

U.S. Energy Information Administration (EIA), Short-Term Energy Outlook (`https://www.eia.gov/outlooks/steo/`), crude oil and natural gas production by region, through the EIA API v2 route `steo`. The connector first reads the Outlook's list of series (`https://api.eia.gov/v2/steo/facet/seriesId`) and keeps the ids that are COPR (crude) or NGMP (marketed gas) followed by AP, BK, EF, HA, PM, AN, NI or R48; then it asks `https://api.eia.gov/v2/steo/data/?frequency=monthly&data[0]=value&start=2015-01` with those ids as `seriesId` facets, sorted by period and seriesId, pages of 5,000. Source id `eia:steo:basin_production`. Connector: `warehouse/connectors/eia_supply.py` (session 134), one of its four tables. The key from `EIA_API_KEY` is sent apart from the address, so the address kept in `source_url` and in the raw files has none.

## Vintage and revision

January 2015 to July 2026 in the file on the data machine, read by run `20261010T145819Z` (10 October 2026) and restored from the Redivis draft by `scripts/sync.py`, as its header says. Header: "1,872 rows returned, 1,668 values"; the Outlook's months after 2026-07, "EIA's newest estimates and its forecast: 204 such rows were not written".

The Outlook's series run on into EIA's forecast, so only months up to `HISTORY_LAG` (3) months before the month of the run are written: a run in October 2026 ends on July 2026. Each run reads the whole series from 2015, deletes the file and writes the table again, so the Outlook's revisions of its history are taken. A table whose newest month is more than 150 days old is not written.

## Shape and variables

Series, 1,668 rows: 12 series of 139 months each. `entity` `eia:<Outlook series id>`; `ts_utc` the month's first day; `freq` P1M; `geo` US for every series; `node` EIA's series name; `market` and `vintage` empty.

| Variable | Unit | Series (EIA's names) |
|---|---|---|
| `crude_production` | kbbl/d (the Outlook's million barrels a day times 1,000) | COPRAP Appalachia, COPRBK Bakken, COPREF Eagle Ford, COPRHA Haynesville, COPRPM Permian, COPRR48 "Rest of Lower 48 States" |
| `gas_marketed_production` | bcf/d, as published | NGMPAP Appalachia, NGMPBK Bakken, NGMPEF Eagle Ford, NGMPHA Haynesville, NGMPPM Permian, NGMPR48 "Rest of U.S." |

The R48 series are remainders, EIA's "Rest of Lower 48 States" for crude and "Rest of U.S." for gas, not totals. The table holds no AN or NI series, though the code would take them.

## Reading the API

- Fewer than 8 matching series in the Outlook's list stops the table.
- The rows read must equal the total the API reports, or the table is not written.
- A unit not in the connector's map stops the table; an (entity, variable, ts_utc) given twice stops it.
- A value that is empty, "W", "NA", "--", "null" or "None" is not written and is counted (none here); any other value that is not a number stops the table.
- Ceiling: 1,200,000 rows returned in a run, counted from session 134's 6,000 rows of probes; past it the run stops. A page is tried up to four times; pages are 0.4 seconds apart.

## License

Public: a work of the U.S. government (record 1 of `license_reads.csv`).

## Cross-checks (session 2004)

- The counts above were computed from the rows, read past the header lines; 1,872 rows returned less the 204 forecast rows is the 1,668 written.
- No series is a total of the others, so no sum is checked against one. The six crude series sum to 11,482.809 kbbl/d in July 2026, the Permian 6,853.305 of it (1,726.540 in January 2015); the six gas series sum to 121.940 bcf/d. The two sums cover different areas, since the crude remainder is the rest of the Lower 48 and the gas remainder the rest of the U.S.
- The connector has no cross-check of its own beyond its reading rules.

## What it does not hold

- The Outlook's forecast and the months the lag leaves out.
- The Outlook's other series, and months before 2015.
- State production: crude by state is `eia_crude_production_state_monthly`, gas by state `eia_gas_production_state_monthly`.
