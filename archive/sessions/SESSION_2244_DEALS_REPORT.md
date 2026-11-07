# Session 2244 (chain 156, deals and datacenters) report: the tracker by grid

6 November 2026, from about 10:38 UTC (while session 2242's gate ran), portable-laptop (code role), unattended. Worktree `erw-2244` on `wip/2244-deals`, cut from `wip/2243-deals`. Model spend **USD 0**. Nothing deployed (`/datacenters` stays `review`); no warehouse data written.

- **`site/lib/dcrollups.ts`**: `gridLoads` (by grid, the facilities the page's sums count, those stating MW and those stating none, and the MW stated planned, under construction and operating) and `shareOfPeak` (the planned and building MW over the grid's peak hour, to a tenth of a percent; none where the facilities state no MW or the peak is not held); `gridKey` (`dcgrid|<stat>|<grid>`).
- **`site/app/datacenters/FacilitiesVsGrid.tsx`** (new), drawn on `/datacenters?view=grids` under the queues: for each of the seven grids, the facilities' stated MW beside the grid's 2025 peak hour and its operating generators' net summer capacity (`grid_peak_vs_capacity`, as `site/data/siting/headroom.json` carries it for the All grids tab), the share of the peak, and the reserve margin: ERCOT's from its Capacity, Demand and Reserves report (summer 2027, the same file); the others' cells say "not held" with a footnote (NERC's assessments are not read while NERC's terms are not, session 666). **Under the hold of `datacenter_facilities`** every facility cell is "license needed" with its footnote, never an empty cell (your rule for licensed figures), and the grid's public figures stay.
- **`site/scripts/check-values.mjs`**: the `dcgrid|` keys: the facility figures with the page's function on the live set, the peak and capacity from `grid_peak_vs_capacity` in the live set, the reserve margin from the file the page reads.
- **`subregion_demand_growth`** (the desktop's chain 147) was not used: the facilities are placed by grid, not by EIA-930 sub-region, and no facility states its sub-region; the grid's peak and capacity are the measures the live set holds for each grid.
- **`tests/test_session2244_deals.py`** (5 tests); with 2243: 10 passed. The type check of 2243 and 2244 waits for the gate's build (memory), and is run in a later session of this chain.

## Decisions made without you

1. **The share is of the peak hour, of the planned and building MW the facilities state**, not of what they will draw; the note says so in those words.
2. **The reserve margin's file is the site's own** (`headroom.json`, built by the data machine from `ercot_cdr_reserve_margins`), so the check reads the same file; the peak and capacity are checked against the live set.

## For Samuel's ruling

- None new.
