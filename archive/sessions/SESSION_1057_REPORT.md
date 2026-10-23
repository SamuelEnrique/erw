# Session 1057 report: the changed addresses at 390 and in AccessLint

23 October 2026, about 08:40 UTC, on samueloldlaptop, unattended, on `wip/1042-allgrids`. Chain `queue/done/072-day-23-october-code-allgrids-packages-2.md`, session 1057. Model spend USD 0. No request; a local build (port 3142, the internal view) and a headless Chrome on port 9342, stopped after the scan.

- **AccessLint: 10 scans, 0 findings, 0 errors, 0 pages wider than the window** (session 583's scanner, `docs/brand/review-583/scan-583.mjs`, the engine `audit_live` runs, WCAG 2.2 A and AA), at 1280 and 390 on the addresses this chain changed: `/cost-of-power?view=allgrids&rows=nodes` (the County and Zone columns and filters), the panel of a placed node (7RNCHSLR_ALL) and of an unplaced one (ABINDUST_RN), `/cost-of-power?view=allgrids` (the reserve margin's tip) and `/data/methods/siting` (version 7).
- **`site/scripts/check-390.mjs` on four of them: 4 read, 0 with a finding**: each 390 px wide at 390, no table or label cut. The node list scrolls sideways in its own region at 390, as before.
- `/data` and the package pages changed only in their words in `docs/methods/packages.md` (rendered at `/data/methods/packages`, a methods page of the same template, scanned by 1036).

## Checks

| Check | Exit | Result |
|---|---|---|
| `scan-583.mjs`, 5 addresses at 1280 and 390 (`SCAN_ONLY`) | 0 | 10 scans, 0 findings (`runs/chain_072/scan1057.json`) |
| `check-390.mjs --pages` (4) | 0 | 0 with a finding |

## The landing

Landed with sessions 1043 to 1061 in one push: `wip/1042-allgrids` gated by `scripts/land_check.py` at `a8a91dde` (freeze, main merged, task branches, the clean-copy suite 6,224 tests OK, npm ci, the build: pass; check-values: 12 failures, all the chain's known three: the ten license-held floors, `/digest` before the day's issue, and the 21 October Digest's revised WTI; every All grids value matched). As the rules say, the same commit was built locally on its own and checked by hand: check-routes 0 (225 pages in review, 0 failed), check-cross-checks 0 (92 passed), check-csp 0 (97 pages, 0 violations). Main then gained one queue file only (data chain 052's), merged without a third gate (`3306941d`). Snapshot `c072a-before` as its own command at 08:58 UTC; pushed to `task/1042-1061-allgrids` after the ancestry check; merged by run 39928557187 as `cbf8662e`; production served the node list's county filter (`data-node-county`) at 09:18 UTC (9 minutes of probing); `c072a-after` and `compare`: **0 differences** on the 25 pages (every page is in review: a visitor sees the in-review page), expected.

## Decisions made without you

- None.

## For Samuel's ruling

- None new.
