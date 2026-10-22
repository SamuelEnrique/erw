# Session 706 report: headroom on the All grids tab

22 October 2026, from 09:27 UTC, on samueloldlaptop, unattended, in the worktree `C:\Users\lossa\Documents\erw-706` on `wip/706-allgrids` (cut from `wip/705-allgrids`). Chain `queue/done/050-night-23-october-code-allgrids.md`, session 706. Model spend USD 0. No warehouse data written; no request to a publisher.

## Read these first

- **Each row's Headroom cell has three figures, all the grid's.**
  - **Demand growth**: the mean demand of the last twelve months over the twelve before (October 2025 to September 2026 against the year before), the monthly means weighted by their hours. This is "Your load"'s own EIA-930 file (`demand_growth.json`, `eia930_demand_growth`).
    - ERCOT +5.41 percent, SPP +5.25, PJM +4.12, CAISO +3.64, ISO-NE +2.90, MISO +2.80, NYISO +0.52.
    - It is the grid's balancing authority, not the row's zone: sub-region demand is not in the tab's files. Weather is not removed.
  - **"MW coming"**: generators under construction (EIA status U, V or TS) due from September 2026 to August 2027, the twelve months after the table's vintage (EIA-860M of August 2026), in the new `site/data/siting/headroom.json`.
    - ERCOT 24,269 MW (137 generators), MISO 8,887, CAISO 8,276, PJM 7,696, SPP 3,870, NYISO 1,537, ISO-NE 1,124.
    - The tip gives approvals received and the planned rest. It also says EIA-860M records no interconnection agreement, so construction is the nearest it states.
  - **Capacity over peak**: installed net summer capacity (2024, `eia_state_capacity_annual`) over the 2025 peak, only where the grid is whole states: NYISO 130 percent (New York), ISO-NE 134 (the six New England states).
    - The tip says this is not a reserve margin.
    - Every other grid has no such figure: it is not a set of whole states, and the tip says so.
- **Keys**: `allgrids|demand|<row>`, `allgrids|planned|<row>`, `allgrids|capratio|<row>`.

## What to review

1. After the landing, open `https://erw-flame.vercel.app/cost-of-power?view=allgrids` (internal view) and scroll to "Headroom".
2. ERCOT rows: "+5.41 %", then "24,269 MW coming". NYISO rows add "capacity 130% of peak". Hover each.
3. Screenshots: `docs/brand/review-706/` (taken on 712's build, which holds this session).

## Checks

| Check | Exit | Result |
|---|---|---|
| precheck | 0 | |
| `tests.test_session706` (growth recomputed here month by month; capacity over peak only for whole states; the file recomputed from the tables) and 700 to 705 | 0 | OK, 1 skip |
| built and checked on 712's branch | 0 | see 712's report: check-values 2,487 of 2,487 on every `/cost-of-power` address, the existing tab 0 differences |

## The landing

Landed with sessions 706 to 712 in one push, merged at 11:24 UTC (`8a54e3b4`); Vercel rate-limited the deploy at first and served it at 11:54 UTC; snapshots 0 differences: `SESSION_712_REPORT.md`, "The landing".

## Decisions made without you

1. **Demand growth is the balancing authority's**, from "Your load"'s own file (the prompt's "or the Grid tool's function").
2. **The twelve months after the vintage** stand for "the next twelve months".
3. **Capacity over peak only for NYISO and ISO-NE**: every other grid crosses state lines.

## For Samuel's ruling

- Sub-region demand (`eia930_subba_demand_hourly`, held) would give a zone's own growth for NYISO's and ISO-NE's zones, and ERCOT's weather zones. It is not in the live set.

## Files

- Changed: `site/lib/siting.ts` (`demandGrowth`, `capacityOverPeak`, `BA_OF`), `site/lib/sitingdata.ts`, `site/app/cost-of-power/AllGridsView.tsx` (`HeadroomTd`), `site/scripts/siting-files.mjs`, `warehouse/derived/siting_page.py` (`headroom.json`).
- New: `site/data/siting/headroom.json`, `tests/test_session706.py`, this report.
