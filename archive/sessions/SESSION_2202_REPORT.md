# Session 2202 report: the interconnection explorer, and the stacked chart's hover card

Energy Research Warehouse (ERW), chain 086 (`queue/done/086-day-23-october-portable-explorers.md`), session 2202, portable-laptop, 23 October 2026, about 20:26 to 20:33 UTC. Model Fable 5.1. Model spend USD 0. No warehouse data written; no web request but GitHub; nothing sent or posted; the site stays in review.

## Read these first

- **Every figure of `/explore/interconnection` carries its source in its hover:** `iso_queue_statistics`, the queue and its entry year ("CAISO's queue, entry year 2024"), the variable, the year, the ISO's own queue table (`caiso_interconnection_queue`) and the method note; the header's count of positions with no queue date names the header line it is read from. Each of the three headline numbers has a keyboard-reachable `Tip` with the same words. A held queue (NYISO, MISO, ISO-NE) shows "license needed" as before and carries no source words: `Num` draws the hold before the source.
- **The stacked chart has the brand's hover card.** `components/tool/SeriesChart.tsx` (the tool pages' stacked and line chart, a client component whose only hover was the `<title>` tooltip) now draws the card on fog with a rule-colored edge for the entry year under the pointer: the year (and "entry year not over" where it is partial), each status named in its color with its figure in mono, and the total under a rule. The chart takes focus and the arrows (Home, End, Escape) move or hide the card. The `<title>` stays; nothing drawn and no figure changed. Every page that draws `SeriesChart` gains the card: the explorer, and the tool pages of sessions 296 onward (`/cost-of-power/battery`'s income chart among them).
- **Three earlier tests read the new figure markup** (`tests/test_session403.py`, `404`, `405`: the one assertion each that quoted the `Num` line without `source`); 57 tests of the six sessions pass together.
- **No build and no gate:** 2.6 to 3.5 GB free, under the chain's line.

## What to review

- `https://erw-flame.vercel.app/explore/interconnection` (after the landing; until then, the branch on a local build): move over a year's bar of the stacked chart: the card names the year, each status with its count, the total. Tab to the chart, press the right arrow: the same, year by year. Point at a figure in either table, or press the "i" after a headline: the source words. Choose NYISO in the Queue filter: "license needed", no figure, no source.
- `https://erw-flame.vercel.app/cost-of-power/battery` (the income chart) and the other tool pages that draw the stacked chart: the same card; nothing else changed.

## Checks

| Check | Exit | Result |
|---|---|---|
| `scripts/precheck.py --what "session 2202"` | 0 | on duty (another session of this machine had been on duty as "session 2301") |
| `python -m unittest` on sessions 403, 404, 405, 2200, 2201 and 2202 | 0 | 57 passed, 2 skipped (sessions 403 to 405's own skips) |
| `tsc --noEmit` (`runs/tsc_2202.out`) | 2 | the same 15 errors of a fresh worktree; none in this session's files |
| `eslint` on the two changed files | 0 | clean |
| free memory at 20:30 UTC | | 3,504,024 KB: under the line |

## The landing

Not run: the memory line. `wip/2202-explorers` (`2c4fa213`, on top of `wip/2201-explorers`) is pushed.

## Decisions made without you

1. The card's category is read from the pointer's share of the plot's width (the chart is drawn at the width it has), as the bar chart's wrapper reads it; the card sits beside the category's middle.
2. The stacked card shows the total only where the chart stacks more than one series; a value the chart does not hold reads "not held", never 0.
3. The three earlier tests' assertions were updated to the new markup rather than kept: each tests that the figure carries its key, which it still does, with the source beside it.
4. The report's times: session 2201's report said about 20:25 to 20:45 UTC; the machine's clock read 20:19 to 20:26 for it, and this one 20:26 to 20:33.

## For Samuel's ruling

- Nothing new.

## To finish

With 4,000,000 KB free and the lock free: the gate on the chain's stacked branch (session 2205).
