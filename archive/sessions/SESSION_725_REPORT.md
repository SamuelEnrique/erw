# Session 725 report: the utility's path, walked

22 October 2026, from 15:12 UTC, on samueloldlaptop, unattended, in the worktree `C:\Users\lossa\Documents\erw-725` on `wip/725-allgrids` (cut from `wip/724-allgrids`). Chain `queue/done/062-day-23-october-code-allgrids-2.md`, session 725. Model spend USD 0. No warehouse data written; no request to a publisher. The reads were production's pages in the internal view.

## Read these first

- **The walk**: `docs/reviews/siting-utility-path.md`, 12 steps on production; shots in `docs/brand/review-725/`.
- **The main finding: the Utility column mixes three kinds of figure** and its cell does not say which. Bundled is a full price; delivery only is the wires; energy only is a retailer's energy.
  - PJM's row is FirstEnergy Pennsylvania's delivery revenue, USD 11.34 per MWh, sorted beside PG&E's bundled 325.37.
  - The A and B panel subtracts one kind from another (LZ_HOUSTON's coop 89.39 against PJM's 11.34: "-78.05").
  - Session 726 names the kind in the cell and the panel.
- **The second: the "utility" is sometimes a retailer.** For ISO-NE's Massachusetts zones and MISO's Illinois hub, the state's largest seller to industry is Direct Energy Business, an energy-only retailer, not the wires utility a planner means. Changing which utility a row names changes what the figure is, so it is listed for your ruling, beside chain 050's item 18 (Texas's wires utilities).
- **Rows inside a grid tie on headroom and time to connect**: both are the grid's figures. A zone's own growth is session 728's; a load's own wait is a gap.
- **The tracker shows no facility** while `datacenter_facilities` is held, so 719's links do not show.

## What to review

1. `docs/reviews/siting-utility-path.md`: the steps, then "What session 726 fixes".
2. `https://erw-flame.vercel.app/cost-of-power?view=allgrids&mw=1000&sort=utility&dir=desc` (internal view): find PJM's row, and hover its 11.34. The tip says delivery; the cell does not (`docs/brand/review-725/u01_utility_sort_1280.png`).

## Checks

| Check | Exit | Result |
|---|---|---|
| precheck | 0 | |
| `runs/chain_062/walk.mjs` on production, 11 addresses | 0 | 11 shots and texts; no page wider than its window |
| `site/data/siting/utility.json`, PJM's entry | | FirstEnergy Pennsylvania Electric Co, service "Delivery", 2025 |

## The landing

Sessions 722 to 730 landed in one push at 16:15 UTC: see `SESSION_730_REPORT.md`, "The landing".

## Decisions made without you

1. **The walk's planner is a utility's or a commission's**, asking where loads go and what they ask of the grid, as the chain file says.

## For Samuel's ruling

- Where the largest seller to industry in a row's state is an energy-only retailer (Direct Energy Business for ISO-NE's Massachusetts zones and MISO's Illinois), should the Utility column name the wires utility (and so show a delivery revenue) instead? Beside chain 050's item 18 for Texas.

## Files

- New: `docs/reviews/siting-utility-path.md`, `docs/brand/review-725/` (11 shots and the steps), this report.
