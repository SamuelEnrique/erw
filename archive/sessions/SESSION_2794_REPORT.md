# Session 2794 report: NYPA not taken (its net generation by facility is on Open NY, whose terms forbid automated access)

26 October 2026, about 03:03 to 03:04 UTC, on lab-desktop (the data machine), chain 142, unattended. Precheck passed (`runs/c142/pre2794.out`). Model spend USD 0. Pulls: 2 requests of 15, both by the probe; one web search.

## Read these first

- **NYPA not taken:**
  - www.nypa.gov's and nypa.gov's robots files allow every path and name no Claude agent (reads 1592 and 1593).
  - The search found **"New York Power Authority Net Generation (MWh) Produced by Facility: Beginning 2013"**, a real series, on data.ny.gov (dataset isux-jnrn), listed through data.gov. NYPA's own pages give the same per plant in GWh, in annual reports.
  - **data.ny.gov is Open NY, whose terms forbid access "by using an automated device, script, bot, spider, crawler or scraper"**: the verdict on record is that it needs written permission (session 2114, read 272). File 142's session text says so. Nothing was asked of data.ny.gov or of the data.gov mirror, which points at the same host.
  - NYPA's sales are held through EIA-861, and its plants through EIA-923.
- **For Samuel:** Open NY's written permission would open this dataset among others (chain 069's note).
- **No table.**

## Requests (2 of 15)

| n | What | Outcome |
|---|---|---|
| 1 | www.nypa.gov's robots file (its own request) | 200 |
| 2 | nypa.gov's robots file (its own request) | 200, the same file |

Reads recorded: 1592 and 1593.

## Decisions made without you

- **The data.gov listing not followed:** its CSV is served by data.ny.gov, under Open NY's terms.

## For Samuel's ruling

- **Open NY's written permission** (standing since session 2114): it would open NYPA's net generation by facility since 2013.

## Files

- New: this report. Changed: the license record (reads 1592 and 1593) and `docs/licenses.md`.
- On the data machine only: `runs/c142/s2794/`, `runs/license_reads/s2794/`.
