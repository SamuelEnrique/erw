# Session 187 report: the raw files handed to the data machine

10 to 11 October 2026, 06:55 to about 07:50 UTC (23:55 to 00:50 Pacific), unattended, on the old laptop (`samueloldlaptop`, role `code`). Branch `wip/187-raw-handover`, pushed, not deployed. Model spend USD 0, no model call. No pull: no request to any publisher. No data lock taken.

## Read these first

- **All of `warehouse/raw` is in the archive bucket**: 33,630 files, 25,988,648,080 bytes (25.99 GB), 56 folders, as 857 objects of at most 42 MB, 22,069,096,527 bytes stored. Private bucket `erw-archive`, prefix `_handover/187/`. `ercot_zone_prices` went first, `zone_price_history` second, then the smallest folder first. 0 parts failed.
- **`runs/session187/handover.json` is the index** (in git on the branch, 352 kB): every object with its bytes and SHA-256, per folder. The manifest of every file's name, bytes, SHA-256 and time is one object in the bucket, named in it (`_handover/187/manifest/raw_files_20261011T073906Z.csv.gzip`, 33,630 rows).
- **Nothing was uploaded for `iso_zone_prices_history`, because nothing is missing.** All four runs in this laptop's archive are already in the bucket, the same line for line. Session 184's report is not on this laptop and not on GitHub, so I could not read which two days it names. Detail below; it needs your eye.
- **Nothing here was deleted, moved or changed.** After the upload every local raw file was hashed again against the manifest: 33,630 of 33,630 the same, 0 missing, 0 different.
- **On lab-desktop, three commands** (below): check out the branch, `fetch`, `verify`. The fetch never overwrites a file already there with other bytes.

## On lab-desktop

1. `git fetch origin` then `git checkout wip/187-raw-handover` (or `main` once session 188 has landed: the script goes to main with it).
2. `python scripts/raw_handover.py fetch --folders ercot_zone_prices` (6 objects, 234 MB; a first try).
3. `python scripts/raw_handover.py fetch` (everything: 857 objects, 22.07 GB down; it resumes where it stopped).
4. `python scripts/raw_handover.py verify` (every file against the manifest; exit 0 when none is missing or different).
- Needs only `.env` (`SUPABASE_URL`, `SUPABASE_SERVICE_KEY`) and the venv. No data lock.
- A file already on lab-desktop with other bytes is kept, and listed in `runs/session187/fetch_conflicts.csv`.
- For the archive: `python warehouse/archive/archive.py pull`, then `python warehouse/archive/restore.py iso_zone_prices_history --from-bucket` (1,664,445 rows expected).

## iso_zone_prices_history: what I found

- Asked: upload the two days that session 184's report says exist only in this laptop's archive.
- `archive/sessions/` holds no `SESSION_184_REPORT.md` on `main` or on any branch (fetched 11 October), and `runs/` has no `session184` folder. Reports 184 and 185 are missing from GitHub.
- This laptop's month file `warehouse/archive/iso_zone_prices_history/2026-10.csv` holds four runs. The bucket holds the same four objects. I downloaded each and compared it with the local run by key, operation, value and timestamp: all four the same (1,598,612; 5,592; 58,919; 5,564 lines).
- The newest run, `20261009T075050Z-local`, holds the newest days (1 to 10 October 2026). Its object was written to the bucket on 9 October at 07:58 UTC.
- The table on this laptop has the data SHA-256 the archive manifest records (`6b0ef0cc...`, 1,664,445 rows): it holds nothing the archive lacks.
- Every table: of this laptop's 135 month files, 0 runs are absent from the bucket. 268 runs in the bucket are not on this laptop (the other direction).
- So either the two days reached the bucket after session 184 wrote its line, or they are of another table. **If lab-desktop still lacks a day after `pull` and `restore`, name the table and the day.**

## What was built

- `scripts/raw_handover.py`: `plan`, `upload`, `handover`, `fetch`, `verify`. Standard library plus `requests`.
  - A part is a tar of whole files (gzip when they compress) or a slice of one file larger than 40 MiB. 330 tar parts, 527 slices.
  - Every object is written once (`x-upsert: false`). An interrupted upload resumes; an object already there with the same bytes is taken as uploaded.
- `tests/test_session187_raw_handover.py`: 7 tests (round trip byte for byte, slices, resume, never replace, never overwrite on the receiving side, a damaged part writes nothing, a path that leaves the folder is refused).
- `docs/machines.md`: one paragraph and one line in "Cloud copies".

## Decisions made without you

- **A prefix of `erw-archive`, not a new bucket.** You named the archive store. The Thesis Builder's store chose a bucket of its own because the archive's scripts list everything. I checked those scripts: `pull` and `status` walk the top level, `restore --all` skips names beginning with an underscore, and all read only `.csv.gz` objects at the third level. The handover has none there. One visible effect: `archive.py status` counts 2 more "run parts". Reversible: delete the prefix.
- **Left out: `madeup_as_prices`** (31 files, written by `tests/test_session85.py` with made-up documents) **and one `__pycache__`** (3 files). Rule 1: real data only.
- **Included: MISO's raw files** (`miso_as_prices`, 515 MB) **and Virginia's** (in the `large_load_*` folders). Both publishers are paused. No request was sent to either: these are files already held, copied to the project's own private bucket. They cannot be pulled again while the pause stands. Reversible: delete those objects.
- **No archive write.** `archive.py sync` takes the data lock, and this machine takes none. Nothing needed it.
- **The per-file manifest is in the bucket, not in git** (1.9 MB). `handover.json` in git names it with its SHA-256.
- **The script reaches `main` with session 188's landing**, as a report does. This session pushed only `wip/187-raw-handover`.
- **The handover is a copy for a move, not a backup.** It adds 22 GB to the bucket (docs/machines.md records 100 GB included in the plan; 0.5 GB was used on 2 October). Delete the prefix once lab-desktop has verified. The download of 22 GB counts against the plan's egress, which I did not check.
- `warehouse/output/raw/` (untracked, 46 kB, the same made-up test folder) was left as it is.

## Checks run

| Check | Result |
|---|---|
| `pytest tests/test_session187_raw_handover.py` | exit 0, 7 passed |
| Upload, first folder (`upload_1.out`) | exit 0, 6 parts, 234 MB |
| Upload, the rest (`upload_2.out`) | exit 0, 851 parts, 21,835 MB in 33.9 minutes (about 86 Mbit/s), 0 failed |
| Every object against the bucket's listing (`check_bucket.py`) | exit 0: 857 of 857 present with the recorded bytes |
| Round trip from the bucket, `ercot_zone_prices` (58 files) | fetch exit 0, verify exit 0, `diff -r` identical |
| Round trip from the bucket, `texas_transmission_matrix` (219 files, one sliced file) | fetch exit 0, `diff -r` exit 0 |
| Every local raw file against the manifest (`verify_local.out`) | exit 0: 33,630 the same, 0 missing, 0 different |
| Em dashes in the files written | 0 |

Outputs are in `runs/session187/` on this laptop (not in git, except `handover.json`).

## Pulls and spend

- Pulls: none. Requests went only to the project's own Supabase storage.
- Model spend: USD 0. No model call.

## To finish

- Nothing is held. On lab-desktop: the commands above.
- After lab-desktop's `verify` exits 0: decide whether to delete `_handover/187/` from the bucket.
