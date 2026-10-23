# Working gas in underground storage, a week (EIA's Weekly Natural Gas Storage Report)

Energy Research Warehouse (ERW), method note written in session 2004 (chain 056) for a table first written on 6 October 2026 (session 134).

Tables: `eia_gas_storage_weekly`

## Publisher and address

U.S. Energy Information Administration (EIA), Weekly Natural Gas Storage Report (`https://ir.eia.gov/ngs/ngs.html`), through the EIA API v2 route `natural-gas/stor/wkly`: `https://api.eia.gov/v2/natural-gas/stor/wkly/data/?frequency=weekly&data[0]=value&start=2010-01-01`, sorted by period and series, pages of 5,000, with no facet (every series the route gives). Source id `eia:natural-gas/stor/wkly`. Connector: `warehouse/connectors/eia_supply.py` (session 134), one of its four tables. The key from `EIA_API_KEY` is sent apart from the address, so the address kept in `source_url` and in the raw files has none.

## Vintage and revision

1 January 2010 to 2 October 2026 in the file on the data machine, read by run `20261010T145819Z` (10 October 2026) and restored from the Redivis draft by `scripts/sync.py`, as its header says. Header: "7,000 rows returned, 7,000 values"; no date without a value.

Each run reads the whole history from 2010, deletes the file and writes the table again, so EIA's revisions are taken and a row EIA no longer gives leaves the table. A table whose newest week is more than 21 days old is not written.

## Shape and variables

Series, 7,000 rows: 8 series of 875 weeks each. `entity` `eia:<EIA series id>`; `variable` `working_gas`; `unit` bcf, whole numbers as EIA publishes them; `ts_utc` EIA's date at 00:00:00Z, the Friday the report week ends (a Friday in all 875 weeks, each 7 days after the last, none missing); `freq` P1W; `geo` US for every series, the regions included; `node` EIA's series name without its unit.

| Series | Area |
|---|---|
| NW2_EPG0_SWO_R48_BCF | Lower 48 States |
| NW2_EPG0_SWO_R31_BCF to R35 | East, Midwest, South Central, Mountain, Pacific |
| NW2_EPG0_SSO_R33_BCF, NW2_EPG0_SNO_R33_BCF | the South Central's Salt and Nonsalt regions |

The Lower 48 holds the five regions, and the South Central its two parts: a sum takes one level.

## Reading the API

- The rows read must equal the total the API reports, or the table is not written.
- A unit not in the connector's map stops the table; an (entity, variable, ts_utc) given twice stops it.
- A value that is empty, "W", "NA", "--", "null" or "None" is not written and is counted; any other value that is not a number stops the table.
- Ceiling: 1,200,000 rows returned in a run, counted from session 134's 6,000 rows of probes; past it the run stops. A page is tried up to four times; pages are 0.4 seconds apart.

## License

Public: a work of the U.S. government (record 1 of `license_reads.csv`).

## Cross-checks (session 2004)

- The counts above were computed from the rows, read past the header lines.
- The five regions sum to the Lower 48 within 2 bcf in all 875 weeks (2 October 2026: 862 + 1,010 + 1,076 + 253 + 299 = 3,500), and Salt plus Nonsalt to the South Central within 1 bcf (2 October 2026: 227 + 849 = 1,076).
- The connector has no cross-check of its own beyond its reading rules.

## What it does not hold

- The report's net changes, five-year averages and year-ago figures: levels only.
- Weeks before 2010.
- States and fields: the monthly storage by state is `eia_gas_storage_state_monthly`, and the capacity `eia_gas_storage_capacity_monthly`.
- The header's line on "the Outlook's crude" is the connector's text for all its tables; it does not concern this one.
