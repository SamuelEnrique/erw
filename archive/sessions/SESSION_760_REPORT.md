# Session 760 report: 390 pixels and accessibility

22 October 2026, from 19:27 UTC, on samueloldlaptop, unattended, in the worktree `C:\Users\lossa\Documents\erw-760` on `wip/760-allgrids` (cut from `wip/759-allgrids`). Chain `queue/done/063-evening-22-october-code-allgrids-3.md`, session 760. Model spend USD 0. No warehouse data written; no request to a publisher. The reads: production's pages in the internal view.

## Read these first

- **AccessLint at 1280 and 390** (session 583's scanner, WCAG 2.2 A and AA), on the three addresses this chain added or changed, on production, which serves 746 since 19:20 UTC:
  - the node list by intraday swing;
  - a node's panel with its swing line (APPLE_RN);
  - the list filtered by name and sorted by spread.
  - **6 scans, 0 findings, 0 errors.**
- **`check-390.mjs` on the same three: 0 with a finding**; no page wider than 390.
- 757's fix (the sort line's case) is words only, and lands with 764.
- The headless browser was stopped (10 processes of its profile). The results are in `docs/brand/review-760/`.

## What to review

1. `docs/brand/review-760/scan760.json`.

## Checks

| Check | Exit | Result |
|---|---|---|
| precheck | 0 | |
| `chrome-583.mjs` on production (port 9760) | 0 | internal view open |
| `scan-583.mjs`, 3 addresses at 1280 and 390 | 0 | 6 scans, 0 findings |
| `check-390.mjs --pages` (3) | 0 | 0 with a finding |

## The landing

With 757 to 764, in session 764.

## Decisions made without you

1. **Production, not a local build**: 746, this chain's only new page part, is served there; no address had a comma this time.

## For Samuel's ruling

- Nothing new.

## Files

- New: `docs/brand/review-760/`, this report.
