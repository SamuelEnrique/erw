# Session 2811 report: the licenses' sixty-fourth round (two verdicts this chain, in its source sessions; Svenska kraftnät's data portal read, not settling its table)

26 October 2026, from about 05:11 to 05:15 UTC, on lab-desktop (the data machine), chain 143, unattended. Precheck passed (`runs/c143/pre2811.out`). Model spend USD 0. Pulls: 2 of 20 (both by the probe, 10 seconds apart, the host's crawl delay); three web searches.

## Read these first

- **`license_verdicts.csv` was read first.** This chain's sources so far all have verdicts:
  - Eurostat (sessions 2806, nrg_ind_re) and the SFOE (session 2808, ogd51) had theirs already;
  - **Destatis's and the CZSO's are new**, recorded in sessions 2807 (read 1606) and 2809 (read 1617), each sentence cut by code.
  - INE Portugal refused the reader at its robots files (session 2806), so there is nothing to read.
  - ERSE offered no table.
  - The license record: 619 tables, 259 publishers with a verdict, 0 problems.
- **The publishers chains 046 to 142 did not reach:** 52 publishers of held tables have no verdict. Most were read and state no terms (E-Control, the Danish Energy Agency, REN, PSE, MakStat, Kosovo's ASK, ERU). Two had no read on record at all, though sessions 2350 and 2351 left them to "the next licenses round": Statnett and Svenska kraftnät.
  - **Svenska kraftnät:**
    - data.svk.se's robots file (read 1618) allows its dataset lists (`/dataset/?page=`), disallows `/api/`, history pages and filtered searches, and sets `Crawl-Delay: 10`.
    - Its list (read 1619) holds ten datasets: physical flows, the balancing and capacity markets, and day-ahead prices. Its dataset pages state CC BY 4.0 (a web search).
    - **None of the ten is Mimer's production statistics,** which `svk_sweden_production_hourly` reads. So that licence does not settle the table: it stays internal. When data.svk.se carries the production statistics (its front page says it will gradually replace Mimer), its page will.
  - **Statnett:** a search of statnett.no found no terms of use, only its privacy page. No address was guessed; `statnett_norway_daily` stays internal.
- **No verdict this round.**

## Decisions made without you

- **data.svk.se's CC BY 4.0 not applied to Mimer's data,** a different platform and dataset.

## For Samuel's ruling

- None new. Statnett's and Svenska kraftnät's tables stay internal until a page states their terms.

## Files

- New: this report.
- Changed: the license record (reads 1618 and 1619) and `docs/licenses.md`.
- On the data machine only: `runs/c143/s2811/`, `runs/license_reads/s2811/`.
