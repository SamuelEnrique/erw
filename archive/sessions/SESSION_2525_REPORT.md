# Session 2525 report: Serbia's balance of electricity, 2024 (SORS's Energy Balances), the second own choice, public

24 October 2026, about 19:20 to 19:23 UTC for the reads and the connector; the table written under the data lock at 19:24 UTC. On lab-desktop (the data machine), chain 123, unattended. Precheck passed (`runs/c123/pre2525.out`). Model spend USD 0. Pulls: 5 requests of 20 (4 by the probe, 1 by the fetch the connector reads offline).

## Read these first

- **Why Serbia:** a grid the ERW held only in EIA's and Eurostat's international tables.
- **The Statistical Office of the Republic of Serbia (SORS):** www.stat.gov.rs, data.stat.gov.rs and publikacije.stat.gov.rs have no robots file (reads 964, 965, 967). Its copyright page (read 966): "Files and statistical data from this website may be downloaded, reproduced, distributed, shared, and used for commercial and non-commercial purposes (unless otherwise indicated), provided that any changes to the data are clearly indicated and the Statistical Office of the Republic of Serbia (SORS) is cited as the source of the original data." Verdict: may be public.
- **The bulletin "Energy Balances, 2024"** (final data, February 2026, 1.7 MB) was fetched once. Its table 1, "Balance of Electricity in 2024", is read from its GWh page.
- **A new table, `sors_serbia_electricity_annual`** (series, 36 rows, 20 entities, `power`), 2024: primary production by source (solar 0.16, wind 1.35, hydro 10.51 TWh), imports 6.94 and exports 6.42 TWh, gross production by plant type (37.49 TWh, thermal 23.22), own use in the energy sector by branch (3.96 TWh), losses (3.98 TWh) and final consumption by sector (29.55 TWh; households 13.23, industry 9.56).
  - Each section's parts sum to its total (gross production, own use, final consumption).
  - Written by run `20261024T192418Z`, validated (0 errors, 0 warnings), archived, held from the live set; public, so in the release package and the next draft.

## Cross-checks

- `eia_world_electricity_annual`'s Serbia for 2024: imports 6,936,172 and exports 6,416,312 MWh, equal to SORS's; generation 36.99 TWh against SORS's gross 37.49 TWh.

## Requests (5 of 20)

| n | What | Outcome |
|---|---|---|
| 1, 2 | www.stat.gov.rs and data.stat.gov.rs robots files | 404 |
| 3 | SORS's copyright page | 200 |
| 4 | publikacije.stat.gov.rs/robots.txt | 404 |
| 5 | the bulletin (the fetch) | 200, 1.7 MB |

Reads recorded: 964 to 967 (on this branch). Test 205's bound was raised by 40 for chain 123's reads. One web search found the bulletin; it reached no publisher's host.

## Decisions made without you

- **Serbia as the second own choice; public** under SORS's copyright page, the scaling to MWh stated.
- **One year:** the 2024 bulletin's table; earlier years are in earlier bulletins at other addresses.

## For Samuel's ruling

- None.

## Files

- New: `warehouse/connectors/sors_serbia_electricity.py`, `tests/test_session2525.py`, this report.
- Changed: the registration; the metadata files; `docs/redivis/release-v1/`; the license record (reads 964 to 967, one verdict); `tests/test_session205.py` (its bound).
- On the data machine only: `runs/c123/s2525/`, `warehouse/raw/sors_energy_balances/`, `warehouse/output/sors_serbia_electricity_annual.csv`.
