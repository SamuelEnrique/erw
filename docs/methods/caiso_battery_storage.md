# Battery storage output, every 5 minutes, in all and stand-alone and hybrid (CAISO Today's Outlook)

Energy Research Warehouse (ERW), method note written in session 2060 (chain 066) for a table first written on 28 September 2026 (session 23).

Tables: `caiso_battery_storage`

## Publisher and address

California Independent System Operator (CAISO), Today's Outlook, the batteries trend (`https://www.caiso.com/todays-outlook/supply`), read from its public history file for each Pacific day:

`https://www.caiso.com/outlook/history/<YYYYMMDD>/storage.csv`

The connector reads the file's columns "Time", "Total batteries", "Stand-alone batteries" and "Hybrid batteries". Source id `caiso:todays_outlook_storage`. Connector: `warehouse/connectors/caiso_outlook.py` (session 23, for the Automated Analysis template storage_evening_peak), its only table. EIA-930 returns no battery rows (`warehouse/connectors/eia930_storage.py`), so this is CAISO's own figure. The daily run (`warehouse/run_daily.sh`) runs it with its default, the last 30 complete Pacific days.

## Vintage and revision

24 August 2025 to 22 October 2026 (Pacific days; 24 August 2025 07:00 UTC to 23 October 2026 06:55 UTC) in the file on the data machine, rebuilt from the ERW archive by `warehouse/restore_tables.py` as of run `20261023T152740Z-github`, from the connector's run `20261023T144753Z`. Its header: "This run wrote 25920 rows: 864 new, 25056 replacing earlier rows". `coverage.csv` gives the same 365,472 rows and dates. The rows' `retrieved_at` begin on 28 September 2026 (317,952 rows; session 23's report: "backfilled to 2025-08-24"); the rest are spread over the daily runs since.

Each run asks CAISO again for each of the last 30 complete Pacific days (no raw file is reused; each run's requests are saved under `warehouse/raw/caiso_outlook/<run_id>/`), and `ip.write_csv` merges them into the file on (entity, variable, ts_utc): an interval read again replaces the held one, so CAISO's changes within 30 days are taken, and older intervals are kept as they were.

## Shape and variables

Series, 365,472 rows: one entity, 3 variables of 121,824 intervals each (423 Pacific days). `entity` `caiso:ISO`; `unit` MW, whole numbers; positive is discharge to the grid, negative is charging, as CAISO publishes them; `freq` PT5M; `ts_utc` the interval's start, the file's Pacific clock time converted to UTC; `geo` US-CA; `market`, `node` and `vintage` empty; `source_url` the day's file, whose date is the interval's Pacific day in every row.

| Variable | CAISO's column | Mean MW | Lowest | Highest |
|---|---|---|---|---|
| `batteries_mw` | Total batteries | -274.9 | -11,838 (6 October 2026, 16:40 UTC) | 13,441 (19 August 2026, 03:10 UTC) |
| `standalone_batteries_mw` | Stand-alone batteries | -250.9 | -11,080 | 12,503 |
| `hybrid_batteries_mw` | Hybrid batteries | -23.6 | -1,078 | 1,102 |

From the total, a day discharged 42,209 MWh and charged 48,806 MWh on average over the 423 days (discharge over charge: median 0.871); the monthly mean of discharge rose from 36,235 MWh in August 2025 to 47,579 in August 2026.

## Reading the history files

- A request is tried up to four times (5, 10 and 15 seconds apart); any answer but HTTP 200 counts as a failure, an HTTP 404 included. A day whose request still fails is skipped and named in the header; the run goes on.
- The file must hold "Time" and the three battery columns, or the day is skipped.
- The time is read as a Pacific clock time on the day of the file and placed in UTC with the clock change inferred from the order of the rows (`ambiguous="infer"`); a file whose time cannot be read that way is read as full timestamps.
- A row with an empty battery value is dropped. A day is written only with every 5-minute interval of the Pacific day (288; 276 or 300 on the clock-change days) and no interval twice; a day short of that is skipped, logged and named in the header.
- No day complete stops the run, and nothing is written. No ceiling and no test of the newest day's age. No pause between requests. The connector does not consult `warehouse/metadata/paused_sources.csv` (CAISO is not on it).

## License

The header: "License: public (CAISO public system data; cite "California ISO, Today's Outlook")." `coverage.csv`: public. `license_tables.csv` names CAISO as the table's one publisher (from the source registry); `license_verdicts.csv` gives CAISO "may be public" (read 3 of `license_reads.csv`, 12 October 2026), with the note that the same page's API terms forbid use "for any other benchmarking or competitive purposes". `docs/licenses.md`: ERW verdict public.

## Cross-checks (session 2060)

- The counts above were computed from the rows, read past the 11 header lines; no (entity, variable, ts_utc) is given twice, and consecutive intervals are 5 minutes apart within the days held.
- Days complete: each of the 423 days holds 288 intervals for each variable. Of the 425 calendar days from 24 August 2025 to 22 October 2026, the two missing are the two clock-change days, 2 November 2025 and 8 March 2026; session 23's report: "the two clock-change days are not written, under the complete-day rule". The rule as the code writes it would take 300 and 276 intervals on those days; the rows hold neither day.
- The two parts do not sum to the total as CAISO publishes them: total less stand-alone less hybrid is 0 MW in 3,180 of 121,824 intervals and within 2 MW in 14,931; its middle half lies between -13 and 14 MW, its mean is -0.3 MW, and it reaches 1,182 MW (27 August 2026, 16:15 UTC). The connector writes the three columns as given and does not compare them.
- The connector has no cross-check of its own beyond its reading rules.

## What it does not hold

- State of charge, capacity and any figure by plant or by owner.
- The other trends of Today's Outlook (demand, supply by fuel, emissions).
- Days before 24 August 2025, and the two clock-change days 2 November 2025 and 8 March 2026.
- Batteries of other balancing areas: EIA-930 carries none (`eia930_storage.py`).
