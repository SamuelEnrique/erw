# Session 258 report: a finding's source line names only the tables whose rows it uses

13 October 2026, 18:09 to 18:55 UTC, unattended, on the old laptop (a code machine), one session of the chain of sessions 257 to 260. Branch `wip/258-source-lines` in the worktree `erw-143`. Model spend USD 0: no model call. Pulls: none. Writes: none to the warehouse, to Supabase, to the archive or to Redivis. Nothing under `site/` changed.

## Read these first

- **NOT LANDED. It is on `wip/258-source-lines`, checked on three modules only, and waits for one word from you** (under "The landing"). Two things met at 18:47 UTC. The data machine landed session 251 three minutes after this session's push, with its own change to the same builder (`hunt.py`), so GitHub could not merge the pushed commit. And Claude Code stopped this chain's two background jobs for low memory, with the note not to start them again unattended: the whole suite on a clean copy, which every landing here rests on, is one of the heavy runs it means, and I did not run it again.
- **Session 251 and this session solved the same fault two ways, and the merge keeps both.** Session 251's engine names a finding's own tables by grid from a list (`hunt.OWN_TABLES`) and gives its 13 new measures their own region's tables. This session decides from the rows the finding read. Merged: where the reads are known (every real hunt), the rows decide; where they are not, session 251's list does; a measure's draft keeps session 251's words. The two disagree on one thing you should know: for an ERCOT draft session 251's list names `ercot_all_hub_prices_history` and `iso_rtm_hub_prices`; this session names the first alone, because the second brings ERCOT's rows only to the year under way (it is said in the CSV instead). Ruling 5.
- **The review list holds 28 drafts now, not 16** (session 251 raised 12 at 18:18 UTC, all measures). The command under "To finish" rewrites the eight older ones and leaves the twelve as they are (a test holds it).
- **The fault is fixed in the builder, and the eight drafts on the review list still carry the old line until the data machine runs one command** (under "To finish"). A code machine writes no data, and the site prints the stored line as it is: it cannot be put right on the page from the stored fields without guessing which table brought which grid's rows.
- **The rule is now decided from what the finding read, not from a list.** The hunt records every read of its finding (`findings_common.record_reads`: the rows kept and, for a table of prices by market, the timestamps kept for each market and node), and `hunt.tables_used` names a table only when it brought rows of the draft's grid in the claim's years that no earlier read had brought.
- **On this machine's real tables (read only), the whole hunt as a dry run raises the same eight drafts as the review list holds, by id, and each now names one table: `ercot_all_hub_prices_history`.** No draft names `iso_rtm_hub_prices`, `iso_hub_prices_history` or `iso_zone_prices_history` in its card, its caption or its pictures. ERCOT's history holds HB_NORTH to 2026-08-26 04:45 UTC and the live table's ERCOT rows begin at 05:00 that day: the live table brings rows to 2026 only, the year under way, which is in the CSV (`full_year` 0) and not in the claim.
- **A true source is not dropped: the CSV says it apart.** Its fourth line reads `# Sources: ercot_all_hub_prices_history; the rows with full_year 0 also read ERCOT's rows of iso_rtm_hub_prices`. If the history ever ends inside a claim year, the live table is named in the card too (a test holds this).
- **Cards kept as files in git: 11 full cards (`site/data/findings/`), 0 corrected, because none names a table without rows in it.** Checked by reading each finding's code, not by a run on tables. The one card of ERCOT alone, `batteries_lunch`, names `iso_rtm_hub_prices` truly: its months run to 2026-10-08, past the history's end, and those are ERCOT's rows of that table. No hunt draft is kept as a file in git.
- **Found and not fixed: the chart-of-the-week cards (`docs/analysis/`, another builder) name the right table and the wrong publishers.** An ERCOT chart from `iso_rtm_hub_prices` says "Source: CAISO, ERCOT, MISO, SPP via the Energy Research Warehouse (ERW), table iso_rtm_hub_prices". 104 stored lines of 5 forms name four grids' publishers for a table; the ones I read are charts of one grid. It is ruling 1 below.

## What changed

- `warehouse/analysis/findings/findings_common.py`: `record_reads`, the note `read_table` takes while it is open (nothing a finding computes changes: a test compares the rows with and without it), and `only_tables_read` for a full card.
- `warehouse/analysis/findings/hunt.py`: `tables_used`, `source_line_of`, `sources_comment`; `run_pattern` records the reads and hands each region's tables on; `build_draft` uses them (without them it keeps session 233's rule, by name); the gas pattern says the one table its measure needs beside prices (`measure_tables`: Henry Hub's); `rewrite_draft` and `fix_source_lines`, with the flag `--fix-source-lines`.
- `warehouse/analysis/findings/run_finding.py`: a full card leaves out a table its finding asked for and kept no row of. A table that brought rows always stays; a table read by another reader is left as it is.
- `docs/methods/automated_analysis_findings.md`: one bullet under "The weekly hunt".
- `tests/test_session258.py`: 22 tests.

## The line, before and after (the eight drafts, from the dry run on this machine)

- Before, evening and midday: `Source: ERCOT's rows of the ERW tables ercot_all_hub_prices_history, iso_rtm_hub_prices, iso_hub_prices_history, iso_zone_prices_history, eia860m_operating_generators, eia860m_retired_generators_all; computed by the finding peak_hour_grids (warehouse/analysis/findings/).`
- After, all eight: `Source: ERCOT's rows of the ERW table ercot_all_hub_prices_history; computed by the finding <its module> (warehouse/analysis/findings/). Found by the weekly hunt.`
- The eight ids of the dry run equal the eight of `docs/reviews/findings-verified-2026-10-13.md`: `346d3337bb15`, `4bee49d6e8c5`, `8c67230bc8b7`, `9868ad33205b`, `bbb2fe2a3844`, `e5fe5b80e074`, `f5c8f78e8cf0`, `f732d699c6b7`. An id is made of the pattern, the region, the last year and the change to three decimals: the claims are the same.
- Tables no longer named that are not "license needed": the battery fleet, ERCOT's load, EIA's daily demand and Henry Hub for the spike drafts, the two EIA-860M tables for the peak-hour drafts. The finding's module reads them for other columns of its full card; a draft's measure is made of prices alone. Decision 2.

## The diff: only the source line moves

- The eight drafts were built twice from the same yearly series (each new draft's CSV, where a number is written whole): by the builder of the commit before this session, given every table of the finding's module as the old hunt gave it, and by the new one. Eight ids equal.
- 56 files (seven a draft). 16 are byte for byte equal: the eight do-files and the eight Python mirrors.
- The eight cards differ in four keys and no other: `source_line`, `tables`, `hunt.caption` (which carries the line) and `computed_at` (the clock). No key under `numbers`, `chart`, `callouts`, `subtitle`, `footnote` or `scanner` differs.
- The eight CSVs differ in line 2 (the clock) and line 4 (`# Sources:`); no data row differs. The eight captions differ in line 9, the source line.
- The 16 pictures differ, as they must: the line is burned into the bottom of each. Their chart is drawn from the card's `chart`, which is equal. I did not compare them pixel by pixel.
- The old builder's lines name the tables session 252 counted: three shared tables in four drafts, two in two, one in two.

## What to review

- Nothing on the site changed. https://erw-flame.vercel.app/internal/findings (after https://erw-flame.vercel.app/internal/open) shows the eight drafts with their old line until "To finish" is done; afterwards each draft's line, caption, CSV and two pictures carry the new one.
- The rule, in the method: https://github.com/SamuelEnrique/erw/blob/main/docs/methods/automated_analysis_findings.md (the bullet "A draft's source line names only the tables whose rows it uses").
- On this machine, not in git: `runs/session258/` (`dry_hunt.out`: the eight drafts and their lines; `old_builder.out` and `diff_runs.out`: the diff; `real_reads.out`: what the reads of ERCOT North and SPP North kept; `hunt/2026-10-13/`: the drafts' files; `notes.md`).

## To finish (the data machine, after this branch is on main)

```
git pull origin main
.venv\Scripts\python.exe warehouse\analysis\findings\hunt.py --fix-source-lines --dry-run
.venv\Scripts\python.exe warehouse\analysis\findings\hunt.py --fix-source-lines
```

- The first command prints, for each of the eight drafts, the line as it is and as it would be, and writes nothing. Expected: 8 hunt drafts, 8 with a line to rewrite, each naming `ercot_all_hub_prices_history` alone. Read it before the second.
- The second rewrites, in `public.scanner_drafts`, each draft's `card` (the line, the tables, the caption), `files` (the caption, the CSV's sources line, the two pictures, drawn again from the stored card) and `table_name`. It refuses a draft in which anything else would change, or whose line a person has edited. A second run says "already right" eight times.
- It needs the tables and the service key, so it is the data machine's. It runs each finding once (about two minutes in all) and calls no model. `scanner_drafts` is read by `/internal/findings` and `/analysis`, both in review: no live page reads it.
- Not run by me against the real list: the command was tested with a made-up list and a stand-in for the two requests. Its first real run is the dry run above.

## Checks, with exit codes

| What | Exit | Notes |
|---|---|---|
| `python -m unittest tests.test_session258 tests.test_session233 tests.test_session252` | 0 | 62 tests |
| `tests.test_session170 tests.test_session173 tests.test_session174` | 0 | 47 tests, 2 skipped |
| `tests.test_session181 tests.test_session182 tests.test_session238` | 0 | 112 tests, 1 skipped |
| `tests.test_session177 tests.test_session181_worker tests.test_session182_flow` | 0 | 76 tests |
| `tests.test_session183_replication tests.test_session190_replication tests.test_session231` | 0 | 86 tests, 2 skipped |
| `tests.test_session232 tests.test_session241b tests.test_session191` | 0 | 64 tests |
| `tests.test_session194 tests.test_session164 tests.test_session176` | 0 | 75 tests, 2 skipped |
| `tests.test_session192 tests.test_session245 tests.test_session247` | 0 | 25 tests |
| `tests.test_session154_audit tests.test_session157_audit tests.test_session188_waits` | 0 | 59 tests, 1 skipped |
| `tests.test_session89 tests.test_session91 tests.test_session163` | 0 | 69 tests, 6 skipped |
| `runs/session258/real_reads.py` (read only, under the mutex) | 0 | ERCOT North and SPP North as the finding reads them, 8 s |
| `runs/session258/dry_hunt.py` (the whole hunt, dry run, read only, under the mutex) | 0 | 7 patterns, 36 claims, 13 pass, 8 drafts, none loaded, no pattern failed |
| `runs/session258/old_builder.py`, then `diff_runs.py` | 0, 0 | the eight drafts built again by the builder as it stood before this session, from the same yearly series; 56 files compared: see "The diff" |
| The old code's whole dry run on the tables | 1 | not completed: my copy of the old code lacked `warehouse/analysis/style.py`, and the mutex was then another session's. The old builder on the same series stands in its place |
| Em dash in the files written | 0 found | also a test |

- Not run: the whole suite (the orchestrator runs it on a clean copy at the landing); the site's checks (nothing under `site/` changed); a Stata do-file (no Stata here).
- Pins moved: none. `tests/test_session233.py` still passes as it stood (`region_tables` is kept as the rule of a draft built without the reads).

## Decisions made without you

1. **The card names the claim's tables; the CSV names every table a row of the file rests on.** The live table brings ERCOT's rows only to the year under way, which is in the file and not in the claim. Naming it in the card would say more than the card shows; leaving it out of the file would drop a true source.
2. **A draft of a price measure does not name the tables its module reads for other columns** (the fleet, the load, the solar fleet). A table without a market column cannot be given to a grid by its rows, so the pattern names what its measure needs (`measure_tables`): only the gas pattern has one, Henry Hub's prices. This is the one hand-kept part, and a test holds it inside the module's own tables.
3. **By grid, not by node.** A table is named for a draft when it brought rows of the draft's grid; two hubs of one grid come from the same tables. If one hub's history had a gap the live table filled, the other hubs' drafts would name the live table too: more, never less.
4. **1 January's first twelve UTC hours count for both years,** since every grid here is behind UTC. More, never less.
5. **The site was not changed.** It prints the stored line. To correct it on the page I would have to know which stored table held which grid's rows in which years, which the stored fields do not say.
6. **The rewrite command sits in `hunt.py`** as a flag, with `--dry-run`, and writes its pictures under `runs/hunt/source_lines/`. It rewrites a draft in any state (an approved draft is shown on `/analysis` with its line).
7. **The full cards' builder got the same record, with a narrow rule:** it leaves a table out only when the finding asked for it through `read_table` and kept no row. By their code it should change none of today's eleven cards; that was read, not run on tables.

## For Samuel's ruling

1. The chart-of-the-week cards (`warehouse/analysis/templates/common.py`, shown on `/research`): the publishers named are every publisher of the table, not the grid charted. An ERCOT chart names CAISO, MISO and SPP. Change it to the charted grid's publisher ("Source: ERCOT's rows of ... table iso_rtm_hub_prices")? It changes 104 stored lines under `docs/analysis/` and the source line burned into those charts' pictures, so it is a data-machine regeneration and a page change.
2. `batteries_lunch` (ERCOT alone) names `iso_rtm_hub_prices`, truly: ERCOT's rows after 26 August 2026 come from it, and the table is "license needed" from 21 October for MISO's rows. Should a full card of one grid say "ERCOT's rows of" before such a table, as the drafts do?
3. The words of the new line: "Source: ERCOT's rows of the ERW table ercot_all_hub_prices_history; computed by the finding peak_hour_grids (warehouse/analysis/findings/). Found by the weekly hunt." (singular "table" when there is one; ", with the ERW table eia_fuel_spot_prices" for the gas pattern).
4. Session 252's ruling 7 (EIA's own sentence in the scanner's source line) is untouched.
5. One rule or two for a finding's draft? Session 251's list (`hunt.OWN_TABLES`) and this session's record of the reads both stand in the merged builder; the reads win where they are known. If you want one: the reads need no list to be kept as findings are added, and the list needs no run. For an ERCOT draft they differ by `iso_rtm_hub_prices` (named by the list; said only in the CSV by the reads).

## The landing of session 259

- Freeze: `python scripts/freeze.py status` exit 0, no freeze. Main fetched: it had not moved (`34b468fa`).
- The whole suite on a clean copy of `e4623795`: exit 0, 3,942 tests, OK, 237 skipped.
- Before snapshot `s259-before`: 18:19:35 UTC, 25 pages, 0 failed. Pushed 18:19:48 UTC (`task/259-tidy`, `998371a8`).
- Check run 38445845515: success. It merged the branch as `e01f397d` at 18:28:48 UTC.
- After snapshot `s259-after`: 18:32:26 UTC, 25 pages, 0 failed, taken 3 minutes 38 seconds after the merge. The landing changes no file the site is built from, so the style sheet's name could not show the new deployment: the wait is by the clock (three minutes), and GitHub's deployment record was not read.
- `compare s259-before s259-after`: exit 0, **0 differences in all**, on each of the 25 pages. Expected.
- The remote branch `wip/259-tidy` was deleted after the merge (all of it is on main); GitHub's workflow had deleted `task/259-tidy`.

## The landing: not made

- **What went out:** main (with session 259) merged into the branch as `8528f5ce`; the whole suite on a clean copy of `53c48e7b`: exit 0, 3,964 tests, OK, 237 skipped; freeze exit 0; before snapshot `s258-before` at 18:43:34 UTC (25 pages, 0 failed); pushed 18:43:45 UTC as `task/258-source-lines` (`53c48e7b`); check run 38449106332.
- **What stopped it:** the data machine merged session 251 into main at 18:47:10 UTC (`ceac3a77`). It changes `warehouse/analysis/findings/hunt.py` in the places this session changes: the pushed commit cannot be merged into main (tried here with `git merge-tree`: a conflict in that file), so GitHub's workflow cannot land it, and nothing of this session was deployed. At about the same time Claude Code stopped the wait on that run for low memory.
- **No after snapshot was taken,** because no deploy of this session happened: production serves main as sessions 259 and 251 left it.
- **What stands now:** `wip/258-source-lines` holds main (with session 251) merged in as `e6c897d9`, the conflict resolved by hand as "Read these first" says. On it: `tests.test_session258 tests.test_session251 tests.test_session233`, exit 0, 71 tests; `tests.test_session252 tests.test_session238 tests.test_session188_waits`, exit 0, 42 tests. **The whole suite has not been run on it.**
- **To land it** (say "land 258" to this session, or run on the old laptop, with nothing else heavy running):

```
cd C:\Users\lossa\Documents\erw
git fetch origin
git -C ..\erw-143 merge --no-edit origin/main
bash runs/chain_oct13/suite.sh land258b <the branch's last commit>      (read runs/chain_oct13/land258b/suite_result.txt: "suite exit=0")
.venv\Scripts\python.exe scripts\freeze.py status
node site/scripts/snapshot-live.mjs take s258b-before
git -C ..\erw-143 push origin HEAD:refs/heads/task/258-source-lines
(after the merge commit is on main, and three minutes more)
node site/scripts/snapshot-live.mjs take s258b-after
node site/scripts/snapshot-live.mjs compare s258b-before s258b-after     (expected: 0 differences on the 25 pages)
```

- Then the data machine's three commands under "To finish". They were not put on the task queue: their first real run rewrites eight drafts' stored cards and pictures, `/internal/findings` is on tonight's demo path, and the command has only been run against a made-up list. It waits for you (the reversible choice).
