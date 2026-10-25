# Session 2709 report: Manitoba's electricity not taken (Manitoba Hydro's terms require written permission to download; the CCEI's certificate fails)

25 October 2026, about 17:00 to 17:04 UTC, on lab-desktop (the data machine), chain 136, unattended. Run while this machine's own daily task held the data lock (from 17:00 UTC), with session 2708's write waiting for it. Precheck passed (`runs/c136/pre2709.out`). Model spend USD 0. Pulls: 7 requests of 15, all by the probe; one web search.

## Read these first

- **The ERW held Manitoba only in Statistics Canada's tables and as EIA-930's MHEB interchange partner;** no source or read named Manitoba Hydro.
- **Manitoba Hydro** (www.hydro.mb.ca):
  - Its robots file closes its regulatory, project and external documents, its hydrological data and some account paths, and names no Claude agent (read 1430).
  - Its operations page gives no figures table (read 1433). Its system figures are in its annual reports' operating statistics, PDFs listed on its publications page (read 1434).
  - **Its Terms of use** (read 1435), under Ownership: "You may use the Manitoba Hydro website content for your personal, non-commercial use. You must have the written permission of Manitoba Hydro before you can reproduce, download, modify, or distribute any of our website content, in whole or in part". The bar covers downloading itself, so no report was fetched and the host is not asked again.
  - Two addresses I guessed for its annual reports and legal pages answered 404 (reads 1431 and 1432). They were two requests spent on guesses; the next requests followed the site's own links.
- **A replacement tried:** the Canadian Centre for Energy Information's high-frequency electricity data (energy-information.canada.ca, Statistics Canada and its federal partners), which a search named as gathering provincial utilities' data. Its robots file could not be read: the certificate fails verification (read 1436). The host is closed, as earlier chains closed such hosts.
- **No table.**

## Requests (7 of 15)

| n | What | Outcome |
|---|---|---|
| 1 | www.hydro.mb.ca's robots file (its own request) | 200 |
| 2 | a guessed annual reports address | 404 |
| 3 | a guessed legal page address | 404 |
| 4 | Operations and exports | 200 |
| 5 | Reports and publications | 200 |
| 6 | Terms of use | 200 |
| 7 | energy-information.canada.ca's robots file | certificate fails |

Reads recorded: 1430 to 1436.

## Decisions made without you

- **Manitoba Hydro closed for its terms,** which require written permission to download: no file fetched. Its verdict (written permission) goes to session 2713's round.
- **The CCEI host closed for its certificate,** without a second try.

## For Samuel's ruling

- **Manitoba Hydro grants permission on request:** a request would open its annual operating statistics (generation, exports to MISO and Saskatchewan, load).

## Files

- New: this report. Changed: the license record (reads 1430 to 1436) and `docs/licenses.md`.
- On the data machine only: `runs/c136/s2709/`, `runs/license_reads/s2709/`.
