# Session 931 report: a siting gap, the planned generation in an ERCOT node's county

23 October 2026, from 10:17 UTC, on lab-desktop (the data machine), a session of `queue/done/052-day-23-october-data-world-oil-reactors-stocks.md`. Model spend USD 0. Pulls: none of 10.

## Read these first

- **The gap row, read from the code machine's latest state first** (chain 072's section, about 08:10 UTC): "a node's county, so the planned generation near it" stood open, "the county is known; the sum by county is not built". Both inputs are public ERW tables (ERCOT's queue and EIA-860M), so no ruling is needed and no robots-held path is asked.
- **One derived table written, validated, archived, in coverage (sector power, public), in the release package, both holds, with its method note** (`docs/methods/ercot_node_planned_generation.md`): `ercot_node_planned_generation`, 569 nodes in 148 counties. For each placed node, ERCOT's active interconnection queue projects in its county (count, MW, MW by solar, wind, storage, gas and other, the earliest proposed in-service date) and EIA-860M's planned generators there (count, nameplate MW, MW by technology group).
  - ERCOT's queue held 1,169 active projects (298,606 MW); 1,031 are in a node's county. The most: Pecos 36 projects, 16,313 MW; Jack 6,913; Reeves 6,703; Mitchell 6,616; Milam 5,781.
  - EIA-860M held 545 planned generators in Texas; 475 are in a node's county.
- **The cross-check:** Pecos, Brazoria and Harris counted by hand from the two tables equal the table in every column checked (Pecos: 36 queue projects, 16,312.91 MW; 10 EIA-860M generators, 1,098.5 MW).
- **The two sources are not the same list:** in the 148 counties the queue holds 264,182 MW, EIA-860M 76,866; 32 counties have queued capacity and no EIA-860M plan; their county rankings agree only loosely (Spearman 0.42). The method note says so.
- **The siting gaps' file has a state section for this chain,** naming the row built as a table, not yet drawn on the tab.

## Decisions made without you

- **Active queue positions only;** withdrawn and completed ones are left out.
- **Both sources side by side,** since each counts a different kind of plan, rather than one chosen for the node panel.
- **The queue's kinds from its fuel and technology's first word,** battery storage named apart, the rest "other".

## For Samuel's ruling

- None new.

## Files

- New: `warehouse/derived/ercot_node_planned_generation.py`, `docs/methods/ercot_node_planned_generation.md`, `tests/test_session931.py` (3 tests), this report.
- Changed: `docs/reviews/siting-gaps.md` (a state section), `build_coverage.py`, `release_v1.py`, `live_set.yaml`, `docs/coverage.md`, `coverage.csv`, `archive_manifest.csv`, `sources.csv`, `license_tables.csv`, `docs/licenses.md`, `docs/redivis/release-v1/`.
- On the data machine only: `runs/c052/s931/`, `runs/s931*`.
