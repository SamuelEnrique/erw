# What households spend on energy, by state and source, a year (EIA, State Energy Data System, the residential sector)

Energy Research Warehouse (ERW), method note written in session 2116 (chain 069) for a table first written on 23 October 2026 (session 2108).

Tables: `eia_seds_residential_annual`

## Publisher and address

U.S. Energy Information Administration (EIA), State Energy Data System (SEDS), through EIA's API v2, route `seds`, annual, from 1990, eleven series asked together in pages of 5,000 rows sorted by period, series and state:

`https://api.eia.gov/v2/seds/data/?api_key=<key>&frequency=annual&data[]=value&facets[seriesId][]=<id>...&start=1990&length=5000&offset=<n>`

The key is read from `EIA_API_KEY` (the environment or `.env`) and redacted from every address the table and the log keep. Report page `https://www.eia.gov/state/seds/`. Source id `eia:seds_residential`. Connector: `warehouse/connectors/eia_seds_residential.py` (session 2108), its only table. api.eia.gov has no robots file (session 2108's report: its robots address answers 403, as every path without a key does). The file asked for BEA's personal consumption by state; session 2108 did not pull it (apps.bea.gov's robots file does not allow `/regional/zip/`, and BEA's API needs a key the ERW does not hold) and took SEDS in its place.

The table is not scheduled: no line of `warehouse/run_daily.sh`, the other `warehouse/*.sh` scripts, `scripts/` or `.github/workflows/` names the connector (searched in session 2116), and `run_status.csv` holds no row for it. It was written once, by run `20261023T214112Z` on the data machine.

## Vintage and revision

Years 1990 to 2024 (`ts_utc` 1 January), the 50 states, DC and the nation. EIA answered the five pages from 2026-10-23T21:38:44Z to 21:39:01Z (the trial run `20261023T213840Z`, saved in `warehouse/raw/eia_seds_residential/`); the write run reused them and asked EIA nothing (its header: "0 requests of 10"). `vintage` is empty. `coverage.csv` gives the same 20,020 rows and the same first and last `ts_utc`; its `n_nodes` of 11 counts the series' names (`node`), while the rows hold 572 entities (11 series by 52 places).

Each run writes the whole table again (`ip.write_snapshot`). SEDS's figures are EIA's estimates and are revised when EIA releases a new year; a run without `--fresh` reads the saved pages, so a revision reaches the table only with `--fresh`.

## Shape and variables

Series, 20,020 rows: 11 series, 52 places (`US` and `US-<state>`, DC included), 35 years, every cell present (no withheld value). `entity` `eia_seds_res:<seriesId>:<state>`; `variable` `expenditures` (USD, EIA's million dollars times 1,000,000), `consumption` (TBtu, billion Btu times 0.001), `price` (USD/MMBtu) or `population` (count, thousands times 1,000); values rounded to six decimals after scaling; `freq` P1Y; `market` empty; `node` the series' name as EIA gives it; `x_series` the series id; `x_source` the energy source. Expenditures are nominal dollars.

| Series (`x_source`) | Variable, unit | Rows | Nation, 2024 | Mean a state-year | Lowest state-year | Highest state-year |
|---|---|---|---|---|---|---|
| TERCV (total) | expenditures, USD | 1,820 | 333,267,900,000 | 4,117,029,636 | 175,300,000 (WY, 1992) | 36,289,100,000 (CA, 2024) |
| ESRCV (electricity) | expenditures, USD | 1,820 | 244,367,400,000 | 2,779,651,485 | 90,300,000 (DC, 1990) | 27,443,700,000 (CA, 2024) |
| NGRCV (natural_gas) | expenditures, USD | 1,820 | 63,578,300,000 | 923,640,504 | 4,900,000 (ME, 1990) | 10,119,400,000 (CA, 2023) |
| PARCV (petroleum) | expenditures, USD | 1,820 | 23,711,300,000 | 385,573,501 | 1,000,000 (DC, 2020) | 4,856,000,000 (NY, 2008) |
| DFRCV (distillate_fuel_oil) | expenditures, USD | 1,820 | 10,923,800,000 | 193,861,176 | 0 (89 state-years) | 4,047,400,000 (NY, 2008) |
| HLRCV (hgl) | expenditures, USD | 1,820 | 12,451,200,000 | 181,585,994 | 0 (3 state-years) | 1,078,500,000 (MI, 2014) |
| KSRCV (kerosene) | expenditures, USD | 1,820 | 336,200,000 | 10,125,938 | 0 (194 state-years) | 198,800,000 (NY, 2005) |
| WDRCV (wood) | expenditures, USD | 1,820 | 1,611,000,000 | 27,720,168 | 0 (26 state-years) | 298,300,000 (CA, 2013) |
| TERCB (total) | consumption, TBtu | 1,820 | 18,424.026 | 375.127 | 26.003 (HI, 1991) | 1,669.597 (TX, 2011) |
| TERCD (total) | price, USD/MMBtu | 1,820 | 31.08 | 19.895 | 8.04 (UT, 1993) | 118.79 (HI, 2022) |
| TPOPP (population) | population, count | 1,820 | 340,004,000 | 5,858,170 | 454,000 (WY, 1990) | 39,528,000 (CA, 2020) |

Each series' 1,820 rows are 35 national rows and 1,785 state rows (51 with DC); the means, lowest and highest are of the state rows. In 2024 the nation's sources sum to its total (electricity, natural gas, petroleum and wood, USD 333.268 billion against TERCV's 333.2679), petroleum is the sum of distillate, HGL and kerosene (USD 23.7112 billion against PARCV's 23.7113), and the total is USD 980 a resident. The counts were computed in session 2116 from the rows, read past the 10 header lines; no (entity, variable, ts_utc) is given twice.

## Checks the connector makes

- Before any request, api.eia.gov is checked against `warehouse/metadata/paused_sources.csv` by connector and by host; a paused publisher stops the run with no request. EIA is not paused. No key in the environment stops the run.
- A series not asked for, a unit not in the map (billion Btu, dollars per million Btu, million dollars, thousand), an (entity, variable, ts_utc) given twice on a page or across pages, a count of rows read that is not the API's total, or a series with no row stops the run, and nothing is written.
- A value that is not a number (withheld) has no row. Nothing is filled.
- Ceiling: 10 requests a run, counted by the code (a saved page reused does not count); 3 seconds before each request; an HTTP 429 or 5xx is asked once more after 60 seconds and then stops the run; any other error status stops it at once. `--offline` reads only saved pages; `--fresh` asks every page again.

## The cross-check

Session 2108 set SEDS's residential electricity expenditures against EIA-861's residential revenue summed to the state (`eia861_utility_sales`), 510 state-years from 2015 to 2024, in `runs/c069/s2108/cross.py` (on the data machine, not in git). The median ratio is 1.014 and SEDS is never below EIA-861 (5th percentile 1.000); the widest gap, South Dakota at about 1.33, fits the short-form utilities that `eia861_utility_sales` does not hold, a cause the session did not test.

## License

The header: "License: public (a work of the U.S. government; cite "U.S. Energy Information Administration, State Energy Data System")." `license_verdicts.csv` gives EIA "may be public" (read 1; the same if the ERW sells anything), and `docs/licenses.md` gives the ERW verdict public. `coverage.csv`: public. Session 2108's report holds the table in the live set's catalogue hold and the release's storage hold.

## Found while writing this note

- Every row's `retrieved_at` is 2026-10-23T21:41:12Z, the write run's clock (`retrieved` is set when the run starts), but the write run made no request: EIA answered the pages from 21:38:44Z to 21:39:01Z in the trial run, and the write run reused them. The rows therefore name a retrieval time at which nothing was retrieved; `iso_prices.raw_cached`, used by the other connectors, keeps the first download's time for this reason.
- The docstring's "a 429 or a 5xx asked once more after 60 seconds" is what the code does, but after the second failure it also waits 60 seconds more before it stops.
**Acted on in session 2116:** each page's rows now carry the time EIA answered that page (a reused page, its first download's: 21:38:44Z to 21:39:01Z on 23 October 2026, not the write's clock), and a second failure stops the run without another wait; the table was written again offline with those times.

## What it does not hold

- All sectors' expenditures and consumption: `eia_seds_state_energy` holds those series (ESTCV, TETCV); this table does not repeat them.
- The commercial, industrial and transportation sectors, and the residential sector's consumption by source.
- Years before 1990, and real (inflation-adjusted) dollars.
- Spending by income, tenure or building (DOE's LEAD Tool, left for a later chain by session 2108).
