# Session 2070 report: Ontario's market (the IESO's public reports), chain 068 written

23 October 2026, from 20:01 UTC, on lab-desktop (the data machine), the first session of `queue/done/067-day-25-october-data-neighbours-emitters-disasters-world-oil.md`, run by chain 059's agent after its landing (the owner's instruction for that run: run the file the queue step prints). Model spend USD 0. Pulls: 13 requests of 15 (reports-public.ieso.ca's robots file, HTTP 404, and www.ieso.ca's, each asked in a call of its own and read first; the IESO's Terms of Use; the reports directory; four folder listings; the HOEP files of 2024 and 2025 and the demand files of 2025 and 2026). The trial and the write reused the saved demand files (`--offline`).

## Read these first

- **Chain 067 taken beside chain 066:** chain 057's agent took chain 066 at 19:50 UTC and wrote chain 067 at its start; chain 059 landed at 19:59 UTC (`555220b6`), and its queue step took chain 067 at 20:00 UTC (`1d6e1747`). This chain runs in `erw-c067` on `wip/2070-2083-data`, cut from main after chain 059's landing; chain 066's agent was told. Snapshots `c067-take-before` and `c067-take-after`: 0 differences (nothing deployed: Vercel rate limited).
- **Chain 068 written and pushed first:** `queue/next/068-day-26-october-data-mexico-renewables-loans-credits-pipelines.md` (sessions 2084 to 2097: CENACE's Mexican grid, IRENA's capacity statistics, USDA's rural utilities loans, the IRS's energy credits, EIA's state-to-state pipeline capacity, the IAEA's PRIS, CPC's ENSO index, the licenses' sixteenth round and the rest), committed alone and pushed to main (`33aa3cf1`). Snapshots `s2070-before` and `s2070-after`: **0 differences in all**; Vercel rate limited, nothing deployed. 068 was the next free number; sessions 2084 to 2097 were free on main and in chains 057 and 058's worktrees.
- **One table written, validated, archived, in coverage (sector power, public), in the release package, both holds:** `ieso_ontario_demand_hourly`, 31,680 rows: Ontario demand and market demand (Ontario demand plus exports) in MW, an hour, 1 January 2025 to 23 October 2026. One hour is missing in the IESO's own file: 2025-05-01T05:00Z, the first hour of the market renewal (found by session 2079). The IESO's hour ending in Eastern Standard Time (all year) is written as the hour's start in UTC.
- **The prices were not taken:**
  - The Hourly Ontario Energy Price ends with April 2025: the market renewal of 1 May 2025 replaced it with the Ontario zonal price, which the IESO publishes only as daily and hourly files (about three months of them, 187 day-ahead files and 12,707 real-time ones), far beyond a ceiling of 15.
  - The ERW has no Canadian dollar unit, a standing question for the owner since the CER's tables. The HOEP files of 2024 and 2025 are saved on this machine (`runs/license_reads/s2070/`), not written.
- **A new verdict, the IESO: may be public** (read 218, its Terms of Use): "you are granted a limited, non-exclusive, non-sublicensable, non-transferrable licence to use and reproduce the Content", provided each reproduction carries the IESO's copyright notice, which the table's header does, word for word.

## The cross-check

Ontario's exports by the IESO's own figures (market demand less Ontario demand) against the flows NYISO and MISO report with the IESO in EIA-930 (`eia930_all_interchange`), 864 hours from 13 September to 21 October 2026 (the hourly interchange the ERW holds), `runs/c067/s2070/cross.py`: correlation 0.905 hour by hour, falling to 0.836 and 0.830 with an hour's shift either way, so the two tables' hours line up; exports average 2,486 MW and the flow into NYISO and MISO 1,482 MW, and the U.S. flow exceeds Ontario's exports in only 7 hours, all on 6 October 2026 between 12:00 and 19:00 UTC, by at most 202 MW (Ontario also exports to Quebec and Manitoba, which EIA-930 does not report). (Session 2079's note corrected an earlier line here, which said the U.S. flow never exceeds Ontario's exports.)

## Errors

- None.

## Decisions made without you

- **Demand only, the prices left for a `CAD` unit** (the standing question).
- **Hours as the IESO gives them,** Eastern Standard Time all year, turned to UTC by five hours.
- **The IESO's verdict "may be public"** for public and commercial use: the licence names no use it excludes but the trade-marks (reversible by a ruling).

## For Samuel's ruling

- **A `CAD` unit** now also decides Ontario's prices (the HOEP to April 2025, saved here, and the zonal price since).

## Files

- New: `warehouse/connectors/ieso_demand.py`, `tests/test_session2070.py` (3 tests), `queue/next/068-day-26-october-data-mexico-renewables-loans-credits-pipelines.md` (on main), this report.
- Changed: `build_coverage.py`, `release_v1.py`, `live_set.yaml`, `docs/coverage.md`, `coverage.csv`, `archive_manifest.csv`, `sources.csv`, `license_reads.csv` (216 to 218), `license_verdicts.csv`, `license_tables.csv`, `docs/licenses.md`, `docs/redivis/release-v1/`.
- On the data machine only: `runs/c067/`, `runs/license_reads/s2070/`, `runs/s2070*`, `warehouse/raw/ieso_demand/`.
