# Session 288 report: the Games menu, the problem sets' words and the bill

14 October 2026, from 22:01 UTC, unattended, on samueloldlaptop (the code machine), the first session of the afternoon chain of 14 October (sessions 288 to 294). Branch `task/288-games-menu`, from `origin/wip/279-games` merged with `origin/main`. **Lands on main** (the prompt). Model spend USD 0: no model call. No pull, no warehouse data written.

## Read these first

- **The landing carries sessions 261 and 279's Games branch with it** (the prompt: start from `wip/279-games` merged with main): their fourteen plain fixes, the brand wrapper on the tour and the problem sets, and the review folders `docs/reviews/games-2026-10-13/` and `docs/reviews/games-2026-10-14/` (about 400 screenshots, 128-colour PNGs).
- **Every Games page is still in review** (`site/lib/release.ts`): a visitor sees the in-review page at each address. Nothing a visitor sees changes but the menu.
- **Set B question 2 could not take a month complete at all hubs: there is none.** ISO-NE's internal hub misses hours in most months (720 of 744 in August 2026, 576 of 720 in September; whole only in November and December 2024, January and March 2026). The question takes the latest month in which every hub holds at least 95 percent of its hours (today August 2026) and names the short hub with its hours. My choice, below; for your ruling.
- **Set E question 5, 18 days against 18 (ruling 6a): 78.54 times, where the old one-week comparison said 201.95.**
- **The PG&E default bill in winter is $229.63** (it was $262.33 in summer); SDG&E's default moved to winter too.

## What to review

- The menu, on production once this lands (every Games page stays in review, so open the internal view first):
  1. Open https://erw-flame.vercel.app/internal/unlock?token=<INTERNAL_COSTS_TOKEN> (the token is in `site/.env.local`).
  2. Open https://erw-flame.vercel.app/ and the menu "Games": four entries, Home battery game, The tour, What is on a bill, Problem sets. "Economics" no longer lists the bill.
  3. Click "Problem sets": https://erw-flame.vercel.app/learn/problems lists all five sets.
- Set B question 2 and question 5: https://erw-flame.vercel.app/learn/problems/prices-and-your-bill , "Show answer" under each.
- Set E question 5: https://erw-flame.vercel.app/learn/problems/networks-and-money , "Show answer" under question 5.
- The bill: https://erw-flame.vercel.app/learn/bill : the PG&E and SDG&E cards' first lines say winter; pick SCE, type 80 in "Share of use from 4 to 9 p.m.": it is held at 66.7 percent, with the line "Held at ... the two shares together can be at most 100 percent."
- The code: https://github.com/SamuelEnrique/erw/blob/main/site/lib/problems.ts (search "session 288"), https://github.com/SamuelEnrique/erw/blob/main/docs/methods/problem_sets.md (new).

## What was done

- **The menu (ruling 14):** `site/lib/pages.ts`: Games is the battery game, the tour, the bill explainer (moved from Economics) and "Problem sets" (`/learn/problems`, the index of all five; the four sets listed one by one left the menu and keep their addresses). The EV game joins it on the games branch (session 294).
- **Problem sets (`site/lib/problems.ts`):**
  - Ruling 4: set B question 2 names the seven hubs (CAISO NP15, CAISO SP15, ERCOT hub average, ISO-NE internal hub, MISO Indiana hub, NYISO New York City, SPP North hub) and counts them; the worked solution is one step for the seven, not a step each.
  - Ruling 5a: B5 and D3 take the latest complete month (ERCOT's hours all held in `cost_of_power_monthly`): 2026-09 today, where they took 2026-10 with two days in it. B2 as above.
  - Ruling 6a: E5 sets the storm's 18 days against 18 normal days: the mean baseline day times the window's days. New check keys `mrs|<inputs>|<event>|days|base_mean|base_window`, recomputed in `site/scripts/check-values.mjs` from `lib/merchant.ts`'s `stress()` (merchant.ts itself unchanged).
  - Ruling 7a: A1, A3, C1 and C5 reworded ("ERCOT's peak was how many times CAISO's?").
- **The bill (`site/data/bill_rules.json` version 2026-10-14.1, `site/lib/bill.ts`, `BillCalc.tsx`, `page.tsx`):**
  - Ruling 9a: PG&E and SDG&E default to winter, as SCE did; each default's label says why.
  - Ruling 10b: `clampShares()`: the 4-to-9 p.m. share and the super off-peak share together hold at most 100 percent; the share just typed is held to what the other leaves, and a line says so. The old warning (and the negative off-peak share it billed) is gone.
  - The "written, cited" chip is 12 px (it was 10, under the brand's floor).
- **Tests:** `tests/test_session288.py` (11 tests); `site/scripts/test-bill.mjs` names its summer cases and adds the winter defaults and three clamp cases; five older menu tests (sessions 53, 55, 203, 237, 239) and session 264's key count follow the rulings, each line marked "session 288".
- **A methods note:** `docs/methods/problem_sets.md`.

## Checks

| Check | Exit | Notes |
|---|---|---|
| `scripts/precheck.py` | 0 | six of six |
| `npx tsc --noEmit` (worktree) | 0 | |
| `node scripts/test-bill.mjs` | 0 | every bill matches the hand-computed figures |
| `npm run build`, main copy, the landing commit | 0 | no "statement timeout", no "unexpected error" (the first build of the day had one: set B found no month complete at all hubs; fixed, above) |
| `check-values.mjs`, the Games pages | 0 | 105 of 105 |
| `check-values.mjs`, full, first run | 1 | 25 on `/grid`, the grid pages, `/mix` and `/cost-of-power`: data that moved after the build, no Games page |
| `check-values.mjs`, full, second run | 0 | 4,918 of 4,940; 22 latest prices superseded within 45 minutes |
| Suite, clean copy (`erw-check`), `acc00c70` | 1 | 4,249 tests, one failure: session 264's count of grid-checked keys (now three with `mrs|`); fixed in `f7dc9234`, that test then passes. The whole suite was not run again for a one-line test change |
| `scripts/freeze.py status` | 0 | no freeze |
| Open task branches | | `task/198-battery-data` only, trial merge clean |

The snapshot and the landing are recorded under "Landing" below, written after the push.

## Decisions made without you

- **Set B question 2: the latest month every hub holds at 95 percent of its hours**, since no month is whole at all seven. Reversible: one constant, `NEAR_FULL` in `site/lib/problems.ts`.
- **Ruling 9a read as winter for all three California bills**, as the pack's option (a) said, although PG&E's tariffs were read on 30 September, the last day of its summer. SDG&E's own season change was not read as a date; its label says so.
- **Ruling 10b clamps the share just typed**, not the other one, so the reader's last number is the one held.
- **`site/scripts/check-values.mjs` gained one key kind (`mrs|`)** for set E. It is the checker of every page, outside the Games tab's own folders; it was the only way to make the new numbers checkable without touching `lib/merchant.ts` (the seller tool's code).
- **The 10 px chip on the bill fixed** (the brand's 12 px floor): plain, unruled.
- **The bill's "Related" line now links set B** ("Prices and your bill") and the cost of power, so the bill and the set link each way.

## For Samuel's ruling

- Set B question 2's month: the 95 percent rule (today August 2026), or one of: drop ISO-NE from the question; take the latest month whole at all hubs but ISO-NE and say so.
- `wip/261-games` and `wip/279-games` can be deleted once this lands (memory: merged branches are deleted; I leave them for the review folders' links).

## Files

- New: `tests/test_session288.py`, `docs/methods/problem_sets.md`, this report.
- Changed: `site/lib/pages.ts`, `site/lib/problems.ts`, `site/lib/bill.ts`, `site/app/learn/bill/BillCalc.tsx`, `site/app/learn/bill/page.tsx`, `site/data/bill_rules.json`, `site/scripts/check-values.mjs`, `site/scripts/test-bill.mjs`, `tests/test_session53.py`, `tests/test_session55.py`, `tests/test_session203.py`, `tests/test_session237.py`, `tests/test_session239.py`, `tests/test_session264.py`.

## Landing

- Before `s288-before` 22:32:43 UTC; pushed 22:32:51 (`task/288-games-menu`, `7eabf0ca`); check run 38648395552 success; merged `0137e1f6`; Vercel production success 22:43:19; production serves it (the internal view of set E reads "as many normal days").
- After `s288-after` 22:45:18; `compare`: **125 differences, all expected**: on each of the 25 pages the menu's four "Problems: ..." entries are gone and "Problem sets" is there (5 lines a page). No checked number moved (none is on a page a visitor sees: every page is in review). Nothing unexpected.
- This section was written on `wip/games-v2` after the landing; main carries the report as pushed.
