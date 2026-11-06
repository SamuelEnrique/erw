# Session 782 report: 390 pixels and accessibility

22 October 2026, from 21:41 UTC, on samueloldlaptop, unattended, in the worktree `C:\Users\lossa\Documents\erw-782` on `wip/782-allgrids` (cut from `wip/781-allgrids`). Chain `queue/done/064-night-22-october-code-allgrids-4.md`, session 782. Model spend USD 0. No warehouse data written; no request to a publisher. The reads: production's pages in the internal view.

## Read these first

- **AccessLint at 1280 and 390** (session 583's scanner, WCAG 2.2 A and AA), on production, which serves 772 to 777 since 21:30 UTC:
  - the node list filtered to storage by its swing (772);
  - the third card (773);
  - the node list as 777 hands it over.
  - **6 scans, 0 findings, 0 errors.**
- **`check-390.mjs` on the same three: 0 with a finding.**
- The headless browser was stopped. The results are in `docs/brand/review-782/`.

## What to review

1. `docs/brand/review-782/scan782.json`.

## Checks

| Check | Exit | Result |
|---|---|---|
| precheck | 0 | |
| `scan-583.mjs`, 3 addresses at 1280 and 390 | 0 | 6 scans, 0 findings |
| `check-390.mjs --pages` (3) | 0 | 0 with a finding |

## The landing

Sessions 778 to 787 landed in one push at 22:09 UTC: see `SESSION_787_REPORT.md`, "The landing".

## Decisions made without you

1. **Production**, which serves every page this chain changed.

## For Samuel's ruling

- Nothing new.

## Files

- New: `docs/brand/review-782/`, this report.
