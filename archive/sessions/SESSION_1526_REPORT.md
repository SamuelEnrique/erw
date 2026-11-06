# Session 1526 report: the scenario block's two scrolling tables reachable by keyboard

Energy Research Warehouse (ERW), session 1526, chain 163, samueloldlaptop, 6 November 2026, 13:13 to 13:15 UTC. Model: Claude Opus 5.5. Model spend USD 0. No warehouse data written; nothing sent or posted. Branch `wip/1526-a11y`, cut from `origin/main`.

## What it did, with commits (`080935384`)

- **The fault** (session 1504's AccessLint, `/cost-of-power`): "a scrolling region not reachable by keyboard (`figure > details > div`)". The region is the sensitivity chart's "The chart as a table" in `site/components/decisions/ScenarioBlock.tsx`, the block the battery, the generator and the datacenter share. The scenarios table above it, in the same file, scrolls too and has the same fault where it overflows.
- **The fix**: both scrolling divs carry `lib/cells.ts`'s `scrollRegion`, which gives `tabIndex` 0, a region and a name ("The sensitivity chart, as a table", "Scenarios A and B"), as session 412 gave the tool pages' tables. Nothing changes in the layout or the look; the focus ring is the token session 412 set (`.brand-a [data-scroll-focus]:focus-visible`).
- **Tests**: `tests/test_session1526.py` (3 tests: the helper imported, both regions named, no bare scrolling div left in the block). Every test that reads the block passes: sessions 179, 186, 194, 195, 263, 296, 298 and 412, 148 tests in all.
- The file had not changed since 19 October (session 298), so none of the desktop's chains 155 and 157 was in it.
- **The landing** is session 1531's: see its report.

## Decisions made without you

- The scenarios table got the same fix as the region AccessLint named, since it is the same fault one div up.

## For Samuel's ruling

- None.
