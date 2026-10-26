# Session 2769 report: the licenses' sixty-first round (ISTAT and ELSTAT may be public)

26 October 2026, about 00:00 to 00:04 UTC, on lab-desktop (the data machine), chain 140, unattended. Precheck passed (`runs/c140/pre2769.out`). Model spend USD 0. Pulls: 6 requests of 20, two pages a host beside its robots file (redirects capped at 5).

## Read these first

- **`license_verdicts.csv` was read first.** Of this chain's publishers, Statistics Austria (session 2764) and Spain's INE (session 2765) had verdicts already, given when their tables were written; ISTAT and ELSTAT had none.
- **Two verdicts, "may be public"** (`runs/c140/s2769_verdicts.py`), each sentence cut by code. The cuts stop short of the pages' dashes, which the repository does not carry.
  - **ISTAT** (its legal notice, read 1545): "Unless otherwise stated, content on this website is licensed under a Creative Commons License [...] copy and redistribute the material in any medium or format for any purpose, even commercially". That is Attribution 4.0, with credit, a link to the licence and changes indicated. Third parties' images and logos are excluded.
  - **ELSTAT** (its copyright and reuse policy, a PDF embedded in its "Copyright and reuse of data" page, read 1546): free reuse, commercial included, "without any payment or written licence", with the source indicated and any modification stated. ELSTAT bears no responsibility for modified results.
  - Neither holds a table in the ERW (sessions 2766 and 2767). The verdicts serve a later chain.
- **Robots files asked again in their own requests:** www.statistics.gr's and www.istat.it's, each byte for byte as sessions 2767 and 2766 read them (reads 1541 and 1542).
- **Sessions 2770 and 2771 come after this one,** so their publishers fall to a later chain's round, as chain 139's did.
- **The record:** 605 tables, 255 publishers with a verdict, 0 problems. Tests 378, 205 and 152 pass (36 tests).

## Requests (6 of 20)

| n | What | Outcome |
|---|---|---|
| 1 | www.statistics.gr's robots file (its own request) | 200, as before |
| 2 | www.istat.it's robots file (its own request) | 200, as before |
| 3 | ELSTAT's Copyright and reuse of data page | 200, the PDF linked |
| 4 | ISTAT's English home page | 200, the legal notice linked |
| 5 | ISTAT's legal notice | 200 |
| 6 | ELSTAT's Copyright_Reuse_Policy_EN.pdf | 200 |

Reads recorded: 1541 to 1546.

## Decisions made without you

- **No address guessed:** each terms page was found from a link on the host's own pages.

## For Samuel's ruling

- None new.

## Files

- New: this report. Changed: `warehouse/metadata/license_verdicts.csv` (two rows), the license record (reads 1541 to 1546), `docs/licenses.md`.
- On the data machine only: `runs/c140/s2769/`, `runs/c140/s2769_verdicts.py`, `runs/license_reads/s2769/`.
