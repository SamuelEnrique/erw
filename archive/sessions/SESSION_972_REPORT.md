# Session 972 report: the reads and the weight

23 October 2026, from about 00:09 UTC, on samueloldlaptop, unattended, in the worktree `C:\Users\lossa\Documents\erw-972` on `wip/972-allgrids` (cut from `wip/971-allgrids`). Chain `queue/done/065-late-22-october-code-allgrids-5.md`, session 972. Model spend USD 0. No warehouse data written; no request to a publisher. The reads: production's pages.

## Read these first

- **The tab still reads nothing from the database.**
  - This chain added no server read: 793's download works in the browser; 794's and 795's lines read a file of the build.
  - Test 716 holds.
- **The weight, on production**:
  - the hub table: 1.60 MB, from 1.59 (793's download, 10.6 KB);
  - the node list: 227 KB, unchanged;
  - two nodes as A and B: 1.64 MB (the two panels with 794's chart and table, 46.5 KB over the hub table's page).
- `weigh.mjs` stopped at the battery card: the card page has no `main` element, which the script waits for. Session 783 weighed the card at 41 KB, and 970 changed only its labels, so the card was not weighed again.
- A new section of `docs/reviews/siting-reads-2026-10-22.md`.

## What to review

1. `docs/reviews/siting-reads-2026-10-22.md`, the last section.

## Checks

| Check | Exit | Result |
|---|---|---|
| precheck | 0 | |
| `weigh.mjs` on production, four addresses | 1 | three weighed, as above; the card has no `main` |
| `tests.test_session716` | 0 | OK |

## The landing

Sessions 970 to 977 landed in one push: see `SESSION_977_REPORT.md`, "The landing".

## Decisions made without you

1. **No timer build**, as at 783: no server read was added.
2. **The card not weighed again**: its weight is 783's, and 970's change is a few labels.

## For Samuel's ruling

- Nothing new.

## Files

- Changed: `docs/reviews/siting-reads-2026-10-22.md`.
- New: this report.
