# EIA's daily NYMEX futures prices, contracts 1 to 4 of crude oil, heating oil, RBOB gasoline and natural gas, trading days from 1 January 2019 to 5 April 2024

Energy Research Warehouse (ERW), method note written in session 2298 (chain 105) for a table first written on 5 October 2026 (session 127, `archive/sessions/SESSION_127_REPORT.md`, "the price board, to finished", an approved pull of EIA's spot and futures series; commit `f58fb14f`). Session 127's own note, `docs/methods/price_board_v4.md`, quotes EIA's terms and the notices on these series ("The pull, and what EIA does and does not publish", "EIA's terms, quoted"); they are cited here, not repeated. EIA's spot prices of the same commodities are `eia_fuel_spot_prices` and `eia_product_spot_prices` (`docs/methods/eia_fuel_spot_prices.md`, `docs/methods/eia_product_spot_prices.md`).

Tables: `eia_all_futures_prices`

## Publisher and address

U.S. Energy Information Administration (EIA), republishing the New York Mercantile Exchange's (NYMEX, CME Group) daily settlement prices, through EIA's API v2, frequency daily, from 2019-01-01, sorted by period, paged by 5,000, one series a request:

- `eia:nymex_futures_petroleum`: route `petroleum/pri/fut` (`https://api.eia.gov/v2/petroleum/pri/fut/data/`), EIA's page `https://www.eia.gov/dnav/pet/pet_pri_fut_s1_d.htm`, "NYMEX Futures Prices, crude oil and petroleum products, daily (ends 5 April 2024)". Twelve series: `RCLC1` to `RCLC4` (crude oil, Cushing, Oklahoma), `EER_EPD2F_PE1_Y35NY_DPG` to `PE4` (New York Harbor No. 2 heating oil) and `EER_EPMRR_PE1_Y35NY_DPG` to `PE4` (New York Harbor reformulated RBOB regular gasoline).
- `eia:nymex_futures_natural_gas`: route `natural-gas/pri/fut` (`https://api.eia.gov/v2/natural-gas/pri/fut/data/`), EIA's page `https://www.eia.gov/dnav/ng/ng_pri_fut_s1_d.htm`, "Natural Gas Futures Prices (NYMEX), daily (ends 5 April 2024)". Four series, `RNGC1` to `RNGC4` (EIA: "Natural Gas Futures Contract 1 (Dollars per Million Btu)"; the connector places them at Henry Hub, `geo` US-LA).

The key is never stored: every `source_url` is the request without it (16 values, one a series). Raw files: `warehouse/raw/eia_futures/20261005T235403Z/` on this machine, 16 answers (6,921,250 bytes) and a manifest of 32 lines (each answer under its address with the key replaced by `REDACTED` and without it).

Connector: `warehouse/connectors/eia_futures.py` (session 127), ceiling 600,000 rows "(the rows the API returns, the session's probe of 72 rows included)". Each series is read whole; a unit other than the expected one, a date listed twice or a value that is not a number stops the pull; "A date EIA lists with no value is not written. Nothing is filled." Entity `eia:<EIA series>`, `node` the contract (1 to 4). The table is deleted and rebuilt whole from the answers on each run ("a closed history, rebuilt whole from the answers"), and an answer already in the raw files is not asked again.

Schedule: none. The docstring: "The table is a closed history; this connector is not in the daily run, and a rerun finds nothing new unless EIA resumes." No line of `warehouse/run_daily.sh`, `run_data_machine.sh`, `run_data_machine_tables.sh` or `run_monthly.sh`, no workflow in `.github/workflows/` and no step of `warehouse/scheduled.py` names it; `warehouse/refresh_board_v4.sh` (retired with its page in session 271) says "EIA's futures are a closed history (they end on 5 April 2024): warehouse/connectors/eia_futures.py is not run here." `run_status.csv`: no row (a run by hand writes `runs/status/eia_futures.json`, which `warehouse/metadata/run_status.py record` appends only when a scheduled run calls it; disagreement 4). `archive_manifest.csv`: 21,240 rows, run `20261006T181138Z-local` (archived 2026-10-06T18:11:38Z). `redivis_uploads.csv`: the internal dataset's draft (`energy_research_warehouse_internal`), 21,240 rows, 2026-10-05T23:57:52Z. Live set: listed under `catalogue_hold` in `warehouse/supabase/live_set.yaml` with the comment "internal by that session's reading, about 21,000 rows ... Neither is loaded"; it is not in Supabase. Readers: none. No script under `warehouse/`, `site/lib`, `site/app` or `package/` reads its rows; the board, version 4, does not show them ("Nothing on the board shows them", `price_board_v4.md`), and `package/src/erw/data/tables.csv` and `scripts/licenses.py` name it only for its license.

## Vintage and revision

One write: header line 4, "Retrieved: 20261005T235738Z (UTC) by warehouse/connectors/eia_futures.py"; header line 14, "This run wrote 21240 rows: 21240 new ... 0 rows are kept from earlier runs". The answers themselves were fetched by an earlier run that morning, `20261005T235403Z` (the raw folder): `retrieved_at` has 14 values, 2026-10-05T23:54:04Z to 23:54:18Z, and the writing run read them from the raw files (disagreement 3). `vintage` is blank in every row: EIA's API gives no publish time (the raw manifest's `last_modified` is blank for every answer). Header line 3: "EIA's series end on 5 April 2024 ('Futures prices after April 5, 2024, are not available'): the newest day held is 2024-04-05. A closed history, not a current price." Nothing has been written since; the archive and the Redivis draft hold the same rows.

The copy on this machine was restored from the Redivis draft by `scripts/sync.py` (header line 15). Its rows are not in key order (it begins with `eia:RNGC1` on 2023-02-28, then 2022-08-18), so its data hash as it lies, `7422efee...`, is not the archive manifest's `9839c2a3...`; put in (entity, variable, ts_utc) order, the same lines give `9839c2a3...` exactly (disagreement 5).

## Shape and variables

Series, 21,240 rows, 13 columns (`entity, variable, ts_utc, value, unit, freq, geo, market, node, source, source_url, retrieved_at, vintage`), 15 header lines. One variable, `futures_price`; `freq` P1D, `market` nymex and `vintage` blank in every row. `node` 1 to 4, 5,310 rows each. Units: USD/bbl (crude oil, 5,320 rows, `geo` US-OK), USD/gal (heating oil and gasoline, 10,600 rows, US-NY), USD/MMBtu (natural gas, 5,320 rows, US-LA). Values are EIA's strings unchanged: 14,320 with three decimals, 6,239 with two, 681 with one (a trailing zero is not written).

| Series | Contract | Rows | First day | Mean | Lowest (day) | Highest (day) |
|---|---|---|---|---|---|---|
| `eia:RCLC1` crude oil, USD/bbl | 1 | 1,330 | 2019-01-01 | 67.69 | -37.63 (2020-04-20) | 123.70 (2022-03-08) |
| `eia:RCLC2` | 2 | 1,330 | 2019-01-01 | 67.53 | 11.57 (2020-04-21) | 119.78 (2022-06-08) |
| `eia:RCLC3` | 3 | 1,330 | 2019-01-01 | 67.21 | 18.69 (2020-04-21) | 117.15 (2022-06-08) |
| `eia:RCLC4` | 4 | 1,330 | 2019-01-01 | 66.80 | 21.61 (2020-04-21) | 114.57 (2022-06-08) |
| `eia:EER_EPD2F_PE1_Y35NY_DPG` heating oil, USD/gal | 1 | 1,325 | 2019-01-02 | 2.341 | 0.610 (2020-04-27) | 5.135 (2022-04-28) |
| `eia:EER_EPD2F_PE2_Y35NY_DPG` | 2 | 1,325 | 2019-01-02 | 2.306 | 0.704 (2020-04-27) | 4.418 (2022-06-16) |
| `eia:EER_EPD2F_PE3_Y35NY_DPG` | 3 | 1,325 | 2019-01-02 | 2.279 | 0.773 (2020-04-27) | 4.302 (2022-06-16) |
| `eia:EER_EPD2F_PE4_Y35NY_DPG` | 4 | 1,325 | 2019-01-02 | 2.257 | 0.833 (2020-04-28) | 4.203 (2022-06-16) |
| `eia:EER_EPMRR_PE1_Y35NY_DPG` RBOB gasoline, USD/gal | 1 | 1,325 | 2019-01-02 | 2.110 | 0.412 (2020-03-23) | 4.276 (2022-06-09) |
| `eia:EER_EPMRR_PE2_Y35NY_DPG` | 2 | 1,325 | 2019-01-02 | 2.086 | 0.495 (2020-03-23) | 4.084 (2022-06-09) |
| `eia:EER_EPMRR_PE3_Y35NY_DPG` | 3 | 1,325 | 2019-01-02 | 2.063 | 0.548 (2020-03-23) | 3.892 (2022-06-09) |
| `eia:EER_EPMRR_PE4_Y35NY_DPG` | 4 | 1,325 | 2019-01-02 | 2.041 | 0.597 (2020-03-23) | 3.607 (2022-06-09) |
| `eia:RNGC1` natural gas, USD/MMBtu | 1 | 1,330 | 2019-01-01 | 3.436 | 1.482 (2020-06-25) | 9.680 (2022-08-22) |
| `eia:RNGC2` | 2 | 1,330 | 2019-01-01 | 3.498 | 1.544 (2020-06-26) | 9.647 (2022-08-22) |
| `eia:RNGC3` | 3 | 1,330 | 2019-01-01 | 3.555 | 1.605 (2020-06-26) | 9.710 (2022-08-22) |
| `eia:RNGC4` | 4 | 1,330 | 2019-01-01 | 3.592 | 1.725 (2020-06-26) | 9.810 (2022-08-22) |

Every series ends on 2024-04-05. Means are over each series' own days.

- **The one negative price** is crude oil contract 1 on 2020-04-20, -37.63 USD/bbl; contracts 2 to 4 that day were 20.43, 26.28 and 28.51, and contract 1 was 10.01 the next day.
- **A contract is a place in the curve, not a delivery month.** Contract 1 is "the earliest delivery month, as EIA defines it" (the docstring), so it moves to the next month when a contract expires; no row says which month it prices.
- **The curve.** Contract 1 is below contract 2 on 640 of 1,330 days for crude oil, 930 of 1,330 for natural gas, 460 of 1,325 for heating oil and 405 of 1,325 for gasoline.
- **"No. 2 heating oil" is EIA's name** ("New York Harbor No. 2 Heating Oil Future Contract 1", the raw answers). Its contract 1 follows EIA's New York Harbor ultra-low sulfur diesel spot price (`eia:EER_EPD2DXL0_PF4_Y35NY_DPG`) far more closely than EIA's No. 2 heating oil spot price: over 1,318 shared days, within 1 percent on 999 days (median absolute gap 0.008 USD/gal) against 133 days (0.09) (disagreement 2).
- Rows a year: 4,124 (2019), 4,032, 4,012, 4,016, 4,000 and 1,056 (2024, to 5 April).

## Placing values in time, and what is filled

`ts_utc` is the trading day at 00:00:00Z, a label for EIA's date, not an instant (header line 2). 1,331 days, all Monday to Friday; all 16 series on 1,324 of them. Nothing is filled by the ERW, and EIA listed no date without a value (header line 12: "Dates EIA lists with no value, not written: 0").

- **Days EIA leaves out:** crude oil and the two products on 2019-11-29 (natural gas only, 4 series; EIA's WTI spot price has that day), and natural gas on 2021-10-11 (12 series; EIA's Henry Hub spot price has that day).
- **Rows on holidays, in 2019 only.** Nine days that are US federal holidays or Good Friday are held: 2019-01-01, 01-21, 02-18, 04-19, 05-27, 07-04, 09-02, 11-28 and 12-25, with crude oil and natural gas on all nine and the two products on four (02-18, 05-27, 07-04, 09-02). Every value on them equals the previous business day's, except on 2 September 2019, where six product contracts each equal the next contract's value of 30 August (contract 1 having expired); 2019-01-01 is the first day held, with nothing before it. They are carried prices, not a settlement of that day (disagreement 1). No federal holiday from 2020 to 2024 is held, which is why 2019 has 261 days against 250 to 252 in the full years after.

## License

Header line 13: "License: internal, by session 127's reading, for a person to rule. EIA names the New York Mercantile Exchange as the source of these prices and stopped republishing them on 5 April 2024; its reuse policy says items licensed by companies 'may be protected'. Nothing on EIA's pages forbids republishing them in so many words." `coverage.csv` and `sources.csv`: internal. `warehouse/metadata/license_tables.csv` names two publishers, "CME Group (NYMEX), whose prices EIA republished; EIA", "by hand: its header: EIA names the New York Mercantile Exchange as the source of these prices".

**What the verdicts say about CME Group's prices: nothing yet, because CME Group's page has never been read.** `license_verdicts.csv` has no CME Group row. `license_reads.csv` has two attempts, both unread: #49, `https://www.cmegroup.com/tools-information/cme-website-terms-of-use.html`, 2026-10-19T12:06:40Z, "not read: ConnectionError"; and #93, `https://www.cmegroup.com/robots.txt`, 2026-10-23T02:12:33Z, "not read: the connection was reset by the host, not asked again (session 859)". EIA's verdict (read 1, "may be public") carries the note "Items others contributed to EIA's site (NYMEX futures, ICE hub prices) are their owners'", so EIA's public-domain sentence does not settle these rows. `docs/licenses.md`, the table's row: verdict today "not settled (needs written permission by default)", not read: CME Group (NYMEX), flag internal, flag and verdict "not settled", if the ERW sells anything "may be public" (disagreement 6), ERW verdict internal; and under "Not settled: a publisher was not read": "`eia_all_futures_prices` (flag internal): not read: CME Group (NYMEX), whose prices EIA republished." `docs/state/unsettled_licenses_2026-10-19.md` drafts the question for Samuel to send or not: "May the Energy Research Warehouse republish the NYMEX settlement prices that EIA republishes in its futures series, with CME Group credited, for noncommercial research?" No row in `license_status.csv`. The package says: "The ERW holds it for its own use only (not settled (needs written permission by default)); it is never redistributed."

## Checks (session 2298)

The figures in this note were computed from the rows of `warehouse/output/eia_all_futures_prices.csv` in the main checkout, read past its 15 header lines (counted, never parsed as comments), by `runs/c105/s2298/check_eia_all_futures_prices.py`, `check_eia_all_futures_prices_2.py` and `check_eia_all_futures_prices_3.py` (outputs beside them, `.out`). No request was made.

- 21,240 rows and 2019-01-01 to 2024-04-05, as header line 14 states; no (entity, variable, ts_utc) twice; no blank value; every `ts_utc` a midnight; one unit a series, as `SERIES` in the connector gives it; no `source_url` holds a key.
- **Against EIA's own answers** (the 16 raw files of session 127): each answer's `total` equals the rows it holds (1,330 for crude oil and natural gas, 1,325 for the products), 21,240 in all; every row of the table is in them with the same value, and no row of theirs is missing from the table; none had a blank value. With session 127's probe of 72 rows, that is header line 12's "21,312".
- **Against EIA's spot prices** (`eia_fuel_spot_prices`, `eia_product_spot_prices`; Refinitiv's, as EIA notes, not NYMEX's), contract 1 on the same day:

| Futures | Spot | Days in both | Within 1 percent | Within 5 percent | Median futures less spot | Largest gap |
|---|---|---|---|---|---|---|
| crude oil (`RCLC1`) | WTI Cushing | 1,319 | 1,219 (76 equal) | 1,309 | 0.00 | 6.03 on 2020-03-27 (21.51 against 15.48) |
| natural gas (`RNGC1`) | Henry Hub | 1,322 | 240 | 900 | 0.02 | -20.641 on 2021-02-17 (3.219 against 23.86) |
| heating oil (`EER_EPD2F_PE1`) | NY Harbor ULSD | 1,318 | 999 | 1,263 | -0.002 | not computed |
| heating oil (`EER_EPD2F_PE1`) | NY Harbor No. 2 heating oil | 1,318 | 133 | 730 | 0.08 | -1.244 on 2022-05-16 |
| RBOB gasoline (`EER_EPMRR_PE1`) | NY Harbor conventional regular gasoline (not RBOB) | 1,318 | 201 | 980 | -0.036 | -0.506 on 2022-11-07 |

  Contract 1 and WTI's spot price are mostly within 1 percent; Henry Hub's spot price parts from contract 1 on days it spikes (2021-02-17). The spot tables run on to 2026-10-20; the futures stop at 2024-04-05.

## Where the description and the data disagree

1. **"The official daily closing price ... per trading day."** The docstring and header line 2 describe every row as NYMEX's official closing price of a trading day. Nine 2019 days that are federal holidays or Good Friday carry the previous business day's values (rolled by one contract on 2 September 2019), so they are EIA's carried rows, not settlements.
2. **"No. 2 heating oil."** The docstring and the header's `Series:` line call contracts `EER_EPD2F_PE1` to `PE4` "No. 2 heating oil, New York Harbor", as EIA names them; their prices follow EIA's New York Harbor ultra-low sulfur diesel spot (within 1 percent on 999 of 1,318 days), not its No. 2 heating oil spot (133).
3. **"Retrieved: 20261005T235738Z."** Header line 4 names the run that wrote the file; no request was made in it. The rows were fetched from 23:54:04 to 23:54:18Z by run `20261005T235403Z`, whose raw folder holds them, and `retrieved_at` says so.
4. **No record of the run.** `CLAUDE.md` describes `run_status.csv` as "every run and every gap"; it holds no row of `eia_futures`, because a run by hand writes only `runs/status/eia_futures.json` (not on this machine).
5. **The archive's hash and the file here.** `archive_manifest.csv` gives `data_sha256` `9839c2a3...`; the copy `scripts/sync.py` restored from the Redivis draft hashes `7422efee...` because its rows are in another order. The rows are the same.
6. **"If the ERW sells anything: may be public."** `docs/licenses.md` gives that for a table whose verdict today is "not settled" because CME Group was never read; the commercial column takes EIA's verdict alone.
7. **`catalogue_hold` is described as public tables.** Its comment in `live_set.yaml` reads "public tables held out of the live catalogue ... while the live site is frozen"; this table is internal and is listed there only so that it is not loaded.

Not acted on: this note changes no file but itself.

## The session report against the table

`SESSION_127_REPORT.md`: "`eia_all_futures_prices` | 21,240 | internal | pass | done (internal dataset's draft, 21,240 counted)": holds (21,240 rows, the internal draft in `redivis_uploads.csv`). "Its pages say 'Futures prices after April 5, 2024, are not available', and the API's newest day for all sixteen contracts is that day": holds, every series ends on 2024-04-05. "I pulled the sixteen from 2019 (21,240 rows, a closed history)": holds; the products begin on 2019-01-02, crude oil and natural gas on 2019-01-01 (a holiday row). "Neither table is loaded into Supabase": holds. "I marked the futures internal, on a reading, not on words": the table is still internal, and the ruling the report asked for has not been recorded (no `license_status.csv` row).

## What it does not hold

- Any price after 5 April 2024 (CME Group's, not free; `price_board_v4.md`, "What is named in the plan and not held"); contracts beyond the fourth; the delivery month each contract prices, expiry dates, volume or open interest.
- EIA's other futures series (propane, and the regular gasoline contract RBOB replaced, which the docstring says ended in 2009 and 2006); days before 2019; any exchange but NYMEX (no ICE Brent).
- Crude oil and products on 2019-11-29, natural gas on 2021-10-11.
- Spot prices (`eia_fuel_spot_prices`, `eia_product_spot_prices`).
