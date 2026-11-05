# ERCOT storage resources' day-ahead awards by resource and hour (60-Day DAM Disclosure, the ESR file)

Energy Research Warehouse (ERW), method note written in session 2124 (chain 079) for a table first written in session 115 (its oldest rows retrieved on 4 October 2026). The method of the monthly awards built from it is `docs/methods/ercot_storage_dam_awards.md`, which the connector names; this note describes the row-level table.

Tables: `ercot_dam_esr_awards`

## Publisher and address

Electric Reliability Council of Texas (ERCOT), 60-Day DAM Disclosure Reports, EMIL NP3-966-ER, report type 13051: `https://www.ercot.com/mp/data-products/data-product-details?id=NP3-966-ER`; document list `https://www.ercot.com/misapp/servlets/IceDocListJsonWS?reportTypeId=13051`; each zip at `https://www.ercot.com/misdownload/servlets/mirDownload?doclookupId=<DocID>`. ERCOT posts one zip a day for the operating day 60 days before; the table reads one file in it, `60d_DAM_ESR_Data-DD-MMM-YY.csv`. Source id `ercot:NP3-966-ER` (in `sources.csv`, license public, first and last seen 2026-10-05). Zips are kept once, in `warehouse/raw/ercot_60d_dam/zips/` with `manifest.csv`.

Connector: `warehouse/connectors/ercot_dam_esr.py` (session 115). `--pull` reads each operating day's zip (asking ERCOT for one not held) and writes a month at a time to `warehouse/raw/ercot_60d_dam/months/`; `--write` builds the table from those months under the data lock; `--daily` (session 116, the standing pull) asks for the list and at most one zip, the first listed operating day after the last day held, adds its rows to the end of the table, and then runs `warehouse/derived/ercot_storage_dam_awards.py` and `warehouse/derived/ercot_storage_dam_offers.py --days <day>`. Ceilings of the approved pull: 9,000,000 rows and 3 GB of downloads; a daily zip above 60 MB is not asked.

Schedule: `warehouse/run_daily.sh`, soft step `ercot_storage_dam`, runs `warehouse/scheduled.py ercot_storage_dam`, which restores the table and its three derived tables from the ERW's archive when the machine lacks them and runs `ercot_dam_esr.py --daily`. The daily run is `.github/workflows/daily-prices.yml` (its fallback `cron: "0 14 * * *"`). The data machine's `scheduled.py ercot_rtm_node_prices` restores this table as an input (it reads the settlement points). Readers named in `license_tables.csv`: `ercot_storage_dam_awards_monthly`, `ercot_storage_dam_offers_daily`, `ercot_storage_node_basis`.

## Vintage and revision

Header line 1: "Rebuilt from the ERW archive by warehouse/restore_tables.py (session 305), as of run 20261023T152740Z-github (2026-10-23T15:27:40Z)"; the table's own header follows, last retrieved by run `20261023T151606Z`. Each row's `retrieved_at` is when its zip was downloaded (from 2026-10-04T21:33:39Z to 2026-10-23T15:16:10Z) and `vintage` ERCOT's publication time; both take 260 distinct values, one per day.

The month records on the data machine (`warehouse/raw/ercot_60d_dam/months/*.json`) hold 243 days, 2025-12-06 to 2026-08-05, and 1,833,357 rows, none missing; the 17 days from 6 to 22 August 2026 (136,440 rows) were added one a run by the standing pull. A day is never rewritten once held: `--daily` only appends a day after the last one, and `--write` refuses to replace a table that reaches further than its months.

## Shape and variables

Series (Decision 40 of `docs/datastandard.md`), 1,969,797 rows, one per Energy Storage Resource and hour. `entity` `ercot:<Resource Name>` (339 resources); `variable` hsl_mw; `value` the High Sustained Limit for the hour, MW; `unit` MW, `freq` PT1H, `geo` US-TX, `market` ercot_dam; `node` the resource's settlement point (295 distinct); `source_url` the day's zip. The awards and limits are `x_` columns, written as ERCOT prints them:

| Column | ERCOT's column | Blank in |
|---|---|---|
| `x_qse` | QSE (119 distinct) | 0 rows |
| `x_dme` | DME (186 distinct, blank counted) | 1,895 rows |
| `x_resource_status` | Resource Status: ON 1,591,319, OUT 256,525, ONTEST 121,952, ONOS 1 | 0 rows |
| `x_lsl_mw` | LSL (negative: charging) | 0 rows |
| `x_energy_award_mw` | Awarded Quantity (negative: a purchase, charging) | 1,014,719 rows |
| `x_energy_price_usd_per_mwh` | Energy Settlement Point Price at the resource's settlement point | 0 rows |
| `x_regup_award_mw`, `x_regup_mcpc` | RegUp Awarded, RegUp MCPC | 820,935 rows each |
| `x_regdn_award_mw`, `x_regdn_mcpc` | RegDown Awarded, RegDown MCPC | 820,935 rows each |
| `x_rrspfr_award_mw`, `x_rrsffr_award_mw`, `x_rrsufr_award_mw`, `x_rrs_mcpc` | RRSPFR, RRSFFR, RRSUFR Awarded; RRS MCPC | 820,935 rows each |
| `x_ecrs_award_mw`, `x_ecrs_mcpc` | ECRSSD Awarded, ECRS MCPC | 820,935 rows each |
| `x_nonspin_award_mw`, `x_nonspin_mcpc` | NonSpin Awarded, NonSpin MCPC | 820,935 rows each |

MCPCs are USD per MW per hour. Of the energy awards given, 51,116 are negative, 815,207 zero and 88,755 positive. The offer curve columns of ERCOT's file are not kept.

## Placing values in time

- ERCOT gives each row a Delivery Date and an Hour Ending from 1 to 24 in Central prevailing time. The hour's start is the day's local midnight plus (Hour Ending - 1) hours, placed in America/Chicago and converted to UTC; `ts_utc` is the start of the hour. An hour that the clock change would make ambiguous or absent fails the day's check rather than being guessed.
- The span holds one clock change, 8 March 2026: 308 resources have 23 hours that day. No autumn change falls in the span.
- `vintage` is ERCOT's publication of the zip; its Central date is the operating day plus 60 days in every row.

## What is and is not filled

- A day is written only when its file passes every check (one delivery date, the right one; every HSL present; every numeric column a number; hours 1 to 24; no resource and hour twice). A day that fails has no rows and, in the standing pull, a line in `warehouse/metadata/ercot_dam_esr_missing_days.csv` (no such file exists in the main checkout: no day has failed there).
- A blank award stays blank: it is no award, not zero. Values are ERCOT's strings, not re-rounded.

## License

Header: "License: public. ERCOT's terms (https://www.ercot.com/help/terms): "The publicly available contents of this website may be used, reproduced, and redistributed, provided that the contents are not modified and that you maintain all copyright and other notices contained in the contents, including this Agreement. Notwithstanding the foregoing, raw data provided in public portions of this website may be used, reproduced, and redistributed in compilations, charts, and analyses without maintaining such notices."" `license_verdicts.csv` records ERCOT, read 2: "may be public", for public and for commercial use. `docs/licenses.md` lists `ercot_dam_esr_awards` under ERCOT: "may be public", flag public, ERW verdict public.

## Checks (session 2124)

The figures in this note were computed from the rows of `warehouse/output/ercot_dam_esr_awards.csv`, read past its 11 header lines.

- 1,969,797 rows, `ts_utc` from 2025-12-06T06:00:00Z to 2026-08-23T04:00:00Z: operating days 2025-12-06 to 2026-08-22 (Central), 260 days with none absent between them, as the header says ("Operating days held: 260", "File holds 1,969,797 rows").
- No (entity, variable, ts_utc) is given twice. Every zip holds exactly one operating day.
- Resources a day: 244 on the first day (2025-12-06), 335 at most (first on 2026-08-09) and on the last day. Of the 82,091 resource-days, 81,772 have 24 hours, 312 have 23 (308 on 8 March 2026, 4 on 9 March) and 7 have between 9 and 19.
- Consistency of prices: each of the five MCPCs takes one value in each of the 6,239 hours across every resource that carries it; the energy price takes one value for each of the 1,711,009 (settlement point, hour) pairs.
- Consistency of awards: the energy award lies between LSL and HSL (0.01 MW tolerance) in all but 9 rows, all of RRC_WIND_ESR1 and RRC_WIND_ESR2 on 19 May 2026 UTC, where the award passes the HSL by up to 0.9 MW (18.1 against 17.2 at 2026-05-19T02:00:00Z). The upward awards (RegUp, the three RRS, ECRS, NonSpin) and any positive energy award add to more than the HSL in 2,635 rows, for example SHEEPCRK_ESR1 at 2025-12-06T21:00:00Z, 137.7 MW of upward awards against an HSL of 135 while charging 57.3 MW.
- Limits: the HSL is negative in 48 rows (lowest -0.3, ALAMO_ST_ESR1 at 2026-06-06T23:00:00Z); the LSL is positive in 2.
- The seven Ancillary Service award columns are blank together, never some of them: 820,935 rows, spread over every month.

## Where the description and the data disagree

1. **"246 zips."** Header line 6: "246 zips in warehouse/raw/ercot_60d_dam/zips/manifest.csv." The table holds 260 operating days, each from its own zip (260 distinct `source_url`). The standing pull's `append_day` moves the days, the rows, the Retrieved and the Run log lines of the header and leaves the zip count as `--write` wrote it.
2. **Blank prices beside blank awards.** The header says "A blank award is no award and stays blank." In the same 820,935 rows the five MCPC columns are blank too, although every hour has its prices on other rows. Neither the header nor the docstring says the clearing prices are left out where a resource has no award.
3. **5 December 2025.** The docstring's example pulls `--from 2025-12-05` (the day ERCOT began clearing energy and ancillary services together in real time, as `ercot_rt_adders.py` records). The table begins on 2025-12-06; the December month record lists 26 days held and no day missing, so 5 December was never in the written window, and the header's "Days missing between them: 0" does not cover it.

Recorded, not changed in session 2124: the header's zip count is written by the full pull and not by the daily append; the clearing prices blank beside a blank award and the first day are as listed above.

## What it does not hold

- Real-time settlement, deployment energy, contracts, or what any battery earned (header line 4).
- The offer curves of ERCOT's file (`warehouse/derived/ercot_storage_dam_offers.py` reads them from the saved zips), and any resource type but storage.
- Operating days before 2025-12-06 or after the last day the standing pull reached.
