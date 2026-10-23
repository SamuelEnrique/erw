# Session 1000 report: the next file, then the specification

23 October 2026, from 02:14 UTC, on samueloldlaptop, unattended, in the worktree `C:\Users\lossa\Documents\erw-1000` on `wip/1000-packages` (cut from origin/main, with `wip/977-records` merged: chain 065's last landing record rides here). Chain `queue/done/070-evening-22-october-code-packages.md`, session 1000, the first. Model spend USD 0. No warehouse data written. Requests: Redivis 1 (of 50), the live set 0.

## Read these first

- **The next file was written first and is on main**: `queue/next/071-night-23-october-code-allgrids-packages.md`.
  - 22 sessions, numbered 1020 to 1041, `machine: samueloldlaptop`.
  - It was committed alone (`b71ce446`) and pushed to main at 02:15 UTC, with snapshots (`s071q-before`, `s071q-after`: 0 differences).
  - Its content: the All grids tab's rulings and tables as they come (the data machine's chains 045 to 047 queue three of the tab's awaited tables), its three paths walked again, and the packages' second pass.
  - Session 1019 updates it.
- **`docs/methods/packages.md`, version 0: the one specification the three packages follow.**
  - The six calls: `tables()`, `coverage(table)`, `fetch(table, entity=, variable=, start=, end=, backend=)`, `cite(table)`, `license(table)`, `standard(table)`.
  - The three backends and `auto`, which takes local, then the live set within its last 30 days, then Redivis's latest release.
  - The citation's exact words (`release_v1.py`'s), the column types by shape in Python, Stata and R, the version line, and what a held table does.
- **The Python package read against it**: a gaps table, call by call, for session 1001. The largest gaps:
  - no `tables()`, `license()` or `standard()`;
  - no `backend=` per call;
  - a held table answers "not found" on Redivis and the live set;
  - Redivis defaults to the owner's old dataset and its draft, which a public reader cannot read or cite;
  - `cite` lacks the release's words.
- **One Redivis read**: the Stanford dataset's current version is `v1.0`, released (the starter table). The ERW's "version 1" will be Redivis's next tag, as the release note's item 1 already says, so the specification cites what Redivis shows (decision 4).

## What to review

1. `docs/methods/packages.md` on GitHub (the branch, then main once it lands), or on the site after the landing: open `https://erw-flame.vercel.app/internal/open`, enter the token, then `https://erw-flame.vercel.app/data/methods/packages`.
2. Read "The six calls" and "What a held table does": these are the two places where a choice was made for you (decisions 2 and 3).

## Checks

| Check | Exit | Result |
|---|---|---|
| precheck | 0 | |
| the next file: `chain_queue.py list` after its commit | 0 | 071 listed for samueloldlaptop |
| snapshots around the next file's push | 0 | 0 differences |
| `tests.test_session1000` | 0 | 5 tests OK |

## The landing

With 1001, in session 1001: a document alone would spend a deployment, and Vercel has been rate limiting this account's deployments since 01:25 UTC.

## Decisions made without you

1. **Six calls, the same names in all three** (R with an `erw_` prefix, Stata as subcommands); Python keeps its older calls.
2. **A held table is refused on Redivis and the live set, and warned from local files**: the ERW's own code reads internal tables through the package from local files.
3. **`auto` routes local, then the live set (window within its last 30 days), then Redivis's latest release.**
4. **The citation follows Redivis's tag** (`v1.0`, `v2.0`) until you settle the release's number.
5. **1000 lands with 1001**, to spare a deployment.

## For Samuel's ruling

- The release's number: "version 1" in the ERW's documents against Redivis's next tag (the release note's item 1, already listed; the packages cite Redivis's tag meanwhile).

## Files

- New: `docs/methods/packages.md`, `tests/test_session1000.py`, this report; on main, `queue/next/071-night-23-october-code-allgrids-packages.md`.
- Carried: chain 065's landing record (`wip/977-records`: `SESSION_970_REPORT.md` to `SESSION_977_REPORT.md`).
