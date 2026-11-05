# Session 2510 report: Greenland's renewable electricity, 1996 to 2024, and Nukissiorfiit's sales, 2004 to 2024 (Statistics Greenland), the session's own choice, internal

24 October 2026, about 17:49 to 17:53 UTC for the reads and the connector; the table written under the data lock at 18:22 UTC. On lab-desktop (the data machine), chain 122, unattended. Precheck passed (`runs/c122/pre2510.out`). Model spend USD 0. Pulls: 13 requests of 20 (11 by the probe, 2 by the connector's queries).

## Read these first

- **Why Greenland:** a grid the ERW did not hold (`sources.csv`, `license_verdicts.csv` and `warehouse/output/retired/` searched), published through a PxWeb API.
- **Statistics Greenland:** stat.gl and bank.stat.gl have no robots file (reads 908, 909). stat.gl's llms.txt (read 917) asks agents to use the Statbank API rather than its pages and to cite the Statbank with a link to the table; it states no licence for the statistics.
- **Two tables** of the Statbank's energy folder (reads 910 to 915):
  - ENX3VVE, renewable energy produced and consumed by source (hydropower, waste), 1996 to 2024, in MWh (TJ not taken);
  - ENX4NUK, the electricity Nukissiorfiit (the national utility) sold by location (the country, towns, settlements, five municipalities, their towns and settlements) and rate (normal, fishing industry, electric heating), 2004 to 2024; kWh to MWh. District heating and water not taken.
  - Every value of every dimension is selected in the query (an empty query would eliminate a dimension, as in session 2502).
- **A new table, `statgl_greenland_electricity_annual`** (series, 2,064 rows, 33 entities, `power`). Written by run `20261024T182205Z`, validated (0 errors, 0 warnings), archived, held from the Redivis storage and the live set.
- **Internal, not settled.** No page of terms for the statistics was found within the ceiling. The "CC-BY-4.0" of Statistics Greenland's agent profile (read 918) licenses that profile, not the data.

## Cross-checks

- Hydropower production, GWh: 162 in 1996, 207 in 2005, 423 in 2015, 487 in 2024; over `owid_ember_electricity_annual`'s demand for Greenland, 0.56 in 1996 rising to 0.81 in 2024 (diesel supplies the rest).
- Nukissiorfiit's sales at normal rates: 153 GWh in 2004, 229 GWh in 2024.

## Requests (13 of 20)

| n | What | Outcome |
|---|---|---|
| 1, 2 | stat.gl and bank.stat.gl robots addresses | no robots file |
| 3 to 6 | the Statbank API down to the energy tables | 200 |
| 7, 8 | the two tables' metadata | 200 |
| 9 | stat.gl's English home page | 200: no terms page linked |
| 10 | stat.gl's llms.txt | 200 |
| 11 | the Statbank agent profile | 200: CC-BY-4.0 for itself |
| 12, 13 | ENX3VVE and ENX4NUK by POST | 200 |

Reads recorded: 908 to 918 (on this branch). One web search for the terms reached no publisher's host.

## Decisions made without you

- **Greenland as the session's own choice; internal** until the statistics' terms are read.

## For Samuel's ruling

- **Statistics Greenland's terms for its Statbank data:** a page saying so, or a letter, would likely make the table public.

## Files

- New: `warehouse/connectors/statgl_greenland_electricity.py`, `tests/test_session2510.py`, this report.
- Changed: the registration; the metadata files; the license record (reads 908 to 918).
- On the data machine only: `runs/c122/s2510/`, `warehouse/raw/statgl_energy/`, `warehouse/output/statgl_greenland_electricity_annual.csv`.
