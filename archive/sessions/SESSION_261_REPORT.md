# Session 261 report: the Games tab, set up for Samuel's review

13 October 2026, 20:50 to 21:45 UTC, unattended, on samueloldlaptop (the code machine). Branch `wip/261-games`, pushed, **not landed** (the prompt: do not land). Model spend USD 0 of USD 0: no model call. Pulls: none. No warehouse data written. The queue was not run.

## Read these first

- **All four items work and every number is right: 100 of 100 values match Supabase**, before and after the fixes; no page error, no dead link. What is wrong is in words, rules and looks, and most of it waits for you: 16 questions, each with its options, in `docs/reviews/games-2026-10-13/README.md`.
- **Ranked by how close to real users:** the bill explainer, the problem sets, the tour, the battery game. The game is the most built and the furthest: it does not wear the brand, and a first play on Hard ends at minus $105 by following what the screen says (the backup reserve holds 2.70 kWh, the outage needs 3.16).
- **Eleven plain fixes are on the branch.** The game's chart at the end of a play was empty; its simple page scrolled sideways on a phone; the bill had no Reset and showed "session 48" and "session 49" to the reader; the tour pointed at three headings and a count that are gone. No rule of the game, no answer of a problem set, no rate of a bill changed.
- **Henry's ten questions have no answer on file, and nothing of Kelsey's conversation of 5 October is in the repository.** I could not mark either done or open beyond that (questions 12 and 13).
- **One decision to look at first:** the tour and the problem sets now draw inside `<Brand>` (commit `46fd7338`, alone, so it can be dropped). The game was left in its old look: its canvas and buttons carry their own colors and a wrapper alone would half-brand it.

## What to review

- The README, on GitHub: https://github.com/SamuelEnrique/erw/blob/wip/261-games/docs/reviews/games-2026-10-13/README.md
  1. "Ranked by how close each is to real users".
  2. "Questions only Samuel can answer": 16, each with options.
  3. "Proposed order of sessions": eight, with what each needs from you.
- The four reviews beside it: `battery.md`, `problems.md`, `bill.md`, `tour.md`. Each: what it is for, what it teaches, where a first-time user gets stuck, the bugs (a table, with the screenshot of each), the brand, Henry and Kelsey, and "done for real users" with effort.
- The screenshots: `docs/reviews/games-2026-10-13/<item>/before/` and `<item>/after/`, 202 files, each name ending `-desktop` (1280 px) or `-390`.
  1. The game's end chart: `battery/before/04-simple-done-desktop.png` against `battery/after/04-simple-done-desktop.png`.
  2. The phone's sideways scroll: `battery/before/01-simple-pick-390.png` against the same name under `after/`.
  3. The lost round on Hard: `battery/before/17-hard-done-desktop.png` and `16-hard-status-2-desktop.png`.
  4. The brand on the tour: `tour/before/01-tour-desktop.png` against `tour/after/01-tour-desktop.png`.
  5. The bill's Reset: `bill/after/11-after-reset-390.png`.
- The pages themselves are not deployed (a `wip/` push deploys nothing to production). On this machine, in `C:\Users\lossa\Documents\erw-261\site` (built): `npx next start -p 3261`, open the internal view, then:
  1. http://localhost:3261/play/battery : Start, hold Sell, let the day end: the chart keeps the day's last six hours.
  2. http://localhost:3261/play/battery?more=1 : Hard, Play, sell down to the reserve, wait for 21:00.
  3. http://localhost:3261/learn/bill : change three fields, press "Reset this bill to its defaults".
  4. http://localhost:3261/learn/problems/prices-and-your-bill : open question 2's answer (seven hubs under "all six").
  5. http://localhost:3261/tour : open stop 2 and look for the three headings it names.

## What was done

- Each item played or read end to end on a local production build of `origin/main` (`811328fe`), at 1280 px (keys) and 390 px (touch): 100 screenshots before, 102 after.
- The game was played four times before and four after (the simple page and Hard on the desktop, the simple page and Easy on the phone), each play marked `x-erw-check: 1`: none is on a leaderboard or in the research data.
- Fixes, in three commits:
  - `d3227ecd`: the game's four (end chart, the list of days at 390 px, "see the rules below", "now" at the end), the bill's Reset and "All five tariffs", the tour's stops 2 and 5.
  - `46fd7338`: `<Brand>` on `/tour`, `/learn/problems` and `/learn/problems/[slug]`.
  - `e6af43c9`: the PG&E note without session numbers; the tour's stop 3 without "six hubs".
- The five documents and the screenshots: the fourth commit.

## Checks, with their exit codes

| Check | Result | Exit |
|---|---|---|
| `scripts/precheck.py --what "session 261"` | six of six pass | 0 |
| `npm ci` in the worktree | done | 0 |
| `npm run build`, before any fix | built | 0 |
| `npm run build`, after the fixes (three times: the first fixes, the bill's note, the tour's stop 3) | built each time | 0, 0, 0 |
| `check-values.mjs`, `/learn/` and `/tour`, before | 91 of 91 match | 0 |
| `check-values.mjs`, `/play/battery`, before | 9 of 9 match | 1: the script's own floor of ten values a run, not a mismatch |
| `check-values.mjs`, all Games pages, after | 100 of 100 match | 0 |
| `eslint` on `app/play/battery`, `app/learn`, `app/tour`, `lib/tour.ts` | clean | 0 |
| `unittest`, the 18 modules that read these files (sessions 38, 43, 44, 46, 50, 52, 53, 55, 56, 63, 66, 70, 111, 149, 203, 235, 237, 241a), in the worktree | 165 tests, 5 skipped, OK | 0 |
| The screenshot runs (`runs/session261/shots.mjs`) | 0 page errors in 202 screens | 0 each |

- Not run, because nothing lands: the whole suite in a clean copy, `check-routes.mjs`, the snapshot of rule 8, `freeze.py status`.
- Not run: AccessLint and Impeccable (README, "How this was made").
- The build log holds no "statement timeout" in the three builds after the fixes. The first build's `/grid?grid=ercot` carried one failed read (the queue): a local build's cached timeout, not the Games tab's.

## The landing

- None. To land later, after your rulings: merge `origin/main` into `wip/261-games`, the suite in a clean copy, the build in the main copy, `freeze.py status`, the snapshot before as its own command, push `task/261-games`, the snapshot after and the comparison. All four pages are in review, so a visitor sees no difference until a release line changes.

## Decisions made without you

- **A worktree, `C:\Users\lossa\Documents\erw-261`,** not the main copy: the registered worker switches branches in the main copy. It is left in place with its build and `node_modules` (about 0.6 GB) so that the pages can be opened; remove it with `git worktree remove ../erw-261` when the review is over.
- **`<Brand>` on the tour and the problem sets**, read as covered by your ruling of 12 October (every page is brought to the brand through the shared components). Its own commit. The game was not wrapped.
- **`site/lib/tour.ts`, `site/lib/problems.ts` and `site/data/bill_rules.json` were read as the tab's data**, inside the session's limits. `site/lib/pages.ts` (the menu) was read as outside: the missing fifth problem set is reported, not fixed.
- **Three wordings were treated as stale facts, not as words for a ruling:** a heading that is not on the page, a count of hubs that is wrong, and session numbers shown to a reader.
- **Not fixed though plainly loose:** the seven hubs under "all six" (problem set B, question 2). The prompt keeps every answer of a problem set for your ruling.
- **The external links** (ERCOT's ADER document, the Commission's release, Brattle's study, PG&E's tariff) were not requested: no pull was approved.
- **The screenshots are 128-color PNGs** (17 MB in place of 47 MB), to keep the branch small.
- **The machine was signed off duty** (`scripts/duty.py off`) at the end, since the queue was not to be run: no "ready for review" email follows from this session.

## Errors of this session

- One helper command (a text edit of `Game.tsx`) ran with the bare `python`, against the prompt's rule. It needed no package and did what it should; every later python command named `.venv\Scripts\python.exe`.
- The first `check-values` run lost `/play/battery`: Git Bash rewrote the leading slash of `CHECK_VALUES_PAGES`. Run again with `MSYS_NO_PATHCONV=1`.
- `site/lib/tour.ts` was edited while a build ran, so the build was made again to be sure of what it held.
- The first after pass took the bill's new Reset button for a sixth bill and made two mislabelled screenshots; they were removed, the script corrected and the bill shot again.

## For Samuel's ruling

- The game, Hard: the default backup reserve (2.70 kWh) is smaller than the outage's need (3.16 kWh): raise the reserve, shorten the outage, say so before the day, or ask Henry (README question 1).
- The game, Hard: "Keep charge to sell then" is followed one interval later by "keep charge for the house" (question 2).
- The game: a first play earns $0.13 against $0.87 for perfect: show the fleet on the simple page, open on a famous day, or leave it (question 3).
- Problem set B, question 2: "all six ISO hubs" lists seven, two named CAISO, in a partial month (question 4).
- Problem sets B question 5 and D question 3: October's profile is used without saying it is a partial month (question 5).
- Problem set E, question 5: 18 days of Uri are compared with one normal week (question 6).
- The problem sets' ratio questions: the word order of "how many times CAISO's was ERCOT's?" (question 7).
- The problem sets' answers move every day: a dated edition, live with a date, or frozen (question 8).
- The bill: PG&E and SDG&E default to summer and SCE to winter, side by side in October (question 9).
- The bill: two shares past 100 percent are warned about and billed all the same: refuse, clamp or leave (question 10).
- The tour: a list of links as now, a guided path with a bar on each stop, or folded into the home page (question 11).
- Henry's ten questions have no answer on file: has he answered, and does the game wait for him (question 12).
- Kelsey's conversation of 5 October is not in the repository: what did it ask for, item by item (question 13).
- The menu: Games lists four of five problem sets and not their index, and the bill explainer is under Economics (question 14).
- The brand wrapper on the tour and the problem sets (commit 46fd7338): keep or drop, and is the game's restyle the next brand session (question 15).
- Who each item is for: is the game's full page meant for an investor or an operator, or for a class only (question 16).
- The price board showed ERCOT's prices dated 7 and 8 October on the local build where other hubs were 11 to 13 October: to be checked on production by a session that owns the board.
- `/grid?grid=ercot` and `/events/uri-2021` scroll sideways on a 390 px screen (500 px wide): two of the tour's stops, outside this session's files.
