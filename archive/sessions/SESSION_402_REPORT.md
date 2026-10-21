# Session 402 report: the Digest audited, every number traced

21 October 2026, about 04:30 to 06:15 UTC, unattended, on samueloldlaptop (the code machine), in the worktree `C:\Users\lossa\Documents\erw-402` on `wip/402-s` (from `wip/381-382-land`). Chain `queue/done/015-day-20-october-code-pm.md`, session 402. Model spend USD 0; the Digest's writer was not run; no news table and no warehouse data written; no pull from any publisher (the live set was read with the anon key, read only).

## Read these first

- **Until this session no figure of the Digest carried a key, check-values read none of them, and the license hold of 21 October reached none of them.** `/digest` and `/digest/<date>` render committed markdown, not Num spans: since 00:00 UTC NYISO's and ISO-NE's prices (and MISO's rows of the consolidated tables) were drawn as plain numbers on every Digest. New `site/lib/digest.ts` reads the numbers section as `warehouse/news/brief.py` writes it (both of its forms: the table in the row until 27 September, footnotes since) and the chart of the day, and gives each figure the key and raw value a Num carries: `digest_dam|<ISO>|<table>|<node>|<day>`, `digest_rt|<table>|<node>|<variable>|<ts_utc>`, `digest_fuel|eia_fuel_spot_prices|<entity>|<day>`, `digest_chart|<date>|<table>|<number>`. A held figure is drawn as Num draws one ("license needed", the publishers in the hover, no key).
- **Every figure of every Digest is traced to its table** (12 Digests, 25 September to 20 October): new `scripts/check_digest.py` recomputes each by the Digest's own rule. Against the CSVs and the live set together: **120 figures ok, 0 failed**; the 3 "strength" figures of the chart are the scan's statistics, checked against the chart's record; 6 fun facts are history facts checked word for word when written; the 4 warehouse fun facts (WTI and Henry Hub lows, Washington's hydro share) recompute exactly.
- **Today, 21 October, has no Digest yet** (the daily run starts at 14:00 UTC). Until this session `/digest` showed the newest Digest, whatever its day. It now shows today's, or one line: "No Digest yet for Wednesday 21 October 2026: the weekday brief is written by the daily run, which starts at 14:00 UTC. The newest is the Digest of Tuesday 20 October 2026." The weekdays that passed without a Digest (29 and 30 September, 1, 5, 6, 15, 16 and 19 October) answered 404 and were missing from the archive; they are now listed and answer "No Digest was published for Monday 19 October 2026."
- **The Digest's stories are held, with the news index**: the license table of 21 October (`docs/state/licenses_2026-10-21.md`) says `/digest` goes dark ("all of it": `news_index` is held whole), but the page drew every story. The three story sections now read "license needed" while `news_index` is held; the policy actions (`policy_actions`) under Policy stay. This is a decision, listed for your ruling.
- **The method note** (`/about#digest`) is current: the chart of the day, the keys and both checkers, the hold, and the schedule (the daily run from 14:00 UTC; a day without a Digest says so).

## What to review

- The branch: `https://github.com/SamuelEnrique/erw/tree/wip/402-s`; the code: `site/lib/digest.ts`, `site/app/digest/page.tsx`, `site/app/digest/[date]/page.tsx`, `site/lib/markdown.ts` (`renderDigest`, `archiveDays`), `site/scripts/check-values.mjs`, `scripts/check_digest.py`, `site/app/about/page.tsx`.
- The shots, 1280 and 390 px, whole page, internal view: `docs/brand/review-402/` (`digest`, `digest-2026-10-20`, `digest-2026-10-19`, `digest-2026-09-25`, `digest-2026-10-13`), with `pages-402.json` (each page's held and checked figures; no horizontal overflow at either width) and `shots-402.mjs`.
- After the landing, in the internal view: `/digest` (the one line, the archive with every day), `/digest/2026-10-20` (ERCOT 23.41, CAISO 44.78, SPP 21.85 with keys; NYISO, ISO-NE, the real-time price at N.Y.C. and the summary held), `/digest/2026-10-19` (no Digest), `/digest/2026-09-25` (the old form), `/about#digest`.

## Checks

Every gate redirected to a file under `runs/chain_oct21/s402/`, never piped; the exit code read before the next step.

| Check | Exit | Result |
|---|---|---|
| `node scripts/digest-figures.mjs --now 2026-10-21` | 0 | 12 Digests, 120 figures with keys; 32 of them held on 21 October |
| `scripts/check_digest.py` against the CSVs of the main copy (`warehouse/output`, last written 9 October) | 0 | 92 ok, 0 failed, 28 not held by the CSVs (days after 8 October) |
| `scripts/check_digest.py --supabase` (all Digests) | 1 | 58 ok, 0 failed; reads of `eia_fuel_spot_prices` met statement timeouts (HTTP 500) and a fun-fact read raised; the retry and the guard were then added |
| `scripts/check_digest.py --supabase` for 9, 12, 13, 14 and 20 October | 0 | 48 ok, 0 failed, 4 not in the live set (the charts' monthly rows) |
| The two runs together | | 120 figures ok, 0 failed, none unchecked; 3 chart statistics from the record; 6 history fun facts |
| `node scripts/test-digest-numbers.mjs` | 0 | 9 tests |
| `tests.test_session402` | 0 | 9 tests (the first run caught a fault in the checker's own day length on the day the clocks go back; fixed) |
| `npm ci`, then `npm run build` at `c9ece56d` | 0, 0 | no statement timeout in the build |
| `shots-402.mjs http://localhost:3402` | 0 | 10 shots, each looked at |
| `check-values.mjs http://localhost:3402`, `CHECK_VALUES_PAGES=/digest` (restricted) | 0 | 64 of 64 values match Supabase: `/digest/2026-09-25` to `/digest/2026-10-20` |
| `test-markdown-safe.mjs`, `test-digest-chart.mjs` | 0, 0 | |
| Tests near the change (177, 215, 232, 238, 248, 268, 315, 369, 382, 402) | 1, then 0 | two source-text assertions met the change (177: the pages write markdown through `render`; 315: the text rule's line); 177 now also accepts `renderDigest`, which renders through `render` and adds only escaped spans; 315's line is kept as written. 154 tests OK |
| Whole suite (`unittest discover -s tests`) at `0f5a17b5` | 1 | 4,791 tests, 3 failures: `test_session156` (the ask fixtures, expected tonight); `test_session103` (`check_digest.py` read the CSVs with `comment="#"`: now skips the header by its count); `test_session241b` (the day page opened `<Brand>` three times where two are counted: the two pages without a Digest are one now) |
| `tests.test_session103`, `241b`, `402`, `177` after those two fixes | 0 | 76 tests OK |

## Decisions made without you

1. **The figures are wrapped in the page, not in the writer.** The Digest's markdown stays as `brief.py` writes it; the site reads it. The writer was not to be run, and the archive's Digests had to be keyed too.
2. **The summary above the numbers is held whole when it names a held figure** ("license needed: the summary of these numbers names figures of a table held since 21 October 2026"). Its sentences compare the grids: with the held figure taken out, "dearest at NYISO's N.Y.C." would still say what the held table says. When it names no held figure, each figure it names carries the section's key.
3. **The story sections are held while `news_index` is held**, by `licenseNeeded("news_index")`: a permission recorded for it brings them back by itself. The intro line's count of scored stories and the policy actions stay.
4. **A chart of a held table would be held with its picture.** No chart in the archive is (the chart-maker passes over held tables); the rule is tested.
5. **check-values reads `/digest` and each Digest whose day the live set still holds** (33 days: ISO prices are kept 35). Older Digests are traced by `check_digest.py` against the CSVs. The fun facts are not keyed on the page; `check_digest.py` traces the warehouse ones.
6. **`/digest` is regenerated every 10 minutes, not every hour**, so that after midnight the day before's Digest does not stand in today's place for long. It reads no database.
7. **The "highest" in "Highest real-time price" is not rechecked** (it would read every real-time table for the day); the figure at its interval is.

## For Samuel's ruling

- The Digest's stories are held with `news_index` since 21 October (decision 3); say if the Digest's headlines, the ERW's own words from the outlets' titles, may show without a permission.
- The home page's five Digest stories (`app/page.tsx`, from `docs/digest/latest.md`) and the Roundup's stories and numbers (`/roundup`, markdown, no keys) are not held: the same gap as the Digest's, on pages outside this session.
- The e-mailed Digest (`warehouse/news/email_digest.py`) carries NYISO's and ISO-NE's figures and the stories; the hold of 21 October is the site's only.
- Eight weekdays passed without a Digest (29 and 30 September, 1, 5, 6, 15, 16 and 19 October): `run_status.csv` names a date-parse failure (30 September), duplicate items (5 and 6 October); a local run on 29 September is recorded ok but its Digest was never committed; no run is recorded for 1, 15, 16 and 19 October.

## To finish

- The day page was restructured after the build (one `<Brand>` for the days without a Digest): the landing's build covers it; on its own, `cd site && npx tsc --noEmit -p . > ../runs/s402-tsc.out 2>&1; echo exit=$?` (see the type check's line in the hand-back), then the shots again with `node docs/brand/review-402/shots-402.mjs http://localhost:<port>`.
- The whole suite once more in the landing's clean copy (`test_session156` may fail without this session).
- After today's Digest is written (from 14:00 UTC) and landed: on a build, `MSYS_NO_PATHCONV=1 CHECK_VALUES_PAGES=/digest node scripts/check-values.mjs http://localhost:<port>` (from `site/`), and `python scripts/check_digest.py --supabase --date 2026-10-21`.
- The full `check-values.mjs` run belongs to the landing.

## Files

- New: `site/lib/digest.ts`, `site/scripts/digest-figures.mjs`, `site/scripts/test-digest-numbers.mjs`, `scripts/check_digest.py`, `tests/test_session402.py`, `docs/brand/review-402/`.
- Changed: `site/app/digest/page.tsx`, `site/app/digest/[date]/page.tsx`, `site/lib/markdown.ts`, `site/app/about/page.tsx`, `site/scripts/check-values.mjs`, `tests/test_session177.py`.

## Finished on the combined branch (21 October)

On `wip/015-finish` (the worktree `C:\Users\lossa\Documents\erw-finish`, cut from `wip/015-land`: sessions 401 to 410, 413 and 414 merged on main), 21 October 2026, 09:17 to 09:42 UTC under the build mutex: `duty.py beat` exit 0, `npm ci` exit 0, **one build, `npm run build` exit 0** (no statement timeout in its log), `npx next start -p 3415`. Every output is under `runs/chain_oct21/finish/` (outside git). Common to every section below: the **full `check-values.mjs`** (no restriction) exit 1: **6,359 of 6,359 values match Supabase**; 10 pages below their floors, exactly session 408's list with its counts (`/deals` 0 of 10, `/map` 0 of 1, `/events` 2 of 9, `/events/uri-2021` 9 of 10, `/events/covid-2020` 7 of 10, `/events/caiso-heat-2020`, `/events/caiso-heat-2022` and `/events/east-heat-2025` 0 of 10, `/learn/bill` 5 of 10, `/research/card/gas_sets_price` 4 of 6), every one license-held, expected; no other failure. **`check-routes.mjs`** exit 0 (1 live page and 223 in review asked as a visitor, 0 failed). The **whole suite** (`ERW_LOCK_EXEMPT=1 python -m unittest discover -s tests`, 09:43 to 09:49 UTC, the server stopped) exit 1: 4,911 tests, 1 failure, `test_session156` (the ask fixtures, the chain's known failure tonight), 254 skipped; the ten sessions' own modules (402 to 410, 414) exit 0, 107 tests. The server was stopped and the mutex released at 09:42 UTC.

- **The Digest's floors:** `MSYS_NO_PATHCONV=1 CHECK_VALUES_WRITE_FLOOR=1 CHECK_VALUES_PAGES=/digest node scripts/check-values.mjs http://localhost:3415` exit 0, 64 of 64 values match Supabase. `site/scripts/check-values-floor.json` gained 13 lines: `/digest` 0 (today's Digest is not written yet, so the page carries no checked number), `/digest/2026-09-25` 7, `09-26` 6, `09-27` 7, `09-28` 7, `10-02` 6, `10-07` 7, `10-08` 7, `10-09` 6, `10-12` 7, `10-13` 9, `10-14` 10, `10-20` 9 (commit `16261335`). A floor of a dated page that a later run does not read fails nothing (`check-values.mjs`, line 1076).
- **The re-shoot:** `node docs/brand/review-402/shots-402.mjs http://localhost:3415` exit 0; the ten PNGs came out byte for byte the ones committed, so the restructured day page draws as before; `pages-402.json` rewritten with no change of content. Looked at: `digest-1280.png` (no Digest yet for 21 October, the newest is 20 October's, the archive of 12 digests beside it) and `digest-2026-10-19-1280.png` ("No Digest was published for Monday 19 October 2026", with the archive's links before and after).
- **The type check:** the build's own type check passed (exit 0), which covers the restructured page; no separate `tsc` was run.
- `tests.test_session402`: exit 0 within the ten sessions' modules (107 tests, OK, 2 skipped).

To finish (still): after today's Digest is written (from 14:00 UTC) and landed, `python scripts/check_digest.py --supabase --date 2026-10-21` and a restricted check-values on `/digest`; then the `/digest` floor can be written again from that run.
