# Session 2492 report: Fiji's electricity production and sales, 2011 to 2024 (the Fiji Bureau of Statistics, from EFL's figures), public

24 October 2026, from about 14:59 UTC to 15:02 UTC for the reads and the connector; the table written under the data lock at 16:29 UTC. On lab-desktop (the data machine), chain 121, unattended. Precheck passed (`runs/c121/pre2492.out`). Model spend USD 0. Pulls: 7 requests of 15 (5 by the probe, 2 by the fetches the connector reads offline).

## Read these first

- **The ERW held no Fijian source** (`sources.csv` and the connectors on main and on chains 118's to 120's branches). Chain 119's session 2465 found efl.com.fj's pages a day's demand figure a post and its year pages frames with no figures, so the Bureau of Statistics was asked.
- **The Fiji Bureau of Statistics (FBoS):** www.statsfiji.gov.fj's robots file disallows nothing (read 826). Its site search (read 827) lists the Electricity reports 2010 to 2024 and Key Statistics tables 3.7A and 3.7B.
- **A new table, `fbos_fiji_electricity_annual`** (series, 83 rows, 5 entities, `power`), 2011 to 2024:
  - Energy Fiji Limited's units produced and sold, from table 3.7[A] (kWh, divided by 1,000);
  - its sales to industrial, commercial, domestic and other consumers, from Appendix III of "Electricity 2024" (February 2026).
  - The appendix heads its figures "kwh (000's)", but its totals are 3.7[A]'s units sold in millions of kWh. Each year's total is checked against 3.7[A] within 0.1 GWh (the run stops on a difference), so they are read as GWh.
  - Not written: one cell "n/a" (2011's others); the appendix's totals (checked); the sales' value (FJD).
  - Written by run `20261024T162915Z`, validated (0 errors, 0 warnings), archived, held from the live set. Public: its rows are added to the release package, and it goes in the next Stanford draft (session 2499).
- **Public, with a citation.** The report's page ii (read 831): "Any table or material published in this Report may be reproduced and published without the Fiji Bureau of Statistics' prior approval. However, the source of information should always be identified and acknowledged in all modes of presentation." The header carries the citation. Session 2495's verdict: may be public, sold or not.
- **Not taken:** generation by source (hydro, diesel, biomass, solar). Neither file gives it, and the report's questionnaire asks only for own generation.

## Cross-checks

- Units produced over `owid_ember_electricity_annual`'s demand for Fiji: 0.87 to 1.06 (2011 to 2024).
- Produced, GWh: 837.2 in 2011, 1,061.2 in 2019, 976.4 in 2020, 1,218.9 in 2024. Sold: 740.9, 945.4, 862.5 and 1,088.4.
- 2014's units sold are within 0.1 percent of its units produced, against 7 to 12 percent of production not sold in the other years; as printed.

## Requests (7 of 15)

| n | What | Outcome |
|---|---|---|
| 1 | www.statsfiji.gov.fj/robots.txt | 200: nothing closed |
| 2 | the site's search for electricity | 200 |
| 3 | table 3.7A's file page | 200: its download address |
| 4 | Electricity 2024's file page | 200 |
| 5 | table 3.7B's file page | 200 (3.7B not fetched: the report's Appendix III holds the same sales by type) |
| 6 | table 3.7[A] (the fetch) | 200, 136 kB |
| 7 | Electricity 2024 (the fetch) | 200, 678 kB |

Reads recorded: 826 to 831 (on this branch; read 831 is the report itself, its page ii).

## Errors

- **The second fetch reused the first's run folder** (`warehouse/raw/fbos_fiji_electricity/s2492-fetch/`) and rewrote its manifest, dropping table 3.7[A]'s row; the first offline trial stopped ("offline: ... is not in warehouse/raw"). The row was restored from the saved file, its retrieval time (in its name) and its hash, and the trial passed. No request was repeated.

## Decisions made without you

- **Appendix III read as GWh** on the strength of its totals, checked every year, not on its heading.
- **Public** under the report's reproduction statement, with the citation in the header.

## For Samuel's ruling

- None.

## Files

- New: `warehouse/connectors/fbos_fiji_electricity.py`, `tests/test_session2492.py`, this report.
- Changed: the registration; the metadata files; `docs/redivis/release-v1/` (the table's rows); the license record (reads 826 to 831).
- On the data machine only: `runs/c121/s2492/`, `warehouse/raw/fbos_fiji_electricity/`, `warehouse/output/fbos_fiji_electricity_annual.csv`.
