# Sessions 1972 to 1999: chain 228, the disk, the Daily Digest and the Weekly Roundup (13 November 2026)

Energy Research Warehouse (ERW). Chain 228 (`queue/done/228-day-13-november-oldlaptop-periodicals.md`), sessions 1972 to 1999, samueloldlaptop (code role), unattended, Opus 5.5 high effort. From about 09:15 UTC. One report for the chain, a section per session.

## Session 1972: the next file, the disk, the memory

- **Chain file:** 228 was the first queue number free on origin's main and every branch; sessions 1972 to 1999 named by nothing; committed alone, pushed (`a5fef75e2`), taken by name (`5652d5e66`).
- **Next file:** `queue/next/232-day-14-november-oldlaptop-periodicals-continued.md` (`ed7dc1779`), `machine: samueloldlaptop`. 229 to 231 went to the desktop's windows minutes before. Sessions 3311 to 3326: 2001 to 3310 are taken by reports, commit subjects or queue-file reservations (3000 to 3079, 3300 to 3305, 3400 to 3419).
- **Precheck:** exit 0, on duty until 2026-11-14 01:34 UTC.
- **Disk:** 65 GB free before, 82 GB free after (target 10 GB).
  - Worktrees: 5 before, 4 after. None was of a branch that is an ancestor of `origin/main`; `erw-1425` (`wip/1425-grid`), `erw-1600` (`wip/1642-board`) and `erw-1905` (`wip/1905-revert`) kept, each clean and equal to its origin branch.
  - `erw-land-77e8916a` removed (1.2 GB): the gate's detached worktree at `77e8916a0`, which is `wip/1905-revert`'s head on origin. This machine runs no gate now.
  - `runs/`: 71,011 untracked files older than 7 days deleted (39,044 of them old snapshots), 17 GB to 411 MB; no tracked file touched (`git status` shows no deletion).
  - `npm cache clean --force`: exit 0.
- **Memory:** MemFree about 2.1 GB of 7.3 GB.
- **Row 9** (`wip/1905-revert`, `77e8916a0`, task `1944-revert`, port 3944): **requested, for the desktop**; not an ancestor of `origin/main` at `ed7dc1779`; the desktop's queued chain 230 does not name it.

### Decisions made without you

- `erw-land-77e8916a` removed though its commit is not on main: it is a gate leftover at a commit saved on origin as `wip/1905-revert`.
- The next file's numbers 3311 to 3326, the first free block of fourteen or more above 2001.

## Session 1973: the open rows, the Digest of 12 November read

- **The open rows:** session 1881's rows 59 to 76 are all fixed on main (their branches `wip/1882`, `wip/1894` and `wip/1896-periodicals` landed; the commits are ancestors of `origin/main`). Open before this chain: row 65 only (the why lines' rule, with row 39 for the owner). Rows 19, 20, 23, 40, 47, 49 are `ruling`; 27, 35, 48, 61, 77 the data machine's.
- **The issues:** of the last seven on main (14, 20 to 23 October, 6 and 12 November), only 12 November's was written by the v2 code; the six older ones' faults are rows 1 to 58. No W46 Roundup is stored yet (the week ends 15 November).
- **The harness:** `brief.py --date 2026-11-12 --now 2026-11-12T22:56Z --no-model` with `ERW_BACKEND=supabase` reproduces the stored issue's numbers, block and chart to the digit (`runs/periodicals_dryrun/s1973/`). USD 0.00.
- **Read:** twelve new rows, 79 to 90, in `docs/reviews/periodicals-faults-2026-11-05.md`.
- **Branch:** `wip/1973-periodicals` from `origin/main` at `ed7dc1779`, worktree `C:\Users\lossa\Documents\erw-1973`.

## Sessions 1974 to 1985: rows 79 to 90 fixed

One row a session, each with tests in `tests/test_periodicals_1973.py` (28 tests), on `wip/1973-periodicals`:

- 79: the opening names the single hub's move it passed over ("SPP SPPSOUTH_HUB day-ahead down 39.1%") instead of "No price moved enough to lead".
- 80: the market row is never a 0.0% move; an oil headline that "settles", "jumps" or "rises" names Brent and WTI (12 November: Brent, +2.2%, not Henry Hub unchanged).
- 81: the market row names the close's trading day, not "about a week after"; "1 day".
- 82: "Storage dispatched, USA: 580 MW", not "Storage capacity".
- 83: outlets by name: "JPT", not "JPT Homepage"; "CA.gov".
- 84: no "parties:" line repeating the headline; "Also named:" for the rest; the Roundup's field kept beside a figure.
- 85: the Digest's policy line closes "(... policy action). [DOE](...)" where the why line fails; `site/lib/digest.ts` keeps it.
- 86: the money style on the titles printed as published.
- 87: the scanner's "record until now" is the highest value before the new point (Wyoming: July 2026's 1,034,451 MWh, not July 2024's 765,381); the held record kept beside it and traced; the method note says so.
- 88: the chart's line ties it to a story only when the shared words name the measure; else "No top story of the day names this measure."
- 89: the subject carries the top story's headline with no figure ("ERW Daily | SpaceX plans data center projects in Arizona and Texas").
- 90: the first line in order, with "the first issue since 6 November" after a gap.
- **Tests run:** `test_periodicals_1973`, `test_periodicals`, `test_session176`, `test_session181`, `test_session192`, `test_session267`, `test_session150`, `test_session402`, `test_session470`, `test_session802`, `test_session804`, `test_session805`, `test_session810`, `test_session1882`, `test_session1908`, `test_session2206`: all OK; `site/scripts/test-digest-numbers.mjs` 15 passed. The whole suite not run (this machine's rule).
- **The dry run on the stack** (`runs/periodicals_dryrun/s1973/digest/2026-11-12-stack-nomodel.md`): every fix shows on 12 November's inputs. The chart's caption is the data machine's stored scan, so row 87 shows from its next scan.
- Two existing tests' expectations changed with the rule they pinned: `test_periodicals.py` (row 84: no "parties: Sesterce." under a headline naming Sesterce) and `test_session2206.py` (row 90: the new first line).

### Decisions made without you

- Row 84 keeps "; parties: ..." beside a figure, since `roundup.issue_items` matches a week's story to an earlier Digest item by two parties read there.
- Row 87 keeps the record test's statistics against the held history (the fresh window broke a two-year record) and changes only what "the record until now" names, the margin and the strength. The other choice, to measure the test from the record until now, would have flagged nothing when two record months arrive in one release.
- Row 90 keeps "for the N hours to <time> UTC" first: `STAMP_END` opens the next window from it.

### For Samuel's ruling

- The stored Digest of 12 November says Wyoming's August gas generation broke July 2024's record when July 2026 had already broken it. Default: the issue stays as written (no stored issue rewritten); a one-line correction note on it waits for your word.

## Session 1986: two faults the stack's dry run found (rows 91, 92)

- 91: a mover whose reason links a story printed above was dropped as a repeated item (Brent on the stack, Henry Hub on main's run); mover lines are now figures to the repeat drop and the hard check.
- 92: "the 5 largest moves" then listed Henry Hub "up 0.00 (0.0%)"; the list ranks moves of 0.05% or more, counts them, and names the unchanged ones ("- Unchanged: Henry Hub natural gas, WTI Cushing crude.").

## Session 1987: the Roundups of W45 and W46 read (rows 93 to 99)

- Dry runs on the stack, no model: W45 (now 399 stories: stories of 6 to 8 November were ingested since session 1881's read) and W46 so far (262 stories to 12 November 21:52 UTC). USD 0.00.
- **Row 93, the serious one:** the stored W44 and W45 print NYISO's and ISO-NE's weekly day-ahead means (W45: 40.90 and 40.28 USD/MWh; W44: 47.64 and 40.34) from tables held for license since 21 October. The Roundup's table read the hold only for its five numbers. The Digest was right all along.

## Sessions 1988 to 1994: rows 93 to 99 fixed

- 93: the Roundup prints "licensed source needed" for a held grid and skips its real-time table ("Not read: NYISO (licensed source needed).").
- 94: the `/roundup` page holds a held grid's price cells in a stored issue (`holdRoundupGrids`, `site/lib/digest.ts`), as the Digest's page does.
- 95: the weekly subject carries no outlet figure in any case; a cut does not split a name.
- 96: the deal of the week names the outlet of its sum ("the sum as Hart Energy reported it"; JPT wrote USD 2.1 billion).
- 97: a stand-in move passes the opening's bar and is the next unused one (W46's "+0.3%" of Brent is gone).
- 98: a story naming a benchmark is given the warehouse's close in its limitation, and no party is asked of a market move.
- 99: one colon in the deal opening's status.
- The W46 dry run again on the stack shows each fix (`runs/periodicals_dryrun/s1973/roundup/2026-W46-stack2-nomodel.md`).
- **Tests:** `tests/test_periodicals_1973.py` (41 tests), with `test_periodicals`, `test_session806`, `test_session1882`, `test_session1894`, `test_session1895`, `test_session1907`, `test_session1908`, `test_session135`, `test_session177`: OK; `site/scripts/test-digest-numbers.mjs` 16 passed. Two old expectations changed with their rule: `test_periodicals.py` (the subject's outlet figure, row 95) and `test_session1907.py` (the stand-in by index, row 97).

## Sessions 1995 and 1996: the method notes

- `docs/methods/digest_scoring.md` and `docs/methods/roundup_selection.md`, internal (added to `INTERNAL_METHODS` in `site/scripts/build-content.mjs`, so the site does not publish them), each with what changed on 13 November.
- `docs/methods/periodicals.md` (the readers' note): a section "Changed on 13 November 2026".

### Decisions made without you

- Row 93's page fix holds the cells at render time; the stored W44 and W45 markdown are not rewritten.
- Row 97: the stand-in is the next unused move at the bar, not the k-th by index, so an unused 3.6% move no longer gives way to a 2.7% one.
- The method notes are internal, as the chain asked; the readers' note gets only what a reader sees.

### For Samuel's ruling

- **W44 and W45 printed held prices (row 93).** NYISO's and ISO-NE's weekly means went into the stored markdown and, if the Sunday emails were sent to `DIGEST_RECIPIENTS`, into those emails. Default: nothing re-sent and the stored files left as written; the page now holds the cells. Whether the publishers need to be told is yours.
