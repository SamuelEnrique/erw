# Session 1855: the datacenter tracker's faults fixed (chain 213, 12 November 2026)

Energy Research Warehouse (ERW). Chain 213, session 1855, samueloldlaptop, unattended, Fable 5.1. About 12:50 to 13:15 UTC. Long end 1:30. Precheck passed.

## What it did, with commits

- `wip/1855-datacenters` cut from `wip/1853-deals` (the chain's newest unlanded branch) in the worktree `erw-1852`.
- **`c42dea88c`, rows 2, 3, 5, 6 and 9 of `docs/reviews/datacenter-faults-2026-11-11.md`, and row 4's footnote:**
  - row 2: `site/app/datacenters/Held.tsx` (new, after `deals/Held.tsx`): one paragraph where the facilities would be, with the catalogue's row count, the hold's day, why, what is not drawn and where the record is; `page.tsx` draws it for a license reason; `LargeLoad.tsx`'s "Beside it" box says the facilities are held and points to the note instead of listing 25 publishers;
  - rows 3 and 4: `FacilitiesVsGrid.tsx` draws the placeholder with footnote 1 for a held reserve margin, peak hour or capacity (`heldBy`), so "license needed% (summer 2027)" is gone and the public columns carry the footnote while the owner's item 28 is open;
  - row 5: `components/tool/GroupedBars.tsx` raises every second series' figure by 12 units when a group's bars are under 40 units wide, so "30.8230.82" and "146.46150.61151.76" read as three figures (the explorers' three bar charts take the same);
  - row 6: `app/map/page.tsx` writes the sentence for the held count ("Some queue positions ... Their count is held (license needed)") instead of the hold's words in its middle;
  - row 9: `lib/dcrollups.ts` `timeline()` reads `energized_year`, else the old `planned_year`, so the nine live rows that state both dates give ERCOT its count and median.
  - `tests/test_session1855.py` (7 tests), with the datacenter tests, the grouped bars' and the map's: 73 passed, 2 skipped; `tsc --noEmit`: exit 0.
- The branch pushed to origin; the five rows marked fixed on main.

## Decisions made without you

- Row 4 keeps the hold on the public peak, capacity and reserve-margin columns (the owner's item 28) and adds the footnote; the keys were not changed.
- The staggered figures change a shared component, so the explorers' bar charts change too: the same overlap would occur there, and the brand's direct labels are worth nothing unreadable.
- No build: the harness's instruction after 1852 stands; the branch is proved by its tests and the type check until a landing gate builds it.

## For Samuel's ruling

- None new beyond the datacenter faults file's rows 1, 4, 7 and 11.
