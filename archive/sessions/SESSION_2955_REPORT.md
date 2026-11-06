# Session 2955 report: the reactor fleet

6 November 2026, about 08:24 to 08:27 UTC, on lab-desktop (the data machine), chain 157 (the owner's), unattended. Model spend USD 0. Pulls: none.

## Read these first

- **`nuclear_fleet_status` is written:** 15,048 rows, public, commit `fda5cc187`.
  - **Inputs:** EIA's daily outages by reactor (`eia_nuclear_outages_generator_daily`, 2007 to 21 October 2026; the table session 2946 looked for as `nuclear_outages*` is held under this name). Each reactor's grid comes from EIA-860M's operating NUC generators.
  - **123 reactors**, one row a reactor and year: capacity, outage share, full-outage days, long outages (14 days or more in a row, the refuelings), available MWh, days held, and the capacity change. Each reactor's first and last days held mark its restart or retirement.
  - **The fleet** by balancing authority and for the US: 93 reactors and 98.0 GW in 2024; 94 and 99.2 GW in 2025; 95 and 100.1 GW in 2026 to date. PJM holds 33.7 GW, MISO 11.8, TVA 8.4, SOCO 8.1, DUK 7.5 and ERCOT 5.1 (2025).
  - **Uprates show:** Turkey Point 3 and 4, 109 MW each (2012 and 2013); R. E. Ginna 81.7 MW (2008).
  - **Cross-check: available energy against EIA-923's nuclear net generation** is within 1 percent: 2023, 769.5 against 774.9 TWh; 2024, 775.1 against 781.9 TWh.
- **The write:** validator PASS, coverage, archive run `20261106T082634Z-local`. Method note `docs/methods/nuclear_fleet_status.md`; test `tests/test_session2955.py` (3 passed).

## Decisions made without you

- **A reactor year with fewer than 300 days held gets its days only**, except its first and last years.
- **A reactor's grid is its plant's balancing authority in EIA-860M**, "none" where the plant is no longer listed (a retired one).

## For Samuel's ruling

- None.
