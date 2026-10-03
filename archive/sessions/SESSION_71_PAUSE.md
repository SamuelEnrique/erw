# Session 71: paused

Energy Research Warehouse (ERW), session 71, paused at Samuel's request on 2026-10-03 at about 04:05 UTC. **Model spend: USD 0.00.** No pull, no model call, no Supabase or Redivis write, no force push. The data lock was never taken (it is free). The `task/071-presend` branch has **not** been pushed, so nothing is merged or deployed. A copy is on `origin/wip/071-presend`, a branch name no workflow runs on.

The local site server (`npm start` on port 3000) was stopped. Logs and screenshots are in `runs/` (not in git): `runs/s71_*.out`, `runs/s71_shots/`.

## Done (committed on `task/071-presend`)

| Commit | What |
|---|---|
| `8795c42` | **Part C:** session 68's "The push and production" section, cherry-picked from `e86d701` (local `task/068-network`) |
| `28c825e` | **Part A:** the battery page leads with the last twelve months: the summary sentence, the first headline number (USD per kW, with the US dollars beneath), the income table's first column, and the contract's market lines. The bad month is the 10th percentile of the last 36 months. The income table has four spans: last twelve months; average of the last three full years; average of every year held; the same average without the month that is more than a quarter of everything held. The upper-bound sentence sits directly under the chart, not folded. The box under the summary is removed. New stats in `lib/batterystack.ts` (`l12_kw`, `l12_share`, `p10_36`, `n36`, `y3`, `y3_kw`, `avg_without`, `avg_without_kw`). The outlier threshold is now "more than a quarter" (was a fifth). |
| `aef8dd6` | **Part B:** home page. Tools in review are named once in an "In review" section near the bottom, greyed and not links (links in the internal view). Audience sections show only their live cards. The tour button and the price-board and digest links to pages in review are dropped while those pages are in review. `SiteLink` gains `gate="quiet"` (greyed, no label) and `gate="plain"` (plain text, no label). `Cite` table names use `plain` site-wide. |
| `041b21f` | Column labels say USD. `test-battery-stack.mjs` and `check-battery-production.mjs` follow the new page. `docs/methods/battery_stack.md` gains "How the page reads the tables (session 71)". |
| `f28e16a` | Income-table columns become a short title with the span beneath, so the table fits at 1280 px. A one- or two-card audience grid is sized to its cards. The browser test checks the fit. |

**The new summary sentences (4 hours, perfect foresight, local build):**
- ERCOT: "Over the last twelve months a 100 MW, 4-hour battery in ERCOT earned USD 81.40 per kW, 33 percent of it from ancillary services, and covered its debt 0.88 times."
- CAISO: "Over the last twelve months a 100 MW, 4-hour battery in CAISO earned USD 78.90 per kW, 43 percent of it from ancillary services, and covered its debt 0.84 times."

**ERCOT 4 hours, total per kW by column:** 81.40 (Oct 2025 to Sep 2026); 255.08 (2023 to 2025); 614.58 (every year held, Jan 2018 to Sep 2026); 269.68 (without Feb 2021, which is 57 percent of everything held). **CAISO 4 hours:** 78.90; not held (CAISO holds one full year, 2025); 89.11 (Sep 2024 to Sep 2026); no fourth column (no month above a quarter).

## Local checks on the final build (`f28e16a`)

| Check | Result |
|---|---|
| `python -m unittest discover -s tests` | 328 tests, OK, exit 0 |
| `pytest package/tests` | 408 passed, 32 skipped, exit 0 |
| `npx tsc --noEmit` | exit 0 |
| `npm run build` | exit 0 |
| `check-routes` | exit 0: pass 1, 74 of 74; pass 2, 14 live and 60 in review asked, 0 failed |
| `test-battery-stack.mjs` | 66 assertions pass, exit 0 |
| `check-values` | **not yet passed.** Run 1 (01:45): 6,618 of 6,657 match; 39 fail, all `latest_prices` on `/` and `/prices` (the 15-minute timing issue from session 67). Run 2 (02:02, in one window): 6,624 of 6,657 match; 33 fail, all `latest_prices` on `/prices` (that page had not regenerated). Run 3 (02:17, after `runs/s71_fresh.mjs` confirmed both pages fresh): hung for about 70 minutes, then `check-values FAILED: fetch failed`, a network error and not a value result. **Every battery value matched in runs 1 and 2.** |

## In progress when paused

The third `check-values` run. It has finished, with the network error above, and no file was left half-written.

## Left

1. **check-values inside one window.** Restart the local server on the final build. Then run `bash runs/s71_window.sh > runs/s71_window.out 2>&1; echo "exit=$?"` and read `check-values exit=` in `runs/s71_window.out`. The script waits for the next `latest_prices` update, waits until `/` and `/prices` show it (`runs/s71_fresh.mjs`), then runs `check-values`. If the machine is idle or asleep, the run stalls, as run 3 did.
2. **Push `task/071-presend` once** (`git push origin task/071-presend`). This merges to main and deploys. Then run the production checks: `node site/scripts/check-battery-production.mjs https://erw-flame.vercel.app` (12 combinations; the summary must begin "Over the last twelve months") and the home page as a visitor (`test-battery-stack.mjs` against production covers it).
3. **Part D (the game).** After step 2's merge, run session 70's "To finish" in `C:\Users\samen\Documents\erw-game`. **Known before running:** `git merge-tree` shows the game branch conflicts with main in one place: the link import at the top of `site/app/play/battery/Game.tsx`. Main has `import { SiteLink as Link } from "@/components/SiteLink";` (session 67); the game branch keeps `import Link from "next/link";` and adds a comment block above it. As written, step 4's workflow merge would fail on that conflict. My planned decision was to run `git merge origin/main` on `wip/066-battery-game-v4` before step 1, keep main's import and the game's comment, rerun step 3's tests, then follow the steps. The game branch adds no new route, so `site/lib/release.ts` needs no entry and `/play/battery` stays `review`. Step 6's live checks hit the in-review page as a visitor, so run them on a local build of main with the internal cookie, and on production only if the unlock link works.
4. **Part E.** Test `https://erw-flame.vercel.app/internal/unlock?token=<INTERNAL_COSTS_TOKEN from .env>` and report whether it still answers 404.
5. **Write `archive/sessions/SESSION_71_REPORT.md`** as the prompt specifies.

## Decisions so far (for the report)

- **Outlier rule:** the threshold is now "more than a quarter" of everything held, to match the prompt (session 67 used a fifth). Only ERCOT's February 2021 qualifies, at every duration and under both strategies (56 to 62 percent).
- **"From the market after the contract ends"** now also uses the last twelve months, with the every-year average beside it. The prompt named only the uncontracted-share line, but the old line would have led with the Uri-weighted average.
- **Table units:** the income table stays in US dollars for the reader's size, with a last row, "Total, USD per kW", that carries the 614.58 and 269.68 figures.
- **The 36-month window** ends with the last twelve months' last month. CAISO holds 25 of those months, and the page says so.
- **Citation lines are plain text site-wide**, because `Cite` is shared.
- **Home page:** the price board, gas and oil, digest items and status strip stay. Only their links to pages in review are removed, and those pages are named in "In review".

## For Samuel (so far)

1. **The home page's "Open now" strip still shows the battery as "An average year" (USD 61.46 million, Uri-weighted).** The prompt said the live tools stay as they are, so I did not change it. It contradicts the battery page's new lead. It is one line in `site/app/page.tsx` (`OpenNow`, and the `bs|...|avg:total` read in `liveNumbers`).
2. **The site footer still carries "Data and methods" with an "in review" label** on every page. It was not in Part B's list.
