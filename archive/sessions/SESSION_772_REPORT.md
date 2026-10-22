# Session 772 report: the node list by class

22 October 2026, from 20:31 UTC, on samueloldlaptop, unattended, in the worktree `C:\Users\lossa\Documents\erw-772` on `wip/772-allgrids` (cut from `wip/771-allgrids`). Chain `queue/done/064-night-22-october-code-allgrids-4.md`, session 772. Model spend USD 0. No warehouse data written; no request to a publisher.

## Read these first

- **A "Class" filter beside "Find a node by name"**: every class, or one of storage (238 nodes), gas (201), wind (171), solar (143), mixed (60) or other (60), as ERCOT's disclosures settle them (`node_basis_daily`, `x_class`).
  - It is kept in the address (`ncls`), so a battery trader can send "the storage nodes by their swing".
  - The count line says which ("238 of 873 nodes shown (class storage)"), and the download's file name carries it.
- **A checked address**: `&rows=nodes&ncls=storage&nsort=swing&ndir=desc`, floor 10.
- **No figure moved**: check-values 2,908 of 2,908; the existing tab 0 differences.

## What to review

1. After the landing, `https://erw-flame.vercel.app/cost-of-power?view=allgrids&mw=1000&rows=nodes&ncls=storage&nsort=swing&ndir=desc` (internal view).
2. Shots: `docs/brand/review-772/`.

## Checks

| Check | Exit | Result |
|---|---|---|
| precheck | 0 | |
| `tests.test_session772`, `724`, `746` | 0 | OK |
| `db_probe.py` (the build only on its 0) | 0 | |
| `npm ci`, `npm run build` (lock `s772`, beat) | 0 | |
| check-values, `CHECK_VALUES_PAGES=/cost-of-power` | 0 | 2,908 of 2,908 |
| `check-existing-tab.mjs` | 0 | every figure the same |

## The landing

Sessions 766 to 777 landed in one push at 21:13 UTC: see `SESSION_777_REPORT.md`, "The landing".

## Decisions made without you

1. **The classes are the node file's own**, listed from its rows, so a class the table adds appears without a change.

## For Samuel's ruling

- Nothing new.

## Files

- Changed: `site/app/cost-of-power/AllGridsNodes.tsx`, `site/app/cost-of-power/AllGridsView.tsx` (the class from the address), `site/scripts/check-values.mjs` and `check-values-floor.json` (one address).
- New: `tests/test_session772.py`, `docs/brand/review-772/`, this report.
