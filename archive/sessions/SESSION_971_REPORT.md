# Session 971 report: 390 pixels and accessibility

23 October 2026, from about 00:35 UTC, on samueloldlaptop, unattended, in the worktree `C:\Users\lossa\Documents\erw-971` on `wip/971-allgrids` (cut from `wip/970-allgrids`). Chain `queue/done/065-late-22-october-code-allgrids-5.md`, session 971. Model spend USD 0. No warehouse data written; no request to a publisher. The reads: production's pages in the internal view (production serves 788 to 799 since 23:59 UTC).

## Read these first

- **AccessLint at 1280 and 390** (session 583's scanner, WCAG 2.2 A and AA), on production, on this chain's addresses:
  - the tab as it opens, with the hub table's download (793);
  - two nodes as A and B (794), BBREEZE_1_2 with PALACIOS_RN: BBREEZE_1_2's panel also carries the "settles at the same prices" line (795);
  - 799's pair, 7RNCHSLR_ALL with A4_DGR1_RN;
  - the battery card (its 970 labels are not on production yet; the frame and the rest are).
  - **8 scans, 0 findings, 0 errors.**
- **`check-390.mjs` on the same four: 0 with a finding** (no sideways scroll, no table unframed, no label cut).
- The headless browser was stopped. The results are in `docs/brand/review-971/`.

## What to review

1. `docs/brand/review-971/scan971.json` and `c390_971.json`.

## Checks

| Check | Exit | Result |
|---|---|---|
| precheck | 0 | |
| `scan-583.mjs`, 4 addresses at 1280 and 390 | 0 | 8 scans, 0 findings |
| `check-390.mjs --pages` (4) | 0 | 0 with a finding |

## The landing

With 970 to 977, in session 977.

## Decisions made without you

1. **Production**, which serves every page of 788 to 799; 970's card labels were measured on a build in session 970.

## For Samuel's ruling

- Nothing new.

## Files

- New: `docs/brand/review-971/`, this report.
