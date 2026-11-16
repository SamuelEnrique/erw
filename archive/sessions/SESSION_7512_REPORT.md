# Session 7512 report: "The shoulder hours" (`/shoulder`) read as the reader it is for

Chain 304, part B, samueloldlaptop (code role), 16 November 2026, unattended. Branch `wip/7503-shoulder` (worktree `erw-7503`), stacked on session 7503's work, not pushed. Model spend USD 0. The read: `docs/reviews/shoulder-read-2026-11-16.md`, 18 rows.

## At the top

- **California's two sources give two answers for the same month, and nothing on the page set them together.** August 2025 needs 3.63 hours by EIA-930 and 4.65 by CAISO's own data; the shoulder's MWh are 28 to 42 percent higher by CAISO's own data in each of the six months both hold. The cause, found on the rows: EIA-930's demand counts the batteries' charging and the sum of CAISO's sources does not (August 2025: a gap of 42,466 MWh a day, 42,433 MWh charged). Since December 2025 only the second source is held, and by it the more the fleet charges at midday the more hours the page says it needs. The page now shows both side by side; which demand the measure stands on is ruling 1.
- **A month the grid does not hold opened another month with no word.** `/shoulder?grid=caiso&month=2026-04` showed November 2025. Fixed: the page says what was asked and links the source that holds it.
- **The "worst days" are the largest swings, not the hardest evenings.** All ten of ERCOT's 2025 are October to February days whose evening peaks (40,269 to 58,028 MW) are below the average August day's (61,192 MW). Ruling 2.
- **Nothing was changed outside this tool's files.** No other page's code, no shared component, no table. Two disagreements with the lab desktop's pages are rows for the data machine (the fleet's freshness against `/storage`, three months of curtailment against `/curtailment`).
- **The replication on the changed page, every view:** 21,353 of 21,354 inside the tolerance, the same one rounding edge named, 0 differ (the page draws 720 more figures than part A's 20,634). Part A's committed figure files are of its page; its data request row 1 rewrites them.

## The reader and the five cases

- **The reader:** a fund analyst testing the claim that four hours of batteries is enough for the evening, in Texas and California. Why: every figure is the whole grid's and the whole fleet's; no price, no node, no single battery.
- 1. ERCOT, August 2025 against August 2023: 5 hours and 4.30 hours needed (fleet 11,046 MW at 1.52 hours) against 4 hours and 11.75 (3,184 MW).
- 2. California, April 2026 against April 2024: 3.27 hours needed (CAISO's own data, 15,979 MW) against 4.13 (EIA-930, 8,978 MW): two sources.
- 3. The worst day of ERCOT's 2025: 31 January, 7 hours from 17:00, 118,152.54 MWh above its mean, 13.86 hours needed; mean 26,784 MW, evening peak 46,346 MW.
- 4. Texas, the months lowest before dawn (August 2023, May 2024): the shoulder is not moved; "the midday surplus" is mostly the night's (part A's row 7).
- 5. California, August 2025 by its two sources: 3.63 against 4.65 hours needed on the same fleet.

## The rows by kind (18)

- **site, 9, all fixed with a test:** rows 1 to 6 and 8 to 10.
- **data machine, 3:** rows 7, 15, 16 (below).
- **ruling, 5:** rows 11 to 14 and 17 (below).
- **browser, 1:** row 18 (three ready rows below).
- license, key: none.
- Cited from part A and not written again: its rows 7, 10, 11, 12, 13, 14.

## What was fixed (all on `/shoulder`; nothing the page had is dropped)

- Row 1: one line above the summary when the address names a grid or a month that is not held, with a link to California's other source when it holds the month (`notShown` in `site/lib/shoulder.ts`).
- Row 2: the months' chart's hover ends with the month's hours needed.
- Row 3: the first chart's note writes net load's daily mean (a row with its check key).
- Row 4: "not held hours" gone: where the batteries' output is not held the words say so.
- Row 5: a section "California's two sources, side by side" on both California grids: six months, two sources, seven figures each, all rows of the table; the tip says what is the same and why the rest differs.
- Row 6: two columns in the ten days' table, the day's mean net load and its evening peak.
- Row 8: the second headline's note says whether the hours needed are less or more than the hours the fleet holds.
- Rows 9 and 10: both links to the battery page carry the grid shown; "What this cannot see" opens with "A price" and what that page holds, read from `site/lib/batterystack.ts`.
- `docs/methods/shoulder.md` completed for the new figures (section 3, section 7); `site/scripts/shoulder-figures.mjs` and `replication/shoulder/replicate.py` read the hover's new figure.

## Tests

Each in its own process, one at a time, output under `runs/s7512/`, exit code read.

- `node --import ./scripts/tsx-register.mjs scripts/test-shoulder-read.mjs` (new): 40 of 40. It draws 12 views on real rows (`tests/fixtures/session7512`, 1,367 rows copied from the table: the cases' months).
- `tests/test_session7512_shoulder_read.py` (new): 4, pass (runs the Node check; the review's form; the figures it quotes against the fixture; no dash).
- `tests/test_session7503_shoulder.py`: 14, pass (the replication on the changed page among them).
- Files that name the page's files: `test_session78` 18 (3 skipped), `80` 15 (5 skipped), `90` 26 (1 skipped), `92` 28 (15 skipped), `241a` 17: pass.
- Files that walk every method note: `test_session142` 42, `147` 65, `158` 58, `160` 40, `199` 7: pass.
- `scripts/test-usage.mjs`: 16 passed. `scripts/check-methods.mjs`: 544 of 544.
- A type check of `app/shoulder/page.tsx` and `lib/shoulder.ts` alone (`tsc`, a scratch config, removed): exit 0.
- The replication on all 193 views of the changed page, against the main copy's tables (read only): 21,353 of 21,354, 1 named, 0 differ.
- Not run: the site build, the full suite, `check-shoulder.mjs` and `check-values` (they need a built site).

## What to review

Once the branch has landed (in review: the internal view).

1. `https://erw-flame.vercel.app/shoulder?grid=caiso&month=2026-04`: a boxed line above the summary: "April 2026 is not held for CAISO by EIA-930, which holds 81 months from January 2019 to November 2025, so November 2025 is shown. CAISO by its own data holds it: April 2026, CAISO, its own data." Click the link: April 2026 opens, 3.27 hours needed.
2. On that view, the second headline: "... would take 3.27 hours, less than the 3.43 hours it holds."
3. Scroll to "California's two sources, side by side": twelve rows, June to November 2025; August 2025 reads 3.63 (EIA-930) and 4.65 (CAISO's own data) under "Needed, h". Hover the "i": the tip names the batteries' charging.
4. `https://erw-flame.vercel.app/shoulder?grid=ercot&month=2025-08`: under the first chart, "the dashed line is net load's daily mean, 46,901.84 MW". On the second chart hover August 2023: "shoulder 4 hours; fleet covers 1.37; hours needed 11.75". In the ten days' table, 31 January 2025 has "26,784.21" and "46,346" in the two new columns.
5. `https://erw-flame.vercel.app/shoulder?grid=ercot&month=2023-08`: the third headline of the worst days ends "the batteries' output in those shoulders is not held for ERCOT in 2023."
6. Any view, the fold "What this cannot see": the first line is "A price." and its link opens the battery page on the grid shown; so does the lead's "what a battery earns".
7. `https://erw-flame.vercel.app/shoulder?grid=pjm`: 'Grid: "pjm" is not held here (ERCOT; CAISO; CAISO, its own data are), so ERCOT is shown.'

(The figures are of this machine's table of 4 October; the site's newer copy moves the opening month, not these months' rows unless EIA revised the fleet.)

## Data request rows

| Requested (UTC) | Session | Table or file | What, exactly | Source | State |
|---|---|---|---|---|---|
| 2026-11-16 12:40 | 7512 | `shoulder_hours_monthly`, `iso:caiso_own` (demand, net load and every measure built on them); `docs/methods/shoulder_hours.md`; `known_data_faults` | The demand of `iso:caiso_own` is the sum of CAISO's sources with a charging battery as a negative source, so it leaves the fleet's charging out; EIA-930's demand (`iso:caiso`) counts it. On the average day of August 2025 the two demands differ by 42,466 MWh and the batteries charge 42,433 MWh (June 40,282 against 40,957; November 31,939 against 35,628). Asked: (a) the note states this with the six months' figures, and a row in `known_data_faults` names it; (b) on the owner's ruling 1 of session 7512, a second set of variables for one of the entities on the other's definition of demand, so that one California series runs across December 2025. No figure is wrong by the table's own rule | `docs/reviews/shoulder-read-2026-11-16.md`, rows 5, 7 and 13; `runs/s7512/q5.py` reads it from the table | requested |
| 2026-11-16 12:40 | 7512 | `shoulder_hours_monthly` against `storage_buildout_monthly`, in the warehouse and in the live set; `warehouse/run_daily.sh` | `run_daily.sh` builds `storage_buildout` and not `shoulder_hours`, and no workflow names the builder. Asked: (a) for every month, `fleet_mw` and `fleet_mwh` of the shoulder table beside `battery_operating_mw` and `battery_operating_mwh` as loaded now (on this laptop's copies of 3 and 4 October: 188 of 188 months equal); (b) `warehouse/derived/shoulder_hours.py` run in the daily sequence after `storage_buildout`, or a check that fails when the two differ | row 15; part A's faults row 13 | requested |
| 2026-11-16 12:40 | 7512 | `curtailed_mwh_per_day` of `iso:caiso_own`, March, August and September 2026, against `site/data/curtailment/shares.json` (`grids.caiso.months`) | March 2026: 24,981.1253 MWh a day in the shoulder table; 709,508.93 MWh over 30 of 31 days in the shares file (23,650.30 a day). August: 4,997.971 against 148,546.848 over 30 of 31. September: 5,554.3153 against 163,505.332 over 29 of 30. The other 94 months both hold agree. Asked: which days each takes in a month that lacks one, and one rule for both | row 16; `runs/s7512/q3.py` | requested |

**For the desktop's tool (`/curtailment`):** nothing in its code was read as wrong. Its month figure for California in March, August and September 2026 stands on fewer days than `/shoulder`'s MWh a day (the third data request row); if the shares file's rule is the right one, the shoulder builder follows it, and if not, that page's "30 of 31" months change.

## Browser read rows

| Asked (UTC) | Session | Branch | Address | What to look at | What should be seen | State |
|---|---|---|---|---|---|---|
| 2026-11-16 12:40 | 7512 | `wip/7503-shoulder` | `/shoulder?grid=caiso&month=2025-08` at 1280 and 390 | The section "California's two sources, side by side": the table, and the "i" after its first sentence, hovered and tapped | Twelve rows; the row "August 2025, EIA-930" on the beige ground and bold; at 390 the table scrolls inside its own frame and the page does not scroll sideways, with the tip open too (it is 288 px wide and opens from the mark's left edge, which here falls at the end of a sentence) | wanted |
| 2026-11-16 12:40 | 7512 | `wip/7503-shoulder` | `/shoulder?grid=ercot&month=2025-08` at 1280 and 390 | The table of the ten days (twelve columns now, at least 920 px); the second chart, hovering August 2023; the note under the first chart | The table scrolls inside its frame at both widths; the hover reads "August 2023: shoulder 4 hours; fleet covers 1.37; hours needed 11.75"; the note's "46,901.84 MW" does not break badly at 390 | wanted |
| 2026-11-16 12:40 | 7512 | `wip/7503-shoulder` | `/shoulder?grid=caiso&month=2026-04` at 1280 and 390, signed in and as a visitor | The boxed line above the summary and its link | Signed in: the line, and the link opens `/shoulder?grid=caiso-own&month=2026-04`. As a visitor: the in-review page, as for every address of this page | wanted |

## Landing request

- **Head:** the commit that holds this report on `wip/7503-shoulder` (read it with `git log -1` in `erw-7503`); it is stacked on session 7503's commits, so one landing carries both.
- **Tests:** `site/scripts/test-shoulder-read.mjs` 40; `tests/test_session7512_shoulder_read.py` 4; `tests/test_session7503_shoulder.py` 14; with them the ten python files and two node scripts under "Tests", all passing here. The landing machine runs the full suite and the build: neither was run here.
- **What changes:** `/shoulder` only: a line when the address asks for what is not held; a clause in the second headline's note; a figure in the first chart's note; one more figure in the second chart's hover; two columns in the ten days' table; words in place of "not held hours"; a new section on the two California grids; one bullet in "What this cannot see"; the grid on two links. `site/lib/shoulder.ts` gains three exports. The method note `docs/methods/shoulder.md` (its page `/data/methods/shoulder`) gains four passages. A new fixture, two tests, one review.
- **What does not:** no table, no builder, no connector, no workflow, no page file a builder writes, no shared component, `site/lib/release.ts`, `site/lib/batterystack.ts` (read, not changed), no other page.
- **check-values:** the page draws more checked numbers a view (the mean, the two day columns, the two sources' 84 figures on a California view); each is a row of `shoulder_hours_monthly` under the same key form, so the floor can only rise.
- **The snapshot:** `/shoulder` and the methods pages are in review and none is among the 25 addresses read as a visitor: no difference is expected on any.

## Needs the key

None. No step of this read needs a model.

## Decisions made without you

- The reader is a fund analyst, not the merchant developer or the planner the prompt also offered: the page has no price, node or single battery.
- California's two sources were set side by side in a new section (rows of the table only), not merged and not adjusted.
- Part A's row 12 (two views side by side) was not reopened: the months' hover got the hours needed instead, which answers "and the same month two years before" on one view.
- The price page's facts on this page are read from its own library, not typed, so they follow it.
- The fixture is a new file of real rows (four columns of the table), not an extension of part A's: its months are other months.
- The whole replication was run on the changed page against the main copy's tables, read only; part A's committed counts were left as they are.
- From the coordinator's word in mid-session (no permission prompt to be raised), every command was one short step and every script a file under `runs/s7512/`.
- A fix not made: the fleet's MW written without decimals as `/storage` writes it (row 14), because it would move the replication's committed text and sit on a tolerance edge.

## For Samuel's ruling

1. **Which demand California's shoulder stands on.** EIA-930's demand includes the batteries' charging; CAISO's own does not. On the second, the only one after November 2025, the shoulder's energy is 28 to 42 percent higher for the same month, and grows as the fleet charges more at midday. Default taken: both stay, shown side by side, the page naming the difference.
2. **What "the worst days" should rank.** Today: the ten days with the most evening energy above the day's own mean, which are winter days of large swings, none with a high evening peak. A reader testing adequacy would expect the highest evening net load. Default taken: the rule and the word stay; each day's peak is now in its row.
3. **Hours needed for a battery of 2, 4 or 8 hours.** Today the figure is the whole fleet's at its own MW, so it falls as the fleet grows. Default taken: nothing added; a figure by duration would be new rows of the table.
4. **The fleet's MW with or without decimals.** `/storage` writes 13,909, this page 13,909.30. Default taken: not changed.
5. **A mark on the "Midday surplus" column of the yearly table for Texas 2019 to 2024**, where most months' lowest hour is before dawn. Default taken: none added; it goes with part A's ruling 2.
