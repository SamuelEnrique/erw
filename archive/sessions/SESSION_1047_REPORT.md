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

Lands with the next landing of this chain.

## Decisions made without you

1. **EIA-411's figures are not drawn as a grid's reserve margin** (decision 30). Reversible: the numbers are in the method note, and drawing them is a function and a cell.
2. **The tip carries no number** (no unchecked figure in a tip); the numbers are in the method note.

## For Samuel's ruling

- Whether to draw EIA-411's 2016 projections as each grid's reserve margin, labelled as projections made in 2016; or to read NERC's Long-Term Reliability Assessment instead (a new source for the data machine); or neither.

## Files

- Changed: `site/lib/siting.ts` (`EIA411_AREA`, `reserveMargin`'s why), `docs/methods/siting.md` (decision 30). New: `tests/test_session1047.py`, this report.
