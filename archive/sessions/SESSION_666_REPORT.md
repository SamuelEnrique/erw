# Session 666 report: the gap sources, probed

22 October 2026, from 09:13 UTC, on lab-desktop (the data machine), a session of `queue/done/043-night-23-october-data-redivis-gaps.md`. Model spend USD 0. It ran while session 663's upload of the largest tables was processing on Redivis, since it reaches no Redivis host and 664 and 665 wait for 663.

## Read these first

- **Two of the five sources can be written: EIA's service territories (public, no request: the 2025 zip is saved) and Berkeley Lab's durations (derived from the held queue table).** OpenEI's rates are public (CC0) but need an API key this machine lacks.
- **HIFLD Open no longer answers** (its hub's front page is HTTP 404); the substations and transmission lines exist on ArcGIS only as copies made by others, none the publisher's own. Sessions 668 and 669 write nothing.
- **NERC's terms page loads its text by script**, so it could not be read; the reserve margins are not pulled (session 672 does its second half only).
- **EIA's robots file disallows `/archive/`**, where EIA-861's earlier years live: listed for the owner, not changed.
- The findings, one row a source: [`docs/reviews/siting-sources-2026-10-23.md`](../../docs/reviews/siting-sources-2026-10-23.md). The reads are records 88 to 90 of `license_reads.csv`; OpenEI's verdict is in `license_verdicts.csv`. `licenses.py check`: 0 problems.

## Pulls against their ceilings

| Host | Requests | What |
|---|---|---|
| www.eia.gov | 1 | the robots file |
| hifld-geoplatform.hub.arcgis.com | 2 | the robots file; the front page (404) |
| www.arcgis.com | 3 | the robots file; two catalogue searches (the layers by title; EIA's organization, a guess that found nothing) |
| openei.org | 2 | the robots file; the Utility Rate Database's page |
| www.nerc.com | 4 | the robots file; two guessed terms addresses (404); the home page, for the terms link |
| www.nerc.com | 1 | the terms page (`/terms-of-use-policy`) |
| eta-publications.lbl.gov | 2 | the robots file; a HEAD of the Queued Up file |
| All | 15 of 16 | two a host was the plan; NERC took five and ArcGIS's catalogue was added to find HIFLD's layers, within the session's 16 |

## Decisions made without you

- ArcGIS Online's catalogue was asked once to find where HIFLD's layers went, since HIFLD's own hub answered 404; no copy made by others is taken as a source.
- NERC took more than two requests (its terms were at neither guessed address, and its home page gave the link); the session's total stayed under 16.
- The session ran during session 663's upload, out of order, since it shares nothing with it.

## For Samuel's ruling

- An OpenEI API key for session 670 (`OPENEI_API_KEY`).
- HIFLD's successor for substations and transmission lines, or a ruling on Esri's archive copy of the lines.
- NERC's terms, read in a browser.
- EIA's robots file and the EIA-861 connectors' earlier years under `/archive/`.

## Files

- New: `docs/reviews/siting-sources-2026-10-23.md`, this report. Changed: `warehouse/metadata/license_reads.csv`, `warehouse/metadata/license_verdicts.csv`. On the data machine only: `runs/s666/`, `runs/license_reads/s666/` and records 88 to 90's pages.
