# Cote d'Ivoire's electricity a year from the regulator, ANARE-CI: gross generation by kind of plant, national consumption by voltage and the system's peak demand, 1960 to 2020

Energy Research Warehouse (ERW), method note written in session 2471 (chain 119) for a table first written on 24 October 2026 (session 2463 of chain 119, `archive/sessions/SESSION_2463_REPORT.md`), taken from the regulator since CI-ENERGIES' host does not resolve. Session 2467's licenses round (`archive/sessions/SESSION_2467_REPORT.md`) recorded no verdict: the pages state no terms of reuse. Ember's yearly demand for Cote d'Ivoire, against which session 2463 compared it, is in `owid_ember_electricity_annual` (entity `owid_energy:CIV`).

Tables: `anare_cotedivoire_electricity_annual`

## Publisher and address

ANARE-CI (Autorite nationale de regulation du secteur de l'electricite de Cote d'Ivoire), the "Open Data" pages of anare.ci: three HTML pages, each with one table (wpDataTables) and a chart, asked by GET without a key:

- `https://anare.ci/big-data-2/production-brute-delectricite-2/`: "Production brute d'electricite (GWh)", columns Annee, Hydraulique, Thermique, Centrales Isolees;
- `https://anare.ci/anare/consommation-nat-2/` (answered at `https://anare.ci/big-data-2/consommation-nat-2/`): "Consommation nat (GWh)", columns Annee, BT, HT/MT;
- `https://anare.ci/anare/pointe-mw-2/` (answered at `https://anare.ci/big-data-2/pointe-mw-2/`): "Pointe MW", columns Annee, MW.

The pages print the accents (Annee, Electricite, Isolees) that this note leaves out. The unit of the generation and consumption tables is the one their charts give ("(GWh)"); the tables themselves carry no unit. The installed capacity page (`https://anare.ci/anare/puissance-installee-totale-2/`, answered at `.../big-data-2/puissance-installee-totale-2/`) draws a chart with no table and is not read.

Source id `anare_ci:open_data` (`sources.csv`: license internal, first and last seen 2026-10-24).

Saved pages, in `warehouse/raw/anare_cotedivoire/20261024T125629Z_probe/`, fetched by session 2463's probe, not by the connector, each HTTP 200 with no Last-Modified:

| Page | Bytes | sha256 | Retrieved (UTC) |
|---|---|---|---|
| Generation | 264,718 | `0a48d59b...` | 2026-10-24T12:57:13Z |
| Peak | 257,260 | `44926681...` | 12:57:39Z |
| Consumption | 261,086 | `77ab4dc8...` | 12:57:44Z |

The folder's `manifest.csv` lists the peak and consumption files twice, once under the address asked (`/anare/...`) and once under the address that answered (`/big-data-2/...`), with the same hash; the hashes recomputed in session 2471 agree. The connector's run folders (`20261024T125919Z`, an empty manifest, and `20261024T125928Z`) hold only the data-lock check, so its runs were offline.

Session 2463 made 8 requests of 15 (`runs/c119/s2463/probe.csv`):
- www.cienergies.ci's robots address (the name does not resolve);
- www.anare.ci's robots file (14 bytes, Last-Modified 25 March 2021) and its home page, which redirects to anare.ci;
- anare.ci's robots file (the same 14 bytes), asked before any other path of that host;
- the three pages read and the installed capacity page.

Both robots files are one line, "User-agent: *", which disallows nothing and names no AI agent. These are reads 814 to 817 in `docs/licenses.md`; the data pages are not counted there.

Connector: `warehouse/connectors/anare_cotedivoire.py` (session 2463), `[--offline] [--out-dir DIR]`.
- **Ceiling:** three requests, 2 seconds apart; saved pages reused with `--offline`. A paused `anare_ci` or host anare.ci is never asked.
- **Values:** generation and consumption are ANARE-CI's GWh times 1,000, written as MWh; peak demand is MW as printed.
- **A year printed twice** with the same figures is taken once (2019 in the generation table); twice with different figures stops the run. A blank cell has no row. No total is computed.
- **Stops also:** a page with other than one table, a header not ANARE-CI's, a row that does not read, a value not a number, or a key given twice.

## Schedule and records

Schedule: none. No shell script under `warehouse/`, no workflow in `.github/workflows/`, no file in `scripts/` and not `warehouse/scheduled.py` names it.

Records:
- `runs/status/anare_cotedivoire.json` (main checkout): run `20261024T125928Z`, ok, "361 rows". `run_status.csv`: no row.
- `archive_manifest.csv`: 361 rows, run `20261024T125933Z-local`, `data_sha256` `c9f28684...` (not recomputed here).
- `coverage.csv`: iso `anare`, 1 node, P1Y, 1960-01-01 to 2020-01-01, 361 rows, last run 2026-10-24T12:59:28Z, validator pass, license internal, sector power, tier source.
- Live set: listed under `catalogue_hold` in `warehouse/supabase/live_set.yaml`, not loaded.
- Release: no row in `docs/redivis/release-v1/tables.csv` and not in `STORAGE_HELD`: an internal table is not in version 1.
- Package: `package/src/erw/data/tables.csv` has its row (internal, "not settled (needs written permission by default)") since session 2473; `site/data/table_citations.json` and `table_verdicts.json` have none.
- `license_tables.csv`: ANARE-CI, Cote d'Ivoire's electricity regulator, "the source registry".

Readers: none. `tests/test_session2463.py` (3 tests) tests the reader on HTML built in the test.

License: no terms of reuse on the pages read (read 816, the home page: "no terms of reuse linked"). `docs/licenses.md`, the table's row: verdict "not settled (needs written permission by default)", flag internal, "not settled"; listed among the tables whose publisher no read covers. Header line 9: "internal. ANARE-CI's pages state no terms of reuse; internal until a ruling. Cite: ANARE-CI, Open Data."

## Vintage and revision

One write, run `20261024T125928Z`, offline from the saved pages; header line 10: "This run wrote 361 rows: 361 new, 0 replacing earlier rows ...; 0 rows are kept from earlier runs." `retrieved_at` is the page's fetch (the table above) in every row from that page; `source_url` is the address asked, so the `/anare/...` form for consumption and peak. `vintage` is blank in every row: the pages carry no Last-Modified.

The pages end in 2020; a later year comes only if ANARE-CI adds it. A revised figure replaces the old one by (entity, variable, ts_utc); no earlier version is kept.

## Shape and variables

Series, 361 rows, 13 columns (`entity, variable, ts_utc, value, unit, freq, geo, market, node, source, source_url, retrieved_at, vintage`), 10 header lines. `entity` `anare_ci:CI` in every row; `node` Cote d'Ivoire; `geo` CI; `freq` P1Y; `ts_utc` the year's 1 January, 1960 to 2020; `market` blank.

- **Variables, 6:**
  - `generation_hydro`, `generation_thermal`: 61 rows each, 1960 to 2020, MWh;
  - `generation_isolated` ("Centrales Isolees"): 56 rows, MWh, no row in 1986 to 1990, where the page's cells are blank;
  - `consumption_low_voltage` (BT), `consumption_high_medium_voltage` (HT/MT): 61 rows each, MWh;
  - `peak_demand`: 61 rows, MW.
- **Units:** MWh in 300 rows, MW in 61.
- **Values:** every figure on the pages is a whole number (GWh or MW); no zero, no negative.
- **The largest value** is thermal generation in 2016, 8,543,000 MWh. Peak demand runs from 11 MW (1960) to 1,545 MW (2020).

Selected years (GWh; peak in MW):

| Year | Hydro | Thermal | Isolated | Low voltage | High and medium voltage | Peak |
|---|---|---|---|---|---|---|
| 1960 | 59 | 4 | 6 | 30 | 27 | 11 |
| 1970 | 260 | 178 | 78 | 204 | 225 | 70 |
| 1980 | 1,352 | 343 | 55 | 688 | 831 | 262 |
| 1990 | 1,322 | 656 | | 826 | 1,113 | 369 |
| 2000 | 1,764 | 3,036 | 13 | 1,375 | 1,517 | 594 |
| 2010 | 1,618 | 4,258 | 8 | 2,161 | 1,879 | 912 |
| 2015 | 1,353 | 7,255 | 10 | 3,192 | 2,743 | 1,193 |
| 2016 | 1,529 | 8,543 | 8 | 3,506 | 2,900 | 1,288 |
| 2017 | 2,047 | 7,894 | 7 | 3,576 | 3,059 | 1,342 |
| 2018 | 2,962 | 7,028 | 7 | 3,803 | 3,147 | 1,388 |
| 2019 | 3,481 | 7,125 | 7 | 4,145 | 3,494 | 1,443 |
| 2020 | 3,376 | 7,828 | 6 | 4,325 | 3,699 | 1,545 |

## Checks

Counted in session 2471 from the table in the main checkout (`C:\Users\Shared\Documents\erw\warehouse\output`), read past its 10 header lines with `keep_default_na=False`, and from the saved pages, by scripts outside the repository. No request was made.

- 361 rows, 1960 to 2020, as header line 10 states; no (entity, variable, ts_utc) twice; no blank value.
- **The saved pages:** the generation table has 62 rows for 61 years, 2019 printed twice with the same figures (3,481, 7,125, 7); the peak and consumption tables have 61 rows each. The generation table's blank cells are the isolated plants' in 1986, 1987, 1988, 1989 and 1990, and no other. No figure on the three pages has a decimal.
- **Rows by variable** add to 361: 61 x 5 + 56.
- **Against Ember** (`owid_ember_electricity_annual`, `owid_energy:CIV`, `electricity_demand`), 2016 to 2020:

| Year | Generation, three kinds (GWh) | Consumption, BT + HT/MT (GWh) | Ember's demand (GWh) | Generation / Ember | Consumption / Ember |
|---|---|---|---|---|---|
| 2016 | 10,080 | 6,406 | 9,020 | 1.118 | 0.710 |
| 2017 | 9,948 | 6,635 | 8,260 | 1.204 | 0.803 |
| 2018 | 9,997 | 6,950 | 8,990 | 1.112 | 0.773 |
| 2019 | 10,613 | 7,639 | 9,570 | 1.109 | 0.798 |
| 2020 | 11,210 | 8,024 | 10,140 | 1.106 | 0.791 |

  The report's ranges (generation 1.11 to 1.20 times Ember's demand, consumption 0.71 to 0.80) and its 2020 figures (11,210, 8,024, 10,140 GWh) hold, rounded to two places. These sums are made for the check only; the table holds no total. The report notes that the country exports power and that consumption is net of losses; neither exports nor losses are on the pages.
- No contradiction was found between the connector's docstring, its header and the table.

## What it cannot say

- **After 2020:** the pages end there.
- **A total generation or consumption** as ANARE-CI would state it: the pages give none, and the table computes none.
- **Exports, imports, losses and own use:** not on the pages read.
- **Installed capacity:** its page has a chart and no table.
- **Isolated plants in 1986 to 1990:** blank on the page.
- **Whether a figure is gross or net beyond the page's titles** ("Production brute", gross generation; "Consommation nat"): no definitions are given on the pages read.
- **Earlier versions of a revised year.**

## Acted on in session 2471

- **Nothing to act on.** The checks found no contradiction, and the table is internal, so it is not in the Stanford draft.
