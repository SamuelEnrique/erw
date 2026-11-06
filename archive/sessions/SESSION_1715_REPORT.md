# Session 1715 report: a scrolling box's run-time name takes its fold's heading

Energy Research Warehouse (ERW), session 1715, chain 191, samueloldlaptop, 6 November 2026, 17:42 to 17:45 UTC. Model: Claude Opus 5.5 (the file names Fable 5.1). Model spend USD 0. No warehouse data written; nothing sent or posted. Branch `wip/1715-a11y`, cut from `origin/main`.

## What it did, with commits (`cfe6575dc`)

- **The fault** (session 1694's reading of `/board`): an opened fold's scrolling box was named "Capacity and equities2 rows". `site/components/ScrollRegions.tsx`'s `regionName` asked for the first of "h2, h3, summary". A selector list returns the first match in the page's order, and a fold's `<summary>` comes before the `<h2>` inside it, so the name took the summary's whole text with its row count run in.
- **The fix**: the heading first (`h2, h3` within the section or fold), the summary only where there is none. On the gate's build, `/board`'s box is now named "Capacity and equities, 2 of 2" (the page has two regions of that heading, which `uniqueNames` numbers).
- **Tests**: `tests/test_session1715.py` (2 tests), and sessions 412, 428 and 583's, 43 tests in all.
- The file had not changed since session 583 (21 October).

## Decisions made without you

- None.

## For Samuel's ruling

- None.
