# Session 928 report: the licenses' sixth round

23 October 2026, from 10:07 UTC, on lab-desktop (the data machine), a session of `queue/done/052-day-23-october-data-world-oil-reactors-stocks.md`. Model spend USD 0. Pulls: 2 requests of 20 (the Texas Comptroller's robots file, asked alone and read first, and its policies page); sessions 924, 925 and 926's ten license reads recorded with them (reads 132 to 143).

## Read these first

- **Two new verdicts** (77 publishers with one):
  - **World Bank: may be public** (read 141, by session 926): its Summary Terms of Use: "Unless indicated otherwise in the data or indicator metadata, you are free to copy, distribute, adapt, display or include the data in other products for commercial or noncommercial purposes at no cost under a Creative Commons Attribution 4.0 International License". Settles `wb_commodity_prices_monthly`.
  - **Ember: may be public** (read 133, by session 924): "All content is released under a Creative Commons Attribution Licence (CC-BY-4.0)". No ERW table holds Ember's data: its files sit on a host whose robots file disallows every path but PDFs (read 134), as session 924 found.
- **The sessions of this chain first:** EIA (record 1) and the NRC (read 16) already had verdicts; the NRC's robots file is recorded as read 135. The World Bank's "Terms of Use for Datasets" address answers with its general Terms and Conditions (read 139, not read as terms); the verdict rests on the Summary Terms of Use, which name CC BY 4.0.
- **The Texas Comptroller:** its policies page (read 143) lists the agency's policies and states no terms of reuse; its privacy and security policy (`/about/policies/privacy.php`) is the next page to read. No verdict.
- `test_session205`'s bound holds exactly (102 reads after session 205's 41); the next round must raise it.

## Decisions made without you

- **A verdict for Ember although no table uses it,** so that a ruling on its robots file needs no second read of its terms.

## For Samuel's ruling

- None new (Ember's robots file is session 924's question).

## Files

- New: this report.
- Changed: `warehouse/metadata/license_reads.csv` (132 to 143), `license_verdicts.csv` (two rows), `docs/licenses.md`.
- On the data machine only: `runs/c052/s928/`, `runs/license_reads/s928/`.
