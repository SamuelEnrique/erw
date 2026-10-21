# The data machine's note of the chain of 21 October, evening: public federal sources (written 21 October 2026, about 19:00 UTC)

Energy Research Warehouse (ERW), for Samuel. The data machine's chain of 21 October, evening (sessions 483 to 496 and 507 to 509, `queue/done/022-evening-21-october-sources.md` and the owner's instruction of 21 October), unattended on lab-desktop, from about 16:40 UTC to this note's push. Model spend USD 0 in every session. Before it: [`docs/state/note_2026-10-22_evening_data.md`](note_2026-10-22_evening_data.md).

## Read these first

- **`node_basis_daily` is out of the live set** (session 483, landed as `745abfd9`). It was deleted from Supabase through the loader's client at your instruction. It stays in `warehouse/output`, in the archive and in coverage. `series` keeps its 2,154 MB on disk until a `VACUUM FULL` (yours to run).
- **Ten new public sources, 29 tables, 20,218,905 rows, held on the data machine and in the archive.** None is in the live set, and none was uploaded to Redivis.

  | Source | Table | Rows | Cross-check |
  |---|---|---|---|
  | FERC Form 714, through PUDL's core table (484, 494) | `ferc714_area_demand_2006` to `_2025` | 19,520,470 | ERCOT's own load: 1,184 MW mean difference at the hour's start, 2,717 MW as stamped |
  | EIA-861 utility sales (485, 495) | `eia861_utility_sales`, 2015 to 2025 | 433,115 | EIA's monthly state sales: 97% to 99% |
  | EPA eGRID2023 (486) | `egrid_power_plants` | 12,612 plants | 4,191 TWh against EIA's 4,178 |
  | NLR (NREL) ATB 2025 (487) | `nlr_atb_electricity_costs` | 95,000 | equal to session 312's workbook reading |
  | EIA AEO2026, Tables 8 and 9 (490) | `eia_aeo_electricity` | 34,034 | 4,069 TWh against 4,058 |
  | EIA STEO (491) | `eia_steo_forecasts` | 5,088 | 78 of 79 months equal |
  | EPA GHGRP, subpart D (492) | `epa_ghgrp_power_co2` | 17,035 | eGRID: median ratio 1.000 |
  | BOEM's renewable leases (493) | `boem_renewable_leases` | 52 | |
  | USGS's Wind Turbine Database (496) | `uswtdb_wind_turbines` | 77,839 turbines | EIA-860M: median ratio 1.000 by plant |
  | EIA SEDS (507) | `eia_seds_state_energy` | 23,660 | EIA's retail sales: within 0.04% in all 1,248 state-years |

- **Not pulled, and why:**
  - **EPA CAMPD** (488) needs an API key the ERW does not hold.
  - **DOE's OE-417** (508) has no file to pull: the old host is gone, and the new form site is a JavaScript application.
  - **BLS's price indexes** (509): `api.bls.gov`'s robots file disallows every path.
  - **FERC's own site** answers 403 from Cloudflare (484), so PUDL's open copy was used, and FERC's own site was not worked around.
- **Two faults caught before anything was written**:
  - EIA-861's reader read columns by position, and 2019's extra column shifted every figure. It now reads by heading (495).
  - Session 494's first metadata commit held merge markers. It was undone before any push.
- **Main failed ten tests after today's daily run, and this landing fixes them** (session 489). The daily recompute of the Research cards (session 361) committed its first run in `c8aa37ff` and moved numbers that five sessions' tests hold. Every `task/` branch would have failed its checks.
  - The cards are put back as they were.
  - The data machine's run now tests the cards after each recompute, and puts them back when a test fails.
  - Which gives way is yours to rule (item 1 below).
- **The nine new public tables are held** from `/data`'s catalogue and from Redivis v1 until they are uploaded.
- **Session numbers**: this chain's 497 to 499 became 507 to 509, since the code machine's chain 023 holds 497 to 506.

## What each session landed

| Session | Landed |
|---|---|
| 483 | `live_set.yaml` and two test fixes (`745abfd9`) |
| 484 to 487 | the FERC 714, EIA-861, eGRID and ATB connectors with tests (`ffc3b0c0`) |
| 490 to 493, 496 | the AEO, STEO, GHGRP, BOEM and USWTDB connectors with tests (`1e87846a`) |
| 489, 494, 495, 507 to 509 | the tables' metadata (coverage, archive manifest, sources, licenses), the SEDS connector, the reader's fix, the cards put back and tested after each recompute, the holds, the reports and this note (this landing, `task/489-499-sources`) |

## Pulls against their ceilings

Every session's pulls stayed under its ceiling; each report has its table. The largest: PUDL's parquet (122 MB, once, then reused), api.eia.gov 33 requests in session 489's write, and energy.usgs.gov 8 of 30.

## Decisions made without you (one line each; the reasons are in each report)

- 484: PUDL's core table, never its imputed `out_` table; the hour shifted by one, as ERCOT's load shows.
- 484, 494: FERC 714 as yearly tables, internal until you rule.
- 485: EIA's imputed rows and its 88888 and 99999 codes left out.
- 490: every AEO case kept; rows in short tons not taken (no such unit in the vocabulary).
- 507: SEDS from 1990.
- 489: coverage rebuilt with the branch's sector rules.
- 489: the Research cards put back and tested after each recompute, not the tests changed to today's numbers; the new public tables held from `/data` and Redivis v1.

## Waiting for Samuel, highest value first

1. **The daily recompute or the cards' pinned tests** (sessions 361 against 173, 174, 182, 274 and 381): which gives way. Until you rule, the cards are put back every day the tests fail (489).
2. **FERC 714's license**: public (PUDL's CC-BY-4.0, a U.S. government work) or internal until FERC's own terms page can be read (484).
3. **`VACUUM FULL` of `series`** (about 600 MB back): `python warehouse/supabase/load.py --vacuum-full` (483).
4. **`tCO2e` and short tons in the unit vocabulary**, for GHGRP's other gases and AEO's emissions (490, 492).
5. **An EPA API key** for CAMPD (488).
6. **Which AEO2026 case is central**, if a page should show one (490).
7. **Redivis**: whether the new tables, FERC 714's 5.7 GB above all, are uploaded (494).
8. **BLS** by another route, or not at all (509).

## The next chain

Written by this chain's last session and taken at once, at your instruction ("write the next chain of new public sources and take it"). Its file and its numbers are in the queue commit that follows this landing.
