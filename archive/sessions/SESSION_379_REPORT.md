# Session 379 report: two probes, bounded

20 October 2026, from 18:31 UTC, unattended, on lab-desktop (the data machine), the seventh session of the chain of 20 October, day. Model spend USD 0. Pulls: CAISO 0 of 6; the Wayback Machine 6 of 6 (below).

## Read these first

- **(a) CAISO's available supply: not probed, by the task's own rule.** `queue/todo/009-data-available-supply-probe.md` begins: "The health gate must be open when you start: `python warehouse/metadata/build_status.py --gate` exits 0. If it does not, stop and report why." It exited 1 at 18:31 UTC: "health gate CLOSED: daily run on GitHub 20261020, 1 failed tables outside warehouse/metadata/known_gaps.csv: state_generation_mix_monthly". That table's newest row is the run of 00:50 UTC ("input table absent: eia_state_generation_monthly"), whose cause session 327's guard fixed after the run started (session 377's root causes); the gate opens at the next daily run that writes the table. **No file was fetched, and the task file stays in `queue/todo/`**, not moved to `queue/done/`: it was not run, and moving it would lose it. The next data chain can run it as written.
- **(b) ERCOT's 4CP intervals of 2021: not found.** Six requests to the Wayback Machine (its terms read by session 155, saved under `warehouse/raw/large_load_waits/terms/`), read only: the archive holds ERCOT's 4CP page in 2021 and 2022 (nine captures), but the page itself gives no year's intervals, only links to ERCOT's report list (type 13037, "Planned Service Four Coincident Peak Calculations"), where each year's workbook was, and to the historical zip (in December 2021, "1996-2015"; in June 2022, "1996-2017"). The archive holds no copy of that report list (its index answered empty under the list's address, 503 to a filtered query, and "has not archived that URL" for the list as the 2021 page linked it). **Nothing was written to `ercot_4cp_intervals`.**

## Where (b) looked, request by request

| # | Asked | Answer |
|---|---|---|
| 1 | the index, `ercot.com/mktinfo/data_agg/4cp`, 2021 to 2022, a capture a month | 200: 9 captures (18 Feb 2021 to 1 Dec 2022) |
| 2 | the capture of 8 December 2021 | 200, 43,010 bytes: links to the report list and to `1996-2015_FourCoincidentPeakCalculations.zip`; no interval on the page |
| 3 | the index, the report list's address as a prefix, 2021 to 2023 | 200, empty (the archive orders a query's parameters, so the prefix matched nothing) |
| 4 | the index, every `GetReports.do` address filtered on 13037 | 503 (the archive's index refused the filtered query) |
| 5 | the capture of 2 June 2022 | 200, 58,120 bytes: the list's link and `1996-2017_FourCoincidentPeakCalculations.zip`; no interval on the page |
| 6 | the report list as linked in December 2021, nearest to 15 January 2022 | 404: "The Wayback Machine has not archived that URL" |

The six answers are saved in the session's scratch folder (`s379/`), not in the repository.

**Where 2021 can still come from:** the 1996-2017 zip of June 2022 does not reach 2021, and neither does the 1996-2020 zip ERCOT lists today (session 359). Left: ERCOT itself, by an information request (session 359's question to Samuel), or a later capture of the historical zip, should ERCOT publish one to 2021; the archive's index of `ercot.com/files/docs/` was not asked (the ceiling was reached).

## Checks

| What | Exit | Notes |
|---|---|---|
| `warehouse/metadata/build_status.py --gate` | 1 | the gate closed (above): probe (a) stops |

## Decisions made without you

1. **Probe (a)'s task file stays in `queue/todo/`**, since its own first rule stopped it; the chain prompt's "move it to `queue/done/`" assumed it ran.
2. **The last request asked for the report list itself** rather than an index query, after the index refused the filtered one: an answer either way.

## For Samuel's ruling

- 2021's four intervals: an information request to ERCOT, or leave the year out (session 359's question, unchanged).

## Files

- New: this report. Nothing written to the warehouse.
