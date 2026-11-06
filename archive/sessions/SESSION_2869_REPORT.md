# Session 2869 report: this machine's own branches

6 November 2026, about 00:33 to 01:45 UTC, on lab-desktop (the data machine), chain 147, unattended. Model spend USD 0. Pulls: none but the snapshots and GitHub reads.

## Read these first

- **Each branch's report was read first** (`archive/sessions/SESSION_455_REPORT.md`, `_477_`, `_478_`, `_479_`). Each was "for Samuel's ruling, not landed", and the owner's ruling of 5 November lands them. None moves a page's default figure or changes what a visitor sees:
  - **455:** the loader writes a row only when its values move, so a moved stamp alone writes nothing. An older copy equal in value is no rollback. `series` is vacuumed only after a large write.
  - **477** (stacked on 455): the loader asks the database gate before its first write (closed: a skip, exit 75), and pauses 10 s after a large table.
  - **478:** a held board row two or more days behind its group carries a `held` mark. Its status stays "ok", so the board shows it as before. The site does not yet read the mark.
  - **479:** a job with fewer than half its expected runs is "short" in the day's record. It ends the streak only when `SHORT_ENDS_STREAK` is set, and it is off.
  - Every page is in review, so a visitor sees none of this.
- **Landed together** as one branch, `wip/2869-combined` (477, which holds 455, then 478 and 479, each merged with main). That took one gate instead of four.
  - **The first gate failed in the suite on `test_session45`:** it read the loader's `vacuum(url, full=args.vacuum_full)`, which session 455 made `vacuum(url, full=args.vacuum_full, changed=changed)`. The test was updated.
  - **The second gate:** suite OK; check-values had 12 failures, all known, 0 new.
  - The health tests (114, with 2864's) and the loader tests pass.
- **Landed as `bab0b4ecb`** (task/2869-combined, run 42144016506, checks passed 01:43 UTC; deployed 01:45). Snapshots `s2869-before` (01:27) and `s2869-after` (01:45): 25 pages, **0 differences**. The code machine's `task/1434-periodicals` landed between the two (`57967174`), and also changed nothing a visitor sees.
- **What `/internal/health` will show:** the record of days (`site/data/health_days.json`) gains `short` for a job under half its runs; the streak is unchanged while `SHORT_ENDS_STREAK` is off. The board gains `held` marks in `site/data/board.json` on its next build; nothing is drawn from them until the code machine's page reads them.

## Decisions made without you

- **The four branches landed as one.**
- **`SHORT_ENDS_STREAK` left off** (479's ruling item: 0.5 as the chain asked, or 0.9).

## For Samuel's ruling

- **479's line:** half or 90 percent of the expected runs.
- **478's mark on the board's tiles:** the code machine's page change.

## Files

- New: this report.
- On the data machine only: `runs/c147/land_2869*.out`, the snapshots.
