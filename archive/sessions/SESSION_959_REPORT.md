# Session 959 report: a gap of the siting review (none can close without a ruling)

23 October 2026, from 12:57 UTC, on lab-desktop (the data machine), a session of `queue/done/054-day-23-october-data-federal-royalties-wind-costs-minerals.md`. Model spend USD 0. Pulls: none.

## Read these first

- **Main's latest state read first:** `docs/reviews/siting-gaps.md` to session 945's section (chain 053, the last to change a row) and `docs/reviews/siting-open-2026-10-23.md`'s list; the code machine has moved no row since (its chain 074 was withdrawn).
- **No open row can be closed by a public table without a ruling or a key,** each for its reason:
  - **A 2026 sub-region table** (list item 28): waits on ruling 16 of `siting-rulings-2026-10-23.md` ("the data machine keeps `eia930_subba_demand_hourly_2026`"), not ruled. The data are held (`eia930_subba_demand_hourly`, from 24 July 2026); only the ruling is missing.
  - **Large-load tariffs outside ERCOT** (item 7): `utility_large_load_tariffs`' connector waits on `OPENEI_API_KEY`.
  - **Substations and lines** (item 12): wait on a publisher of record for them, the standing question.
  - **A node's hub and bus** (items 11, 21): ERCOT's settlement point and electrical bus mapping is served only under `/misdownload`, which ERCOT's robots file disallows.
  - **A large load's own wait outside NYISO** (item 8): no public source found.
- **A state section added** to `docs/reviews/siting-gaps.md` saying so; the table's rows are left as written.

## Decisions made without you

- None.

## For Samuel's ruling

- None new; ruling 16 (a 2026 sub-region table) is the one that would let the next siting session close a row with data already held.

## Files

- New: this report.
- Changed: `docs/reviews/siting-gaps.md` (a state section).
