# Session 317 report: the rest of the chart ruling, part one

19 October 2026, from 22:10 UTC, unattended, on samueloldlaptop (the code machine), the fourth session of the chain of 19 October, daytime (`CHAIN_OCT19B_PROMPT.md`). Branch `wip/317-charts` in the worktree `erw-317` (new), from session 316's commit; lands on main as `task/317-charts` after sessions 315 and 316. Model spend USD 0: no model call. No pull, no warehouse data written.

## Read these first

- **One shared SVG set, five kinds** (`site/components/svgchart.tsx`): `CategoryChart` (bars, lines and areas over categories, stacked where asked, a second axis, a category drawn faint, a note per category in the hover, named reference lines), `HeatChart` (rows by columns, one color at a strength by value over the panel, a hatched cell where nothing is held, the scale's ends named), `BandChart` (a year against the range, mean and last year of the years before), `ScatterChart` (points named beside them) and `BoxPlot` (five-number boxes on one scale, the median in the accent and named with its value). Each is drawn for the width it measures (its text keeps its size on a phone), carries the series' names on the chart in their own colors, a Chart | Table toggle and a hover card on fog; every color is a token; the axis step is session 314's rule.
- **Every page kept its chart files, names and props**: `app/curtailment/Charts.tsx` (XY, Heat), `components/mix/Charts.tsx` (HourStack, Lines, Bars, Heat), `components/supply/SupplyCharts.tsx` (Band), `components/BoxChart.tsx`, `app/cost-of-power/charts.tsx` (RankBars, HeatGrid, CostCarbon), `LoadCharts.tsx` (YearCost), `seller/SellerCharts.tsx` (MonthlyRevenue, CoverageLine and the two unused) now draw through the set with the arrays they took on the canvas, so no page changed its data. **No number moved**: `check-values` on the moved pages reads 2,633 of 2,633 keys matching Supabase.
- **The detector reads 0 canvas charts** on `/curtailment` (9 SVG charts with labels and toggles), `/supply` (10), `/cost-of-power` and `?view=grids` (1 and 9), `/cost-of-power/seller`, the Grid tool's Clean tab (4) and `/prices?tab=ercot` (the box plot). **The Mix tab still reads 4 canvases**: they are the four `ShareBar`s of the day's mix (session 22's single stacked bar on the Now blocks), which the prompt lists under neither session; session 318 moves them with the finding cards, and the Mix tab then reads 0.
- **What the canvas had and the set does not:** the range slider (`zoom` on the curtailment months and the seller's monthly revenue; the box plot's zoom) and the PNG download; the table stands in for both (session 303's ruling note stands).
- **Three check scripts moved with the charts**: `check-curtailment.mjs`, `check-supply.mjs` and `check-mix.mjs` read the canvas's tooltips through the chart library; they now put the mouse on a category of the SVG chart (the svg says where its plot runs) and read the hover card, whose rows read "name: value unit". `check-curtailment` 118 of 118 and `check-supply` 27 of 27 pass; `check-mix` found two things of this session (the heat legend's "not held" on a page whose rule forbids the words, and the Mix tab's `data-chart="stack"` markers, both fixed in the last commit) and is run again on that commit (below).

## What to review

In the internal view (https://erw-flame.vercel.app/internal/open first).

1. `docs/brand/review-317/` (24 shots and a README): each page before (production) and after at 1280 and 390.
2. https://erw-flame.vercel.app/curtailment : the months chart (bars with a share on the right axis), the heat map of free hours; press "Table" on any chart.
3. https://erw-flame.vercel.app/supply : the seasonal bands; point at a band.
4. https://erw-flame.vercel.app/cost-of-power?view=grids : the rank bars, the heat grids, the cost against carbon scatter.
5. https://erw-flame.vercel.app/prices?tab=ercot : the box plot.
6. `site/components/svgchart.tsx`; `tests/test_session317.py`.

## What was done

- `site/components/svgchart.tsx` (new): the five kinds, `Toggle`, `DataTable`, the hover `Card`, `useWidth`, `bounds`, `ticksOf`, `nice`.
- The seven chart files rewritten as adapters over the set (the same exports and props).
- `site/scripts/check-curtailment.mjs`, `check-supply.mjs`, `check-mix.mjs`: the SVG charts' hover cards and svg markers instead of the canvas's tooltips.
- Tests: `tests/test_session317.py` (7); the pins of sessions 144 (page), 145, 194, 236 and 241a that named the canvas library follow, each marked.
- `docs/brand/review-317/` (24 shots and a README).

## Checks

| Check | Exit | Result |
|---|---|---|
| `tsc --noEmit` (worktree, session 296's packages by junction), twice | 2, 2 | every error a fresh worktree's generated types; none in the files changed |
| `eslint` on the eight files | 0 | |
| `tests.test_session317`, `134`, `138`, `140`, `144`, `144_page`, `145`, `194`, `236`, `241a`, `133` | 0 | OK after the five pins moved |
| `npm run build` (erw-296 detached at the session's commits, under the mutex), three times | 0, 0, 0 | 0 statement timeouts |
| The canvas detector (`runs/chain_oct19/s303_canvas.mjs`) on nine pages | 0 | the counts above; 0 canvas on every moved page but the Mix tab's four share bars |
| `check-values.mjs` on `/curtailment`, `/supply`, `/cost-of-power`, `/grid`, `/prices`, `/mix` | 0 | 2,633 of 2,633 |
| `check-routes`, `check-curtailment`, `check-supply`, `check-datacenter-scenarios`, `check-seller-scenarios` | 0 × 5 | 211 pages; 118 of 118; 27 of 27; 119 of 119; all passed |
| `check-mix`, the second commit | 1 | three checks: the heat legend's words and the stack markers (fixed in the third commit); its rerun on `1a0a97da`: MIXRERUN |
| Captures, 1280 and 390, six pages, before and after | | `docs/brand/review-317/`; four shots of 1280 retaken (the internal door's form was not ready the first time) |
| Suite, clean copy, the commit pushed | SUITE | |
| `scripts/freeze.py status` | FREEZE | |

## Landing of session 316 (recorded here: session 316's report is in that landing's own commit)

LANDING316

## Landing

LANDING

## Decisions made without you

- **The adapters keep the pages' chart files**: the seven files still exist with their names and props and call the shared set, so the pages hand the same arrays; the prompt's "the same props so no page changes its data" is kept literally.
- **A heat map is one color at a strength** (the accent over the panel), not a two- or three-color ramp: the brand names one sequential color, and a blank cell is hatched. The curtailment heat's old ramp (duration tokens) and the cost grid's "cheap" to "dear" words are kept as the scale's end words.
- **A hatched bar stands for a partial period** (a partial month on the rank bars, a year short of twelve months on the datacenter and generator charts) where the canvas drew the bar pale.
- **The range slider and the PNG download are gone** (as session 303); the table holds every row.
- **The Mix tab's four share bars are left to session 318** (the day's mix on the Now blocks, session 22's; not in this session's list).
- **The check scripts drive the SVG hover** by putting the mouse on a category, which is what a reader does; the card's rows gained a colon so the old regexes read them.
- Questions skipped (Impeccable's playbooks ask them). Impeccable `detect` was not run: the set writes no color or font literal, and the page files did not change.

## For Samuel's ruling

- Whether a range slider should return on the long category charts (the curtailment months, the seller's monthly revenue), or the table's rows are enough (session 303 asked the same for the time chart).
- The heat maps' one-color scale: keep, or a three-color ramp in the brand's tokens.

## Files

- New: `site/components/svgchart.tsx`, `tests/test_session317.py`, `docs/brand/review-317/`, this report.
- Changed: `site/app/curtailment/Charts.tsx`, `site/components/mix/Charts.tsx`, `site/components/supply/SupplyCharts.tsx`, `site/components/BoxChart.tsx`, `site/app/cost-of-power/charts.tsx`, `site/app/cost-of-power/LoadCharts.tsx`, `site/app/cost-of-power/seller/SellerCharts.tsx`, `site/scripts/check-{curtailment,supply,mix}.mjs`, `tests/test_session{144_page,145,194,236,241a}.py`.
- Not in git: `runs/chain_oct19/s317*`.
