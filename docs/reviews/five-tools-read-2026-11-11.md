# The five tools of 6 and 7 November, read as a reader (chains 213 and 214)

Energy Research Warehouse (ERW). Written by session 1886 of chain 214 on 13 November 2026, in place of chain 213's session 1872, which never ran (chain 213 stopped after its session 1856). Each tool was read on a local production build in the internal view at 1280 and 390, its faults numbered in one file (`docs/reviews/<tool>-faults-2026-11-11.md`), and every `open` row fixed with a test. The fixes of the deal tracker, the datacenter tracker, the policy monitor, the company database and the attention indices landed together on 12 November at 23:50 UTC (`52ccb381e`, `task/1880-five-tools`); the before and after snapshots of the 25 live addresses differ in nothing, since every page is in review.

## The table

Counts after chain 214 (the states in each faults file). "Fixed" is landed on main.

| Tool | Faults file | Rows | Fixed | Open | Data machine | Ruling | Not a fault |
|---|---|---|---|---|---|---|---|
| Deal tracker (`/deals`, comparables, AI view, charts) | `deals-faults-2026-11-11.md` | 21 | 8 | 0 | 5 | 3 | 5 |
| Datacenter tracker (`/datacenters`, the map layer, the timeline) | `datacenter-faults-2026-11-11.md` | 14 | 5 | 0 | 1 | 4 | 4 |
| Policy and regulatory monitor (`/policy?view=monitor`) | `policy-faults-2026-11-11.md` | 31 | 16 | 0 | 7 | 1 | 7 |
| Company database and capital view (`/companies`, `/companies/<id>`, `/deals/capital`) | `companies-faults-2026-11-11.md` | 31 | 15 | 0 | 8 | 1 | 7 |
| Attention and friction indices (`/attention`) | `attention-faults-2026-11-11.md` | 24 | 11 | 0 | 7 | 2 | 4 |
| **All five** | | **121** | **55** | **0** | **28** | **11** | **27** |

After chains 217 and 219 (session 1905, 13 November 2026): the counts are unchanged; no row of the five faults files changed state. The two chains landed the board, the periodicals, the records and the paths' faults (`b1bc8829f`). That landing also printed the datacenter tracker's grids view's public columns (session 1898, lab path fault 2), which are datacenter row 4, the owner's ruling; session 1905 put the default back (the cells carry footnote 1) until the owner rules.

## The three worst of each, in plain words

- **Deal tracker.** Every address shows the license hold and no deal (row 1, the owner's: `energy_deals` held whole since 21 October); before the fix the held page drew zero counts as if there were no deals (fixed); the AI view's dollar list ranked acquisitions and funding rounds as power deals (fixed; the rows themselves are the data machine's, rows 9 to 13).
- **Datacenter tracker.** The facilities, the rollups and the timeline are not drawn under the hold (row 1, the owner's); ERCOT's reserve margin read "license needed% (summer 2027)" (fixed); the timeline reads a field the new extraction no longer writes (fixed in the code; the rows' years are the data machine's, row 8).
- **Policy monitor.** The month-ahead calendar said "No dated step in these thirty days" while it held 5, hidden by the significance floor (fixed), and the date extraction misses most deadlines (row 7, the data machine's: 61 of 1,495 records hold a step); 37 of 48 "next steps" were already past (fixed); at 390 the page was 938 px wide (fixed: 390).
- **Company database.** One firm under several ids (row 17, the data machine's: Callaway under three names, none EIA's Union Electric); two firms under one EIA id (row 19, the data machine's); a license-held table sets the kind of 34 listed companies and a hover names its role (row 20, the data machine's, and for the owner's attention).
- **Attention indices.** The opposition flag is wrong for about one story in eight in ten cells read (row 15, the data machine's); "What rose" counts the unclassified September weeks as zero (row 7, the data machine's); the United States list was not the cell, a future one-story week read as 100 percent, and the opening five-day week was drawn as whole (fixed).

## The owner's five-minute check of each

Open the internal view first (`/internal/open`).

- **Deals:** `/deals`. You should see one sentence of the hold and one keyed count, no zero tables. `/deals?view=ai` the same.
- **Datacenters:** `/datacenters?view=grids`. ERCOT's reserve margin cell reads a percent or the hold's footnote, never "license needed%"; the flat-load bars show one figure each.
- **Policy:** `/policy?view=monitor` at phone width. Nothing scrolls sideways; the table shows "Next 50 (50 of 293 drawn)"; the month ahead names how many steps the significance floor hides, with a link that lifts it; a passed step reads "passed".
- **Companies:** `/companies?sort=planned`, then `/companies/eia-814`. The column heads sort; a shared name shows its EIA id; the headline hover says what is summed ("the 6 rows of 13 neither withdrawn nor completed").
- **Attention:** `/attention`. The opening week reads "(to 2026-11-06)" and is hatched; no week after the build is offered; the map has a Chart and Table toggle; choosing "United States" lists only the stories that name a state, with the note "13 of 49".

## What is not this code machine's

The 28 `data machine` rows go to the desktop's chain in chain 214's note (`docs/state/note_2026-11-13_code_c214.md`); the 11 rulings are the owner's, each named in its file.
