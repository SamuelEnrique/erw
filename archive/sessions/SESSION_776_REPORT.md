# Session 776 report: the phone

22 October 2026, from 20:43 UTC, on samueloldlaptop, unattended, in the worktree `C:\Users\lossa\Documents\erw-776` on `wip/776-allgrids` (cut from `wip/775-allgrids`). Chain `queue/done/064-night-22-october-code-allgrids-4.md`, session 776. Model spend USD 0. No warehouse data written; no request to a publisher. The reads: a local build at 390 by 844.

## Read these first

- **What a phone reader sees, measured** (`runs/chain_062/measure776.mjs`, the hub table at 390 by 844):
  - the table's frame is 358 px wide and the table 1,521 px, so the table scrolls inside its frame and the page does not scroll sideways;
  - the table starts 944 px down the page, a screen below the top, after the folded box and the intro lines.
- **The sorted column already comes first at 390**: sorted by all-in, All-in sits at 151 px, beside the rows' names and in view. Session 717's rule draws the sorted column first at every width, so nothing was needed.
- **In the default order** (by grid, then name), the columns run Energy, Transmission, Capacity, Time to connect, Headroom, Carbon, Utility, All-in. All-in sits at 1,445 px, about four frames to the right. A reader who wants it first sorts by it, and the sort line says so.
- **No change, no figure moved.** Shots: `docs/brand/review-776/` (the default order and the sort by all-in, at 390).

## What to review

1. `docs/brand/review-776/phone_allin_390.png`: All-in beside the names.

## Checks

| Check | Exit | Result |
|---|---|---|
| precheck | 0 | |
| `measure776.mjs` on 775's build (the same code) | 0 | frame 358, table 1,521, the sorted column at 151 |

## The landing

Sessions 766 to 777 landed in one push at 21:13 UTC: see `SESSION_777_REPORT.md`, "The landing".

## Decisions made without you

1. **The default order is kept**: moving All-in first by default would change the screen every reader and every check sees; the sort already does it on request.

## For Samuel's ruling

- Nothing new.

## Files

- New: `docs/brand/review-776/`, this report.
