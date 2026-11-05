# Session 660 report: Redivis, read and planned

22 October 2026, from 08:44 UTC, on lab-desktop (the data machine), the first session of `queue/done/043-night-23-october-data-redivis-gaps.md`. Model spend USD 0.

## Read these first

- **The token on this machine can write the Stanford dataset.** The owner's `erw:b9wm` is `datapages.erw:b9wm`, the Datapages organization's dataset on `stanford.redivis.com` (DOI `10.57761/4f55-6d55`), and Redivis answers `accessLevel: edit` for the token of the user `samuelca`. So the Redivis sessions go ahead; no token step is needed from the owner.
- **That dataset already has a released v1.0, with one table**, `eia930_iso_hourly_demand_2019_2025` (429,525 rows): session 59's starter. It has no draft. The ERW's first full release there will be its second Redivis version.
- **186 tables are public by the ERW verdict**, 13.25 GB of CSV, about 12.4 GB on Redivis (the old draft stored its 128 of them at 0.935 of their CSV size). 104 are excluded: 54 internal, 50 unsettled. FRED's tables were retired on 13 October, so none is in the list.
- **The organization's storage limit cannot be read from the API** (`/organizations/datapages` is not an endpoint). A refusal will show it; the batches put the largest tables last.
- **The plan:** [`docs/reviews/redivis-v1-plan-2026-10-23.md`](../../docs/reviews/redivis-v1-plan-2026-10-23.md), one row a table, with the three batches (661: the 93 smallest, 0.19 GB; 662: the next 81, 5.89 GB; 663: the 12 largest, 7.17 GB, then the metadata tables).
- **Nothing was uploaded, created or released.** `upload.py --reconcile` was not run as written, because it would open a draft on the Stanford dataset (a write); the read-only equivalent is in the plan.

## Pulls against their ceilings

| Host | Requests | What |
|---|---|---|
| Redivis API | 13 of 30 | `/users/me` (2, one lost to Git Bash's path rewriting), the Stanford dataset by four references (4, two of them misses), the old dataset (2), the Stanford table list (1), the organization (1, not an endpoint), the old draft's table list (2), one rerun of the user (1) |

## Decisions made without you

- The uploader reaches the Stanford dataset as a second target (`--target stanford`, its own manifest, an ERW-verdict gate), and the daily run's default stays on the old account's draft. Session 661 makes it.
- The starter table in `datapages.erw` v1.0 is left as it is.
- Chain 041's sessions 641 to 644 were not run (that chain stopped after session 640 at 07:12 UTC; its work waits on `wip/638-644-sources`, untouched). The owner's file 043 was taken in its place.

## For Samuel's ruling

- Whether the daily run's upload, its `--check-license` and the restore move to the Stanford dataset, and when (the plan's three reasons).
- Whether the starter table `eia930_iso_hourly_demand_2019_2025` stays in the next Stanford version.
- Datapages' storage limit, if Redivis's organization settings show it (the draft needs about 12.4 GB).

## Files

- New: `docs/reviews/redivis-v1-plan-2026-10-23.md`, this report. On the data machine only: `runs/s660/` (the probe, the plan and its CSVs).
