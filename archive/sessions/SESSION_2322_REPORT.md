# Session 2322 report: the next file first; Malaysia's electricity supply and consumption a month (DOSM, data.gov.my)

24 October 2026, from 06:27 UTC, on lab-desktop (the data machine), the first session of `queue/done/108-day-10-november-data-malaysia-thailand-ecuador-kenya.md`, unattended. Model spend USD 0. Pulls: 8 of 15 (below).

## Read these first

- **Chain 108 taken** at 06:26 UTC by chain 059's agent when chain 104 landed (3d634f4e), under the owner's instruction for that run: run the file the queue step prints. Chains 105 (another agent) and 106 (another agent) run beside it. Precheck passed (`runs/c108/pre2322.out`).
- **The next file first,** pushed to main on its own before any other work (42245055, with snapshots): `queue/next/109-day-11-november-data-turkey-vietnam-indonesia-us-stocks.md`, sessions 2336 to 2349, machine: data. Its sources are Turkey (EPIAS), Vietnam (NSMO), Indonesia (PLN) and EIA's petroleum stocks by state, away from chains 102 to 108's. 109 was the next free number: 100 to 108 were taken on main, and no running branch had 109.
- **Two corrections followed by message:**
  - Chain 105's agent found its sessions 2300 to 2306 already used, by the code machine's chain 087 and that machine's `wip/2306-audit-fixes`. It renumbered them 2350 to 2356, so file 109's next file now starts at 2357.
  - Chains 105 and 106 found more hosts closed, now in file 109's list: osp.stat.gov.lt (Cloudflare), www.litgrid.eu (its robots file names Claude's agents), donnees.hydroquebec.com, and api.neso.energy.
  - Chain 106 also took Iceland, Latvia and Lithuania for its own-choice sessions.
  - The fixes went to main as two more queue commits, each with snapshots.
- **One public table written, validated, archived, in coverage (sector power), and held from the live set and the release:** `dosm_malaysia_electricity_monthly`. It holds Malaysia's electricity supply and consumption a month by sector, January 2018 to June 2026: 1,224 rows, 12 variables.
  - The source is the Department of Statistics Malaysia's two sets on data.gov.my, compiled from TNB's, Sabah Electricity's, Sarawak Energy's and the Energy Commission's records.
  - The values are million kWh times 1,000, giving MWh.
  - DOSM says the latest six months are provisional.
- **License: CC BY 4.0.** Each dataset page says "This data is made open under the Creative Commons Attribution 4.0 International License (CC BY 4.0)" (reads 503 and 505). A new verdict is recorded: may be public in both columns.
  - data.gov.my's robots file allows every path to every agent and names no AI agent (read 500).
  - The API and storage hosts have no robots file (reads 501 and 504).
  - There is no separate terms page (read 502).

## The cross-check (`runs/c108/s2322/cross.py`, `cross.out`)

- **DOSM's identities hold to the kWh in every month.** The largest gap is under 1e-8 MWh in each of these:
  - public plus private equals local supply;
  - local supply plus imports equals total supply;
  - commercial plus domestic equals local consumption;
  - local consumption plus exports plus losses equals total consumption;
  - total supply equals total consumption.
- **DOSM's `distribution` supply equals total supply in all 102 months.** It is kept as published and recorded here.
- **Against `owid_ember_electricity_annual`'s Malaysia:** that table holds demand only, no generation, for MYS. DOSM's total supply is 1.7 to 5.5 per cent below Ember's demand in every year from 2018 to 2025 (2018: 163.49 against 169.09 TWh; 2025: 193.01 against 199.91 TWh). The gap is likely generation the utilities' records leave out (Ember's demand is generation plus net imports); recorded, not adjusted.
- Imports are small: 0.003 to 0.24 TWh a year (0.003 in 2022), and zero in 26 months. (Session 2326 corrected "0.02 to 0.24".)
- **Session 2326's checks, added here:** `cross.py` first tested distribution against local consumption plus losses and found no Ember generation; it now tests what this report states, on the written table, and `cross.out` bears both out (distribution 0 MWh from the total in all 102 months; DOSM 1.68 to 5.52 per cent below Ember's demand). The header now says that distribution repeats the total, and that private supply and losses change level between December 2022 and January 2023, which DOSM's pages do not explain.

## Pulls against their ceilings

| Host | Requests | What |
|---|---|---|
| data.gov.my, api.data.gov.my, storage.data.gov.my | 8 of 15 | three robots files, a terms address (404), two dataset pages, two data files |

## Errors

- None.

## Decisions made without you

- **The table public** under CC BY 4.0, attributed to DOSM.
- **`supply_distribution` kept** although it equals the total, because DOSM publishes it as a sector.
- **Test 205's bound raised by 40,** for this chain's reads beside chains 105's and 106's.

## For Samuel's ruling

- None new.

## Files

- New:
  - `warehouse/connectors/dosm_malaysia_electricity.py`
  - `tests/test_session2322.py`
  - this report
- Changed:
  - `warehouse/metadata/build_coverage.py` (the sector rule), `warehouse/redivis/release_v1.py` (held), `warehouse/supabase/live_set.yaml` (held)
  - `warehouse/metadata/license_reads.csv` (500 to 505), `license_verdicts.csv` (DOSM), `license_tables.csv`, `docs/licenses.md`
  - `docs/redivis/release-v1/` (the table's rows)
  - the coverage, sources and archive manifest files
  - `tests/test_session205.py`
- On the data machine only: `runs/c108/s2322/`, `runs/license_reads/s2322/`, `runs/c108/write_q109.py`, `runs/c108/register.py`, `runs/c108/for109.md`, `runs/snapshots/c108q*`.
