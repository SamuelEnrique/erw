# Session 375 report: the release v1 package, spliced; node_basis_daily held for Redivis's storage

20 October 2026, from 20:40 UTC, unattended, on lab-desktop (the data machine), the third session of the chain of 20 October, day. Model spend USD 0. Pulls: none; no request to Redivis (not even its metadata: nothing in this session needed it).

## Read these first

- **v1 is 136 tables and the three metadata tables; 41 held for a license; `node_basis_daily` "held: Redivis storage"** (`in_v1 = held`, not dropped: in v1 by its license, uploaded once the storage is settled). `release_v1.py --check`: 0 differences. `tests.test_session275` passes (with the whole suite, 4,700 tests, exit 0).
- **The package was spliced, not rewritten.** `release_v1.py`'s own `build()` read every table on this machine (none missing). A whole rewrite from here would have replaced the description of **63 tables** with the restore's note: since session 373 a restored table's first header line is "Rebuilt from the ERW archive by warehouse/restore_tables.py (session 305), as of run ...", and `build()` takes the first line as the description. So only four rows were taken from it: `node_basis_daily` (held, 957,969 rows to 20 October), and the publishers of `node_basis_summary` and `ercot_4cp_intervals` (ERCOT) and `price_years_by_window` (CAISO; EIA; ERCOT; NOAA NCEI; SPP), from session 378's record. Every other row, and `variables.csv` (4,496 rows), is as it was. The README was written again by `readme()`. Step 1 of `docs/redivis/release-v1.md` and the runbook now say this.
- **The chain's six tables:** `nlr_jedi_multipliers` and `impact_tax_rules` were already in v1 (session 366's splice); `price_years_by_window`, `node_basis_summary` and `ercot_4cp_intervals` were already in v1 and now name their publishers; **`iso_queue_statistics` is not in the package**: it is on the code machine's `wip/348-map`, not on main, and coverage has no row for it. It goes in with that branch.
- **One flag the coverage rebuild would have changed, kept as main has it:** `nyiso_load_queue`. Session 373's `--only` rebuild computed `internal` (the builder's rule: internal when any source is internal, and `nyiso:load_queue` has been internal in `sources.csv` since the owner's ruling of 7 October, session 149); main's row says `public`, from before that ruling. Taking `internal` takes the table out of the release's plan and fails `test_session207` (41 license-needed tables, now 40) and `test_session275`; the license status file and the site's `site/data/license_status.json` would follow. **The row was put back to `public` in both checkouts**, so neither this landing nor tomorrow's daily commit changes it. Either way the table is not in v1 (held for a license, or internal). See "For Samuel's ruling".

## The runbook's section

"The draft on 20 October 2026 (sessions 363 and 375)" now gives the sync check after session 373 (201 current, from 156), the storage hold and the step that keeps it (session 376's `dm_node_rt`, Redivis left out), session 377's skip for a refusal for storage, the tables new since session 312 with the two of session 366 and the one still on `wip/348-map`, and the splice. Its first row expects "139 tables in v1 (with the three metadata tables), 42 public tables held out" (41 for a license and one for storage), and warns about a whole rewrite after a restore.

## Checks

| What | Exit | Notes |
|---|---|---|
| `runs/s375_splice.py diff` | 0 | what `build()` would change: 96 lines, 63 of them a description becoming the restore's note |
| `runs/s375_splice.py write` (four tables) | 0 | 181 rows: 139 in v1 with the metadata, 1 held, 41 out |
| `warehouse/redivis/release_v1.py --check` | 0 | 0 differences |
| `scripts/licenses.py write`, `check` | 0, 0 | 211 tables, 0 problems |
| `tests.test_session275`, `205`, `207`, `376`, `377`, `378` | 0 | the first run, with `nyiso_load_queue` internal, failed three tests (above) |
| the whole suite (`GITHUB_ACTIONS=true python -m unittest discover -s tests`, in the worktree) | 0 | 4,700 tests, 278 skipped, 281 s |

## Decisions made without you

1. **A splice of four rows**, for the reason above; the chain's rule ("splice the release package; do not rewrite it from here").
2. **`nyiso_load_queue` kept public in coverage**, against the builder's computation, until a person rules: the change it would bring touches the license record, a site file and two tests' counts, more than a release session should decide.

## For Samuel's ruling

- `nyiso_load_queue`: coverage says public, `sources.csv` (your ruling of 7 October) says internal. Ruling internal: coverage's row, `license_status.csv` and `site/data/license_status.json` lose it (40 license-needed tables), `test_session207` and `test_session275` follow. Any machine's next `--only` rebuild of the table computes internal again.
- `restore_tables.py` writes its note as a restored table's first header line, which `release_v1.py` and the uploader both read as the table's description. Put the note last instead?

## Files

- Changed: `docs/redivis/release-v1/tables.csv`, `docs/redivis/release-v1/README.md`, `docs/redivis/release-v1.md`, `docs/redivis/release-v1-runbook.md`, `docs/licenses.md` (commit `9115b289`); this report.
- On this machine (not in git): `runs/s375_splice.py`, `runs/s375_diff.out`.
