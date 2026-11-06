# Session 2243 (chain 156, deals and datacenters) report: the datacenter tracker's table and rollups

6 November 2026, from about 09:55 UTC (while session 2242's gate ran), portable-laptop (code role), unattended. Worktree `erw-2243` on `wip/2243-deals`, cut from `wip/2241-deals` (the branch the gate runs on). Model spend **USD 0**. Nothing deployed (`/datacenters` stays `review`); no warehouse data written (the builder was run as a trial into a temporary folder).

- **`warehouse/derived/datacenter_facilities.py`**: the fields of session 2236 carried from the news facilities into the tracker's one table (`power_kind`, `energized_year`, the county's EIA-861 utility and the count of utilities that serve it); a facility's **grid** is the grid its stories name, else its queue's own ISO, else the grid that serves most of its state (`grid_basis` named, queue or state); its **MW basis** is that of the member its MW is from (`unstated` for an operator's list or a news row without one). A trial on the stored inputs: 428 facilities, 171 with a grid (168 by state, 3 by queue; none named yet, since the stored news table was extracted before session 2236), 48 with MW (basis unstated).
- **`site/lib/dcrollups.ts`** (new, pure): the rollups by grid and by operator from `datacenter_facilities` as the live set serves it: the facilities the page's sums count (a named US state, not cancelled), the MW stated summed, those stating MW and those stating none; no sum where none states MW; a row built before this session reads its grid from its state. `rollupKey` (`datacenters|rollup_<facilities|mw|with_mw|without>|<grid|operator>|<value>`).
- **`site/app/datacenters/Rollups.tsx`** (new) drawn under the list; **`DatacentersTable.tsx`**: the filters Grid, Power (the kind of power) and "MW at most" beside the old ones (operator, state, status, source, country, MW at least); each cell's tip (the grid's basis, what the MW measures, the kind of power, the county's utility, the energized year, the sources); the CSV, Python and Stata downloads of the rows shown (no outlet text). **`Body.tsx`** maps the new fields.
- **`site/scripts/check-values.mjs`**: the rollup keys, with the page's function.
- **The map**: the project map (`/map`) already draws every placed facility of the tracker among its kinds, with the plants and the queues, and each placed row says "on the map"; no second map was drawn.
- **`tests/test_session2243_deals.py`** (6 tests): passed.

## Decisions made without you

1. **The grid of a facility**: a story's named grid, else its queue's ISO (a queue position is in one ISO's queue), else the state's main grid, each marked; a state split between grids gives none.
2. **The rollups count what the page's other sums count** (a named US state, not cancelled), so the rollups and the top block agree; the facilities outside them are in the list.
3. **The MW of any basis is summed** with the basis on each row, as in `datacenter_tracker_rollups` (session 2236).

## For Samuel's ruling

- None new.
