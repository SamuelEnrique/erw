# Session 2239 report: Spain's electrical energy balance a month (Red Eléctrica's REData)

24 October 2026, from 03:16 UTC, on lab-desktop (the data machine), the second session of `queue/done/101-day-4-november-data-france-spain-brazil-australia.md`, unattended. Model spend USD 0. Pulls: 14 requests of 15 (below).

## Read these first

- **REE's terms read first.**
  - apidatos.ree.es has no robots file (read 411, HTTP 404).
  - www.ree.es's robots file disallows only search, feeds and press events (read 412).
  - **REE's legal notice** (read 414) gives a new verdict: may be public as the ERW is, needs written permission if it sells. The sentence: "Notwithstanding the above, users may view and obtain a personal temporary copy of the content for their exclusive private use in their computer systems (software and hardware), publish them on their website or create company or academic content, as long as it is for information only, and not for commercial purposes."
  - Users must also name REE as the source, not alter the data's meaning, and give the date of their latest update. REE's "last-update" is in the header.
- **One table written, validated, archived, in coverage (sector power), in the release package, both holds:** `ree_spain_balance_monthly`, January 2020 to September 2026, 1,890 rows.
  - Every series of REE's electrical energy balance, in MWh a month: each technology, REE's three subtotals, pumping and batteries, the cross-border balance, and demand at busbars.
  - **October 2026 left out:** it had not ended when fetched (24 values). The connector leaves out any open month.
  - **REData answers at most a year a request:** a five-year and an eleven-year range both gave HTTP 400 ("The requested data is currently unavailable"). So seven years cost seven requests. The queue file's "by technology, a day or a month, from 2015" became a month from 2020, within the ceiling.
- **The cross-check** (`runs/c101/s2239/cross.py`, `cross.out`):
  - **REE's arithmetic closes:** the three subtotals equal their parts exactly, and generation plus storage plus exchanges equals demand at busbars to within 0.7 MWh in all 81 months.
  - **Against Ember:** a year's demand at busbars is 0.920 to 0.952 of Ember's Spanish demand from 2020 to 2025. For example, 2025 is 256.257 against 275.1 TWh.
    - The steadiness confirms the unit, which the API does not state.
    - Why the ratio drifts from 0.95 to 0.92 is not tested here; self-consumption outside the busbars would explain it.
  - Wind and solar photovoltaic rose from 28.1% of demand in 2020 to 42.5% in 2025 (45.9% in 2026 so far).

## The pulls

1. apidatos.ree.es/robots.txt (read 411): HTTP 404.
2. www.ree.es/robots.txt (read 412).
3. REE's home page (read 413), for the legal notice's address.
4. The legal notice (read 414).
5. The generation structure, 2015 to September 2026, a month: HTTP 400.
6. The generation structure for 2025: served (kept, not used for the table).
7. The generation structure, 2020 to 2024: HTTP 400.
8. to 14. The electrical energy balance, a year a request: 2025, 2020 to 2024, and 2026. They were seeded into the raw store, and the trial and the write read them offline.

## Errors

- **Two requests spent learning REData's one-year limit** (pulls 5 and 7).

## Decisions made without you

- **The balance widget in place of the generation structure.** It carries generation, storage, exchanges and demand together, so one table and one request a year cover them.
- **A month from 2020,** rather than a day from 2015, within the ceiling.
- **REE's subtotals kept** as rows, named in the header so a sum leaves them out.

## For Samuel's ruling

- None new. As for other non-commercial verdicts, the table stays public while the ERW sells nothing.

## Files

- New: `warehouse/connectors/ree_balance.py`, `tests/test_session2239.py`, this report.
- Changed:
  - `warehouse/metadata/build_coverage.py`, `warehouse/redivis/release_v1.py`, `warehouse/supabase/live_set.yaml`
  - `warehouse/metadata/license_reads.csv` (366 to 369), `warehouse/metadata/license_verdicts.csv` (REE)
  - the coverage, sources, archive manifest and license files
  - `docs/redivis/release-v1/`
- On the data machine only: `runs/c101/s2239/`, `runs/license_reads/s2239/`, `runs/s2239_*`, `warehouse/raw/ree_balance/`.
