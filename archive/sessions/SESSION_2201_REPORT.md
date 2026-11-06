# Session 2201 report: the demand growth explorer, and the bar chart's hover card

Energy Research Warehouse (ERW), chain 086 (`queue/done/086-day-23-october-portable-explorers.md`), session 2201, portable-laptop, 23 October 2026, about 20:25 to 20:45 UTC. Model Fable 5.1. Model spend USD 0. No warehouse data written; no web request but GitHub; nothing sent or posted; the site stays in review.

## Read these first

- **Every figure of `/explore/demand-growth` carries its source in its hover** (session 2200's `source` on `Num`, the words read from the figure's own key: `eia930_demand_growth`, the grid's name, the variable, the year, EIA-930 and the method note), and each of the three headline numbers a keyboard-reachable `Tip` with the same words. The signs written outside the number are as they were.
- **The brand's bar chart has a hover card.** `components/tool/GroupedBars.tsx` (drawn on the server as plain SVG; its only hover was the browser's `<title>` tooltip) is now wrapped in `components/tool/BarsHover.tsx` (new, a client component): the brand's card on fog with a rule-colored edge, the group's label, each series named in its color with its figure in mono, for the group under the pointer; the chart takes focus, and the left and right arrows (Home, End, Escape) move or hide the card. The SVG, its patterns, its direct labels, its `<title>` and every figure are unchanged; the card's words are written on the server through the chart's own `fmt`, so the client computes nothing. No hex value.
- **Every page that draws the chart is touched by the wrapper, and only in the hover:** `/explore/demand-growth` (three charts), `/cost-of-power/seller` (the revenue and capture charts) and `/datacenters?view=grids`. Their figures and layout do not change (the wrapper is a positioned block around the same SVG). Their before and after shots wait for a build (below).
- **`check-explorers.mjs`'s fixture gains a bar chart** whose wrapper draws the card: 14 of 14 in the browser.
- **No build and no gate:** 2.6 to 2.7 GB free, under the chain's line.

## What to review

- `https://erw-flame.vercel.app/explore/demand-growth` (after the landing; until then, the branch on a local build): move over any bar of the three charts: the card names the year (or the grid), each series and its figure. Tab to a chart and press the right arrow: the same card, group by group. Point at any figure or press the "i" after a headline's label: the source words.
- `https://erw-flame.vercel.app/cost-of-power/seller` and `/datacenters?view=grids`: the year charts' hover, the same way; nothing else changed.

## Checks

| Check | Exit | Result |
|---|---|---|
| `scripts/precheck.py --what "session 2201"` | 0 | on duty (another session of this machine had been on duty as "session 2400") |
| `python -m unittest tests.test_session2201 tests.test_session2200` | 0 | 14 passed |
| `CHECK_EXPLORERS_BROWSER_TEST=1 node scripts/test-check-explorers.mjs` (under the build lock) | 0 | 14 of 14 |
| `tsc --noEmit` (`runs/tsc_2201.out`) | 2 | the same 15 errors of a fresh worktree as session 2200; none in this session's files |
| `eslint` on the four changed files | 0 | clean |
| free memory at 20:44 UTC | | 2,656,444 KB: under the line |

## The landing

Not run: the memory line. `wip/2201-explorers` (`e94f0ab7`, on top of `wip/2200-explorers`) is pushed.

## Decisions made without you

1. The bar chart's card is a wrapper around the server-drawn SVG, not a rewrite of the chart as a client component: the SVG's markup, which the seller and datacenter checks read (`svg[data-bars] [data-group]`), is byte for byte as before.
2. The card's horizontal place is the group's share of the chart's width (the SVG scales with its frame and the client does not measure it), kept inside the chart's box.
3. The keyboard reads the chart as one focusable group with the arrows, as the brand asks that whatever a card says be reachable by keyboard; the chart's table under it is the other way.
4. The chain file named the battery page's year chart as the reference for the shots; the battery page does not draw `GroupedBars` (the seller, the datacenter grids view and the demand growth explorer do), so those three pages are the ones to shoot before and after, under "To finish".

## For Samuel's ruling

- Nothing new.

## To finish

With 4,000,000 KB free and the lock free: the gate on the chain's stacked branch (session 2205); and, on a local build of the branch, `node scripts/shot.mjs` of `/explore/demand-growth`, `/cost-of-power/seller` and `/datacenters?view=grids` at 1280 by 900 and 390 by 844 into `docs/brand/review-2201/` (the before shots from production, the after from the build), with the pointer over a bar for one shot of each.
