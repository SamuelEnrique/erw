# Session 708 report: the utility on the All grids tab

22 October 2026, from 09:36 UTC, on samueloldlaptop, unattended, in the worktree `C:\Users\lossa\Documents\erw-708` on `wip/708-allgrids` (cut from `wip/707-allgrids`). Chain `queue/done/050-night-23-october-code-allgrids.md`, session 708. Model spend USD 0. No warehouse data written; no request to a publisher.

## Read these first

- **Each row names the utility that sold most to industry in its state inside its grid** in 2025, with its industrial revenue per MWh and its industrial sales on 2024. The source is EIA-861 (`eia861_utility_sales`, rebuilt from the archive, through the new `site/data/siting/utility.json`).
  - Only rows that sell energy count (EIA's Bundled and Energy service types); Delivery rows are wires charges.
  - The grid is matched by the balancing authority EIA gives each row, so Texas inside MISO is Entergy Texas, not an ERCOT retailer.
- **Examples**:
  - ERCOT: TXU Energy Retail, USD 73.57 per MWh, +9.4 percent.
  - CAISO: Pacific Gas & Electric, 325.37, -8.6.
  - NYISO: New York Power Authority, 50.49 (energy only).
  - SPP North (Kansas): Evergy Kansas South, 77.79.
  - MISO Indiana: Duke Energy Indiana, 86.38.
  - The tip says whether the figure is bundled (energy and delivery) or energy only.
- **Service territories are not held**: this is the state's largest seller, not the row's own utility, and the tip says so.
  - ERCOT nodes: "not held" (no node table names its TSP).
  - PJM: "not held" (it spans thirteen states and the District of Columbia).
- **Keys**: `allgrids|utilrev|<row>`, `allgrids|utilgrowth|<row>`.

## What to review

1. After the landing, open `https://erw-flame.vercel.app/cost-of-power?view=allgrids` (internal view), the Utility column: each row's utility name, then its revenue per MWh, then its growth. Hover them.
2. Sort by "the utility's industrial revenue per MWh" under "Sort and filter".
3. Screenshots: `docs/brand/review-708/` (712's build).

## Checks

| Check | Exit | Result |
|---|---|---|
| precheck | 0 | |
| `tests.test_session708` (the file recomputed from the table here; no Delivery row; the keys) and 700 to 707 | 0 | OK, 1 skip |
| built and checked on 712's branch | 0 | see 712's report |

## The landing

Landed with sessions 706 to 712 in one push, merged at 11:24 UTC (`8a54e3b4`); Vercel rate-limited the deploy ("retry in 24 hours"), so production serves it later: `SESSION_712_REPORT.md`, "The landing".

## Decisions made without you

1. **A hub takes a state**: ISO-NE's hub Massachusetts (its largest load), SPP's North hub Kansas and South hub Oklahoma, MISO's hubs the state in their names.
2. **Energy-only sellers count** (Texas's and New England's retail markets), with the tip saying the wires utility bills delivery.

## For Samuel's ruling

- Service territories (EIA's or HIFLD's) would let a row name its own utility. They are in the gaps file.

## Files

- Changed: `site/lib/siting.ts` (`stateOf`, `utilityCell`), `site/lib/sitingdata.ts`, `site/app/cost-of-power/AllGridsView.tsx` (`UtilityTd`), `site/scripts/siting-files.mjs`, `warehouse/derived/siting_page.py` (`utility.json`).
- New: `site/data/siting/utility.json`, `tests/test_session708.py`, this report.
