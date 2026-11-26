# Data request 46: hourly load shed, three events (chain 701, 26 November 2026)

Every document was read through the research reader (`docs/research/large_load/fetch_doc.py`, from `erw-c701n`), robots file first; the copies are under `erw-c701n/runs/s5300/docs/`. Every figure below is in `shed_c701.json` with its page and quote; `verify_quotes.py` on that file: **cites checked: 182; exact 182**. `shed_c701.csv` holds one row per hour a document prints: ERCOT's 144 rows only. No value was read off a chart, no mean computed, no hour filled.

## Where the reports came from

The events pages cite the CAISO Final Root Cause Analysis and the FERC-NERC Elliott report (`docs/methods/events.md`, lines 66 and 81), so those two were used. For Uri the pages cite only EIA's Today in Energy, so ERCOT's own documents were taken from its February 2021 event page.

## 1. ERCOT, Winter Storm Uri, 14 to 20 February 2021

**What it gives.** ERCOT's workbook "Available Generation and Estimated Load without Load Shed Data" (posted 2021-03-18, listed on https://www.ercot.com/news/february2021). It holds the data behind slide 15 of the 24 February 2021 board deck. One sheet, three column pairs: AVAILABLE GENERATION every 15 seconds; ESTIMATED LOAD WITHOUT LOAD SHED hourly from 2021-02-15 01:00 (120 values); and **LOAD SHED MW every minute**, stamped 2021-02-14 00:01 to 2021-02-20 00:00 (8,640 values). The first nonzero minute is 2021-02-15 01:21 (1000 MW). The peak is 20000 MW (first at 2021-02-15 18:55). The last nonzero minute is 2021-02-17 23:55 (1000 MW). Every other minute in the window is 0.

**Resolution.** One minute, not hourly. The CSV takes the 144 rows the workbook prints at a stamp on the hour (hh:00), from 2021-02-14 01:00 to 2021-02-20 00:00, each value exactly as printed. So each row is **the one-minute value at that stamp, not an hourly mean**. The 59 other minutes of each hour are in the workbook and were not averaged here. Hourly means (MWh in each hour) can be computed from the sheet's 60 printed minutes, but that is a calculation, not a printed figure.

**What it does not give.**
- The time zone. The workbook does not say, and neither does the deck. The clock is ERCOT's (Central Standard Time in February, UTC-6): the deck puts EEA 3 and the first 1,000 MW at about 1:20 to 1:23 a.m. on 15 February ("Note: All times are approximate"), and the workbook's first nonzero minute is 01:21.
- Whether a stamp starts or ends its minute. The stamps run from 00:01, which suggests minute-ending stamps, but the sheet does not say so.
- 2021-02-14 00:00 (the sheet's first stamp is 00:01), and every hour after 2021-02-20 00:00.
- Load shed by utility per hour. The deck's slide 20 gives shares by transmission operator for the event, not hours.

**Other figures (deck, marked preliminary on slide 2):** "LEVEL 3: Rotating Outages: 10,800 MW Load" (slide 11, the 15 February timeline), and "20,000 MW peak load shed." (slide 16).

## 2. CAISO, rotating outages of 14 and 15 August 2020

**What it gives.** The Final Root Cause Analysis (13 January 2021), Tables 3.1 and 3.2 on PDF page 47. For each utility (CPUC-jurisdictional only) it gives the CAISO-initiated MW, the utility's actual response MW, minutes, and start and finish. Times are Pacific (PDT).
- **14 August:** CAISO-initiated SCE 400, PG&E 460, SDG&E 71.6, total 931.6 MW. Actual response 400, 588, 84, total 1,072 MW. SCE 6:56 to 7:59 PM (63 min); PG&E 6:38 to ~9:08 PM (~150 min); SDG&E ~15 to 60 min. In the narrative (pp. 40 to 41): Stage 3 at 6:38 p.m., "two phases of controlled load shed of 500 MW each", restoring from 7:40 p.m.
- **15 August:** CAISO-initiated 200, 230, 35.8, total 465.8 MW. Actual 200, 459, 39, total 698 MW. SCE 6:43 to 6:51 PM (8 min); PG&E 6:25 to ~7:55 PM (~90 min). In the narrative (pp. 42 to 43): Stage 3 at 6:28 p.m., "about 500 MW", restored at 6:48 p.m., "The duration of the controlled load shed was 20 minutes."

**Resolution.** One magnitude per utility per event, with clock times. **No hourly values, so no CSV row.**

**What it does not give.** Hourly or minute load shed, and any figure for non-CPUC-jurisdictional utilities ("Neither the agencies nor the CAISO has visibility ...", p. 47). The table's start and finish columns hold only SCE's and PG&E's times. The report does not say how the PG&E response was spread over its ~150 minutes.

## 3. TVA and Duke Energy, Winter Storm Elliott, 23 and 24 December 2022

**What it gives.** The FERC, NERC and Regional Entity inquiry report (the cited file of February 2024). All times are EST, Central-time entities converted (footnote 26, p. 10).
- **Figure 4 (p. 14), the maximum firm load shed ordered:** TVA "over 3,000", DEC 1,000, DEP 961 MW; durations TVA 7 hours, DEC 3, DEP 2.
- **TVA (pp. 10, 64, 71).**
  - 23 December: about 5 percent of peak system load ("over 1,500 MW") by 10:31 a.m.; restoration ordered at 12:43 p.m.
  - 24 December: about 5 percent ("1,500 MW") at 5:51 a.m., another 5 percent at 6:12 a.m. ("10 percent total, estimated by TVA to be a 3,200 MW reduction"); back to 5 percent at 10:27 a.m.; released at 11:30 a.m.
- **DEC (p. 71), 24 December:** 400 MW by 6:27 a.m., 1,000 MW at 7:10 a.m.; restoration ordered 10:00 a.m.; last circuits restored 3:45 p.m.
- **DEP (pp. 71 to 72), 24 December:** 600 MW at 6:25 a.m., 800 MW at 7:10 a.m., maximum 961 MW by 7:56 a.m.; restoring from 8:14 a.m., all by 8:43 a.m.

**A second account of Duke (not the operator's own report).** The South Carolina Office of Regulatory Staff's inspection report on DEC and DEP (p. 49) gives:
- DEC: 400 MW directed 6:14 AM, implemented 6:27 AM; two of 300 MW at 7:00 and 7:01 AM, "a total load shed directive of 1,000 MW", held at 1,000 MW.
- DEP: 600 MW requested 6:25 AM, implemented 6:50 AM; 200 MW at 7:10 AM; 50 MW at 7:43 AM; about 111 MW at 7:52 AM.

Its Figure 2-1 draws Duke's hourly load served and estimated demand: it is a chart and was not read. Its text gives only the two peaks: the hourly integrated served peak of 34,884 MW (6:00 to 7:00 AM), and the estimated demand with DSM and load shed added back, 36,543 MW (8:00 to 9:00 AM) (p. 19).

**Resolution.** Ordered levels as steps with clock times, plus maximums and durations. The levels are orders and estimates ("estimated by TVA"), not metered shed. **No hourly values, so no CSV row.**

**What it does not give.**
- Hourly or metered load shed for TVA, DEC or DEP.
- How TVA's shed moved between its orders.
- The DEC load still off between the 10:00 a.m. restoration order and 3:45 p.m.

**Not read:**
- TVA's own After Action Report. The FERC report cites it at https://www.tva.com/about-tva/reports, but www.tva.com's robots.txt answered 403, which the reader treats as disallow all, so it refused. Not worked around. A copy on a newspaper's host was seen in a search and not used.
- Duke's own briefing materials (NCUC; SC docket ND-2023-6-E). Not looked for beyond one search.

## Hosts: robots and terms

| Host | robots.txt | Terms |
|---|---|---|
| www.ercot.com | 200, allows the reader and `*` (agents named: `*`) | The page links "Terms of Use" (https://www.ercot.com/help/terms, read). Paragraph 5: "The publicly available contents of this website may be used, reproduced, and redistributed, provided that the contents are not modified and that you maintain all copyright and other notices ... raw data provided in public portions of this website may be used, reproduced, and redistributed in compilations, charts, and analyses without maintaining such notices." Paragraph 6 bars use that "negatively affects the performance" of the site. Paragraph 9 covers the ERCOT trademarks. |
| www.caiso.com | 200, allows (agents named: `*`) | The PDF was read directly; no page linked a terms page, so none was read. |
| www.ferc.gov | 200, allows (agents named: `*`) | The PDF was read directly; no terms page linked. A report of federal staff. |
| ors.sc.gov | 404, no robots file, so allowed | The PDF was read directly; no terms page linked. A state agency's public report. |
| www.tva.com | **403, treated as disallow all; refused** | Not read |

## Requests

15 HTTP requests (limit 40), each robots read counted:
- CAISO: robots and PDF (2).
- FERC: robots and PDF (2).
- ERCOT event page: robots and page (2).
- ERCOT workbook: robots and file (2).
- ERCOT deck: robots and PDF (2). The first try failed at name lookup (getaddrinfo), so no request reached the host.
- ERCOT terms: robots and page (2).
- TVA: robots only, 403 (1).
- ORS: robots (404) and PDF (2).

Two WebSearch queries were used to find official addresses (ERCOT's files and Duke's or TVA's reports). The scripts are in this folder: `ercot_xlsx_scan.py` and `ercot_xlsx_cells.py` (reading the cached workbook) and `build_shed.py` (writes the JSON and CSV from the cache, no request).
