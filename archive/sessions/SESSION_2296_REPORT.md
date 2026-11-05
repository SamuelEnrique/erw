# Session 2296 report: Peru's generation (COES), no table

24 October 2026, from 05:37 UTC, on lab-desktop (the data machine), a session of `queue/done/105-day-8-november-data-mexico-india-peru-korea.md`. Model spend USD 0. Pulls: 3 requests of 15, each listed below. No table.

## Read these first

- **COES's data are reached only by POST requests from its pages' scripts.** www.coes.org.pe has no robots file, and its portal and statistics pages answer. But the annual statistics page lists its files through a script that POSTs to its statistics controller (`controlador_estad + 'Detalle'`, with the year), from a file browser whose folders (`Publicaciones/Estadisticas Anuales/<year>/`) the page names but does not list. The generation and maximum demand pages are built the same way.
- **The ERW's fetch helper asks by GET only,** as session 2188 found with USAspending. A connector that POSTs to a publisher's page controller would need the raw store to key a request by its body, which it does not. So no request was made beyond the pages, and no table was written.
- **A code chain could add POST requests to the fetch helper and its raw store** (keyed by address and body). Then COES, USAspending's by-state search and others like them could be read.

## The pulls

1. `www.coes.org.pe/robots.txt`: HTTP 404, no file.
2. The portal's home page.
3. The 2025 annual statistics page.

## Errors

- None in the ERW's code; no table was attempted.

## Decisions made without you

- **No table for Peru** rather than guessing file names in COES's browser.

## For Samuel's ruling

- None new; the fetch helper's GET-only limit is for a code chain.

## Files

- New: this report.
- On the data machine only: `runs/c105/s2296/`.
