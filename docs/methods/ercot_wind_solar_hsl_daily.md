# ERCOT wind and solar output, High Sustained Limit and output below it, system-wide, a day, from 19 September 2026 (ERCOT NP4-732-CD and report type 13483)

Energy Research Warehouse (ERW), method note written in session 2256 (chain 102) for a table first written on 27 September 2026 (session 18).

Tables: `ercot_wind_solar_hsl_daily`

## Publisher and address

Electric Reliability Council of Texas (ERCOT), two hourly reports on its public reports site, each posted once an hour and holding the 48 hours behind it (and forecasts ahead, not read); ERCOT's list keeps about a week of postings:

- NP4-732-CD, "Wind Power Production, Hourly Averaged Actual and Forecasted Values" (report type 13028).
- Report type 13483, which the connector names NP4-745-CD. ERCOT's own list names its files `PVGRHRLYAVGACTNP4737`: it is NP4-737-CD, "Solar Power Production, Hourly Averaged Actual and Forecasted Values" (`docs/methods/ercot_wind_solar_forecast.md`, and the correction in `docs/methods/curtailment.md`). NP4-745-CD is the solar report by region (report type 21809), which `ercot_wind_solar_hsl_hourly` reads.

`https://www.ercot.com/misapp/servlets/IceDocListJsonWS?reportTypeId=<13028 or 13483>` (the document list, JSON)

`https://www.ercot.com/misdownload/servlets/mirDownload?doclookupId=<DocID>` (each posting, a zip of one CSV)

Columns read: DELIVERY_DATE, HOUR_ENDING, DSTFlag, SYSTEM_WIDE_GEN (or GEN_SYSTEM_WIDE) and SYSTEM_WIDE_HSL. The User-Agent is "Mozilla/5.0 (compatible; ERW-curtailment/0.1; +https://github.com/SamuelEnrique/erw)". Every request goes to the host `www.ercot.com`, under `/misapp/` and `/misdownload/`, paths ERCOT's robots file disallows (read 170 of `warehouse/metadata/license_reads.csv`, session 2002, 23 October 2026 at 15:11:50 UTC). Whether the ERW keeps reading these paths is a standing question for the owner.

Source id `ercot:np4_732_745`. Connector: `warehouse/connectors/curtailment.py` (session 18), which also writes `caiso_curtailment_daily` and `spp_curtailment_daily`, each as its own stage; `warehouse/connectors/ercot_wind_solar_history.py` reads this table only for its `--check`. Read by `warehouse/derived/iso_curtailment_monthly.py` (`iso_curtailment_monthly`) and by `/curtailment` (in review; `site/lib/curtailment.ts`, entity `ercot:system`). Method: `docs/methods/curtailment.md` ("ERCOT").

Schedule: `warehouse/run_daily.sh` runs the connector every day (`pull curtailment`, under a pull budget of 15 minutes, `warehouse/pull_budget.py`), and `.github/workflows/daily-prices.yml` runs `run_daily.sh` on GitHub's runner; the runner restores this table first from the Redivis draft (`warehouse/redivis/config.yaml`) and the run merges the new days into it. `warehouse/metadata/run_status.csv` holds 24 runs for the table, all ok: the first `20260927T181734Z` (GitHub), the last `20261023T144531Z` (GitHub), one local (`20260929T010905Z`); none on 2 and 3 October, nor from 15 to 19 October 2026.

The first date is from session 18's report ("run 2026-09-27 (UTC)"), from the earliest `retrieved_at` in the rows, 2026-09-27T08:30:58Z, and from the commit that first adds the table's coverage row, `5c07c232`, 27 September 2026 at 10:15 UTC ("Session 18 Task 4").

## Vintage and revision

Operating days 19 September to 22 October 2026, in the file on the data machine, rebuilt from the ERW archive by `warehouse/restore_tables.py` as of run `20261023T152740Z-github`, with the header of the connector's run `20261023T144531Z` ("4 fuel-days were not complete in this run"). `retrieved_at` keeps the time each day's rows were first archived: 36 rows on 27 September 2026, then 6 or 12 rows on each of 20 later days to 23 October. `vintage` is empty. `coverage.csv` gives the same 198 rows, 2026-09-19T00:00:00Z to 2026-10-22T00:00:00Z, last run 2026-10-23T14:45:31Z; `archive_manifest.csv` holds 198 rows.

A daily run reads, for each fuel, the last posting of each of the last three publish days (`--history`: every publish day listed). The newest posting that holds an hour gives its value, and `ip.write_csv` merges the days into the table held on (entity, variable, ts_utc): a day read again replaces the one held, and days ERCOT's list has dropped are kept. Because a run reads only three publish days, a lapse of more than about two days loses days for good even while ERCOT still lists them: there was no run from 15 to 19 October 2026, and 15 October is missing for both fuels (`ercot_wind_solar_hsl_hourly`, which reads every saved posting, holds it).

## Shape and variables

Series, 198 rows: one entity, `ercot:system`, six variables, 33 days each. `unit` MWh; `freq` P1D; `ts_utc` the ERCOT operating day (Central) at 00:00:00Z; `geo` US-TX; `market` and `node` empty; `source_url` the posting the day's hours came from (33 addresses); values rounded to three decimals.

| `variable` | What it is | Mean | Lowest | Highest | Sum over 33 days |
|---|---|---|---|---|---|
| wind_generation_mwh | the sum of the day's hourly system-wide GEN | 262,819.0 | 94,658.82 (8 October) | 572,167.27 (11 October) | 8,673,026.2 |
| wind_hsl_mwh | the sum of the day's hourly SYSTEM_WIDE_HSL | 280,285.2 | 99,076.67 (8 October) | 653,022.27 (16 October) | 9,249,411.6 |
| wind_below_hsl_mwh | the sum over hours of max(0, HSL - GEN) | 17,591.8 | 3,531.99 (3 October) | 96,403.37 (16 October) | 580,529.2 |
| solar_generation_mwh | as for wind | 230,018.1 | 101,820.15 (2 October) | 291,862.89 (7 October) | 7,590,598.2 |
| solar_hsl_mwh | as for wind | 237,750.8 | 102,514.36 (2 October) | 297,207.21 (10 October) | 7,845,777.2 |
| solar_below_hsl_mwh | as for wind | 11,498.1 | 2,984.36 (2 October) | 61,830.96 (11 October) | 379,438.6 |

All dates are in 2026. Over the 33 days, output below the limit is 6.28 percent of the wind limit and 4.84 percent of the solar limit. An hour with output above the limit adds nothing, so a day's figure below the limit is more than its limit less its output on 14 of the 33 wind days and on every solar day: solar output runs above the limit in the morning hours (`docs/methods/curtailment.md`).

Days held: 19 September to 22 October 2026 but 15 October (33 of 34). The counts in this note were computed in session 2256 with pandas from the rows of `warehouse/output/ercot_wind_solar_hsl_daily.csv` on the data machine, read past its 8 header lines; no (entity, variable, ts_utc) is given twice.

## Checks the connector makes

- No pause check: `curtailment.py` does not call `iso_prices.paused()` or `paused_host()` before its requests, for ERCOT or for its other two publishers. ERCOT is not paused.
- Each list and posting is asked through `ip.with_retries`: up to four tries, 5, 10 and 15 seconds apart; any answer but HTTP 200 is an error and is retried, with no retry once the pull budget has passed. 0.3 seconds after each posting. No ceiling of rows or requests: two lists and six postings a daily run; with `--history`, one posting for each publish day listed.
- Only postings whose name ends `_csv` are read. A posting without a system-wide GEN column (SYSTEM_WIDE_GEN or GEN_SYSTEM_WIDE) or SYSTEM_WIDE_HSL stops the table.
- An hour with GEN or HSL blank is skipped; a value that is not a number stops the table. An hour is keyed by its delivery date, hour ending and DSTFlag, so the repeated autumn hour is a 25th hour.
- A day is written only when every hour of the Central day (23, 24 or 25) has GEN and HSL; the days not whole are counted in the header and logged. No day whole stops the table (a source gap).
- A table that fails does not stop the others, and each table's result goes to `run_status.csv`. Every answer is saved under `warehouse/raw/curtailment/<run_id>/`. The write needs the data lock (`ip.write_csv`).

## License

`license_verdicts.csv` gives ERCOT "may be public" (read 2 of `license_reads.csv`; the same if the ERW sells anything): "raw data provided in public portions of this website may be used, reproduced, and redistributed in compilations, charts, and analyses without maintaining such notices." The header has no license line. `license_tables.csv` names ERCOT as the one publisher, from the source registry; `docs/licenses.md` gives the ERW verdict public; `coverage.csv`: public. `warehouse/supabase/live_set.yaml` loads the table with a window of 100 days (session 18).

## Cross-checks (session 2256)

- Against `ercot_wind_solar_hsl_hourly` (ERCOT's reports by region), its system-wide hours summed by Central day: over the 24 whole days both hold (28 September to 22 October 2026 but 15 October), the 144 day-figures agree to within 0.12 MWh (wind below the limit, 10 October 2026: 19,281.62 here, 19,281.74 from the hours). The two reports print the same hour's output a few hundredths of a MW apart.

## Found while writing this note

- `CLAUDE.md` says every connector that reaches a publisher's servers asks `iso_prices.paused()` first. `curtailment.py` does not, for ERCOT, CAISO or SPP.
- The connector asks `/misapp/` and `/misdownload/` on `www.ercot.com`, paths ERCOT's robots file disallows (read 170, session 2002). Neither its docstring nor the header says so.
- The solar report is named NP4-745-CD in the docstring, `ERCOT_REPORTS`, the header's Source line and product page, the source id `ercot:np4_732_745` and `sources.csv`; report type 13483 is NP4-737-CD. `docs/methods/curtailment.md` corrected its own text in an earlier session; the code and the registry still say NP4-745-CD.
- The docstring says the history "starts when the ERW began reading it" and that ERCOT's list holds about a week. A daily run reads only the last three publish days, so the lapse of 15 to 19 October 2026 lost 15 October for good, though the list still held it on 20 October.
- The header has no license line: `curtailment.py` writes none for any of its three tables. The license is held only in the source registry and the license files.

## What it does not hold

- Hours: `ercot_wind_solar_hsl_hourly` holds them, system-wide and by region, from 28 September 2026.
- Output by region, or a High Sustained Limit by region (ERCOT prints the actual limit system-wide only).
- Curtailment: ERCOT publishes no curtailment figure; output below the limit is the ERW's estimate, not ERCOT's, and part of the solar figure may be the timing of two hourly averages.
- Days before 19 September 2026, and 15 October 2026.
