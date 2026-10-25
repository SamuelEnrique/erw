# Session 2247 report: this chain's method notes, every point acted on; the merge with main; the Stanford draft

24 October 2026, from 03:47 UTC, on lab-desktop (the data machine), the tenth session of `queue/done/101-day-4-november-data-france-spain-brazil-australia.md`, unattended. The notes were drafted by a helper beside sessions 2248 to 2250 and checked here. Model spend USD 0. Pulls: Redivis's API, 134 of 150 requests (below).

## Read these first

- **Six method notes, one for each of this chain's tables,** checked as session 960 checked its notes, against the code, the table, the raw files and the rerun cross-checks. Every point was acted on:
  - **RTE:**
    - **The battery columns were placeholders:** RTE prints 0 for battery charging and discharging in every half hour from 2021 to 2026. They are no longer taken. The table was written again offline, its file removed first under the data lock: 1,448,927 rows, 198,576 fewer.
    - The docstring and header now say that the autumn hour's two UTC hours both have no row (RTE's 12 lines are 24 half hours), and that some borders' commercial exchanges change within the hour.
  - **REE:**
    - The header now carries the latest update date anywhere in REE's answers, as REE's notice asks. The groups and series carry later dates than the answer's own.
    - The docstring says the answers name no geography.
    - Written again offline (the same 1,890 rows).
  - **The three EIA tables:** their rows recorded when the write began, not when EIA served the pages.
    - The connectors now take a reused page's first download time from the raw store, and all three were written again offline: the same rows, now with EIA's serving times.
    - The shale table's header now gives its true access address (annual, eleven processes) and says years, not months.
  - **ONS:** nothing to change in the connector.
- **Corrections to this chain's reports:**
  - **Session 2238:**
    - The autumn count of 12 is 12 lines, 24 half hours in UTC.
    - The zero wind split's 17,520 lines are 2021's and the first line of 2022 in French time.
    - "Mainland France" is withdrawn: the files say France.
    - The battery measures were zeros throughout (now not taken).
  - **Session 2240:**
    - "1,834 to 2,440 hours a subsystem" is 1,834 to 2,421 for the four subsystems (2,440 is the national total's).
    - Every break falls in January to May 2026 but 24 hours in the South in September 2022.
    - The load ratio to Ember is not rising every year: 2022 is below 2021, and 2025 below 2024.
  - **Session 2244:** U.S. gravity's low was 2004's 30.18, not 2005's 30.20. Sulfur peaked at 1.455% in 2008, not near 1.42% in 2005.
  - **Session 2250:**
    - "23 states" is 22 in EIA's route and 20 with rows (New York and Utah only empty).
    - The federal offshore has rows only for 2019, all 0.
    - The production route's end in 2021 rests on the session's printed metadata, which was not saved.
    - The 2020 gap of 596 bcf is New Mexico East's 586 and 10 in Texas districts 7C and 8.
- **The merge with main** (chains 097 and 099 landed; commit 23e60329):
  - Nine conflicts were resolved (`runs/c101/merge_resolve.py`, then `runs/union_resolve.py` for sources and the release variables).
  - This chain's reads were renumbered 404 to 430 after main's 403, with five verdicts and five reports.
  - `degAPI` and `Btu/ft3` stay Decisions 73 and 74 after chain 097's `m3` (70).
  - Test 205's bound was joined, and the release README's held line is the union (231).
  - The license record and the records were rebuilt (470 tables).
- **The Stanford draft** (`runs/c101/s2247/run.sh`, detached, under the data lock from 03:59 to 04:08 UTC, the main checkout pulled to 7ae30e10 first):
  - A reconcile: 304 match, 47 mismatch, 9 not yet uploaded.
  - One plain upload of nine public tables: this chain's six, and chain 098's three that lagged (`usbr_mead_powell_daily`, `energinet_dk_production_hourly`, `usbr_crsp_reservoirs_daily`).
  - With the metadata tables, 12 of 12, in 114 requests.
  - A reconcile: 314 match, 44 mismatch (the live tables' known drift), 2 not yet uploaded.
  - Nothing released.
  - **The draft lags five tables since:** RTE (the battery rows gone), REE and the three EIA tables were written again after the upload. The next draft session uploads them.

## Pulls against their ceilings

| Host | Requests | What |
|---|---|---|
| redivis.com (and Supabase once) | 134 of 150 | reconcile (10), the upload (114), reconcile (10) |

## Errors

- **Two Method-cell rebuilds put back cells from HEAD** rather than from the staged rewrites; the second time it undid the rewrites' rows on the coverage page. Caught, and rebuilt from the staged copy with only the Method cells new.
- **Each offline rewrite's metadata patch met the others'** and left duplicate rows. Each table's newest row was kept (`runs/c098/s2218/dedupe.py`), and no row is twice.

## Decisions made without you

- **RTE's battery columns dropped as placeholders,** like 2021's zero wind split.
- **EIA's serving times in the rows,** taken from the raw store for a reused page.
- **The draft's lag left to the next draft session** rather than a second upload, with 16 requests left under the ceiling.

## For Samuel's ruling

- None new.

## Files

- New:
  - `docs/methods/rte_eco2mix_france_halfhourly.md`, `ree_spain_balance_monthly.md`, `ons_brazil_balance_hourly.md`, `eia_crude_quality_monthly.md`, `eia_gas_heat_content_monthly.md`, `eia_shale_gas_reserves_annual.md`
  - this report
- Changed:
  - `warehouse/connectors/rte_eco2mix.py`, `ree_balance.py`, `eia_crude_quality.py`, `eia_gas_heat_content.py`, `eia_shale_gas_reserves.py`
  - the coverage, sources, archive manifest, license and release files
  - `package/src/erw/data/tables.csv` and the site's two record files
- On the data machine only: `runs/c101/s2247/`, `runs/s2247*`.
