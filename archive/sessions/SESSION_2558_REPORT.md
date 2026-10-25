# Session 2558 report: a third own choice, none taken (the UAE's open data portal moved to a host that does not answer; Hungary's KSH draws its table lists by script)

24 October 2026, about 23:20 to 23:24 UTC, on lab-desktop (the data machine), chain 125, unattended (run before session 2557, so that the package's records are rebuilt once). Precheck passed (`runs/c125/pre2558.out`). Model spend USD 0. Pulls: 4 requests of 20.

## Read these first

- **Looked at and set aside without a request:** New Zealand (held: the Electricity Authority's EMI tables) and the Nordic statistics offices (Sweden, Norway, Finland held).
- **The United Arab Emirates (FCSC):** the ERW holds no Emirati source. A search found the Ministry of Energy and Infrastructure's "Consumption of energy in the United Arab Emirates" (2007 to 2021) on FCSC's open data portal, which lists other datasets under CC BY 4.0. opendata.fcsc.gov.ae redirects its robots address to bayanat.ae, which did not answer (a connection timeout, read 1044). Not asked again.
- **Hungary (KSH):** the ERW holds no Hungarian source, and MEKH's site is drawn by script (session 2539). www.ksh.hu's robots file closes `/apps/` only (read 1045). Its STADAT pages for a theme (energy, then public utilities) serve the same page, whose table lists are drawn by script (reads 1046, 1047); no table's address is in the page.
- **No table this session.**

## Requests (4 of 20)

| n | What | Outcome |
|---|---|---|
| 1 | opendata.fcsc.gov.ae's robots address, by bayanat.ae | a connection timeout |
| 2 | www.ksh.hu's robots file | 200 |
| 3, 4 | KSH's STADAT theme pages | 200, the same page twice |

Reads recorded: 1044 to 1047. Three web searches looked for the UAE's, Hungary's and others' tables; they reached no publisher's host.

## Decisions made without you

- **No table where a host does not answer or draws its lists by script.**
- **Run before session 2557.**

## For Samuel's ruling

- None.

## Files

- Changed: `warehouse/metadata/license_reads.csv` (reads 1044 to 1047), `docs/licenses.md`. New: this report.
- On the data machine only: `runs/c125/s2558/`.
