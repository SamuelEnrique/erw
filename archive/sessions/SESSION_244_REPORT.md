# Session 244 report: ERCOT's scarcity signal

13 October 2026, 06:32 to 07:05 UTC, unattended, on lab-desktop (the data machine), the second session of the chain of 12 to 13 October. Branch `task/244-ercot-reserve-adders`. Model spend USD 0: no model call. Pulls: ERCOT only, 22 requests. Writes under the data lock: one new table, its four stores, and its load into the live set.

## Read these first

- **A new table, `ercot_rtm_price_adders`: ERCOT's real-time reserve price adders by hour, from 1 June 2014.** 601,474 rows, eight variables, public (ERCOT's terms, item 5). It is in coverage, the archive, the Redivis draft (nothing released) and the live set.
- **It goes back as far as ERCOT publishes: 1 June 2014, the day the operating reserve demand curve (ORDC) began.** And it ends: **ERCOT's file has no ORDC adder after 4 December 2025.** On 5 December 2025 the file changes form and carries only a reliability deployment adder. The table keeps the two designs as separate variables and splices nothing.
- **Hours with an ORDC adder above zero, by year (Central time):** 2014 (from June) 1,548; 2015 2,463; 2016 1,862; 2017 1,824; 2018 1,899; 2019 2,384; 2020 1,783; 2021 1,564; 2022 2,732; 2023 1,735; 2024 577; 2025 (to 4 December) 267. The full table, with the hours above USD 1, 10, 100 and 1,000, is below.
- **"Above zero" is mostly fractions of a cent.** The hours that matter are far fewer: at USD 100 or more, 92 hours in 2019, 70 in 2021, 103 in 2022, 4 in 2024, 1 in 2025.
- **No page reads the table yet,** so nothing a visitor sees changed. It is under `review_hold`; its method page (`/data/methods/ercot_rt_price_adders`) is in review like every new page.
- **Session 243 landed:** pushed 06:32:11 UTC (`05ec693a`), check run 38357256091 passed, merged into `main` as `4f7604c3` at about 06:40. Before snapshot `s243-before` (06:31:59, 25 pages, 0 failed); after snapshot `s243-after` (06:48:41, 25 pages, 0 failed); `compare`: 0 differences in all, as expected. **Not yet confirmed: the time the deploy finished.** My watcher spent GitHub's hourly allowance for unsigned readers (60 requests) and could not read the deployment's status; the allowance returns at 07:32 UTC and session 245's report gives the time.

## The table

| Variable | ERCOT's name | Held | Hours |
|---|---|---|---|
| `rtorpa_mean`, `rtorpa_max` | RTORPA, the on-line reserve price adder (the ORDC adder) | 1 June 2014 to 4 December 2025 | 100,878 |
| `rtoffpa_mean`, `rtoffpa_max` | RTOFFPA, the off-line reserve price adder | the same | 100,878 |
| `rtordpa_mean`, `rtordpa_max` | RTORDPA, the on-line reliability deployment price adder | 25 June 2015 to 4 December 2025 | 91,547 |
| `rtrdpa_mean`, `rtrdpa_max` | RTRDPA, the reliability deployment price adder for energy | 5 December 2025 to 10 October 2026 | 7,434 |

- Unit USD/MWh. `_mean` is the hour's time-weighted mean over ERCOT's SCED intervals (about every five minutes); `_max` the largest value an interval of the hour carried.
- Source: ERCOT NP6-792-ER, one Excel workbook a year, 14 read (1,313,747 SCED intervals).
- **Never filled:** a value holds to the next stamp, for at most 15 minutes; an hour is written only when all 3,600 of its seconds are covered. 42 of 100,920 hours of the ORDC adders are left out for a longer silence, 37 of RTORDPA, 3 of RTRDPA. Each is named in the run log.

## Hours a year with an adder above zero (RTORPA, the ORDC adder; Central time)

| Year | Hours held | Above zero | At least USD 1 | At least USD 10 | At least USD 100 | At least USD 1,000 | Year's mean, USD/MWh | Largest interval, USD/MWh |
|---|---|---|---|---|---|---|---|---|
| 2014 (from 1 June) | 5,134 | 1,548 | 119 | 23 | 0 | 0 | 0.20 | 304.34 |
| 2015 | 8,757 | 2,463 | 325 | 84 | 16 | 0 | 0.91 | 932.24 |
| 2016 | 8,778 | 1,862 | 144 | 36 | 2 | 0 | 0.20 | 409.32 |
| 2017 | 8,758 | 1,824 | 167 | 27 | 3 | 0 | 0.17 | 700.12 |
| 2018 | 8,755 | 1,899 | 253 | 108 | 32 | 0 | 1.28 | 1,416.74 |
| 2019 | 8,755 | 2,384 | 494 | 246 | 92 | 12 | 6.22 | 4,850.23 |
| 2020 | 8,783 | 1,783 | 352 | 143 | 43 | 1 | 1.85 | 1,557.93 |
| 2021 | 8,752 | 1,564 | 240 | 134 | 70 | 21 | 7.05 | 7,200.71 |
| 2022 | 8,758 | 2,732 | 713 | 315 | 103 | 6 | 5.18 | 2,756.03 |
| 2023 | 8,759 | 1,735 | 291 | 105 | 18 | 0 | 0.92 | 1,648.67 |
| 2024 | 8,781 | 577 | 78 | 27 | 4 | 0 | 0.20 | 847.97 |
| 2025 (to 4 December) | 8,108 | 267 | 15 | 4 | 1 | 0 | 0.07 | 4,969.39 |

- "Above zero" counts an hour when any SCED interval in it carried an adder above zero. The columns to its right count hours whose mean reached that level.
- The reliability deployment adder (RTORDPA) above zero: 152 hours in 2015 (from 25 June), 651, 322, 374, 161, 201, then 1,112 in 2021, 2,019 in 2022, 1,060, 1,081 and 1,812 in 2025. Its year's mean was USD 64.55 per MWh in 2021 (Winter Storm Uri) and under USD 2.20 in every other year. Its successor (RTRDPA): 23 hours in December 2025, 1,485 in 2026 to 10 October.
- The off-line adder and every count are in `docs/methods/ercot_rt_price_adders.md`.

## The skill's steps

| Step | What was done |
|---|---|
| Probe | ERCOT's document lists for four report types; NP6-792-ER is report type 13231, 15 documents, 2014 to 2026. The files were read once and their header rows printed before any code (`runs/session244/look_at_sheets.out`) |
| Terms | ERCOT's terms were read in an earlier session (`docs/licenses.md`, row 2): public data may be redistributed. ERCOT is not paused; the connector asks `iso_prices.paused("ercot")` first |
| Ceiling | 1,000,000 rows; the table holds 601,474. A pull that would pass it writes nothing |
| Requests | 22 in all: 4 lists in the probe, 1 list and 15 workbooks (about 170 MB) in the first read, 2 lists in the two runs. 3 seconds apart. A workbook held is never asked for again |
| Validator | exit 0: pass, 601,474 rows, 1 entity, 8 variables |
| Coverage | exit 0: `ercot_rtm_price_adders`, public, power, source tier |
| Archive | exit 0 |
| Redivis draft | exit 0: uploaded to the draft; nothing released |
| Live set | exit 0: 601,474 rows written, whole. The database went from 1,130.6 to 1,359.9 MB; the limit is 7,500 |
| Second run | "no new document; the table is as it was"; the file's hash unchanged |
| Daily refresh | a step of the data machine's daily run (`dm_ercot_rt_adders`, then `dm_rt_adders_stores` when the table moved): one request for the list most days, and the year's workbook when ERCOT posts it again (weekly) |

## Cross-checks

| Check | Result |
|---|---|
| One hour by hand: 12:00 to 13:00 Central, 15 February 2021 (Winter Storm Uri), from ERCOT's 14 raw rows | by hand 169.0334 USD/MWh; the table 169.0334 |
| ERCOT's two documents for 2015 (the half-year one, not read, against the whole year, read), January to May | 43,532 intervals in each, the same stamps; RTORPA and RTOFFPA differ in 0 intervals |
| Every row | no value below zero; no hour whose mean is above its max; no (variable, hour) twice; every hour has both statistics |
| Not done | no check against a figure published by someone else (ERCOT's market monitor reports a yearly average adder; I did not fetch it) |

## Checks

| What | Exit | Notes |
|---|---|---|
| `python scripts/precheck.py` | 0 | six of six |
| `python -m unittest tests.test_session244` | 0 | 16 tests |
| `python -m unittest discover -s tests` | 1 | 3,688 tests, 3 failures, the same three as before this chain: `test_session51`, `test_session125`, `test_session165` |
| the connector, twice, under `lock.py run` | 0, 0 | the second run added nothing |
| `table_stores.py ercot_rtm_price_adders` | 0 | four steps, each exit 0 |
| `load.py --only '^ercot_rtm_price_adders$'` | 0 | match: CSV 601,474, Supabase 601,474 |
| `runs/session244/checks.py` | 0 | the cross-checks and the hours by year |
| `python scripts/freeze.py status` | 0 | no freeze |

## Decisions made without you

1. **Hours, not SCED intervals or 15-minute intervals.** You asked for hours with an adder above zero, and the warehouse's other ERCOT price tables that pages read are hourly. The 1.3 million intervals stay in the raw workbooks on this machine.
2. **Mean and max for each adder.** The mean is what an hour of energy was paid; the max says whether any interval of the hour had an adder at all, which is how "above zero" is counted.
3. **Fifteen minutes is the longest a value holds.** The median gap between ERCOT's stamps is 5.00 minutes and the 99th percentile 5.20; 37 gaps in twelve years were longer than 15 minutes. An hour touched by one is left out, not filled: 82 hours in all.
4. **The reliability deployment adder is in the table too.** It is in the same file and is the other half of ERCOT's real-time price adder; you asked for the reserve adders, and it costs nothing to keep.
5. **The megawatts of reserve behind each adder are not in the table** (they are in the same workbooks). A second table if you want them.
6. **Loaded whole into the live set, under `review_hold`,** with its source under `sources_hold`: in Supabase for a page or for Ask, and in no count a visitor sees. 229 MB.
7. **The refresh is a step of the data machine's daily run,** not of GitHub's: the workbooks are on this machine. It adds two `dm_` steps to that run; a failure of either is recorded like any other step of it.
8. **The daily run does not load the live set for this table** (it loads none). After ERCOT posts a new week, the live copy is behind until someone runs `load.py --only '^ercot_rtm_price_adders$'`.
9. **The method document does not list the ORDC's parameter changes.** I know of several from memory and did not check them against ERCOT's own record, so they are not written down.

## For Samuel's ruling

1. **Which page should show this?** The battery page's ERCOT revenue and the peak-premium explorer are the two that would use a scarcity signal. Nothing reads the table today.
2. **Open the table in the catalogue?** It is public by ERCOT's terms and held out of the visible catalogue only because no page reads it (take `ercot_rtm_price_adders` off `review_hold` and its source off `sources_hold`).
3. **What replaces the ORDC adder after 4 December 2025?** ERCOT's real-time ancillary service prices are another report. Pull them as the continuation of this signal?
4. **A weekly live-set load for tables only this machine builds?** Today that is a person's command.

## Files

- New: `warehouse/connectors/ercot_rt_adders.py`, `docs/methods/ercot_rt_price_adders.md`, `tests/test_session244.py`.
- Changed: `warehouse/metadata/build_coverage.py` (the sector rule), `warehouse/supabase/live_set.yaml` (the rule and the two holds), `warehouse/run_data_machine.sh` (the daily step), and the metadata the stores wrote (`coverage.csv`, `docs/coverage.md`, `sources.csv`, `archive_manifest.csv`, `redivis_uploads.csv`).
- On this machine, not in git: `warehouse/output/ercot_rtm_price_adders.csv`, `warehouse/raw/ercot_rt_adders/` (the 15 workbooks), `runs/session244/` (the probe, the checks, `hours_by_year.csv`, the outputs).

## The landing

- Freeze: `python scripts/freeze.py status` exit 0, no freeze. Main pulled and merged before the push. Before snapshot `s244-before`, then the push of `task/244-ercot-reserve-adders`. The check run, the merge, the after snapshot and the comparison are in session 245's report. Expected: 0 differences on the 25 pages (no live page reads the table; the new method page is in review).
