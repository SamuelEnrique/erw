# Session 2656 report: the French island grids' electricity by source a year, 2018 to 2024 (EDF SEI's open data), public, a third source of the session's own choosing

25 October 2026, about 09:12 to 09:30 UTC, on lab-desktop (the data machine), chain 132, unattended. Precheck passed (`runs/c132/pre2656.out`). Model spend USD 0. Pulls: 9 requests of 20 (8 by the probe, 1 GET the connector's online trial made; the write reads it offline).

## First: a redirect followed to a host before its robots file was read

- Request 1 asked opendata-corse-outremer.edf.fr for its robots file. The host sent it to opendata.edf.fr's home page, a new host.
- I did not read the answer's final address before request 4, which asked the old host for the dataset's record. That request too was sent to opendata.edf.fr's home page.
- So that home page was fetched twice before opendata.edf.fr's robots file (request 5) was read. The chain's rule is that a redirect to a new host is a new host, its robots file asked before the next request to it.
- The robots file allows every path to every reader (read 1331), so nothing it bars was read. From the second copy of the home page I took only the API's path (`/data-fair/api/v1/datasets/`).
- From here on, every probe's final address is read before the next request.

## Why this source

- **The ERW held none of the French island grids in a table**, and no chain or queue file had taken them. The grids are Corsica, Reunion, Guadeloupe, Martinique, French Guiana, Saint-Pierre-et-Miquelon, Saint-Barthelemy, Saint-Martin and the Iles du Ponant.
- The ERW's Ember table holds only these grids' demand, and IRENA's only their capacity.
- **Others checked first in the record:** Puerto Rico, already held plant by plant in the EIA-923 tables. Greenland, held (Statistics Greenland, session 2510). Many small territories without a table were tried by earlier chains (the Isle of Man, Bermuda, Sint Maarten and the Turks and Caicos Islands among them).

## Read these first

- **The way in:** data.gouv.fr's robots file (read 1328) leaves its dataset API open. Its record of EDF SEI's dataset (read 1329) gives the license fr-lo and files exported from opendata-corse-outremer.edf.fr.
- That host now sends every request to EDF's new open data portal, opendata.edf.fr (reads 1327 and 1330). Its robots file allows `/` to `*`, with a content signal: search yes, ai-train no, ai-input yes (read 1331). The ERW trains nothing.
- The portal's data-fair API (read 1332) lists one dataset with all the island grids and one for each. The full dataset's record (read 1333) gives 58 lines, 2018 to 2024, its data last updated on 23 October 2025, and the license "Licence Ouverte (Etalab)".
- **Verdict: may be public**, the sentence cut by code from read 1333. The table is **public**.
  - The licence's own text was not read: www.etalab.gouv.fr sends every request to data.gouv.fr's home page (read 1334).
  - The licence is read as an open licence like CC BY.
- **A new table, `edf_sei_islands_electricity_annual`** (series, 326 rows, 51 entities, `power`), from one GET of the dataset's lines:
  - **What it holds:** net production by source (`generation`) for 9 territories; Corsica's links with Sardinia and Italy (`net_imports`); the total (`supply`). MWh as published.
  - **2024 totals, in GWh:** Reunion 3,064.2, of it bioenergy 2,069.0. Corsica 2,255.4, of it the links 619.8. Guadeloupe 1,691.6, Martinique 1,548.2, French Guiana 981.3, Saint-Martin 194.1, Saint-Barthelemy 150.0, Saint-Pierre-et-Miquelon 47.8 and the Iles du Ponant 9.6.
  - **Checks:** each year's published sources add to its total within 0.02 per cent; the run stops past 1 per cent.
  - **Small cells kept as published:** EDF's note says hydro in Martinique and solar in Saint-Barthelemy are not published, yet the file gives a few small figures for them.
  - **Codes:** `geo` is each territory's ISO code: FR-20R for Corsica, and FR for the Iles du Ponant, which lie in two regions.
  - **Its record:** written by run `20261025T092016Z` under the data lock and validated (exit 0). It is in coverage, archived (`20261025T092021Z-local`) and held from the live set. It is in the release package (public).
- **The method note**, `docs/methods/edf_sei_islands_electricity_annual.md`, was written in this session. All 33 figures it names were checked against the table, with 0 differences. Its Method cell is set.
- **Not taken:** the per cent columns; the hourly production and cost datasets of each territory, for a later chain.

## Cross-checks

Against the ERW's `owid_ember_electricity_annual`, whose demand is rounded to 0.01 TWh, for 2022 and 2023 (EDF's figure first):

| Grid | 2022, EDF | 2022, Ember | 2023, EDF | 2023, Ember |
|---|---|---|---|---|
| Guadeloupe | 1,636.6 | 1,640 | 1,670.1 | 1,670 |
| Martinique | 1,485.8 | 1,490 | 1,506.8 | 1,510 |
| French Guiana | 946.4 | 950 | 971.5 | 980 |
| Reunion | 3,062.6 | 3,060 | 3,081.6 | 3,070 |
| Saint-Pierre-et-Miquelon | 49.7 | 50 | 48.8 | 50 |

Each pair agrees within the rounding except Reunion and French Guiana in 2023 (0.4 and 0.9 per cent apart).

## Requests (9 of 20)

| n | What | Outcome |
|---|---|---|
| 1 | opendata-corse-outremer.edf.fr's robots address | 200, sent to opendata.edf.fr's home page |
| 2, 3 | data.gouv.fr's robots file and its record of the dataset | 200 |
| 4 | the old portal's dataset address | 200, sent to opendata.edf.fr's home page |
| 5 | opendata.edf.fr's robots file | 200 |
| 6, 7 | the data-fair API's dataset search and the dataset's record | 200 |
| 8 | www.etalab.gouv.fr's robots address | 200, sent to data.gouv.fr's home page |
| 9 | the dataset's lines (by the connector's online trial) | 200 |

Reads recorded: 1327 to 1334.

## Decisions made without you

- **The French island grids as the third own choice; public** under the Licence Ouverte, read as the dataset's records state it, without the licence's own text.
- **`geo` FR for the Iles du Ponant**, which lie off Brittany and Normandy: no one subdivision code covers them.
- **Not in this chain's Stanford draft:** session 2653 uploaded before this table existed; it waits for the next draft.

## For Samuel's ruling

- **The redirect at the top:** whether the lapse needs more than the reported fix.

## Files

- New: `warehouse/connectors/edf_sei_islands_electricity.py`, `tests/test_session2656.py`, `docs/methods/edf_sei_islands_electricity_annual.md`, this report.
- Changed: the registration; the metadata files; the release package (`docs/redivis/release-v1/`); the license record (reads 1327 to 1334, EDF SEI's verdict) and `docs/licenses.md`; `docs/coverage.md`.
- On the data machine only: `runs/c132/s2656/`, `runs/license_reads/s2656/`, `warehouse/raw/edf_sei/`, `warehouse/output/edf_sei_islands_electricity_annual.csv`.
