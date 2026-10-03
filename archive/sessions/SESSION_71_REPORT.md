# Session 71 report: the battery page before it is sent, the home page, and the game's finish

Energy Research Warehouse (ERW), session 71, on the portable laptop, 2026-10-03 from about 01:00 to 05:35 UTC, unattended, with one pause at Samuel's request (`SESSION_71_PAUSE.md`) and three rulings on resuming. **Model spend: USD 0.00** (the cap was USD 0.00). No pull, no model call, no force push. No table or number changed.

## In plain words

**The battery page now leads with the last twelve months, and it is live.** `task/071-presend` was pushed once. The workflow's checks passed (run 37098513138) and it merged the branch: main is at `7b37330`. Vercel finished the production deploy at about 05:21 UTC, 16 minutes after the merge.

**The new summary sentences, word for word (100 MW, 4 hours, perfect foresight, as production serves them):**

- ERCOT: "Over the last twelve months a 100 MW, 4-hour battery in ERCOT earned USD 81.40 per kW, 33 percent of it from ancillary services, and covered its debt 0.88 times."
- CAISO: "Over the last twelve months a 100 MW, 4-hour battery in CAISO earned USD 78.90 per kW, 43 percent of it from ancillary services, and covered its debt 0.84 times."

**The three headline numbers:** last twelve months (USD per kW, with the US dollars for the reader's size beneath); a bad month, the 10th percentile of the last 36 months (ERCOT: USD 475,477, December 2024, of 36 months held; CAISO: USD 454,771 of the 25 months held, and the page says CAISO is held from September 2024); debt coverage over the last twelve months.

**The income table's columns** (each a short title with its span beneath; the total row for 100 MW, and a last row in USD per kW):

| Column | ERCOT, 4 h, total | ERCOT, USD per kW | CAISO, 4 h, total | CAISO, USD per kW |
|---|---|---|---|---|
| Last twelve months, USD (Oct 2025 to Sep 2026) | 8.14 million | 81.40 | 7.89 million | 78.90 |
| 2023 to 2025, a year, USD (the average of the last three full years) | 25.51 million | 255.08 | not held: CAISO holds one full year (2025) | not held |
| Every year held, a year, USD (the average; ERCOT Jan 2018 to Sep 2026, CAISO Sep 2024 to Sep 2026) | 61.46 million | 614.58 | 8.91 million | 89.11 |
| Without Feb 2021, a year, USD (the same average without that one month) | 26.97 million | 269.68 | no column: no month is above a quarter | |

ERCOT by stream, in the same column order (USD for 100 MW): energy 5.46 million, 9.07 million, 7.38 million, 7.68 million; ancillary services 2.68 million, 16.44 million, 54.08 million, 19.29 million. CAISO: energy 4.48 million, not held, 4.77 million; ancillary 3.41 million, not held, 4.14 million. The USD 614.58 and USD 269.7 figures are session 67's (269.68 to two decimals).

**February 2021 stays visible.** It is on the chart, whose scale still breaks for 2021 with the value written (3,430.56 USD per kW). It also stays in the every-year average. The table's note says it alone is 57 percent of everything the battery earned in the 105 months held, and that the last column is the same average without it. The box under the summary sentence is gone, because the table and the sentence under the chart now say the same thing. Directly under the chart, not folded: "This is an upper bound: the battery is assumed to sell as much of its power as reserves as it likes at the posted price, and is never called, so years before 2024 show more than real batteries earned. Recent years are the ones to read." (CAISO: "... and is never called. CAISO is held from September 2024, so every year here is a recent one.")

**The contract:** "Market income on the uncontracted share" and "From the market after the contract ends" use the last twelve months, each with "average of every year held: USD ..." beside it.

**The home page now** (production, as a visitor):
- The "Open now" strip is first, with four tools. Following your ruling, the battery tile reads "USD 81.40 per kW, What a battery earns: the last twelve months of a 100 MW, 4-hour battery in ERCOT (October 2025 to September 2026)". No tile shows the Uri-weighted average.
- Below it: the real-time price board, without its links to pages in review.
- "Students and teachers" and "Investors and lenders" now hold only their live card each (The network; Cost of power: selling). "Researchers" had none and is not shown.
- Then gas and oil, the digest's top five items, and a compact "In review" section that names the 19 tools once, greyed, not links: the tour, Price board, Every hub and zone, Your grid, What is on a bill, Problem sets, Home battery game, Events, Cost of power: buying, Deals, Datacenters, Severance tax and the lease tool, Companies (the Thesis Builder), Data and downloads, Event studies and the notebook, Methods and the data standard, Ask the ERW, Energy Digest archive, ERW's Roundup. In the internal view they are links.
- The warehouse status comes last.
- No "in review" label appears in the page's body. Table names in citation lines are plain text on every page. The menu is unchanged (every item, the ones in review greyed and labeled).

**The game is not finished.** Session 70's "To finish" stopped at step 2. `warehouse/supabase/apply.py` exited 1 before reaching migration 019. It re-applies every migration in order, and `014_game_v2.sql` re-adds the version 2 preset check, which the 11 version 3 scores already stored violate (`CheckViolation: game_scores_preset_check`). I checked the database read-only afterwards: nothing changed. Both preset checks still hold the version 3 rule from 018. There are no v4 rows and 019 is not applied. Steps 3 to 6 were not run, so the game's live checks were not run either. Your ruling 3 was carried out up to that point: main is merged into the game branch and the game's tests and build pass (see Part D).

**The unlock link still answers 404 on production** (tested at 05:23 and again at 05:31 UTC with the token in `.env`; `/internal/costs` with the same token also 404; `/internal/lock` answers 303). Vercel's `INTERNAL_COSTS_TOKEN` is still unset or different.

## Part A: the battery page (`/cost-of-power/battery`)

All arithmetic is in `site/lib/batterystack.ts`; every figure carries a `bs|` check key. New statistics: `l12_kw`, `l12_share`, `p10_36`, `n36`, `y3`, `y3_kw`, `avg_without`, `avg_without_kw`, with the helpers `last36`, `lastThreeYears`, `threeYearAverage` and `averageWithout`. The old keys still work. Page: `site/app/cost-of-power/battery/page.tsx`; contract: `Contract.tsx`. The method doc has a new section, "How the page reads the tables (session 71)", and its "Results that look implausible" line now points to it.

## Part B: the home page

`site/app/page.tsx`. `SiteLink` gains a `gate` look: `label` (the default, as in the menu), `quiet` (greyed, no label: the "In review" list) and `plain` (plain text, no label: citation table names and the node name on each price card). In none of the three is a page in review a link for a visitor. `Cite` uses `plain` for every table name, so this applies site-wide. Everything a visitor sees is still decided by `site/lib/release.ts`: when a tool goes live, its card and links come back by themselves.

## Part C

Session 68's "The push and production" section (`e86d701`, local `task/068-network`) was cherry-picked as `8795c42` and is on main.

## Part D: the game (session 70's "To finish")

1. **Your ruling 3, before step 1.** In `C:\Users\samen\Documents\erw-game` I merged `origin/main` into `wip/066-battery-game-v4`. The one conflict was the import at the top of `site/app/play/battery/Game.tsx`: main's `import { SiteLink as Link } from "@/components/SiteLink";` is kept, with the game's v4 comment block above it. Nothing else conflicted, and no file in the game imports `next/link` directly. The game adds no route, so `site/lib/release.ts` needs no entry; `/play/battery` stays `review` (from main). Merge commit `92263e4`, pushed to `origin/wip/066-battery-game-v4`, a branch no workflow runs on. After the merge: `tests.test_session70 test_session66 test_session38 test_session56 test_session50`, 42 tests, OK (3 skipped), exit 0; `tsc` exit 0; `npm run build` exit 0.
2. **Step 1:** the data lock was taken (exit 0).
3. **Step 2:** `git fetch origin` exit 0. The copy of 019 was written (exit 0). `python warehouse/supabase/apply.py` **exit 1**. It applied 001 to 013 again (each idempotent, as intended), then failed on `014_game_v2.sql`. Stopped there, as the rules say.
4. **After the stop**, to leave nothing half-done (no Part D step was run past the failure):
   - read-only check that the failed file changed nothing: psycopg sends a multi-statement file as one implicit transaction, so the `drop constraint` in 014 was rolled back with the failed `add`;
   - removed the untracked copy of 019 from the main folder (step 2's own last command, which the failure skipped);
   - released the lock (exit 0).

**What it needs:** `apply.py` cannot run every migration from the start any more, because 014 re-adds a constraint that later rows break. Three ways to fix it, each a decision for you, not for me in an unattended run:
- (a) Make 014's `add constraint ... not valid`, so it does not check old rows.
- (b) Give `apply.py` a way to apply one named migration.
- (c) Apply 019 by hand: its two `drop`/`add` pairs, which the current rows satisfy, since every stored preset is v2 or v3.

Then rerun "To finish" from step 1.

## Part E

`https://erw-flame.vercel.app/internal/unlock?token=<INTERNAL_COSTS_TOKEN from .env>` answers 404 (twice, the last at 05:31 UTC). It does not work yet.

## Tests and checks

**Local, on the final build of `task/071-presend`:**

| Check | Result |
|---|---|
| `python -m unittest discover -s tests` | 328 tests, OK, exit 0 |
| `pytest package/tests` | 408 passed, 32 skipped, exit 0 |
| `npx tsc --noEmit` | exit 0 |
| `npm run build` | exit 0 |
| `check-routes` | exit 0. Pass 1 (internal cookie): 74 of 74. Pass 2 (visitor): 14 live and 60 in review asked, 0 failed |
| `check-values` | **6,637 of 6,637 values match Supabase, exit 0** (run at 04:56 to 05:02 UTC, capped at 15 minutes). 1,784 of them are battery values (`bs|`), 81 storage values and 42 network values (`bsup|`) |
| `test-battery-stack.mjs` | 67 assertions, all pass, exit 0 |

**On production after the deploy:**

| Check | Result |
|---|---|
| The workflow | run 37098513138: tests, site build and check-routes passed; merged to main as `7b37330` |
| `check-battery-production.mjs` | 12 of 12 combinations (ERCOT and CAISO, 2, 4 and 8 hours, both strategies), 2,826 values, 0 wrong. Every summary sentence begins "Over the last twelve months", exit 0 |
| `test-battery-stack.mjs`, as a visitor | **all 62 visitor assertions pass**: the summary, headline numbers, columns, upper-bound sentence, no box, 2021 on the chart, the contract, the phone layout, the six live pages, the in-review page, the menu, and the home page's "In review" list and battery tile. The script then exited 1 in its internal-view block, because `/internal/unlock` answers 404 there (Part E), so it found no menu to read. Those 5 internal assertions pass locally |

The browser test gained assertions for every Part A and Part B rule, including that the income table fits at 1280 px and that the home battery tile is `l12_kw:total`. `check-battery-production.mjs` requires the new opening of the summary.

## Errors and decisions

- **Decision:** the outlier column appears when one month is **more than a quarter** of everything held (session 67 used a fifth). Only ERCOT's February 2021 qualifies, at 56 to 62 percent, at every duration and under both strategies.
- **Decision:** "From the market after the contract ends" also uses the last twelve months, with the every-year average beside it. The prompt named only the uncontracted-share line, but the old line would have led with the Uri-weighted average.
- **Decision:** the 36-month window ends with the last twelve months' last month. The "last three full years" are the newest year with all twelve months held and the two years before it, each also complete; otherwise "not held" with the reason.
- **Decision:** the income table stays in US dollars for the reader's size, with a per-kW total row.
- **Decision:** citation table names are plain text on every page, not only the home page, because `Cite` is shared.
- **Decision:** on the home page the price board, gas and oil, the digest's items and the status strip stay. Only their links to pages in review were removed, and those pages are named once in "In review".
- **Error, mine:** the first version of the income table was wider than its column at 1280 px, and the last column was cut off. Seen in a screenshot. Fixed with short titles and the span beneath; the browser test now checks the fit.
- **Error, mine:** in the first version, the audience sections with one live card left grey empty cells. Fixed.
- **check-values before the pause:** two runs failed only on the 39 and then 33 latest prices of `/` and `/prices`, the 15-minute timing issue from session 67; every battery value matched. A third run hung for about 70 minutes and ended `fetch failed`, a network error. After the pause, under your 15-minute cap, one run passed with nothing failing.
- **The deploy took 16 minutes** (Vercel "pending" from 05:05 to 05:21 UTC), against about two in session 67. Probably the task branch's preview build was queued first. Nothing failed.
- **Not changed, seen:** the site footer, on every page, still carries "Data and methods" with an "in review" label. It was not in Part B's list.
- **The data lock** was held from about 05:27 to 05:30 UTC (step 1 to the release) and nowhere else.
- **This report** is committed on the local branch `task/071-report` and not pushed: a push would merge and deploy again. It reaches main with the next session's branch, as sessions 67 and 68 did.

## For Samuel

1. **The game's migration (Part D).** `apply.py` stops on `014_game_v2.sql` because version 3 plays exist. Choose (a) make 014's constraint `not valid`, (b) let `apply.py` apply one named migration, or (c) apply 019 by hand. Then rerun "To finish" from step 1. The merged game branch is `92263e4` on `origin/wip/066-battery-game-v4`; its tests and build pass.
2. **The unlock link answers 404 on production.** Set `INTERNAL_COSTS_TOKEN` on Vercel to the value in `.env` and redeploy. Until then nobody can open a page in review on production, and the game's live checks (step 6) can only run locally.
3. **The footer's "Data and methods (in review)"** label on every page: keep it or drop it.
4. **Before sending the battery page:** it is live and every number matches Supabase. The CAISO duration requirements are still assumed at one hour (session 67).
