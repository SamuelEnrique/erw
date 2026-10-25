# The French island grids' electricity by source a year, 2018 to 2024 (EDF SEI's open data)

Energy Research Warehouse (ERW), method note written in session 2656 (chain 132) with the table, first written on 25 October 2026.

Tables: `edf_sei_islands_electricity_annual`

## Publisher and address

EDF SA, through EDF Systemes Energetiques Insulaires (EDF SEI), the arm that runs the grids of the French islands not tied to mainland France's grid. The dataset is "Production annuelle d'electricite par filiere d'EDF SA en Corse & Outremer" on EDF's open data portal, `https://opendata.edf.fr/datasets/production-annuelle-delectricite-par-filiere`. It is read through the portal's data-fair API, one GET of its lines (`/data-fair/api/v1/datasets/production-annuelle-delectricite-par-filiere/lines?size=1000`), no key. Source id `edf_sei:production-annuelle-delectricite-par-filiere`. Connector: `warehouse/connectors/edf_sei_islands_electricity.py` (session 2656), whose raw store is `warehouse/raw/edf_sei/` (`lines.json`, the answer with its time of retrieval).

How the reader reached it:
- data.gouv.fr's record of the dataset (read 1329) names the old portal, opendata-corse-outremer.edf.fr. That host now sends every request to opendata.edf.fr's home page (reads 1327 and 1330).
- opendata.edf.fr's robots file allows every path (read 1331). It carries a content signal: search yes, ai-train no, ai-input yes. The ERW trains nothing.

## Vintage and revision

Written by run `20261025T092016Z` (the write under the lock, offline), which read the answer retrieved at 2026-10-25T09:17:20Z. `vintage` is empty. The dataset's record gives its data's last update as 23 October 2025, its period as 2018 to 2024, and its frequency as annual (read 1333). EDF adds a year at a time.

## Shape and variables

Series, 326 rows, 51 entities, each year from 2018 to 2024; the Iles du Ponant from 2023 only. `entity` `edf_sei:<territory>:<source>`:
- **Territories** (`geo`):
  - `corsica` (FR-20R), `reunion` (RE), `guadeloupe` (GP), `martinique` (MQ), `french_guiana` (GF);
  - `saint_pierre_miquelon` (PM), `saint_barthelemy` (BL), `saint_martin` (MF);
  - `iles_du_ponant` (FR: the small islands off Brittany and Normandy).
- **Sources:**
  - `generation`: `bioenergy`, `coal`, `wind`, `geothermal`, `hydro`, `diesel` (diesel engines), `solar` and `oil_turbines` (oil-fired combustion turbines);
  - `net_imports`: `links`, Corsica's links with Sardinia and Italy, the net of what they inject and withdraw;
  - `supply`: `total`.

`unit` MWh, as published and rounded to the MWh; `ts_utc` the year's first day; `freq` P1Y; `node` the territory as EDF names it.

Some 2024 totals, in GWh:
- Reunion 3,064.2: bioenergy 2,069.0, hydro 419.2, solar 310.6, coal 40.6.
- Corsica 2,255.4: the links 619.8, diesel 839.9, hydro 430.0.
- Guadeloupe 1,691.6: coal 236.6, geothermal 94.1.
- Martinique 1,548.2; French Guiana 981.3 (hydro 288.7); Saint-Martin 194.1; Saint-Barthelemy 150.0; Saint-Pierre-et-Miquelon 47.8, all of it diesel; the Iles du Ponant 9.6.

From 2018 to 2024, Saint-Barthelemy's total rose 49.1 per cent and Saint-Martin's 32.3 per cent.

EDF's notes:
- The figures are the net energy injected into each territory's grid. The total adds every source and the storage balance.
- Household waste incineration counts at half in the renewable share. The share is not taken.
- A source of fewer than ten installations under 36 kVA in a territory is not published (hydro in Martinique, solar in Saint-Barthelemy). The file still gives a few small figures for them: Martinique's hydro 13 MWh in 2019 and 15 in 2020, and Saint-Barthelemy's solar 4 to 49 MWh from 2019 to 2023 and 0 in 2024. They are kept as published.

## Reading the source

- The run stops at once, asking nothing, while `edf_sei` or opendata.edf.fr is paused.
- One request a run, refused if it is sent to another host; `--offline` reads the saved answer.
- A cell without a number has no row. The per cent columns are not taken. Nothing is filled.
- **Check:** each year's published sources add to its total within 1 per cent. In the file of 2026 they agree within 0.02 per cent.
- The run stops, and no file is written, for:
  - a column or territory not in the map;
  - a year not of four digits;
  - a count of lines not the dataset's total;
  - a key given twice;
  - a negative production;
  - a check missed.

## License

Public. The dataset's record on the portal (read 1333) gives the license as `"license":{"title":"Licence Ouverte (Etalab)", ...}`, and data.gouv.fr's record gives fr-lo (read 1329). The licence's own text was not read: www.etalab.gouv.fr sends every request to data.gouv.fr's home page (read 1334). The licence is read as an open licence like CC BY. Verdict: may be public. Cited as "Source: EDF SA (EDF Systemes Energetiques Insulaires)". In the release package; held from the live set.

## Cross-check

The ERW's `owid_ember_electricity_annual` gives each grid's electricity demand to 0.01 TWh. Against EDF's totals, in GWh:

| Grid | 2022, Ember | 2022, EDF | 2023, Ember | 2023, EDF |
|---|---|---|---|---|
| Guadeloupe | 1,640 | 1,636.6 | 1,670 | 1,670.1 |
| Martinique | 1,490 | 1,485.8 | 1,510 | 1,506.8 |
| French Guiana | 950 | 946.4 | 980 | 971.5 |
| Reunion | 3,060 | 3,062.6 | 3,070 | 3,081.6 |
| Saint-Pierre-et-Miquelon | 50 | 49.7 | 50 | 48.8 |

Each pair agrees within Ember's rounding, except Reunion in 2023 (0.4 per cent apart) and French Guiana in 2023 (0.9 per cent). EIA's world table in the ERW holds none of these grids. IRENA's capacity table holds Guadeloupe, French Guiana, Martinique, Reunion and Saint-Pierre-et-Miquelon, but not their production.
