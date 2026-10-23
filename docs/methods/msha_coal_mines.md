# Coal mines, and each coal mine's production, hours and employees a quarter (MSHA's open government data)

Energy Research Warehouse (ERW), method note written in session 2038 (chain 058) for tables first written on 23 October 2026 (session 2034).

Tables: `msha_coal_mines`, `msha_coal_production_quarterly`

## Publisher and address

U.S. Department of Labor, Mine Safety and Health Administration (MSHA), Open Government Data (`https://arlweb.msha.gov/OpenGovernmentData/OGIMSHA.asp`, `PAGE`), two pipe-delimited files (`FILES`), refreshed by MSHA each week:

- `https://arlweb.msha.gov/OpenGovernmentData/DataSets/Mines.zip`, holding `Mines.txt`, one row a mine.
- `https://arlweb.msha.gov/OpenGovernmentData/DataSets/MinesProdQuarterly.zip`, holding `MinesProdQuarterly.txt`, one row a mine, subunit and quarter.

The text is read as Latin-1, and only the columns the connector needs (`NEED`) are kept. Two requests a run (about 62 MB, session 2034: 7.3 MB and 54.7 MB), a pause of 1 second after each, timeout 300 seconds, with the ERW's user agent (`UA`). Source id `msha:open_government_data`. Connector: `warehouse/connectors/msha_mines.py` (session 2034).

## Vintage and revision

Both files on the data machine were written by run `20261023T193441Z` (23 October 2026), as their headers say. `retrieved_at` 2026-10-23T19:29:29Z (mines) and 2026-10-23T19:29:38Z (production); `vintage`, the zips' Last-Modified, 2026-10-23T11:58:31Z and 11:58:32Z.

The zips keep their addresses while MSHA refreshes them each week. Until session 2038 they were asked for without `fresh`, so a later run would have reused the files saved in `warehouse/raw/msha_mines/`; since session 2038 a run that is not `--offline` asks for them again (`fresh=not args.offline`) and takes the week's files. Each run replaces both tables whole (`ip.write_snapshot`). The header: "The newest quarters grow as operators report." No age check is made.

## Shape and variables

`msha_coal_mines`: entities, 35,736 rows, every mine `Mines.txt` marks coal (`COAL_METAL_IND` C), no `entity_id` twice.

- `entity_id` `msha_mine:<MINE_ID>`, the seven digits MSHA writes; 2,064 begin with a zero, which EIA's coal tables drop.
- `entity_type` plant; `name` the current mine name; `operator` the current operator; `geo` US-<state>, 33 states.
- `status` from MSHA's current status, its words in `x_mine_status`:

| `status` | Rows | `x_mine_status` |
|---|---|---|
| active | 705 | Active 577, New Mine 128 |
| suspended | 592 | NonProducing 307, Temporarily Idled 285 |
| retired | 34,439 | Abandoned 25,625, Abandoned and Sealed 8,814 |

- `status_date` the current status date, on every row, 1 January 1925 to 22 October 2026.
- `lat`, `lon` as MSHA gives them, six decimals, on 23,947 rows. A coordinate that is empty, not a number, zero or out of range is left empty, and a mine left with only one of the two has both empty (session 2034 counted six such mines; the table cannot show them).
- `x_mine_type` Surface 17,627, Underground 14,588, Facility 3,413, empty 108; `x_controller`, `x_county_fips`, `x_county`, `x_district`, `x_primary_sic`, `x_employees` and `x_nearest_town` as published. `capacity_mw` empty.
- The active mines by state, the most: West Virginia 212, Pennsylvania 181, Kentucky 108, Virginia 55, Illinois 33, Wyoming 19.

`msha_coal_production_quarterly`: series, 294,323 rows, 3,378 mines, 66 quarters, the first quarter of 2010 to the second quarter of 2026. A mine's quarter is its subunits summed (`x_subunits`, 1 to 4).

| Variable | Unit | Rows | What |
|---|---|---|---|
| `coal_production` | short_ton | 98,107 | MSHA's tons |
| `employee_hours` | count | 98,108 | the hours the operator reports its employees worked |
| `average_employees` | count | 98,108 | the subunits' average employees, summed |

`ts_utc` the calendar quarter's first day; `freq` P3M; `geo` US-<state>, 27 states; `node` the mine's name (the last a quarter's rows give); `market` empty; `x_production_blank` the subunits whose production MSHA leaves empty. Values are rounded to two decimals. Hours are a `count`, since the unit `hour` is an hour of the day (Decision 29).

Mines with a production row a quarter: 1,007 in the first quarter of 2025, 950 in the second quarter of 2026.

## Reading the source

- A zip without its file, or a file without its columns, stops the run.
- Mines: a mine given twice, a status not in `STATUS`, a state not a two-letter code, or a status date not MM/DD/YYYY stops the run. Mines that are not coal are not taken.
- Production: only rows marked coal; a year or quarter not a number, or a quarter outside 1 to 4, stops the run (checked before the years before `--from-year`, default 2010, are dropped). In the years taken, an employee, hours or production cell that is neither empty nor a number stops it.
- A mine and quarter whose production every subunit leaves empty has no `coal_production` row (one here: 98,108 hours rows against 98,107 production rows). Where only some leave it empty, the others are summed and the empty ones counted in `x_production_blank` (37 rows). The header counts 65 subunit quarters with production empty. Hours and employees have a row where at least one subunit gives a figure. Nothing is filled.
- A mine, variable and quarter given twice stops the run.
- Each request is tried up to 4 times (`iso_prices.with_retries`), waiting 5 seconds times the attempt number after each failure; HTTP 404 is a `SourceGap`, not retried; any answer but HTTP 200 is a failure.
- Ceiling: two requests (the two zips). No row ceiling is set in the code.
- A failure is recorded for both tables, and neither file is written.
- The connector does not call `iso_prices.paused()`; MSHA is not in `warehouse/metadata/paused_sources.csv`.

## License

Public. `sources.csv` has `public` for `msha:open_government_data`, naming both tables; the headers: "License: public (a work of the U.S. Department of Labor; cite "Mine Safety and Health Administration, Open Government Data")." `license_verdicts.csv`, U.S. Department of Labor, Mine Safety and Health Administration (MSHA), read 207 (the Department of Labor's Copyright page, `https://www.dol.gov/general/aboutdol/copyright`, read 23 October 2026): "Materials created by the federal government are generally part of the public domain and may be used, reproduced and distributed without permission. Therefore, content on this website which is in the public domain may be used without the prior permission of the U.S. Department of Labor (DOL)." Verdict: may be public, and may be public for commercial use. Its note: credit is asked to the U.S. Department of Labor; the data files carry no notice of others' copyright.

Robots: read 205, `arlweb.msha.gov` has no robots file (HTTP 404); read 206, `www.dol.gov`'s file disallows only site machinery, admin, user and search paths (session 2034).

## Cross-checks (session 2038)

- The counts above were computed from the rows, read past the header lines; no `entity_id`, and no (entity, variable, ts_utc), appears twice.
- Session 2034's cross-check, recomputed against `eia_coal_mine_production_annual` (EIA's `production`, short tons): MSHA's `coal_production` summed to the year is within 0.21 percent of EIA's every year from 2010 to 2024, the widest 2022 (595.379 against 594.155 million short tons, 0.206 percent) and 2010 (1,086.386 against 1,084.368, 0.186 percent); 2024 512.548 against 512.540. In 2024 all 773 mines in EIA's table are in MSHA's; 772 are within 5 percent of EIA's figure, and all 76 over a million tons. 1,150 mines have a row in MSHA's 2024 quarters.
- 12 mines of the production table are not in `msha_coal_mines` (among them `msha_mine:1519602` and `msha_mine:4003525`): their quarterly rows are marked coal, and the mines table takes only the mines `Mines.txt` marks coal.

## What it does not hold

- Metal and non-metal mines.
- Quarters before 2010; `--from-year` takes earlier ones.
- A subunit's quarter: subunits are summed.
- A mine's past names, operators and statuses: `Mines.txt` gives the current ones.
- MSHA's other files on its Open Government Data page.
- EIA's yearly figures by mine: `eia_coal_mine_production_annual`.
