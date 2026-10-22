# Session 777 report: the node list's payload

22 October 2026, from 20:45 UTC, on samueloldlaptop, unattended, in the worktree `C:\Users\lossa\Documents\erw-777` on `wip/777-allgrids` (cut from `wip/776-allgrids`). Chain `queue/done/064-night-22-october-code-allgrids-4.md`, session 777. Model spend USD 0. No warehouse data written; no request to a publisher.

## Read these first

- **Where the node list's bytes went**: the 873 rows handed to the browser were 201 KB of JSON.
  - About 70 KB of that was each field's name repeated on every row.
  - 17 KB was an id that is the node's name after "ercot:".
- **What changed, with no word or figure moved**: the rows go to the browser **column by column** (`lib/siting.ts`, `nodeColumns`), and the browser puts them back together (`nodeRowsOf`, the id rebuilt from the name). A test checks that the rows come back equal, field by field, under the flexible profile (`tests/test_session777.py`).
- **The node list's page: 340,129 to 226,143 bytes** (a third less); the server's payload in it 258 KB to 144 KB.
- **No figure moved**: check-values 2,908 of 2,908; the existing tab 0 differences.

## What to review

1. After the landing, `https://erw-flame.vercel.app/cost-of-power?view=allgrids&rows=nodes` (internal view): the same list, sorts, filters and download.

## Checks

| Check | Exit | Result |
|---|---|---|
| precheck | 0 | |
| `tests.test_session777`, `724`, `746`, `772`, `716` | 0 | OK |
| `db_probe.py` (the build only on its 0) | 0 | |
| `npm ci`, `npm run build` (lock `s777`, beat) | 0 | |
| check-values, `CHECK_VALUES_PAGES=/cost-of-power` | 0 | 2,908 of 2,908 |
| `check-existing-tab.mjs` | 0 | every figure the same |
| `weigh.mjs`, the node list | 0 | 226,143 bytes (was 340,129) |

## The landing

With 766 to 781, in session 781.

## Decisions made without you

1. **No figure rounded**: the full figures stay (check-values compares them to the recomputed ones); only the shape of the hand-over changed.

## For Samuel's ruling

- Nothing new.

## Files

- Changed: `site/lib/siting.ts` (`NodeColumns`, `nodeColumns`, `nodeRowsOf`), `site/app/cost-of-power/AllGridsNodes.tsx`, `site/app/cost-of-power/AllGridsView.tsx`.
- New: `tests/test_session777.py`, `docs/brand/review-777/`, this report.
