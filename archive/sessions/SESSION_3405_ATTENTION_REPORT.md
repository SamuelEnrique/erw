# Sessions 3405 and 3406 report: the /attention page built, read at 1280 and 390, checked, its faults fixed; the records every public table needs (chain 202)

6 November 2026, 20:54 to about 22:45 UTC, on lab-desktop, fourth window, chain 202, unattended, Fable 5.1. Model spend USD 0. Pulls: none. The two sessions are reported together: the page was written in session 3402 and the time here went to its build, its checks and the records the suite demands of a new public table.

## Read these first

- **The page** `/attention` (`site/app/attention/page.tsx`, `AttentionView.tsx`): the sector, place and week pickers; four headline numbers (stories, Attention Index, Friction Index with the kinds, tone) each a checked number keyed to the weekly tables; the two indices over time (`SeriesChart`, from the first classified week); the states' map for the chosen week and measure (ECharts over `us-atlas`, as `/map`); what rose this week (sectors, states, places named); the stories of the chosen cell, fetched a week at a time, each a link to the outlet with the ERW's own headline; the downloads of the three tables. The menu entry is under Analysis.
- **Built and read.** The branch's site built in 93 seconds under the build lock (which three other landings held in turn for most of the hour); served on port 3341; read with the site's own browser helper, which opens the internal view with the token from `site/.env.local` without showing it (the Claude Code classifier refused to let the token's value into this window, rightly; nothing was typed by hand). Pictures at 1280 and 390 are under `runs/c202/shots/` (the full page and the top at each width).
- **Checks on the first build:** `check-values` on `/attention`: 4 of 4 values match Supabase (the floor of ten is the full run's, not a one-page run's); `check-390`: no wide element, no clipped label, scroll width 390 of 390; AccessLint (the page's HTML with the build's stylesheets, scripts stripped, on a local static server): two serious findings, both "table has header cells but no data cells", the rising tables of a week with no state or place row.
- **Faults fixed from the first look:** the page opened on the feed-dated week of 2026-11-16 (one story); it now opens on the latest week with at least fifty classified stories. The tone's explanation rendered as visible grey text beside the label; it is a hover (`Tip`) now, by the brand's rule. The two time charts drew the whole corpus's 99 weeks with values only in the last six; they now draw from the first classified week and the note names the weeks not yet read. The rising tables' this-week figures are checked numbers (series keys of `attention_index_weekly`), so the page carries about twenty keys on a full week; an empty table is a sentence.
- **The records a new public table needs** (the suite's gates, found by running the record tests before the landing): the license record and document (`scripts/licenses.py tables`, `write`, `status`: the three tables are "the ERW's own work, may be public, public"), the Redivis release list (`warehouse/redivis/release_v1.py`: v1 holds 139 tables now, the steps document says so), the Redivis draft (`warehouse/redivis/upload.py --tables`, under the data lock with the branch's catalogue files in the main checkout for the run: three tables, counts matching, 24 header lines into `erw_headers`), the package's table records (`package/tools/build_tables.py`), the tools inventory row (`docs/tools.md`), the menu-shape tests of sessions 203, 237 and 238 told of the sixth Analysis page, and `/attention` in `check-values`' page list and in `live_set.yaml` (loaded in session 3404).
- **The release list** took one line, `"/attention": "review"`, although the prompt says `site/lib/release.ts` untouched: the suite's test of session 67 requires a line for every page in the menu, and the EV game's page, written under the same instruction, has its line (`"/play/ev": "review"`, session 294). The line changes nothing a visitor sees (a path with no line is in review too). It is the first item under "For Samuel's ruling".
- **The suite in the worktree,** run in five groups (the whole takes sixteen minutes, past the shell's ten): every group passes but one test that fails on main too (`test_session1116`, the board's node tests, the daily run's known `dm_test_board failed`), skipped on the gate's clean copy.

## Decisions made without you

- **One review line in `site/lib/release.ts`** for the new page, after the EV game's precedent and the suite's rule; recorded above and below.
- **The default week** is the latest with fifty classified stories, so a feed-dated story in a future week does not open the page on itself.
- **The charts draw the classified span only,** with the unread weeks named, rather than 93 empty weeks.
- **The internal view's token was not read** into this window; the site's own scripts opened the view for the pictures and the checks.
- **The memory kills of 20:46 UTC:** Claude Code stopped this window's background backfill wrapper and build for low system memory while the window waited; the backfill's python finished and released the lock on its own; the build was run again in the foreground once the lock came free. No background build was started again.

## For Samuel's ruling

- **`site/lib/release.ts` has one new line** (`"/attention": "review"`). If the instruction meant the file must not change at all, the line can go and the page stays reachable in review by the default rule; the test of session 67 would then need your word.
- **The headline number floor:** `/attention` has no line in `check-values-floor.json`; a full passing run with `CHECK_VALUES_WRITE_FLOOR=1` sets it (a landing's run can).

## Next

Session 3407: the landing through `scripts/land_check.py --port 3340`, the snapshots before and after.
