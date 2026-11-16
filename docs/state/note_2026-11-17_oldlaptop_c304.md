# Note: nine tools at the done line, twelve tools read as their readers, 16 November 2026 (old laptop, chain 304)

Energy Research Warehouse (ERW). Sessions 7500 to 7524, 16 November 2026, unattended, samueloldlaptop (code role). Chain file: `queue/done/304-day-16-november-oldlaptop-done-line-economics.md`. Progress, with every figure and commit: `docs/state/progress_c304.md`. The pack to sign: `docs/reviews/done-line-pack-oldlaptop-2026-11-16.md`. Model spend: USD 0.

## First

- **Nothing was built or seen in a browser on this machine.** The memory never reached the 2.5 GB a build needs. Every page change is held by tests and by the page drawn to HTML with the site's own code; everything that needs a browser is a row of `docs/state/browser_reads_wanted.md` (rows 1 to 75 are this chain's; chain 305 has read rows 15 to 31).
- **Nothing has landed.** Every tool is on its own `wip/` branch stacked on `wip/7500-done-line`, which stands on `wip/7200-large-load` (landing row 15). Landing rows 17 to 28 of `docs/state/landing_request_oldlaptop.md`, each after row 15, none depending on another.
- **The chain was interrupted once,** at about 13:16 UTC, in the middle of B10 to B12 (three agents, none of whose work was lost: two commits and the rest uncommitted in their worktrees). Session 7522 took the resume file 340 at 13:46 UTC and finished the three reads as sessions 7522 to 7524.
- **Every page is in review.** No page opened, no hold lifted, nothing published. The snapshots around each push of this chain's state files: 0 differences.

## By tool: found and fixed (part A, the done line; part B, the read)

- **`/contracts`** (rows 18): replication 2,539 of 2,615 inside the tolerance, 76 named (one data fault); filers 3,704 against FERC's 3,672. Read as a credit analyst: 11 site fixes (a click dropped the balancing authority; a rate filed as 0 was counted as a price, 302 of 1,315).
- **`/severance`** (row 17): 612 of 612; Texas's rates equal the Comptroller's to the cent. Read as a small well operator: 8 site fixes, none changes a tax. Not done: the refund finder's replication (its files are on the data machine).
- **`/shoulder`** (row 19): 20,633 of 20,634; 22,092 of 22,092 values recomputed from EIA's hourly workbooks. Read as a fund analyst testing "four hours is enough": 9 site fixes; California's shoulder is 28 to 42 percent higher by CAISO's data because EIA-930's demand counts the batteries' charging.
- **`/battery/customer`** (row 25): 331 of 331 over 12 real tariffs; the demand saving is an upper bound (a battery's whole power off the peak, against about 0.85 in NREL's report). Read as a grocery chain's energy manager: 3 fixes.
- **`/cost-of-power/battery/awards`** (row 20): 307 of 307; the two monthly tables 297 of 297 from ERCOT's disclosure rows. Read as a lender's analyst: 6 fixes ("5.64 times" and "22%" now drawn as the two different things they are).
- **`/impact`** (row 21): 7,593 of 7,593; Nevada's own fiscal note for Lone Mountain Geothermal: USD 876,631 against 876,653. Read as a state's economic development analyst: one change for Samuel's ruling (Nevada's taxable value column showed 45 percent of the value; the abatement is of the tax), undo `3baff8839`.
- **`/explore/ercot-peak-premium`** (row 22): 24,786 of 24,786 figures; 25,704 rows recomputed from 2,469,864 hub-intervals. Read as a fund analyst: two hubs side by side; "2026 (partial)" marked.
- **`/explore/demand-growth`** (row 23): 35,943 of 35,943 slots. **California's growth on this page is the batteries' charging**: +10.75 percent with it, +2.05 without, January to August 2026 on 2019.
- **`/explore/interconnection`** (row 24): 730 of 730. **ERCOT's "Reached operation" is an agreement signed, not a plant running**: 44 of 44 such 2025 positions have no actual in-service day. Fixed in words here; the cause is the connector's.
- **`/cost-of-power/battery`** (row 26, B10): 11 rows, 6 site fixes (a hub or node in the address is said; the ERCOT node list linked; a contract's income beside merchant: USD 144.96 against 81.40 a year at a USD 12.08 toll; no "-0"); the method note's Uri example was the calendar year's 3,430.56, the page's 18-day window is 3,105.51.
- **`/cost-of-power/seller`** (row 27, B11): 17 rows, 3 site fixes (hours priced below zero at the hub: 1,052 at West over the last twelve months, equal to `/curtailment`'s file in 11 of 11 months; a contract's own worst month, coverage 0.46 in December 2018 where the market's 0.00 stood; each year's capture rate on hover).
- **`/cost-of-power`, "Your load"** (row 28, B12): 23 rows, 6 site fixes, no figure changed. **California's twelve-month carbon stood on 6 of 12 months**: 128.31 kg per MWh on the monthly table, 150.52 over the hours held.

## Waits on the data machine

- `docs/state/data_requests_done_line.md`, this chain's rows 2 to 7, 10 to 31, 35 to 48 (rows 1, 8, 9 and 32 to 34 are the portable laptop's). The ones that change what a reader is told: ERCOT's queue `status` (row 40); California's battery charging by month (row 39); the carbon months (row 44); the shoulder table never rebuilt by `run_daily.sh` (rows 25 to 27); the seller page's snapshot a month behind `/cost-of-power`'s (row 48).
- The landings themselves: rows 15, then 17 to 28.

## Needs the key

- Nothing in this chain. USD 0.

## For Samuel's ruling

- The pack holds 97 numbered rulings for part A's nine tools, each with its default. The part B reads add their own, each in its read file; the three of today's resume are in `archive/sessions/SESSION_7522_REPORT.md`.
