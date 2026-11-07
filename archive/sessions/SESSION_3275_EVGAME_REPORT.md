# Sessions 3275 to 3278: "Should your family get an EV?" on one screen (portable-laptop, 6 November 2026)

Chain 198 (`queue/done/198-day-6-november-portable-evgame.md`, the prompt word for word). Branch `wip/3275-evgame`.

## What landed

- **Landed as `689e28229`** (the merge of `task/evgame`, gated commit `9d62cfe36`, GitHub run 42292894968, merged 21:14 UTC; production served the new stylesheet from 21:15:21 UTC). The branch's commits: `e8ee7d33e` (session 3275, the method), `496a5570c` and `1b5a17c76` (session 3276, the model and the page), `f021d9163` (session 3277, the fixes at 390 px).
- **Snapshots** `s3278-evgame-before` (20:58 UTC) and `s3278-evgame-after` (21:15 UTC): 25 pages, **0 differences**, expected: every page is in review, so a visitor sees no change.

- **The page, `/play/ev`** (the address the Games menu already used): the five screens of session 294 became one. Inputs on the left (state, electricity and gasoline prices, miles a year, mpg, kWh a mile, the two prices, home charging share, years kept, the rate, the credit switch); payback and net present value on the right, a year of fuel each way, and one chart (what each car has cost by year, the crossing marked, a hover, a tap or the arrow keys read a year). Every default is grey with its source in a hover tip; a moved value turns ink and says "changed by you". "Every number, for your parents" (the sourced table and the print button) stays, folded under the results.
- **The model, `site/lib/ev.ts`**: `chargePrice` (home share at the home price, the rest at a public charger's price the family types; none is guessed), `cumulative` (price plus years of fuel, the crossing at the payback year), `keyed` (the four figures check-values reads). The existing `verdict` is unchanged for 100 percent home charging.
- **The test, `site/scripts/test-ev.mjs`**: three households worked by hand in its comment, 23 checks, exit 0.
- **check-values**: `/play/ev` added; `ev|<state>|power_cents, gas, payback, npv` recomputed from `data/ev_prices.json` by `keyed()`. On the local server: 4 of 4 match (18.31 cents, $4.354, 3.2 years, $5,131).
- **The method, `docs/methods/ev_game.md`**: a new section (the two tables and their keys, the model, every input's default and source, the keys).
- **`tests/test_session294.py`**: the five-screens test became a one-screen test.

## The three households (by hand, then the module)

| Household | Inputs | Saved a year | Payback | NPV |
|---|---|---|---|---|
| 1, the US at the defaults (the page's opening) | 183.1 USD/MWh, $4.354, 15,000 mi, 27 mpg, 0.31 kWh/mi, $28,600 and $33,600, 8 years, 5 percent, no credit | $1,567.47 | 3.19 years (shown 3.2) | $5,130.92 (shown $5,131) |
| 2, Texas | 158.8 USD/MWh, $3.874, 12,000 mi, 30 mpg, 0.28 kWh/mi, $25,000 and $35,000, 10 years, 5 percent, credit $7,500, 80 percent at home, public charger 45 cents | $820.35 (charging 217.04 USD/MWh) | 3.05 years | $3,834.49 |
| 3, Ohio | 194.5 USD/MWh, $3.829, 8,000 mi, 40 mpg, 0.35 kWh/mi, $30,000 and $29,000, 5 years, 3 percent, no credit | $221.20 | at once (the EV costs $1,000 less) | $2,013.03 |

## Checks

- **Gate, first run** (`0cd22e3b6`, 19:20 UTC): the suite failed 7 tests (sessions 1491, 190 replication, 538 and 720: the datacenter page's replication and the cross-check notes), none of this branch's. All four files passed on the newer main (`7710f1c54`) and on the branch merged with it, so the branch was merged again and gated again. Not stopped for memory, so no landing request row.
- **Gate, second run** (`9d62cfe36`, 20:06 to 20:50 UTC, port 3320): freeze, main merged, task branches (only the 26-day `task/198-battery-data`, not judged), db probe, build lock, the suite (7,955 tests, OK, 378 skipped), ask replay, npm ci, build (170 s) and serve passed. check-values: **7,797 of 7,797 values match**, the EV game's four among them; exit 1 for three pages: `/datacenters?view=grids` (fetch failed; passed when read again), `/deals` and `/learn/problems/know-your-grid` (their floors: main's known failures, which the code notes of 7 to 12 November say stop every gate). check-routes, check-cross-checks and check-csp were then run by hand on the kept build under the build lock: 225 pages in review, 0 failed; 92 of 92; 97 pages, 0 violations.
- **The page in the browser** (production build, internal view): axe-core 4.13.0, WCAG 2.2 A and AA: **0 violations at 1280 and at 390 px** (one at 390 on the dev server, the sliders' 24 px target size, fixed in session 3277); every tip opens on focus; the chart's hover reads "Year 6: gasoline car $43,113, EV $38,708"; nothing wider than the window; no page errors. Screenshots in `runs/3277/shots/` (dev) and `runs/3278/shots/` (production), at 1280 and 390.
- **Tests on the branch**: `site/scripts/test-ev.mjs` exit 0 (23 checks); `tests/test_session294.py`, 239, 288 and 203 pass; a type check of the changed files exit 0.

## Decisions made without you

- **Session numbers 3275 to 3278, queue file 198.** The first free number at or above 2320 is 2399, but it stands alone: 2400 to 2405 are held (`wip/2400-policy-games`). The next gaps (2998 and 2999; 3024 to 3039; 3190; 3234 to 3260) are too short or reserved by other chains' files, so the chain took the first four free in a row, 3261 to 3264, and file 197 (`9d8521932`). Minutes earlier chain 192 had pushed `queue/next/197` reserving fourteen from 3261, so the file moved to 198 and the sessions to 3275 to 3278 (`fdc0fea6e`), the first four free after that block.
- **The page is reworked in place, not built again.** An EV game already stood at `/play/ev` (session 294, in the menu). The prompt's `/learn/ev` "or the Games path the menu uses" reads as this one page; a second address would split the game.
- **Sources move from beside each figure to hover tips.** Session 2402 had written every source in words beside its figure on this page; the owner's rule in this chain's prompt (explanatory text only as hover) governs now. The sourced table for the parents and the print button stay, folded under the results.
- **The page opens on the United States as a whole**, so a student sees a full result at once and the server's page carries the keyed figures.
- **No public charging price is invented.** The warehouse holds none (`coverage.csv`: AFDC station counts only). Home charging defaults to 100 percent; below it the family types a charger's price and the results wait until then.
- **The 5 percent keeps its place; its hover says what OMB's rates are.** Neither OMB nor Lazard gives 5 percent: OMB Circular A-94 Appendix C (revised 6 March 2026, read 6 November 2026) gives 3.6 percent nominal on a 7-year Treasury note and 3.7 on a 10-year, 1.4 and 1.6 real. Lazard's figure was not read. The hover calls 5 percent "a round rate the game chooses" and gives OMB's beside it.
- **The chart is not discounted**, so its lines cross at the payback year; the NPV is discounted. The chart's hover says so.
- **The check-values figures come from the game's own file**, `data/ev_prices.json`, as the severance keys do: the two EIA tables are not in the live set. The file is from 15 October 2026 (July 2026 electricity, the week of 5 October gasoline); this laptop holds neither table, so it was not rebuilt.
- **The AccessLint MCP tool was not loaded on this machine**; an axe-core 4.13.0 run (WCAG 2.2 A and AA, the levels AccessLint audits) through the repository's own `browser.mjs` stood in for it.
- **The local look used `next dev --webpack`** with `node_modules` linked from `erw-2254` (same lockfile; this checkout's is empty). Dev mode cannot hydrate under the site's CSP (no `unsafe-eval`), so the interactive checks ran on the gate's production build.

## For Samuel's ruling

- **The discount rate.** 5 percent is the game's choice. OMB's 2026 rates for constant-dollar flows such as these are 1.4 to 1.6 percent (real), 3.6 to 3.7 nominal. A lower rate raises the NPV: household 1's $5,131 at 5 percent is $5,730 at 3.6, $6,683 at 1.6 and $6,785 at 1.4 (`lib/ev.ts`). Keep 5, take OMB's real 7-year 1.4, or cite Lazard (not read here)?
- **What the model leaves out** (the NPV's hover names the first five): maintenance and repairs, insurance, a home charger, state and utility incentives, registration fees, resale value, and any change in prices over the years.
- **A public charging price.** Should the warehouse hold one (a source to be chosen), so the home share can have a default other than 100 percent?
- **The prices file is three weeks old.** A data machine's run of `site/scripts/build-ev-prices.mjs` refreshes it.

## To finish

- The gate's clean copy `C:\Users\samen\Documents\erw-land-9d62cfe3` is still on disk: its paths are too long for `git worktree remove`, and this session's shell refused the long-path removal. From PowerShell: `Remove-Item -LiteralPath "\?\C:\Users\samen\Documents\erw-land-9d62cfe3" -Recurse -Force`. It holds no branch and no link out (git no longer lists it as a worktree).
