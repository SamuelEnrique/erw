# Session 2163 report: the crude oil each company imports (EIA's company level imports): not taken, its files are under a path EIA's robots file disallows

24 October 2026, from 00:23 UTC, on lab-desktop (the data machine), the second session of `queue/done/094-day-31-october-data-britain-imports-gas-use-waterways.md`, unattended. Model spend USD 0. Pulls: 2 requests of 15 (below). No table written.

## Read these first

- **The crude part is already held:** `eia_crude_imports_detail_monthly` (session 632) takes EIA-814's crude imports through EIA's API by country of origin, destination (refinery, port state, PADD) and grade, 2009 to July 2026. What the company-level files would add is the importing company's name and the petroleum products.
- **Those files are closed to the ERW's reader:** the Company Level Imports page (allowed) links every monthly and annual file under `/petroleum/imports/companylevel/archive/...` (`import.xlsx` for 2026's months, `impa13d.xls` to `impa25d.xlsx` for the years), and EIA's robots file disallows `/*archive/`, any path holding `archive/` (read 307). None was asked.
- **No replacement source** in this session: the file's rule replaces a source another chain took or the ERW holds, and here the part not held is out of reach. Sessions 2168, 2169 and 2174 (sources of the session's own choosing) can take others.

## The pulls

1. `www.eia.gov/robots.txt` (read 307, read again: EIA's terms are record 1).
2. The Company Level Imports page, for the files' addresses.

## Errors

- None.

## Decisions made without you

- **The company-level files not asked,** reading `Disallow: /*archive/` as covering `/petroleum/imports/companylevel/archive/`.

## For Samuel's ruling

- **EIA's company-level imports** (the importing company and the products) sit under a path EIA's robots file disallows; a person's download, or a word from EIA that its robots rule does not mean these files, would open them.

## Files

- New: this report.
- Changed: `warehouse/metadata/license_reads.csv` (307), `docs/licenses.md`.
- On the data machine only: `runs/c094/s2163/`, `runs/license_reads/s2163/`.
