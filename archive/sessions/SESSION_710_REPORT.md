# Session 710 report: the screen, A against B

22 October 2026, from 09:42 UTC, on samueloldlaptop, unattended, in the worktree `C:\Users\lossa\Documents\erw-710` on `wip/710-allgrids` (cut from `wip/709-allgrids`). Chain `queue/done/050-night-23-october-code-allgrids.md`, session 710. Model spend USD 0. No warehouse data written; no request to a publisher.

## Read these first

- **"Sort and filter"**, a fold in the left box:
  - **Sort** by any column or by grid and name, largest or smallest first.
  - **Filter** by grid (tick boxes), by kind (load zones or hubs), by an energy band (USD per MWh, from and to), and to "only rows whose every cost part is held".
  - The line above the table names the sort, the rows shown of 48, the filters, and that "the order is the column's, not a ranking of sites". A row with no figure, or whose figure is held under a license, sorts last; **a held figure is never sorted by its value**, which the order would give away.
- **"A and B, side by side"**, a second fold, picks two rows. The panel above the table gives, in "Your load"'s form (two columns, B less A, no verdict):
  - every column's figure and the difference;
  - the load's year all-in in USD and the MWh it uses (its draw while running times the hours it runs a year).
  - A sets one headline line, every figure a key: "A datacenter load of 100 MW at ERCOT HB_HUBAVG pays USD 42.13 per MWh all-in, USD 33,212,998 a year; generators there took a median of 45.80 months to connect."
- **Every input is in the address**, so a reader can send the screen: `sort`, `dir`, `grid`, `kind`, `lo`, `hi`, `held`, `a`, `b`. `tests/test_session710.py` reads an address back to the same inputs.
- **Keys**:
  - `allgrids|col|<column>|<row>|<profile key>`, `allgrids|diff|<column>|<a>|<b>|<profile key>`;
  - `allgrids|year|<row>|<year key>`, `allgrids|mwh|<row>|<year key>`, `allgrids|yeardiff|<a>|<b>|<year key>`.
- check-values reads `/cost-of-power?view=allgrids&sort=allin&a=ercot%3AHB_HUBAVG&b=nyiso%3AN.Y.C.` and the node list sorted by energy.

## What to review

1. After the landing, open `https://erw-flame.vercel.app/cost-of-power?view=allgrids` (internal view).
2. Open "A and B, side by side" in the box. Choose A: ERCOT HB_HUBAVG and B: ERCOT LZ_WEST, then press Show. The headline and the panel appear; B less A for energy is +3.08.
3. Open "Sort and filter". Sort by the all-in figure, tick ERCOT and CAISO, and press Show. The line above the table says what is shown, and CAISO's rows go last (their all-in is not held).
4. Copy the address into a new tab: the same screen.
5. Screenshots: `docs/brand/review-710/` (712's build).

## Checks

| Check | Exit | Result |
|---|---|---|
| precheck | 0 | |
| `tests.test_session710` (the address round trip; no figure last; a held capacity never sorted by value; the filters; the A and B keys) | 0 | OK |
| built and checked on 712's branch | 0 | see 712's report; 712 put the signs outside the checked figures and added the whole-number keys check-values asked for |

## The landing

With sessions 706 to 712 in one push.

## Decisions made without you

1. **The screen's inputs are in the left box** (the prompt's rule that the left box holds every input), folded.
2. **"Load band" is read as an energy band**, with a filter by kind beside it. The prompt's words could also mean a band of load sizes, which no row has.
3. **The year's MWh**: a load drawing its size times its load factor in every hour it runs. The electrolyzer draws its full size, its load factor being the share of hours it runs.

## For Samuel's ruling

- What "load band" means, if not an energy band.

## Files

- Changed: `site/lib/siting.ts` (the screen's inputs, `columnValue`, `screen`, `yearOf`, the keys), `site/app/cost-of-power/AllGridsForm.tsx` (the two folds), `site/app/cost-of-power/AllGridsView.tsx` (`Headline`, `AbPanel`, the sort line), `site/scripts/check-values.mjs` (two addresses).
- New: `tests/test_session710.py`, this report.
