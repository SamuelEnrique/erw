# Session 2881 report: the siting gaps file, its state

5 November 2026, about 22:30 UTC, on lab-desktop (the data machine), chain 147, unattended. Model spend USD 0. Pulls: none.

## Read these first

- **A new state section in `docs/reviews/siting-gaps.md`, "State on 5 November 2026, night (chain 147)":** no row changed state on the tab. For each row it gives what is now held and why the row stays as it is, with the tables named:
  - the tariffs held (no tab row in their territories);
  - zone growth (filled for the sub-region rows, unchanged);
  - reserve margins, substations and the node hub (open);
  - the node energy figure (gone since 31 October, waiting on a ruling).
- **Four held tables the open rows can use** were found on this machine and named for chain 148: `ercot_node_wires_utilities`, `eia861_delivery_only`, `interconnection_agreements_signed` and `_by_grid`. 148's sessions 2889, 2894 and 2899 should start from them, not from a new pull.
- **The table at the top of the file is unchanged,** so `gaps.json` does not move.

## Files

- On `wip/c147-data`: `docs/reviews/siting-gaps.md` (a section appended), this report.
