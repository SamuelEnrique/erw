# Session 2246 (chain 156, deals and datacenters) report: the datacenter tracker's charts

6 November 2026, from about 10:44 UTC (while session 2242's gate ran), portable-laptop (code role), unattended. Worktree `erw-2246` on `wip/2246-deals`, cut from `wip/2245-deals`. Model spend **USD 0**. Nothing deployed; no warehouse data written.

- **`site/lib/dcrollups.ts`**: `plannedByQuarter` (the planned and building MW the counted facilities state, by the quarter first reported, by grid: the four with the most and the rest), `operatorMw` (the ten operators, else developers, with the most MW stated), `powerShares` (the counted facilities by the kind of power stated, with "not stated" as its own bar), `dcFigures` (every figure by its key `dcchart|<planned|operator|power>|<x>|<series>`).
- **`site/app/datacenters/DcCharts.tsx`** (new), on the facilities view: the three charts in the brand's five series colors, a legend for the stacked one, every mark's hover and key, a table of every figure under each.
- **`scripts/check_datacenters.py`** (new) with **`site/scripts/datacenters-figures.mjs`** (new): every figure recomputed from `datacenter_facilities.csv` by its own Python and compared with the page's functions: **28 of 28 agree** on the stored 428 facilities. **`site/scripts/check-values.mjs`**: the `dcchart|` keys on the live set.
- **`tests/test_session2246_deals.py`** (4 tests); with 2243 and 2245: 13 passed.

## Decisions made without you

1. **Planned and building only in the first chart**: an operating facility is not a load to come; the third bar of the grid's table (session 2244) holds the operating MW.
2. **"Not stated" is a bar of the power chart**: most facilities state no power source, and a share of only those that do would hide it.

## For Samuel's ruling

- None new.
