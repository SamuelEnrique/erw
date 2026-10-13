# Session 248 report: the 21 October license table

13 October 2026, 08:35 to 09:00 UTC, unattended, on lab-desktop (the data machine), the sixth session of the chain of 12 to 13 October. Branch `task/248-license-table`. Model spend USD 0: no model call. No pull, no request to any publisher, no warehouse table written. No page edited.

## Read these first

- **`docs/state/licenses_2026-10-21.md` is written: 197 tables, each one of three. 124 public, 40 "license needed", 33 internal.** Beside each table, the pages that read it; beside each page, the tables that darken it.
- **3 pages go dark on 21 October and 24 go partly dark,** once they are open. Dark: `/datacenters`, `/digest`, `/roundup` (every table they name is held whole). Partly: 24 pages, the home page, the price board, the three decision tools and the seven grid pages among them.
- **35 of the 40 held tables are held by grid, not whole:** only the rows of ISO-NE, MISO and NYISO read "license needed", and the other grids' rows stay. 5 are held whole (the news and datacenter tables, decided by news publishers).
- **The day moved from 20 to 21 October in the status file too.** Your ruling of 12 October, night, moved the public day; `warehouse/metadata/license_status.csv` and `site/data/license_status.json` still said 20 October. Both say 21 now, and so does the code that writes them. Nothing on the site changes before that day.
- **`site/data/license_status.json` now carries every public and "license needed" table by name, and the internal ones as a count,** in three new keys (`all`: each table's status and its pages; `internal_tables`: 33; `pages`: each page's dark, partly or clear). The key the site reads (`tables`, the 40) is as session 207 left it but for the day, so no page reads anything new. The internal tables' names are in the document, not in the site's file: see decision 9.
- **Session 247 landed:** see "The landing of session 247" below.

## What the table says

| Status | Tables | What it means on 21 October |
|---|---|---|
| public | 124 | shown and downloadable |
| license needed | 40 | the words "license needed" where its numbers would be, until a permission is recorded in its row |
| internal | 33 | never shown: in no public dataset, no download, behind the internal view |

- **Who decides the 40:** NYISO (29 tables), ISO-NE (25), MISO (21), then 21 news and operator publishers (Bloomberg, Data Center Dynamics, Data Center Frontier, the Financial Times and Hart Energy decide 4 tables each).
- **The pages, in the document's first table:** each with its route, the tables held whole, the tables held by grid with the grids, the internal tables it names and how many tables it keeps.
- **A recorded permission turns a table back on:** fill `permission` and `permission_ref` in its row of `license_status.csv`, run `python scripts/licenses.py status`, land. The table and the JSON follow by the same command.

## What to review

- `docs/state/licenses_2026-10-21.md`: "The pages that go dark or partly dark" first (27 rows).
- `site/data/license_status.json`: `from` is `2026-10-21`; `all` has 164 tables (124 public, 40 "license needed"); `internal_tables` is 33; `pages` has the pages that read a table.
- `python scripts/license_state.py --check` on any machine: exit 0 while the document is what the sources give, 1 with the reason once a table or a page's reads have moved.

## How it is built

- **Nothing typed.** `scripts/license_state.py` reads coverage (the flag), the status file (the 40), the publishers file, and the site's code.
- **Which tables a page reads** is session 214's reading, now in the repository as `scripts/page_tables.py`: the page's file, the modules it imports three levels deep, the tables its data files name, and the names in the menu's own line for the page. Run on `main` it gives the same tables as session 214's launch list for all 56 pages (0 differ).
- **Dark and partly:** a page is dark when every table it reads is held whole or internal. A page that reads a table held by grid is partly dark however many of its tables are held, because the other grids' rows stay. This is the site's own rule (`site/lib/license.ts`, session 215).
- `python scripts/licenses.py status` now ends by writing the table again, so the status file and the table cannot drift apart by that command. `python scripts/licenses.py state` writes the table alone.
- The licenses document was rebuilt on the way (`licenses.py tables`, `write`, `check`: 197 tables, 0 problems): it gained session 244's table (`ercot_rtm_price_adders`, ERCOT, may be public) and CAISO as a publisher of the battery stress table (session 246).

## Checks

| What | Exit | Notes |
|---|---|---|
| `python scripts/precheck.py` | 0 | six of six |
| `python scripts/licenses.py tables --headers warehouse/output`, `write`, `check` | 0, 0, 0 | 197 tables, 41 publishers with a verdict, 0 problems |
| `python scripts/licenses.py status --branch main` | 0 | 40 tables "license needed" from 2026-10-21, 0 with a permission; then the table |
| `python scripts/license_state.py --check` | 0 | 197 tables, 56 pages, 0 problems |
| the page reader against session 214's launch rows | 0 | 56 routes compared, 0 differ |
| the 12 test modules that name the license files, with the new one | 0 | 286 tests; `tests/test_session248.py` 12 |
| `python -m unittest discover -s tests` | 1 | 3,734 tests, 3 failures, 61 skipped: the three this machine always has (`test_session51`, `test_session125`, `test_session165`: local tables against committed files, skipped on the runner). A first run had a fourth, mine (decision 9), fixed |
| `python scripts/freeze.py status` | 0 | no freeze |

## Decisions made without you

1. **The day in the status file moved to 21 October.** The session's title and your ruling say 21; the file said 20. A row with a permission keeps its own day (there is none yet); a row whose day someone set to another one keeps it.
2. **The JSON keeps the key the site reads as it was, and adds three.** Changing the shape of `tables` would have changed what pages read, and this chain does not edit pages. The file grew from 40 tables to 164 in `all` (40 KB); it is read on the server only (eight files import it, none a client component).
3. **A permission recorded makes a table "public"** in the three-way table, with "(permission recorded)" beside its name. There is none today.
4. **"Dark" is strict:** only a page all of whose tables are held whole. By the looser reading (every table held, whole or by grid) `/events` would be a fourth dark page; its one table is held for three grids' rows and keeps ERCOT's and CAISO's.
5. **The pages are read from `main`'s code,** not from the code machine's branches of tonight. When sessions 235 to 238 land, a page's reads may have moved; `python scripts/licenses.py state` writes the table again, and `--check` says whether it must.
6. **My tests do not pin files that move.** A first draft held the document to coverage and to the pages' code as they stand; that would have failed the code machine's next landing, or any session that adds a table. They hold the document and the JSON to each other, the rules on stand-in files, and the day.
7. **Two test pins of the day were changed** (`tests/test_session207.py`, `tests/test_session215.py`: 20 to 21 October).
8. **The comments in three site files still say 20 October** (`site/lib/license.ts`, `site/app/data/page.tsx`, a comment in each). They are comments: the day is read from the file. Not edited (pages are the code machine's tonight); listed.
9. **The site's file names no internal table.** My first build listed all 197 by name, and the whole suite caught it: session 149's test holds one internal table's name out of every file under `site/`. The 33 internal tables are a count there now (and a count per page); their names are in `docs/state/licenses_2026-10-21.md`. If you want them in the site's file too, that test's rule is yours to change.

## For Samuel's ruling

1. **The Digest and the Roundup pages are "dark" by the reading of names:** their menu lines name `news_index`, which is held whole. The pages themselves read files of issues already written. Whether a published issue is hidden on 21 October is the ruling session 214 asked for; this table does not settle it.
2. **`/ask` and the data catalogue read every table,** so the 40 are held there too. The table lists pages; it has no row for "everything Ask can answer".
3. **Who writes to the three operators?** NYISO, ISO-NE and MISO decide 35 of the 40 tables and 24 of the 27 pages. One letter each would clear most of the list (`docs/licenses.md` has each one's contact and sentence).
4. **For the code machine:** three comments that say 20 October (decision 8), and a run of `python scripts/licenses.py state` after its pages land.

## Correction to session 245's report

- I wrote that every page reading `carbon_intensity_hourly` asks for its last few days by date. That is true of `main`. It is **not** true of the code machine's unlanded datacenter page (session 228's "How clean?" on `wip/236-datacenter`), which reads the hourly table whole: when session 245 loaded 430 days, its carbon window went from 776 hours to 10,144 and its figure from 346.71 to 313.05 kg per MWh, and its sentence "the hourly table holds the last 35 days" stopped being true. The code machine's session 236 saw it within the half hour and has the patch ready (`runs/session236/patch5.py` on that machine). No page a visitor can open was affected: every page is in review.
- The same report of session 236 says ERCOT's reserve adders are "coming: the warehouse holds no table of them yet". Session 244's table (`ercot_rtm_price_adders`) reached the live set 40 minutes after that page was written. For the code machine: the table is there, readable with the site's key.

## Files

- New: `scripts/license_state.py`, `scripts/page_tables.py`, `docs/state/licenses_2026-10-21.md`, `tests/test_session248.py`.
- Changed: `scripts/licenses.py` (the day, `moved_day`, the `state` command), `warehouse/metadata/license_status.py` (its note of the day), `warehouse/metadata/license_status.csv` and `site/data/license_status.json` (the day; the three new keys), `warehouse/metadata/license_tables.csv` and `docs/licenses.md` (rebuilt: one table more, one publisher more), `tests/test_session207.py`, `tests/test_session215.py`.
- On this machine, not in git: `runs/session248/` (the files before, the commands' outputs).

## The landing of session 247

- Pushed 08:35:10 UTC (`task/247-stale-and-empty`). Checks passed (run 38370259204); merged to `main` 08:44:41 UTC (`de22f049`); the deployment succeeded 08:47:29 UTC.
- Snapshots: before `s246-after` (08:09:45 UTC), after `s247-after` (08:50:36 UTC). `compare`: 25 pages, 0 differences in all. Expected: every page is in review, and session 247 changed no page.

## The landing

- Freeze: `python scripts/freeze.py status` exit 0, no freeze. Main pulled and merged before the push. The before snapshot is `s247-after` (08:50:36 UTC, taken after session 247's deployment); the push of `task/248-license-table` followed at about 09:00 UTC. The check run, the merge, the deployment's time, the after snapshot and the comparison are in session 249's report. Expected: 0 differences on the 25 pages (the day in the file is 21 October; nothing is held before it, and every page is in review).
