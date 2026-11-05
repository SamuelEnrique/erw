# Session 2806 report: queue file 144 written first; INE Portugal not taken (HTTP 403 at its robots files); Europe's rate of electrification (Eurostat, nrg_ind_re) in its place

26 October 2026, from about 04:26 to 04:40 UTC, on lab-desktop (the data machine), chain 143, unattended. Precheck passed first (`runs/c143/pre2806.out`). Model spend USD 0. Pulls: 6 requests of 15 (4 by the probe, 2 by the fetch); one web search.

## Read these first

- **Queue file 144 first:**
  - `queue/next/144-day-14-december-data-mavir-transelectrica-eles-hops.md` (sessions 2820 to 2833) was written from file 143 by `runs/c143/write_144.py` (session 2792's writer's form). It keeps the rules word for word.
  - 144 was the next free number, and 2820 to 2833 were free on main and on every branch.
  - **Its sources are four European transmission system operators:** Hungary's MAVIR, Romania's Transelectrica, Slovenia's ELES and Croatia's HOPS. None is in the record, the queue or the unlanded chains' branches.
  - **The statistics offices left were closed by earlier chains:** Hungary's KSH (its lists drawn by script), Romania's INS (year-to-date totals only), Slovakia's (a timeout) and Croatia's DZS (not PxWeb). Latvia's is on chain 118's branch.
  - Pushed to main alone as `4ae67ff8`; snapshots `c143-q144w-before` and `c143-q144w-after` show **0 differences**.
- **Chain 143's worktree:** `erw-c143` on `wip/2806-2819-data`, from main at `4ae67ff8`.
- **Test 205's bound** is raised by 40 for this chain's reads, from 1600.
- **INE Portugal not taken: its host refuses the reader.** www.ine.pt's robots file answers HTTP 403 (nginx), and ine.pt redirects to it (reads 1600 and 1601). Nothing else of INE was asked; the host is closed, as www.tepco.co.jp's 403 was.
- **Portugal's other public sources:**
  - DGEG was closed by chain 140 (its robots file disallows `/media/*`, where its files are served).
  - **ERSE**'s robots file allows every path (read 1602), but its monthly market summaries are PDFs (a web search). No file was asked.
  - REN's balance and Energy-Charts' Portugal series are held.
- **In INE's place, `eurostat_electrification_rate_annual`:** Eurostat's rate of electrification by end-user (nrg_ind_re), from session 2799's reading of Eurostat's dataflow list.
  - It gives electricity's share of each European country's final energy consumption a year, 1990 to 2023: overall, by sector and branch (industry and its branches, transport and its modes, households, services, agriculture, fishing), and in the energy sector's own use.
  - 38,269 rows, 39 areas, 43 balance items, in pct.
  - The table has been written, validated, archived and put in coverage. It is held from the live set and from Redivis storage until session 2815's draft. It includes Portugal: 17.8 per cent in 1990, 25.9 in 2023.
- **Figures:**
  - **The EU27's final energy consumption was 22.9 per cent electricity in 2023,** against 17.9 in 1990 and 22.2 in 2010.
  - Its sectors in 2023: industry 32.7, services 51.2, households 25.9, transport 2.2 (rail 79.6, road 0.5).
  - Highest in 2023: Iceland 53.4, Norway 50.6, Malta 39.2. Lowest: Latvia 14.3, Moldova 14.5, Romania 15.3.
- **The balance's own logic as the cross-check:**
  - final consumption's rate lies within industry's, transport's and the other sectors' in all 1,238 country years that give the four;
  - households' and services' together lie within theirs in all 1,235.

  No held table gives total final energy consumption, so no other figure could be compared. Kept as published:
  - 3,277 zeros;
  - 2,478 blanks (flag m), with no row;
  - the United Kingdom, Kosovo and EU28, left out.

## The requests

| n | What | Outcome |
|---|---|---|
| 1, 2 | www.ine.pt's and ine.pt's robots files (each its own request) | HTTP 403 (the second by redirect to the first) |
| 3 | www.erse.pt's robots file | 200, open |
| 4 | ec.europa.eu's robots file | 200, byte for byte session 2804's |
| 5 | nrg_ind_re, the whole dataset (3.2 MB) | 200 |
| 6 | the NRG_BAL codelist, under this connector's raw folder | 200, the same file as session 2798's |

Reads recorded: 1600 to 1603.

## Decisions made without you

- **INE's host closed at its robots files' 403,** without asking its JSON API.
- **A Eurostat table in Portugal's place,** after ERSE's PDFs and DGEG's closed files, rather than a second Portuguese host.

## For Samuel's ruling

- None new.

## Files

- New:
  - `warehouse/connectors/eurostat_electrification.py`
  - `tests/test_session2806.py` (5 tests, passing)
  - this report
- Changed:
  - `tests/test_session205.py` (the bound);
  - the table's registration and holds;
  - the license record (reads 1600 to 1603) and `docs/licenses.md`;
  - coverage, sources, the archive manifest and the release v1 records.
- On the data machine only:
  - `runs/c143/write_144.py`, `runs/c143/raise205.py`, `runs/c143/s2806/`, `runs/license_reads/s2806/`;
  - `warehouse/raw/eurostat_electrification/`.
