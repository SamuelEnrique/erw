# Session 483 report: node_basis_daily out of the live set

21 October 2026, from 16:25 UTC, on lab-desktop (the data machine), at the owner's instruction of 21 October ("take node_basis_daily out of the live set; Supabase only; keep it in the archive and on Redivis"). Model spend USD 0. Pulls: none.

## Read these first

- **`node_basis_daily` is out of Supabase.**
  - All 957,969 rows over 888 settlement points were deleted from `series` and its header lines from `headers` (16:44:59 to 16:46:50 UTC), through the loader's own API client and service key, one settlement point at a time so that no statement passed the API's 8-second timeout (`runs/s483_drop_node_basis.py`).
  - Afterwards: 0 rows, 0 header lines. `series` holds 2,651,240 live rows (3,606,639 before).
  - The loader's plain `VACUUM (ANALYZE)` then marked the space for reuse. The file stays 2,154 MB: only a `VACUUM FULL` returns it, a person's command that locks the table for minutes (see "For Samuel's ruling").
- **It stays everywhere else**: `warehouse/output` on this machine, the archive, coverage, and Redivis's list (held for storage, as before).
- **`warehouse/supabase/live_set.yaml`** (landed as `745abfd9`, before this machine's daily run of 17:00 UTC):
  - the rule `'^node_basis_(daily|summary)$'` became `'^node_basis_summary$'`, which the pages read;
  - the table moved from `review_hold` to `catalogue_hold`. A public table that is not loaded reads "no" in the catalogue, and `/data` names every such table as a Redivis table. This one is not on Redivis (held for storage), so it is held out of the live catalogue like the other tables no page reads (`test_session410` caught it).
  - Landed first so that today's `dm_live_set`, after `dm_node_rt` adds a day, does not write the table back.
- **Main had two failing tests, both test-only, fixed in the same landing** (without them no landing of the day could pass its checks):
  - `test_session132`'s board floor: from 21 October NYISO's rows are held for their license (74 "licensed" against 33), so 700 rows were "ok" against a floor of more than 700. The floor now counts the rows held on purpose with the "ok" ones (more than 700), and the "ok" rows alone must be more than 600.
  - `test_session402` runs `site/scripts/test-digest-numbers.mjs`, whose check of the Digest's numbers section took any line beginning "- Brent". Today's Digest has a news line "- Brent crude trades at $110.30 per barrel ..." (a headline's own figure). The check now reads only the "## ERW's Numbers Today" section.
- **The main checkout**: the daily run of 20 October's uncommitted page files and tables (114 files) conflicted with GitHub's commit of 21 October (16:19 UTC). They are set aside in a named stash, `s483 2026-10-21T16:26:22Z`, kept and not applied: the run of 17:00 UTC rebuilds every page file from tables that are now current.

## Checks

| What | Exit | Notes |
|---|---|---|
| `scripts/precheck.py` | 0 | |
| the tests that read `live_set.yaml` (52 modules) with 358 and 376 | 1, then 0 | 102 and 410 fixed by the `catalogue_hold` move; 132 failing on main too |
| `load.py --only '^node_basis' --dry-run` (the new rules) | 0 | 1 table: `node_basis_summary`, 1,260 rows |
| the whole suite | 1 | 4,943 tests: only `test_session132` and `test_session402`, both on main too; each fixed and run again (40 tests, 0) |
| `scripts/freeze.py status` | 0 | |
| `task/483-node-basis-live` | merged | checks passed (run 39636166931), `745abfd9`; Vercel rate limited, so no deployment yet |
| the lock, `db_probe.py` (0.46 s), the deletion, `VACUUM (ANALYZE)`, `db_probe.py` (0.46 s) | 0 | 16:44 to 16:47 UTC |

Rule 8: `s483-land-before` (16:35 UTC; the landing's after snapshot was not taken, since Vercel made no deployment) and `s483-drop-before` against `s483-drop-after`: 0 differences on 25 pages, expected (no page reads the table).

## Decisions made without you

1. The deletion one settlement point at a time through the API, not the loader's `--prune` (a whole load) and not a hand-written SQL delete.
2. `catalogue_hold`, not just out of the live set, so `/data` names no table it cannot link.
3. The two tests fixed in the test, not the content: today's Digest and board are correct.
4. The superseded page files stashed, not applied.

## For Samuel's ruling

- `VACUUM FULL` of `series` (about 600 MB back; the table locked for a few minutes): `python warehouse/supabase/load.py --vacuum-full` is a person's command.

## Files

- Changed (landed): `warehouse/supabase/live_set.yaml`, `tests/test_session132.py`, `site/scripts/test-digest-numbers.mjs`. New: this report.
- On this machine (not in git): `runs/s483_*`.
