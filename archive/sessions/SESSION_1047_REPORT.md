# Session 1047 report: reserve margins for every grid, named and not drawn

23 October 2026, about 07:55 UTC, on samueloldlaptop, unattended, on `wip/1042-allgrids` (cut from chain 071's `wip/1039-allgrids`, main merged). Chain `queue/done/072-day-23-october-code-allgrids-packages-2.md`, session 1047. Model spend USD 0. No request to a publisher; no warehouse data written. The table read: `eia411_capacity_margins_annual`, rebuilt from the archive's bucket into `runs/archive_restore/` (session 1046).

## Read these first

- **The data machine's reserve margin table is EIA-411's last release, of November 2016** (its session 895: the Electric Power Annual no longer carries one). Its figures for summer 2027, the summer the tab's ERCOT margin reads, are projections made in 2016. Set side by side for ERCOT: ERCOT's own CDR of December 2025 gives **11.43%**; EIA-411's 2016 projection for TRE gives **38.07%**: about the same capacity (111,557 MW against 109,350) over a demand 17,300 MW lower than ERCOT's forecast now. PJM's would read 58.56%.
- **So no grid's figure is drawn from it** (decision 30 of `docs/methods/siting.md`): a ten-year-old projection beside "capacity above the peak" would mislead. Each grid's "reserve margin not held" tip now names EIA-411, the area it reports the grid under (WECC, the whole Western Interconnection, for CAISO; NPCC, New York and New England together, for both; TRE, SPP, MISO and PJM each its own) and why its figure is not drawn. ERCOT's cell is unchanged (its CDR). No figure on the page moves.
- Open items line 20 stays open, now for a ruling: whether to draw EIA-411's projections at all, labelled, or to read NERC's current Long-Term Reliability Assessment (the table's method note leaves NERC to you).

## What to review

1. `docs/methods/siting.md`, decision 30 (the two ERCOT figures side by side, and why).
2. On a build of the branch, internal view: `/cost-of-power?view=allgrids`, a CAISO, NYISO, ISO-NE, SPP or PJM row, the Headroom column: hover "reserve margin not held". The tip names EIA-411 and the area.

## Checks

| Check | Exit | Result |
|---|---|---|
| tests 1047, 1027 | 0 | the area of every grid named; the why's words; the method note's two figures |
| the build and the screenshots | see session 1048's report | |

## The landing

Landed with sessions 1043 to 1061 in one push: `wip/1042-allgrids` gated by `scripts/land_check.py` at `a8a91dde` (freeze, main merged, task branches, the clean-copy suite 6,224 tests OK, npm ci, the build: pass; check-values: 12 failures, all the chain's known three: the ten license-held floors, `/digest` before the day's issue, and the 21 October Digest's revised WTI; every All grids value matched). As the rules say, the same commit was built locally on its own and checked by hand: check-routes 0 (225 pages in review, 0 failed), check-cross-checks 0 (92 passed), check-csp 0 (97 pages, 0 violations). Main then gained one queue file only (data chain 052's), merged without a third gate (`3306941d`). Snapshot `c072a-before` as its own command at 08:58 UTC; pushed to `task/1042-1061-allgrids` after the ancestry check; merged by run 39928557187 as `cbf8662e`; production served the node list's county filter (`data-node-county`) at 09:18 UTC (9 minutes of probing); `c072a-after` and `compare`: **0 differences** on the 25 pages (every page is in review: a visitor sees the in-review page), expected.

## Decisions made without you

1. **EIA-411's figures are not drawn as a grid's reserve margin** (decision 30). Reversible: the numbers are in the method note, and drawing them is a function and a cell.
2. **The tip carries no number** (no unchecked figure in a tip); the numbers are in the method note.

## For Samuel's ruling

- Whether to draw EIA-411's 2016 projections as each grid's reserve margin, labelled as projections made in 2016; or to read NERC's Long-Term Reliability Assessment instead (a new source for the data machine); or neither.

## Files

- Changed: `site/lib/siting.ts` (`EIA411_AREA`, `reserveMargin`'s why), `docs/methods/siting.md` (decision 30). New: `tests/test_session1047.py`, this report.
