# Session 3846 report, with 3847: the New York rows' utilities' large-load tariffs, from the Commission's own copies

Energy Research Warehouse (ERW). Chain 221, data machine (lab-desktop), 13 November 2026 05:35 to 05:50 UTC. Opus 5.5. Model spend USD 0. Requests: 14 in session 3846 and 4 in session 3847 (under 25 each), all to the New York Department of Public Service's hosts, kept at `runs/license_reads/s3846/` and `s3847/` (not in git).

## Read these first

- **The NYISO rows' "Transmission and 4CP" cell is filled for six of seven rows.** No session before had tried the Commission's own copies; the utilities' own sites are closed to this reader (Con Edison's and National Grid's terms, NYSEG's robots address, sessions 2921 and 2937).
  - The New York Department of Public Service serves every effective tariff through its Electronic Tariff System (`ets.dps.ny.gov`).
  - Robots: `documents.dps.ny.gov` and `ets.dps.ny.gov` have no robots file (HTTP 404). `dps.ny.gov`'s and `www.ny.gov`'s disallow only admin, search and login paths, and neither names an AI agent.
  - Terms: the DPS's Disclaimer (`dps.ny.gov/disclaimer`) sets no condition on reuse.
- **Three schedules joined `utility_large_load_tariffs`** (now 29 schedules, 95 rows, 22 utilities). Each figure is written as its leaf prints it, with its PDF page:
  - **Niagara Mohawk (National Grid), EIA 13573**, the utility of the CAPITL, WEST, GENESE and CENTRL rows. S.C. No. 3A over 60 kV, PSC No. 220 Leaf 391 (effective 1 April 2026): $10,350.00 a month and $4.89 per kW. It applies above 2,000 kW, with a one-year term.
  - **NYSEG, EIA 13511**, the utility of the DUNWOD and MILLWD rows. S.C. 7-4 Transmission (115 kV and above), PSC No. 120 Leaf 215 (effective 1 June 2026): $5,900.00 a month and $2.07 per kW on-peak. It applies from 500 kW.
  - **Con Edison, EIA 4226**, the utility of the N.Y.C. row. S.C. No. 9 Rate II, PSC No. 10 Leaf 449 (effective 1 February 2026): $510.00 a month and $0.0079 per kWh, mandatory above 1,500 kW. Its demand charges are printed by time period and summed. A high tension customer pays two figures in June to September, so no summer figure is written; in the other months it pays one, $19.41 per kW, written as `demand_charge_winter`.
- **The table** was written under the data lock (95 rows: 11 new, 84 replaced), validated (exit 0), archived (`20261113T054711Z-local`, 11 rows) and given its coverage row. Its records were already in place: the table is public row by row and its source `filed:large_load_tariffs` was registered.
- **The tab:** `site/data/siting/tariffs.json` gained only the three utilities' keys. On the tab:
  - the four Niagara Mohawk rows read "$4.89/kW-mo";
  - the two NYSEG rows read "$2.07/kW-mo";
  - N.Y.C. reads "tariff filed" (no single demand figure);
  - each shows the filing on hover;
  - LONGIL (Long Island Power Authority's territory) still reads "not held".
  - Seen on the gate's build in session 3850.

## What was asked

| n | What | Answer |
|---|---|---|
| 1, 11 | `documents.dps.ny.gov/robots.txt`, `ets.dps.ny.gov/robots.txt` | 404 (none) |
| 2, 3 | `dps.ny.gov/robots.txt`, `www.ny.gov/robots.txt` | 200 |
| 4, 5 | `dps.ny.gov/`, `/disclaimer` | 200 |
| 6 to 9 | `dps.ny.gov/sitemap.xml` and its three pages | 200 |
| 10 | `dps.ny.gov/electric-tariffs` | 200 |
| 12 | the system's list of effective electric tariffs | 200 |
| 13, 14 | Niagara Mohawk PSC No. 220: its leaves listing and the PDF (49.7 MB, 692 pages) | 200 |
| 3847: 1 to 4 | Con Edison PSC No. 10 and NYSEG PSC No. 120: their listings and PDFs (65.4 MB, 760 pages; 47.3 MB, 657 pages) | 200 |

## Decisions made without you

- **The Commission's copy is read where the utility's site is closed,** as the README of the registry allows ("the commission's docket copy or the utility's filed tariff book").
- **The delivery voltage a 100 MW load connects at** (over 60 kV; 115 kV and above; high tension) is the column written. The lower voltages' figures are in the leaf and named in each file's comment.
- **Niagara Mohawk's "Distribution Delivery Charges" are written as `demand_charge`:** the class prints one delivery demand charge a voltage.
- **A summed time-of-day demand charge is not summed by the ERW** (Con Edison's summer); only a figure printed as the one charge is written.
- **The document address** is the system's stable listing of each tariff's effective leaves; the PDF's own address there is a per-request token.

## For Samuel's ruling

- None new. National Grid's, Con Edison's and NYSEG's own sites stay closed; their Commission's copies are public.
