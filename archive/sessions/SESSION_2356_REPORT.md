# Session 2356 report: Europe's electricity capacity by fuel group and operator (Eurostat), a third source of the session's own choosing

24 October 2026, from 07:14 UTC, on lab-desktop (the data machine), a session of `queue/done/105-day-8-november-data-mexico-india-peru-korea.md`, there numbered 2306. The code machine's `wip/2306-audit-fixes` holds 2306, so this chain's sessions 2300 to 2306 are 2350 to 2356 (session 2350's report). Model spend USD 0.

Pulls: 14 requests of 20:
- **eSett:**
  - opendata.esett.com's robots address (the app's page, no robots file);
  - api.opendata.esett.com's robots address (HTTP 404);
  - a guessed API description address (HTTP 404);
  - the site's two script bundles.
- **NB Power:**
  - tso.nbpower.com's robots file;
  - its public home page;
  - its market data page;
  - its system information archive page.
- **BLS:** api.bls.gov's robots file.
- **Eurostat:**
  - ec.europa.eu's robots file;
  - nrg_inf_epc;
  - the SIEC codelist;
  - the PLANT_TEC codelist.

The trial and the write ran offline.

## Read these first

- **Three sources tried first, none open to the reader:**
  - **eSett Open Data** (the Nordic imbalance settlement, which continues Mimer's Swedish production statistics from 18 March 2025). Its pages are a script application: the API's addresses and its terms page are only in lazily loaded chunks, so finding them would mean fetching chunks blind. Left for a later session.
  - **NB Power's system operator** (New Brunswick's load and its flows with ISO-NE). Its robots file closes `/Reports`, `/SystemInformation` and other root paths, and the public archive page is an ASP.NET form answered only by POST, which the reader cannot send.
  - **The Bureau of Labor Statistics' API.** api.bls.gov's robots file disallows `/` to every reader.
- **Eurostat's `nrg_inf_epc`, not held:** the ERW held only the renewables and wastes capacity (`nrg_inf_epcrw`). This adds every fuel group, fossil and nuclear included, and the operator split.
- **One series table, `eurostat_electricity_capacity_annual`:** 159,060 figures, public. Eurostat's verdict is on record: reuse is authorised provided the source is acknowledged.
  - **Coverage:** net maximum electrical capacity, with the capacity commissioned and decommissioned in the year, in MW, 1990 to 2024, 38 European countries and Eurostat's EU27 and euro area aggregates.
  - **Variables:** 9, each a plant technology (net, commissioned or decommissioned) for an operator (total, main activity producers or autoproducers).
  - **Entities:** 1,072, one for each country and SIEC fuel group.
  - **Left out:** Kosovo, by Eurostat's terms, as the held Eurostat connectors do.
- **The checks:**
  - **Operators:** main producers plus autoproducers equal the total in all 30,450 pairs.
  - **Against the held renewables table** (`eurostat_renewable_capacity_annual`), the same capacity:

    | Fuel | Country-years equal within 0.5 MW |
    |---|---|
    | Wind | 1,244 of 1,294 |
    | Solar photovoltaic | 1,155 of 1,269 |
    | Hydro | 1,275 of 1,294 |

    The largest gaps are Romania 2023, where `eurostat_renewable_capacity_annual` holds 0.0 for hydro, wind and solar photovoltaic: a zero in that table, not a second estimate. The counts include the EU27 and euro area rows; the 38 countries alone give 1,200 of 1,224, 1,128 of 1,199 and 1,210 of 1,224 (corrected by session 2366).
  - **The EU in 2024:** 1,170 GW in all, of which combustible fuels 367, natural gas 164, coal 77, nuclear 97 (Eurostat's N9000, "nuclear fuels and other fuels n.e.c.", in effect nuclear), hydro 153, wind 231 and solar photovoltaic 306 GW.
- **Registered:** the sector rule (`power`), the live-set hold, the release package's held list (public), its rows in `docs/redivis/release-v1/` (the release check passes), and the license tables (licenses check: 492 tables, 0 problems). The test is `tests/test_session2356.py` (3 tests).
- **Not uploaded to the Stanford draft yet.** The next draft session takes it (the note says so).

## Errors

- **The test's first fixture wrote "1,5" for a bad value,** which shifted the columns; it is now a value with no comma.
- **The write's metadata patch did not apply** (the main checkout lags main). The table's own rows were put in by `runs/c102/add_own_rows.py` and checked: one row in each file.

## Decisions made without you

- **Eurostat's `nrg_inf_epc`** after eSett, NB Power and BLS were found closed or unreachable.
- **eSett left for a later session.** Its chunks would have to be fetched blind to find the API.

## For Samuel's ruling

- None new.

## Files

- New: `warehouse/connectors/eurostat_capacity.py`, `tests/test_session2356.py`, this report.
- Changed:
  - `warehouse/metadata/build_coverage.py`, `warehouse/supabase/live_set.yaml`, `warehouse/redivis/release_v1.py`;
  - `docs/redivis/release-v1/` (tables, variables, README);
  - `docs/coverage.md`, `coverage.csv`, `sources.csv`, `archive_manifest.csv`, `license_tables.csv`, `docs/licenses.md`.
- On the data machine only: `runs/c105/s2356/`, `runs/license_reads/s2356/`, `runs/s2356_*`.
