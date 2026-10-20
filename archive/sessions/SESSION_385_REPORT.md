# Session 385 report: the warehouse as a citable record, prepared to Ben's click

20 October 2026, from 21:38 UTC, unattended, on lab-desktop (the data machine), the second session of the chain of 20 to 21 October, night (`queue/done/013-night-20-october-data.md`), run while session 384 waits for the scheduled runs of 21 October (its part b). Model spend USD 0. Pulls: Redivis's API, 5 metadata requests of the ceiling of 20 (no upload, no export, no draft opened or created); `docs.redivis.com`, 3 of 4 (its robots file, its sitemap and its pages' sitemap).

## Read these first

- **`docs/redivis/organization-move.md`**: where the two datasets are (owner, references, drafts, sizes), the Redivis pages to read before the clicks, the ERW's changes after the move as a diff not applied (`config.yaml`'s `owner_kind`, `REDIVIS_OWNER` in three places, the token, the address only if it changes), the order against release v1, and the storage set out with what each choice frees.
- **Redivis's steps for the move are not written there, and not from memory.** `docs.redivis.com`'s robots file allows every page (with `Content-Signal: ai-input=yes`), but the host has no terms page and Redivis's terms are not in the ERW's record; the chain's rule puts a new host's terms first, so the pages that describe the move were named from the sitemap and not read. Five questions to read them for are in the document, in the order their answers matter (whether a dataset can be given to an organization or must be copied; whether `05yh` and the address stay; whether the drafts move; whose storage it counts against; whether the private one stays private).
- **The refusals for storage remove tables from the draft.** `ercot_all_hub_prices_history`, uploaded on 15 October, is no longer in the public draft: Redivis answers 404 for it. The uploader deletes a draft table before it uploads the new copy (Redivis uploads append, so that is its only true replace) and deletes the empty new table when the upload fails; the daily's upload at 17:32 UTC on 20 October was refused for storage. **Release v1 marks it "held: Redivis storage"** beside `node_basis_daily` (`STORAGE_HELD`, spliced: one row): **135 tables in v1, 41 held for a license, 2 for storage**; `release_v1.py --check` 0 differences. It is the only table of the upload record (268 rows) missing from the drafts.
- **The storage by Redivis's own sizes**: 9.31 GB in the two drafts (public 184 tables, 8.22 GB; internal 39, 1.09 GB). The ten largest hold 5.21 GB. The 41 tables v1 holds for a license take 0.94 GB of the public draft: removing them, which the release's step 4 does anyway, makes room for the two held tables. No table was dropped.

## Pulls against their ceilings

| Host | Requests | Ceiling | What |
|---|---|---|---|
| redivis.com (API) | 5 | 20 | the two drafts' table lists (3: the public one in two pages), `ercot_all_hub_prices_history` and `node_basis_daily` by name (2, both 404) |
| docs.redivis.com | 3 | 4 | `robots.txt`, `sitemap.xml`, `sitemap-pages.xml` (181 pages); the fourth not spent, since the move's page would be read before the terms |

## Checks

| What | Exit | Notes |
|---|---|---|
| `runs/s375_splice.py write ercot_all_hub_prices_history` | 0 | 181 rows: 138 in v1 with the metadata, 2 held, 41 out |
| `warehouse/redivis/release_v1.py --check` | 0 | 0 differences |
| `tests.test_session275`, `test_redivis_gates`, `376`, `384` | 0 | 45 tests |

## Decisions made without you

1. **`ercot_all_hub_prices_history` held for storage**, not left as "yes": the click would otherwise release a v1 whose list names a table the draft lacks.
2. **Table sizes from `list_tables()`**, three requests, not one request a table (over 200); the two tables `list_tables()` did not show were then asked for by name (the uploader's own rule: never take absence from a list alone).
3. **Redivis's move pages not read** with its terms unread; the fourth request not spent on a guessed address.
4. **The draft read as `version="next"`, not through `open_draft()`**, which creates a draft when none is open.

## For Samuel's ruling

- The storage: the four choices in the document (the 41 license-held tables out of the draft now; the private dataset elsewhere; a paid tier; the organization's storage after the move).
- The uploader's replace: upload the new copy under a temporary name and swap only once it is whole, so a refusal can no longer remove a table from the draft. Not made: it changes the daily's Redivis step and cannot be proven without an upload.
- The order of the move and the click (the document's section).

## Files

- New: `docs/redivis/organization-move.md`, this report.
- Changed: `warehouse/redivis/release_v1.py` (`STORAGE_HELD`), `docs/redivis/release-v1/tables.csv`, `README.md`, `docs/redivis/release-v1.md`, `docs/redivis/release-v1-runbook.md` (commit `2b3a7f88`).
- On this machine (not in git): `runs/s385_sizes.py`, `runs/s385_sizes.csv`, `runs/s385_sizes.out`.
