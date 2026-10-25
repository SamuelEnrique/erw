# Session 2752 report: the Southwestern Power Administration not taken (its hosts do not answer; its annual reports end at FY 2021 and give money, not energy)

25 October 2026, about 22:07 to 22:12 UTC, on lab-desktop (the data machine), chain 139, unattended. Precheck passed (`runs/c139/pre2752.out`). Model spend USD 0. Pulls: 6 requests of 15 (5 by the probe, 1 fetch of a report); one web search.

## Read these first

- **SWPA not taken:**
  - **www.swpa.gov and swpa.gov** closed the connection without a response to their robots files (reads 1491 and 1492). Nothing else of theirs was asked.
  - SWPA's pages now sit on **www.energy.gov/swpa**. energy.gov's robots file closes Drupal's core, admin, search and user paths and leaves `/sites/default/files/` open; it names no Claude agent (read 1493).
  - Its **annual reports page** links three reports, FY 2019, FY 2020 and FY 2021, the last published in May 2023 (read 1494). Their links point at cms.doe.gov, whose robots file timed out (read 1495), so that host was not asked. The same file was fetched from www.energy.gov's `/sites/default/files/` path, which its robots file allows.
  - **The FY 2021 report** (54 pages, 7.6 MB, saved in `warehouse/raw/swpa/s2752ar2021/`): its "Five-Year Statistical Summary" (FY 2017 to 2021, page 20) is revenue, expense and repayable investment in dollars. Its only energy figures are one year's billings by customer, in kWh (page 18). It holds no generation or sales series by year.
  - The ERW holds SWPA's balancing authority hourly through EIA-930 (SPA). Five years of dollars, four years stale, would not make a series within the data standard's units.
- **No table.**

## Requests (6 of 15)

| n | What | Outcome |
|---|---|---|
| 1 | www.swpa.gov's robots file (its own request) | connection closed, no response |
| 2 | swpa.gov's robots file (its own request) | connection closed, no response |
| 3 | www.energy.gov's robots file (its own request) | 200 |
| 4 | SWPA's annual reports page on energy.gov | 200, three reports |
| 5 | cms.doe.gov's robots file (its own request) | connection timed out |
| 6 | AR_2021_Final.pdf from www.energy.gov (the fetch) | 200, 7,560,108 bytes |

Reads recorded: 1491 to 1495.

## Decisions made without you

- **The report fetched from www.energy.gov,** not the cms.doe.gov address the page links: the same path on the host whose robots file was read. cms.doe.gov was not asked beyond its robots file.
- **The one-year billings by customer not taken:** a single year, by customer, from a PDF.

## For Samuel's ruling

- None new.

## Files

- New: this report. Changed: the license record (reads 1491 to 1495) and `docs/licenses.md`.
- On the data machine only: `runs/c139/s2752/`, `runs/license_reads/s2752/`, `warehouse/raw/swpa/s2752ar2021/`.
