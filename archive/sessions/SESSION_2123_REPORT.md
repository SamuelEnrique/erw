# Session 2123 report: Europe's renewable capacity (Eurostat), in place of the world's (IRENA)

23 October 2026, from 22:50 UTC, on lab-desktop (the data machine), the fourth session of `queue/done/079-day-28-october-data-quakes-credits-rates-world-renewables.md`, unattended. Model spend USD 0. Pulls: 5 requests of 15 (below).

## Read these first

- **The file's source was taken first by chain 068:** IRENA's capacity statistics are `irena_capacity_annual` (session 2085, on chain 068's branch, its file in the shared output folder); www.irena.org refused that chain's reader. As the file says, this session took another public source the ERW does not hold: **Eurostat's electricity production capacities for renewables and wastes** (`nrg_inf_epcrw`), the European counterpart, in MW.
- **One table written, validated, archived, in coverage (sector power), in the release package, both holds:** `eurostat_renewable_capacity_annual`, each country's net maximum capacity by fuel or technology, 1990 to 2024: 49,313 rows, 39 countries and Eurostat's two aggregates (EU27_2020, EA21), 34 SIEC codes (hydro and its kinds, wind, solar thermal, solar photovoltaic and its size classes, the bioenergies, geothermal, tide, wastes), with solar photovoltaic's alternating and direct current ratings where a country reports them. Eurostat's last update: 9 October 2026.
- **The license** (read 244, a new verdict, may be public in both columns): Eurostat's copyright notice allows reuse of its statistical data "for commercial or non-commercial purposes ... provided the source is acknowledged", except data "for countries other than" the EU's member states, EFTA's and the official acceding and candidate countries, which may not be reused commercially. The table keeps only those: **the United Kingdom and Kosovo (a potential candidate, not an official one) are left out**, and the header names them. The notice asks that a modification be stated and Eurostat's non-responsibility said; the header does both.
- **The cross-check** (`runs/c079/s2123/cross.py`):
  - Against IRENA's capacity for Germany, France, Spain, Italy and Poland, 2015 to 2024: wind is the same to the MW in all five every year; solar photovoltaic is the same in Germany (91,204 MW in 2024) and within 0.974 to 1.100 of IRENA's elsewhere (France 25,299 against 25,673 in 2024), IRENA taking some countries' figures from other sources.
  - Eurostat's EU27_2020 total equals the sum of the 27 member states' rows for wind, hydro and solid biofuels in every year, and for solar photovoltaic from 2021; from 2015 to 2020 its solar total is 0.2 to 2.3 GW above the members' sum (85,344 MW against 83,236 in 2015), the aggregate not recomputed after a member state revised its earlier years. Eurostat's figure, written as published.

## The pulls

1. `ec.europa.eu/robots.txt` (read 242): disallows the old `/eurostat/SDMX/diss-web/rest/` and the search pages; `/eurostat/api/dissemination/` is not among them.
2. Eurostat's former copyright page (read 243): HTTP 404, moved.
3. The data set as SDMX-CSV (4.5 MB, 50,771 observations).
4. The copyright notice at its new address (read 244).
5. The SIEC codelist (SDMX-ML), for the English names.

The data and the codelist were seeded into the raw store from the probe; the trial and the write read them offline.

## Errors

- **One request spent on the copyright page's old address** (HTTP 404); the page's own links named the new one.

## Decisions made without you

- **Eurostat in place of IRENA:** the same kind of figure for Europe, from a publisher whose terms could be read.
- **The countries Eurostat's terms allow for commercial reuse only,** so that the verdict holds in both columns; the UK and Kosovo left out.
- **Greece written as GR in `geo`** (ISO 3166-1), Eurostat's EL kept in `x_geo_code` and the entity; the aggregates' `geo` blank.
- **The three plant technologies as three variables** (net, AC, DC), never one chosen for another.

## For Samuel's ruling

- None new.

## Files

- New: `warehouse/connectors/eurostat_res_capacity.py`, `tests/test_session2123.py`, this report.
- Changed: `warehouse/metadata/build_coverage.py`, `warehouse/redivis/release_v1.py`, `warehouse/supabase/live_set.yaml`, `warehouse/metadata/license_reads.csv` (242 to 244), `warehouse/metadata/license_verdicts.csv` (Eurostat), `tests/test_session205.py` (the bound raised once more), the coverage, sources, archive manifest and license files, `docs/redivis/release-v1/`.
- On the data machine only: `runs/c079/s2123/`, `runs/license_reads/s2123/`, `runs/s2123_*`, `warehouse/raw/eurostat_res_capacity/`.
