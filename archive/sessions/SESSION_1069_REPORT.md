# Session 1069 report: the planned generation in a node's county

23 October 2026, about 09:40 UTC, on samueloldlaptop, unattended, in the worktree `C:\Users\lossa\Documents\erw-1064` on `wip/1064-allgrids`. Chain `queue/done/073-evening-23-october-code-allgrids-packages-3.md`, session 1069. Model spend USD 0. No request to a publisher; no warehouse data written. Tables read: `ercot_node_places` (rebuilt from the archive), `eia860m_planned_generators` (this machine's `warehouse/output`, vintage 2026-08, the copy the Headroom column was built from).

## Read these first

- **A placed node's panel now counts ERCOT's generators due in its county** in the twelve months after EIA-860M's vintage (September 2026 to August 2027): nameplate MW and count by EIA's status, as the Headroom column counts them (under construction or complete; approvals received; the rest), keyed `allgrids|nodeplanned|<node>|construction|approved|other` and written whole (check-values' list of whole figures gains the key), with "generation in the county is not generation at the node". A county with none says so; an unplaced node says "not placed". Decision 32 of `docs/methods/siting.md`.
- **65 of the 148 counties** of placed nodes hold some; 7RNCHSLR_ALL's FAYETTE: 200.5 MW under construction (one generator), none approved or otherwise.
- **The first part** (a table chain 072 could not wire): none (session 1068).
- Only `nodes.json`'s new `planned` key was written; every other value equals the file as before (checked).
- The gaps file's row 23 ("a node's county, so the planned generation near it") is closed by this session: session 1081 writes it in the state section.

## Checks

| Check | Exit | Result |
|---|---|---|
| the builder on the tables (trial directory) | 0 | 65 of 148 counties |
| tests 1069, 1048, 711, 700, 1042 | 0 | 21 passed, 1 skipped |
| the replication's `planned_figures` against the file | 0 | FAYETTE 200.5, 0, 0; HARRIS 519.8, 0, 0: equal |
| the build and the screenshots | see session 1072's report | |


## The landing

Lands with the next landing of this chain.

## Decisions made without you

1. **ERCOT's generators only** (state TX, balancing authority ERCO): a Texas county's generators in SPP or MISO are not ERCOT's node's.
2. **Nameplate MW**, as the Headroom column sums them.

## For Samuel's ruling

- None new.
