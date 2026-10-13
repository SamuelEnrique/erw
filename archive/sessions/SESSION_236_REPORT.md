# Session 236 report: "What a datacenter pays" on the brand, for a buyer of power

13 October 2026, from 06:27 UTC, unattended, one session of the overnight chain of 12 to 13 October, on the old laptop (`samueloldlaptop`, a code machine). Worktree `erw-190`, branch `wip/236-datacenter`, from `c78835d4`. Not pushed and not landed: the landing is the orchestrator's. Model spend USD 0. Pulls: none from a publisher; the live set in Supabase read with the public key (the site's own reads, and one probe of the catalogue). No warehouse data written. No em dash in anything written.

## Read these first

- **Not green at the hand-back: `check-values` on the final build, 471 of 477.** The six are the hourly carbon window of "How clean?" on the two default addresses. The live set's hourly carbon table grew during the session (another hand's load) and the build served its cached read; the same code was 477 of 477 half an hour earlier. The restart on an empty cache could not be run: the build mutex was session 237's from 07:35 to past 07:57 UTC. Section "The live set moved during the session", and "To finish" for the one command.
- **The page is on the brand.** `/cost-of-power` is wrapped in `<Brand noUsage>` as the battery page is. No rule was added to `app/tokens.css` and no shared component of the brand was changed (`ToolPage.tsx`, `ScenarioBlock.tsx`, `tokens.css` are untouched). The page writes no color and no font of its own: the legend and the view switch name tokens, and the cost chart reads its colors and its text face at its own box.
- **One shared file changed, additively: `site/components/echarts.ts`.** `token(name, from?)` and `baseStyle(from?)` take an optional element; without it they read the page's root, as every other chart does. Session 235 works beside this session: if it touched the same two functions, merge both.
- **The battery page did not move.** Its 47 checked numbers are identical to session 211's (`diff` 0 lines) and its height at 1280 px is 5016 before and after.
- **Every number that was on the page is unchanged.** 57 of 57 checked numbers identical on the default page at 1280 and at 390 px, 19 of 19 on CAISO's, and the 25 results cells and bars identical for the flat load and for the load off in 100 hours. 17 numbers are new: the 16 delivery figures and CAISO's notices in its table's own last twelve months. `docs/brand/review-236/numbers_before_after.txt`.
- **The four questions stay, in their order**, then the two of the decisions: What will it pay? Will the power be there? How clean? How soon? Which option is better? What matters most.
- **A and B compare two sites or two contracts.** The block has a title of its own, "Scenarios A and B: two sites, or two contracts", one line of how to use it, and a list "Scenario B's site": any zone or hub of any grid the page holds (`bsite=<grid>:<region>` in the address). B's column, "B against A" and B's chart then read that site; A's column and the headline do not move. Each of the three other answers adds B's site in one sentence. With no site named, B is at A's site and the page is what it was. The contract's share and price were already two assumptions of each scenario.
- **Scarcity.** USD 1,000 per MWh stays the level for every grid and is stated in a table under the three numbers ("the two counts"). The grid's own signal is its second row: CAISO's notices, two counts each with a check key; for ERCOT one line, "ERCOT's own signal, its reserve adders, the price adders of its operating reserve demand curve, is coming: the warehouse holds no table of them yet, so no second count is stated"; for NYISO, ISO-NE and SPP "not held".
- **ERCOT's reserve adders are not in the live set.** The catalogue was asked on 13 October at 06:29 UTC for a table named for adders, the demand curve, reserves, scarcity or shortage: none answered (`runs/session236/probe.out`). `coverage.csv` names none either.
- **The delivery charges.** One row a component (transmission, distribution, other riders) and "Total delivery", a column a utility, in USD per MWh for a flat load. For 100 MW: Oncor 8.58, 0.48, -0.24, total 8.81; CenterPoint 6.92, 0.83, -0.08, total 7.67; AEP Texas 8.16, 0.23, 0, total 8.39; Texas-New Mexico Power 7.06, 0.03, 0, total 7.10. The 41 tariff lines, each with its schedule's name and rate as filed, are the table `delivery` of `tables.csv`; none is on the page.
- **"The total must equal what the page shows today" could not be met as written: the page showed no total.** It showed one figure per MWh, "the transmission factor alone", for two of the four utilities (Oncor 8.58, AEP Texas 8.16). Those two are the transmission row, unchanged. The distribution row, the other riders, the totals, and CenterPoint's and Texas-New Mexico Power's transmission figures are new arithmetic of this session, on rates the file already held. See "For Samuel's ruling", 1.
- **Seven tests of the branch were red at this session's first run, on files it had not yet touched**: six of `tests/test_session190_replication.py` (session 228 extended the Stata do-file and its mirror and left session 190's pins where they were) and one of `test_session215` (the check prefix `dc`, since the branch was merged with main). All are green now; one real finding among them, below.

## The live set moved during the session

- Between 07:03 and 07:33 UTC the live set's `carbon_intensity_hourly` for ERCOT grew from the 33 days session 228 saw to 10,144 hours, 9 August 2025 to 9 October 2026 (`runs/session236/probe2.out`). This session wrote no table; it is another hand's load.
- The final build's page still showed the cached read (776 hours, 346.71 kg per MWh), so `check-values`, which reads the live set itself, failed 6 of 477, all `co2:window:*` on the two addresses (the live set: 10,144 hours, flat and grid 313.05, flexible 312.31). The first run, half an hour earlier on the same code, was 477 of 477.
- The remedy is the rules file's: remove `site/.next/cache/fetch-cache`, restart, run `check-values` twice. The cache was removed; the restart waited for the build mutex from 07:37 to 07:57 UTC, which session 237 held (two cycles, the second from 07:46), and this session's time was up. **`check-values` is therefore not green on the final build as handed over**; nothing in this session's code reads that table differently from session 228's, and the first run shows the code and the live set agreeing.
- **What this leaves on the page:** session 228's sentence under "How clean?" says "the hourly table holds the last 35 days", and the method note, 4.16, says the same. With the live set as it now stands that is no longer so. Not changed here (no time for another build): one line each. "To finish".

## What to review

1. The screenshots: `docs/brand/review-236/` (`README.md` says what to look at).
2. After the landing, in the internal view (https://erw-flame.vercel.app/internal/open first):
   - https://erw-flame.vercel.app/cost-of-power
   - https://erw-flame.vercel.app/cost-of-power?bsite=caiso:TH_SP15_GEN-APND (two sites)
   - https://erw-flame.vercel.app/cost-of-power?grid=caiso (CAISO's notices as the second count)
   - https://erw-flame.vercel.app/cost-of-power/tables.csv (the tables `delivery` and, with `bsite`, `scenario_b_site`)
   - https://erw-flame.vercel.app/cost-of-power/battery (unchanged)
3. On the old laptop: `cd site`, `npm run build`, `npx next start -p 3236`, http://localhost:3236/internal/open, then http://localhost:3236/cost-of-power .

## What was done

1. **The brand** (`page.tsx`, `LoadCharts.tsx`, `components/echarts.ts`): the wrapper; the legend's four colors and the view switch's two are tokens; the chart reads the tokens and the text face in force at its box. The notes of the cost table are `div`s, so that the brand's own rule "words in a cell are text" reaches them (as `span`s they were set in the figures' face).
2. **Delivery** (`lib/datacenter/delivery.ts`, new, pure; `DeliveryTable` in `page.tsx`; `tables.csv/route.ts`): a rate per kW or kVA a month times 12,000 over 8,760; a rate per kWh times 1,000; a rate per account a month times 12 over MW times 8,760. Three lines that apply only to some loads by the tariff's own words are not added and are said. Check keys `dcd|<MW>|<utility>:<component or total>`, recomputed by `check-values.mjs` from the site's file.
3. **Scarcity** (`LoadAnswers.tsx`, `lib/datacenter/answers.ts`): the table of the two counts; `notices.own`, the notices of the twelve calendar months ending with the table's newest notice (May 2024 to April 2025: 41, of which 20 transmission emergencies, 20 restricted maintenance operations, 1 EEA watch), because CAISO's table ends on 30 April 2025 and holds none of the page's twelve months. The page says that its 0 for those months "is not a count of none".
4. **Two sites** (`model.ts` `siteBOf` and `facts.b`; `LoadScenarios.tsx`; `LoadSiteB.tsx`, new; `finance.ts` `SITE_B`, carried by "Your load" with the scenarios' parameters): B's two ways are computed as A's are, from that site's own files over its own last twelve months. Default against SP15 in CAISO: USD 33.73 per MWh in A, USD 28.58 in B; a year's energy USD 29.55 million against USD 24.97 million.
5. **The method note** (`docs/methods/datacenter_pays_algorithm.md`): 4.6 and 4.15 amended, 4.18 (delivery by component) and 4.19 (scenario B's site) new.
6. **The checks**: `check-datacenter-scenarios.mjs` section 12 (23 assertions: the brand, the level, each grid's own signal, the sixteen delivery figures against the library, B at another site, 390 px); `check-values.mjs` the key `dcd`; `tests/test_session236.py` (22 tests, with a second computation of the delivery figures in Python).

## Checks, with exit codes

None piped; outputs under `runs/session236/` (`before_*`, `after2_*`). Each cycle held the build mutex once.

| Command | Exit | Result |
|---|---|---|
| `npx tsc --noEmit`, first try | 2 | `content/waits.json` is written by the build's first step and a fresh worktree has none; `npm run content` first, then 0 |
| `npx tsc --noEmit`, before, after the first edits, final | 0, 0, 0 | |
| `npm run build`, the same three | 0, 0, 0 | no "statement timeout" line |
| `check-values`, restricted to `/cost-of-power`, before | 0 | 461 of 461 |
| the same, after the first edits, twice (07:02 UTC) | 0, 0 | 477 of 477 |
| the same, final build, twice (07:34 UTC) | 1, 1 | 471 of 477: the six are the hourly carbon window (`co2:window:*`), the live set against the page's cached read; see "The live set moved during the session" |
| the same, the final build restarted on an empty fetch cache, twice | not run | the build mutex was another session's at the hand-back; "To finish" |
| `check-datacenter-scenarios.mjs`, before, final | 0, 0 | 96 of 96 before; 119 of 119 |
| `check-datacenter-face.mjs`, before, final | 1, 0 | 23 of 23 final; before: 4 of 23 failed, the check counted every download link as one of the source line's three (stale since session 213); its two pins moved |
| `check-datacenter.mjs`, `check-how-soon.mjs`, before | 1, 1 | they check the blocks session 213 took off the page (19 failures before any change): they no longer apply and were not run again |
| `check-routes.mjs`, final | 0 | 0 failed (1 live page and 159 in review asked as a visitor) |
| `test-datacenter-finance.mjs`, `test-decisions-195.mjs`, `test-datacenter.mjs`, `test-battery-finance.mjs`, `test-seller-finance.mjs` | 0, 0, 0, 0, 0 | |
| `python -m unittest`, the 33 modules that name a file this session changed, one process each | 0 for each of the 33 | 633 tests; the first run: 3 modules failing (190, 190 replication, 215), below |
| `capture.mjs` on the battery page, `diff` with session 211's numbers | 0 | 0 lines; height 5016 |
| `compare.py`, before against the final build (cached reads) | 0 | no number that stays moved |
| Whole suite in a clean copy; `freeze.py status`; the snapshot | not run | the orchestrator's, at the landing |

Tests whose pins moved, each with a note "session 236":

- `test_session138`: the delivery cell's expression is `lib/datacenter/delivery.ts`'s (`(r.value * 12000) / YEAR_HOURS`); the page still says the charges are never added to the market cost.
- `test_session190`: the same expression, read in the library.
- `test_session215`: the check prefixes `dc` (session 228's, red on the branch since its merge with main) and `dcd` are known; neither reads a held table.
- `test_session190_replication`: six pins of the do-file and its mirror (30 lines printed became 34). Session 190's rules hold on the part before "* Session 228," as they did; the part after it is held to the same rules with its own lists (its three destrings, its recode, its third loop, its ten displays, which the mirror's lines follow in order with the carbon file read).
- `check-datacenter-face.mjs`: the two pins above.

## Decisions made without you

1. **The section's title stays "Which option is better?"** (the owner's words of the chain prompt of 12 October evening, pinned by two tests); the block got a title of its own under it. Reversible: one line.
2. **B's site is one list in the block, read by the server**, not a field the browser computes: a site's prices are the server's files. Choosing a site reloads the page at the same address with `bsite`; the assumptions typed are kept.
3. **B at another site runs the way "Your load" runs and buys in the same market**; only the site differs. B's last twelve months are that site's own and can be other months than A's: "What differs" then names them.
4. **A kVA is counted as a kW** (a power factor of 1), so that CenterPoint's and Texas-New Mexico Power's transmission factors, printed per kVA, have a figure. Until this session they had none.
5. **Every per-kW charge is counted on the load's size, monthly**, as the page already counted the transmission factor; a charge per account is spread over the year's energy for one account with one meter. Texas-New Mexico Power's distribution rider is printed on two lines (per meter and per ESI ID): both are added, as the tariff prints them; together USD 0.02 per MWh at 100 MW.
6. **A total is the sum of the unrounded components, rounded to the cent**, so it can differ by a cent from the sum of the rows shown (Oncor: 8.58 + 0.48 - 0.24 reads 8.82, the total is 8.81). The note under the table says so.
7. **The level's words do not repeat session 228's sentence** that in ERCOT a price above USD 1,000 comes from the reserve adders. The review of 12 October states ERCOT's cap as USD 5,000, so an offer can also be above USD 1,000. The page says: the FERC markets' offer cap; ERCOT is outside FERC with a higher cap of its own; the same level is used there.
8. **CAISO's second count is two rows**: its notices in the page's twelve months (0, with the reason) and in its table's own last twelve months (41). A lone 0 would have read as "no notice".
9. **`<Brand noUsage>` wraps the whole page**, as instructed, so the view switch and "Grid by grid" are inside it: no usage count is taken from them any more.
10. **The Commission's wholesale rate keeps its row in the cost table**, in USD per MWh; the rate per kW as printed moved to the hover and stays in the download.
11. **The do-file's `kg_hours` is `gen double`** and the file ends with one newline: both by the file's own rules, which the moved pins hold. The do-file has still not been run (no Stata on this machine).
12. **No screenshot was taken with a design tool and no audit was run**: the time went to the two sites and the red tests.

## For Samuel's ruling

1. The delivery table's new arithmetic (decisions 4, 5 and 6): keep the three components and the total as computed, or show only what the tariffs let the page state without an assumption (the transmission row of Oncor and AEP Texas).
2. The three conditional lines left out of the sums (CenterPoint's municipal account franchise credit, Texas-New Mexico Power's municipal franchise fees, AEP Texas's nuclear decommissioning rider): left out, or a second total "inside a city".
3. Session 228's sentence on ERCOT's adders (decision 7), which still stands in the method note, section 4.15, and in `answers.ts`'s comment: correct it there too, or keep it.
4. The second count for CAISO on a table that ends in April 2025 (decision 8): keep both rows, or wait for the table to be refreshed on the data machine.
5. B's site as a reload (decision 2) against a second "Your load" panel for B.
6. The cost chart is still ECharts with a legend line; the battery page's is an SVG with direct labels (`docs/brand.md`, section 6). It reads the brand's tokens now; redrawing it is a session of its own.
7. `check-datacenter.mjs` and `check-how-soon.mjs` check blocks that left the page in session 213: retire them, or rewrite them for the download.
8. Sessions 213 and 228's open items stand (the hourly carbon window, `data/large_load_status.json`, the "Grid by grid" switch).

## To finish

- The sentence "the hourly table holds the last 35 days" (`LoadAnswers.tsx`, `data-answer-note="clean"`; the method note, 4.16) against the live set's 14 months of hourly intensity: the ready patch is `runs/session236/patch5.py` (it was applied, passed tests 236, 138 and 190, could not be built for want of the mutex, and was taken out again so that the branch's head is the commit that was built).
- "in 1 hours ... paid USD 114,786 in them" on CAISO's page (session 228's sentence): the singular, in the same patch.
- The commands, from the main copy, with the mutex free: `python runs/session236/patch5.py C:/Users/lossa/Documents/erw-190`, then `bash runs/session236/cycle.sh after3 C:/Users/lossa/Documents/erw/runs/session236/after3.cmds` (it takes the mutex, runs tsc and the build on an empty fetch cache, starts port 3236, runs `check-values` twice on `/cost-of-power`, the captures and `check-datacenter-scenarios.mjs`, and stops the server; results in `runs/session236/after3_cycle.out`). Expected: `check-values` 477 of 477, and three numbers of "How clean?" moved by the live set (the window's hours 776 to 10,144; its flat and grid figure 346.71 to 313.05). The screenshots in `docs/brand/review-236/` show the cached 776.
- Not verified here: the whole suite in a clean copy, and the do-file in Stata.
- The landing: merge `wip/236-datacenter` with session 235's branch (`site/components/echarts.ts` if both touched it), the whole suite in a clean worktree, `npm run build`, the before snapshot as its own command, the push, the after snapshot and the comparison (every page is in review: 0 differences expected on the 25 pages).

## After the hand-back: ERCOT's adders

13 October 2026, 08:45 UTC on, at the orchestrator's follow-up. Worktree `erw-142`, branch `wip/236b-adders`, from `805d88bb` (this session's branch as merged for the landing, with `patch5` and the orchestrator's interim line). Not pushed.

- **The ruling's first branch holds: session 244 landed `ercot_rtm_price_adders` at about 07:05 UTC**, so the line "is coming" is gone and ERCOT's own signal is a second count on "Will the power be there?".
- **The definition, said on the page:** the hours in which the adder of ERCOT's operating reserve demand curve (the on-line adder, `rtorpa_mean`, the hour's mean) was at least USD 100 per MWh. A bare "above zero" would mislead: session 244 found it mostly fractions of a cent.
- **What it covers, said beside the count:** ERCOT published that adder until 4 December 2025 and no longer. Of the page's twelve months (October 2025 to September 2026) the table holds 1,558 hours of it, 1 October to 4 December 2025: the count is of those hours, "not a count of the twelve months". **Default case: 0 hours.**
- **A second row, as for CAISO's notices:** the same count over the last year the adder was published, 5 December 2024 to 4 December 2025: **1 hour** (the hour from 14:00 Central standard time on 30 June 2025, mean USD 412.74).
- **Nothing is spliced.** The reliability deployment adder, which ERCOT's file carries alone since 5 December 2025, is not read, not counted, and the page says so.
- **`review_hold` and the public key.** `review_hold` (`warehouse/supabase/live_set.yaml`) loads a table into Supabase and keeps it out of the catalogue counts a visitor sees (`in_live_set` reads "review"); row-level security lets the public key read it, as every page in review reads such a table (this page already reads `ercot_large_load_status` that way). The page reads the adders through `lib/supabase.ts`'s `rest`, nothing else. Asked with the public key: 200 (`runs/session236/probe3.out`).
- **One thing found: an unbounded read of the table times out.** "The newest hour of `rtorpa_mean`" (a sort with no bound in time) was cancelled by the database's statement timeout, twice. The page's two reads are bounded in time (the hours since the first of the page's months; the hours at or above the level since fourteen months before it), 3 requests in all.
- **Check keys:** `dc|<address>|adders:hours`, `adders:held`, `adders:own:hours`, recomputed by `check-values.mjs` from its own read through the same `readAnswers`.
- **Session 228's sentence, tested with the table** (the method note, 4.15): the default case's four hours at or above USD 1,000 are in January 2026, after the ORDC adder ended, so no ORDC adder made them; the only adder the table holds for that month (reliability deployment) reached an hourly mean of USD 100 in one hour (USD 156.99 on 28 January). The sentence is corrected in the note for the page's months, flagged for the ORDC years (not tested: it needs the hourly prices against the adder), and the comment in `answers.ts` no longer states it.
- **When the count goes:** from December 2026 the page's twelve months hold no hour of the ORDC adder; the row then reads "not held" with the day it ended.

Checks of this change, none piped (`runs/session236/b_cycle.out`, `b0_*` before and `b1_*` after, one hold of the build mutex, 09:20 to 09:30 UTC; the mutex was waited for from 08:49):

| Command | Exit | Result |
|---|---|---|
| `npx tsc --noEmit` | 0 | |
| `npm run build`, before (the four site files stashed) and after | 0, 0 | **one "statement timeout" line in each log**, during the static pages (a static page's read of `series`; `/cost-of-power` is not static). It is in the before build too, so it is not this change's. **Not rebuilt:** a second hold for the rebuild was waited for from 09:30 to 09:35 UTC and the mutex was another session's (`b2_cycle.out`). The landing's build log must be searched for the line; which static page's read it is was not found (the log names only the table `series`) |
| `check-values`, restricted to `/cost-of-power`, twice | 0, 0 | 654 of 654, with the three new keys |
| `check-datacenter-scenarios.mjs` | 0 | 119 of 119 (its ERCOT assertion now holds the two rows and the day the adder ends) |
| `check-datacenter-face.mjs` | 0 | 23 of 23 |
| `test-datacenter-finance.mjs` | 0 | |
| `python -m unittest`, 18 modules that pin the page, one process each | 0 for each | `test_session236` is 23 tests: the adders' test replaces the line's, and one by hand (through node) is new |
| before against after, same hold | | default page: 73 of 73 checked numbers identical, 3 new (`adders:hours` 0, `adders:held` 1,558, `adders:own:hours` 1); CAISO 20 of 20; the 25 results cells and bars identical for the flat load and for off in 100 hours. `docs/brand/review-236/numbers_adders_before_after.txt` |

- Not replicated: the Stata do-file and its Python mirror do not rebuild this count (they read the hourly price file and the carbon file only).
- Changed beside the count: the page's source line names `ercot_rtm_price_adders` for ERCOT, and the download `tables.csv` holds the three figures (`scarce_hours`, row `operator_reserve_adder`).
- The live set as the page now shows it, unchanged by this session: the hourly carbon window is 10,144 hours (9 August 2025 to 9 October 2026), and CAISO's notices in the page's months are 2 where the first hand-back saw 0 (its table was refreshed).

For Samuel's ruling, added:

9. The adder's level. At USD 100 the count is 0 in the covered part of the months and 1 in the adder's last year. Over the same 1,558 hours the hourly mean was at least USD 1 in 8 hours and at least USD 10 in 3. One level, or two rows.
10. Whether a signal that ended in December 2025 should stay on the page past the months it covers, or whether ERCOT's real-time ancillary service prices (the report that replaced it, not held) should be pulled for the count.
11. `warehouse/supabase/live_set.yaml` still says "no page yet" beside `ercot_rtm_price_adders` (two comments): a page in review reads it now. Not edited here (a warehouse file).

## The landing

Filled by the orchestrator.

## The prompt

Session 236 of the chain of 12 to 13 October: "What a datacenter pays (long end 1:30). From wip/213-datacenter-layout with session 228, merged with main. The brand. It serves a buyer of power: its four questions (what will it pay, will the power be there, how clean, how soon) stay, and its A and B compare two sites or two contracts. Scarcity ruling: keep USD 1,000 per MWh for every grid, stated on the page, and add each grid's own signal as a second count where a table is held (CAISO's notices; ERCOT's reserve adders if the data machine's table has landed tonight; else a line that it is coming). The delivery charges: one row per component with its USD per MWh and the total; the tariff lines go to the CSV. Land."
