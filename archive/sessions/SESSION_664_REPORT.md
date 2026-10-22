# Session 664 report: version 1, prepared for the click

22 October 2026, from about 09:52 UTC, on lab-desktop (the data machine), a session of `queue/done/043-night-23-october-data-redivis-gaps.md`. Model spend USD 0.

## Read these first

- **The Stanford draft is ready for the owner's click; nothing was released.** The release note, with what the draft holds against v1.0 and the five things to look at: [`docs/reviews/redivis-v1-release-note-2026-10-23.md`](../../docs/reviews/redivis-v1-release-note-2026-10-23.md).
- **The reconcile:** 188 of 188 match their CSVs (the 186 public tables, `erw_coverage`, `erw_sources`), 45,817,197 rows; the one draft table with no CSV here is v1.0's starter.
- **The package for the dataset's page** is `docs/redivis/release-v1-stanford/` (README, `tables.csv` with each table's citation naming `datapages.erw`, `variables.csv` with 4,646 rows), built by `release_v1.py --target stanford` from the uploader's own gate and manifest: 189 tables in v1 with the metadata tables, 4 held (this chain's new tables, until session 680). `--check`: 0 differences. The older package, `docs/redivis/release-v1/`, is unchanged.
- **The first thing to decide:** Redivis will number the release after v1.0, so the ERW's "version 1" will carry Redivis's second label; the citations should say both.

## Pulls against their ceilings

| Host | Requests | What |
|---|---|---|
| Redivis API | 5 of 50 | the reconcile |

## Decisions made without you

- `release_v1.py` gained a Stanford mode (`--target stanford`) writing to its own folder, so the old dataset's package and its tests stay as they are.
- The note compares the draft with the old account's draft as well as with v1.0, since v1.0 holds only the starter.

## For Samuel's ruling

- The click, with the five items of the release note: the version's label, the starter table, the tables that stopped on this machine before 15 October, the four that grew, and the licenses as released.

## Files

- New: `docs/reviews/redivis-v1-release-note-2026-10-23.md`, `docs/redivis/release-v1-stanford/` (three files), this report. Changed (committed with session 667): `warehouse/redivis/release_v1.py`, `tests/test_session664.py`.
