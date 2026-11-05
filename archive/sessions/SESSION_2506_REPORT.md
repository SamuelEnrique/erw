# Session 2506 report: Guyana's electricity, not taken (the Bureau of Statistics bars Claude agents by name; GEA's statistics end in 2014, GPL's reports in 2012)

24 October 2026, about 17:44 to 17:46 UTC, on lab-desktop (the data machine), chain 122, unattended. Precheck passed (`runs/c122/pre2506.out`). Model spend USD 0. Pulls: 9 requests of 15.

## Read these first

- **The ERW holds no Guyanese source.**
- **The Bureau of Statistics** (statisticsguyana.gov.gy): its robots file, managed by Cloudflare, disallows ClaudeBot, anthropic-ai and Claude-Web by name, and every path to them (read 889). Nothing more was asked of it, and it is not asked again.
- **The Guyana Energy Agency (GEA):** its robots file closes `/wp-admin/` only (read 887). Its site search answers HTTP 401 (read 890). Its sitemaps (reads 891, 892) lead to a downloads page (read 893) whose statistics workbooks are "Stats-for-Website.xls" and "...-2014.xlsx": nothing after 2014.
- **Guyana Power and Light (GPL):** its robots file closes `/pl/wp-admin/` only (read 888). Its publications page (read 895) lists annual reports for 2009 to 2012 only.
- **Not taken:** no current public series in reach. A table ending in 2012 or 2014 was not built when Ember's holds Guyana's later years.

## Requests (9 of 15)

| n | What | Outcome |
|---|---|---|
| 1 to 3 | gea.gov.gy, gplinc.com and statisticsguyana.gov.gy robots files | 200; the Bureau's names Claude agents |
| 4 | GEA's site search | 401 |
| 5, 6 | GEA's sitemap index and pages | 200 |
| 7 | GEA's downloads page | 200: statistics to 2014 |
| 8, 9 | GPL's sitemap and publications page | 200: reports to 2012 |

Reads recorded: 887 to 895 (on this branch). One web search reached no publisher's host.

## Decisions made without you

- **No table for Guyana** rather than one ending in 2012 or 2014.

## For Samuel's ruling

- None.

## Files

- Changed: `warehouse/metadata/license_reads.csv` (reads 887 to 895), `docs/licenses.md`. New: this report.
- On the data machine only: `runs/c122/s2506/`.
