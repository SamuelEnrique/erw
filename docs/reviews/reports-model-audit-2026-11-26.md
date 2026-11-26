# The deep-dive report library: the two drafts audited as a hostile editor would

Session 10232, 26 November 2026, chain 710 part D, on the old laptop. Read as an editor at an energy publication who has to fact-check each report before it runs and wants to find it wrong. Platform tool 13 (`docs/platform-tools.md`, "Deep-dive report library", partial). The findings audit of 19 November and the engine audit (`docs/reviews/analysis-model-audit-2026-11-26.md`) are about Automated Analysis and are not repeated.

The tool refused the agent's own write of this file ("subagents should return findings as text"); session 10201 saved it from the agent's hand-back, unchanged in substance.

- Nothing changed on main but this file and its evidence folder. No table written, no lock taken, no default moved, no report's state changed (none approved, published, rejected or deleted), no model called (spend USD 0), no request to any live service.
- Each finding has its own branch `wip/audit-reports-<n>`. Branches 1, 3, 4, 5 and 7 change words only and are returned for landing, merged as `wip/audit-reports-words`. Branches 2, 6, 8 and 9 hold a test that shows the finding, not for landing; the fix is Samuel's ruling.
- Evidence: every script and its output in `docs/reviews/reports-model-audit-2026-11-26/`: `r1` to `r5`, the drawing script and its stand-ins, the drawn words of each page on main and on each words branch, the test runs. All run on this machine from the main checkout's tables, which were read and never written.

## In short

- **The numbers are right.** All 246 figures the two drafts print (80 on the shape premium report, 166 on the AI gigawatts report) were drawn with the site's own code from the warehouse's tables and re-done by an independent evaluator of each key: 0 differ, to the digit. The table under the AI report was re-done from its own inputs: 134 of its 149 measures agree to four decimals; the 15 that differ moved because their inputs moved after the table was built on 2 October 2026 (finding 6).
- **The AI report reads four regions and says seven (finding 1).** Since 21 October ISO-NE, MISO and NYISO are held for a license. The page names none of them, prints "not held" in their cells, and draws its five findings from what is left: "energy cost differs by a factor of 1.11" (CAISO to ERCOT), where across the seven it was 2.48 (CAISO to ISO-NE). Fixed in words.
- **The shape premium report ranks its grids on two days (finding 2).** It takes the newest month every hub holds, whole or not: on the copy here October 2026, 48 of 744 hours, where CAISO's premium is -0.38 USD/MWh; on September, the latest whole month, 0.81. The fix moves figures: for ruling.
- **Sentences the rows contradict, on both pages (findings 3 and 4, fixed in words):** "In every hub, the grid's own load paid more" beside CAISO's -0.38; "a summer story" when 2024's largest month was January; "it has shrunk" measured from 2021, in which Uri's February alone was 90.8 percent of the premium; "carbon's gap is the largest of the five measures" when hours at or above USD 200/MWh differ 8.42 times against carbon's 2.88; "in every region but none"; two ties written as a single leader.
- **The AI report leads with a figure its own banner calls high (finding 5, words):** California's import share by EIA's balance, 27.02 percent, is 1.10 points above the pair sums before 16 December 2025 and 12.88 after.
- **A date that moved (finding 6):** the AI table's "largest studied event" was built before the event table gained `cold_2026` on 19 October; rebuilt today, six of seven regions move (ERCOT 8.78 to 31.15 percent). The methods appendix also says what the code does not do (finding 7, words).
- **The license hold takes more than the grids' own data (finding 8), and two charts draw what the rows do not say (finding 9).** Both for ruling.
- **Neither draft is reachable by a visitor, and both say they are drafts.** Each answers 404 without the internal token or cookie, counts every try of the token, is not indexed and is not in the navigation. Neither is wrong in its arithmetic; both are listed for wrong sentences, their state untouched.

## The ground: each file and what it does

| File | What it does |
|---|---|
| `site/app/reports/draft/shape-premium/page.tsx` | Report 1, "What flat load pays": the day-ahead premium by hub for one month, twelve months of real-time premium by hub, ERCOT's months since 2018, each hub's hour-of-day profile, the cautions. Reads `cost_of_power_monthly` and `cost_of_power_hourly_profile` from the live set when opened; holds the hubs of license-held grids (session 383) |
| `site/lib/shapepremium.ts` | The report's period statistics (complete months, count, positive count, mean premium, premium times hours summed), shared with `site/scripts/check-values.mjs` |
| `site/app/reports/draft/ai-gigawatts/page.tsx` | "Where the next gigawatts for AI can come from": seven regions on cost, carbon, stress, connection and imports; five findings, a tally, three readings. Reads `ai_power_regions` from the live set |
| `warehouse/derived/ai_power_regions.py` | The table's builder: one row of measures per region over September 2025 to August 2026; built once, on 2 October 2026; not in the daily run |
| `docs/reports/ai_gigawatts_methods.md` | The AI report's methods appendix (finding 7) |
| `docs/methods/cost_of_power.md` | The cost-of-power method; the AI draft's keys (its last section) |
| `site/lib/license.ts`, `site/lib/supabase.ts`, `site/components/Num.tsx` | The license hold: a table held by grid loses the held grids' rows at the read; a figure whose key names a held row is drawn as "license needed" |
| `site/components/CaisoBreakNote.tsx`, `site/lib/caisoJoin.ts` | The banner on the AI report: California's import balance reads high from the join of 16 December 2025 |
| `site/scripts/check-values.mjs` (`INTERNAL`) | Opens both drafts with the internal cookie and checks every keyed figure against the live set |
| `site/lib/guard.ts`, `site/lib/thesis/server.ts` | The token gate: a try with the token in the address is counted; the internal cookie also opens the drafts |

There is no `/reports` index page and no builder for the reports: the library is these two drafts, each a page that computes its figures from tables when opened.

## How the figures were re-done

- **Drawn with the site's own code** (`draw.mjs`, `register.mjs`, `stub.mjs`): both pages rendered by `react-dom/server` through the site's TypeScript loader; every live-set read answered from the main checkout's CSVs as PostgREST would answer it; the token gate opened with a stand-in token; every other read refused and listed. No build, no server, no browser.
- **Re-done independently** (`r1_keys.py`): each figure's key evaluated from the CSVs by its own code, with no import of the site or the builders: 246 of 246 equal.
- **The choices and claims restated** (`r2_claims.py`); **the AI table from its inputs** (`r3_ai_inputs.py`).
- **The limit.** `ai_power_regions` here is the build of 2 October, the one the live set holds. The cost-of-power tables here are the copy of 4 October, while the live set holds a build of 20 November: the shape premium report's newest months differ today (data request 55 of `docs/state/data_requests_five_tools.md`).

| Report | Figures drawn | Re-done | Equal |
|---|---:|---:|---:|
| What flat load pays (shape premium) | 80 (63 keys) | 80 | 80 |
| Where the next gigawatts for AI can come from | 166 (94 keys) | 166 | 166 |
| `ai_power_regions` from its inputs | 149 measures | 149 | 134 (15 moved with their inputs) |

## Findings, most urgent first

| # | Finding | Severity | Measured | Branch | Fix |
|---|---|---|---|---|---|
| 1 | The AI report reads four regions and says seven; the held three print "not held" | high | cost ratio 1.11 shown, 2.48 across seven; the tally's leader and the dirtiest region change | `wip/audit-reports-1` | words: landing |
| 2 | The shape premium report ranks on the newest month whatever its hours, and draws its hour profiles on it | high | 48 of 744 hours; CAISO -0.38 against 0.81 on the latest whole month; ERCOT's hour ratio 1.96 against 3.25 | `wip/audit-reports-2` | figures: ruling |
| 3 | Shape premium sentences the rows contradict | medium | the sign (CAISO -0.38); 5 of 10 largest months in summer; Uri 90.8 percent of 2021; a cause; 2025 unnamed; two dates | `wip/audit-reports-3` | words: landing |
| 4 | AI report sentences its table contradicts or does not hold | medium | carbon's 2.88 against 8.42; two ties; "but none"; mix and margin not held; events as built | `wip/audit-reports-4` | words: landing |
| 5 | The AI report leads with California's balance, which its banner calls high | medium | gap 1.10 points before 16 December 2025, 12.88 after | `wip/audit-reports-5` | words: landing |
| 6 | The AI table's largest event predates `cold_2026`, and mixes two kinds of estimate | medium | six of seven regions move (ERCOT 8.78 to 31.15) | `wip/audit-reports-6` | figures: ruling |
| 7 | The methods appendix says what the builder does not do | medium | "complete months"; the headline import share; a measure the builder does not write; five measures not named | `wip/audit-reports-7` | words: landing |
| 8 | The license hold takes the held regions' public-source measures too | medium | 53 of 80 held rows rest on EIA, Berkeley Lab or the event studies | `wip/audit-reports-8` | figures: ruling |
| 9 | Two charts and two figure formats draw what the rows do not say | low | "0.0" for -3.00 and -1.11; four months with no gap; tonnes to the hundredth | `wip/audit-reports-9` | figures: ruling |

### 1. The AI report reads four regions and says seven (fixed in words)

- `site/data/license_status.json` marks `ai_power_regions` "license needed" from 2026-10-21 for ISO-NE, MISO and NYISO; `restPaged` drops their rows at the read. The page says "Seven U.S. ISO regions", draws five findings from what is left, prints "not held" (false: the warehouse holds them, a license holds them back), a tally with three rows of 0 of 0, and "ISO-NE has no median here" about a region not on the page.
- What the hold changes: cost ratio 1.11 against 2.48; the dirtiest region SPP against MISO; the tally's leader a three-way tie against ERCOT alone at 5 of 5.
- Fix (`wip/audit-reports-1`): one line names the three held regions as "license needed" and says the findings hold the other four (cost three); their cells say "license needed"; the ISO-NE sentences appear only when ISO-NE is shown. Drawn and read: pass; every figure equal to main's. `tests/test_audit_reports_1.py` fails on main, passes on the branch.

### 2. The shape premium report ranks on the newest month whatever its hours

- `latest` is the newest month every open hub holds with a `da_shape_premium` row, with no check of `da_hours` against `hours_in_month`; `pm`, the profile month, is the profile table's newest month.
- October 2026, 48 of 744 hours: CAISO -0.38, ERCOT 0.21, SPP 0.49 USD/MWh. September 2026, whole at all three: 0.81, 1.05, 3.44. Of 26 months every open hub holds, 11 are partial somewhere. The two-day profile puts ERCOT's dearest hour at 1.96 times its cheapest; over September 3.25 (SPP 9.17).
- `tests/test_audit_reports_2.py`, passes on main. For Samuel's ruling: rank and draw profiles on the latest month whole at every open hub. Default: left as it is.

### 3. Shape premium sentences the rows contradict (fixed in words)

- The sign sentence is written whatever the rows say (CAISO -0.38; at or below zero in 8 of 26 months with six hubs). Since 2024 each year's largest month has been in winter (January 2024 3.93, February 2025 3.07, January 2026 6.88). February 2021 is 90.8 percent of 2021 (without it 16,716.40, close to 2020's 13,552.31). "Can fade as storage and solar reshape the day" is a cause two sections after "the warehouse does not say why". 2025 left out of the yearly table without a word; "in progress" and "draft of 2026-10-01" written whatever the rows say; "close but not the same" of two days with opposite signs.
- Fix (`wip/audit-reports-3`): each sentence follows the rows (the sign only when every premium is positive, else the hub named; "nearly every hour" only when whole; the season names the latest whole year's largest month; 2021 called a poor base; the cause removed; years left out named; "words of 2026-10-01"). Drawn and read: pass; all 80 figures equal. `tests/test_audit_reports_3.py`.

### 4. AI report sentences its table contradicts or does not hold (fixed in words)

- Worst over best: hours at or above USD 200/MWh 8.42, carbon 2.88, years 2.06, cost 1.11 (across seven: 21.47, 3.05, 2.06, 2.48). "In every region but none" never read whole. "For certainty" is a cause the table does not hold. Two ties written as one leader (hours above USD 1,000: CAISO and ERCOT 1 each; the tally: CAISO, ERCOT and SPP 3 of 5). No cited table holds a mix or a marginal plant. The events are as built, and rank two kinds of estimate.
- Fix (`wip/audit-reports-4`): the widest gap named from the rows; ties as ties; the day-ahead sentence whole; mix and margin as held and not held; events "as they stood when the table was built". Drawn and read: pass. `tests/test_audit_reports_4.py`.

### 5. California's balance, which the page's own banner calls high (fixed in words)

- Before 16 December 2025 (68 days): balance 19.15 against pair sums 18.05; from that date (244 days): 29.13 against 16.25. California imports the most either way.
- Fix (`wip/audit-reports-5`): where the region named is California, the finding says at the figure that the balance reads high from the join and gives the pair sums; the date from `lib/caisoJoin.ts`. Drawn and read: pass. `tests/test_audit_reports_5.py`.

### 6. The largest studied event is as the table was built

- `cold_2026` joined `event_study_estimates` on 19 October, after the build of 2 October; the table is not in `warehouse/run_daily.sh`. Rebuilt today: ERCOT 8.78 to 31.15, PJM 7.34 to 28.97, SPP 6.14 to 26.29, MISO 7.28 to 22.96, ISO-NE 1.15 to 19.36, NYISO 1.38 to 17.31, CAISO 3.15 unchanged. `cold_2026` has no temperature-controlled estimate; CAISO's figure is one.
- `tests/test_audit_reports_6.py`, passes on main. For Samuel's ruling: rebuild the table (or put it in the daily run) keeping one kind of estimate. Default: left as it is.

### 7. The methods appendix says what the builder does not do (fixed in words)

- "The latest twelve complete months" (the builder asks only for a row a month; hubs priced 8,160 to 8,746 of 8,760 hours); the headline import share described as the pair sums (it is EIA's balance); a check the builder does not write; five measures not named; the events not said to be as built.
- Fix (`wip/audit-reports-7`): each row says what the builder does. `tests/test_audit_reports_7.py`: 5 of 6 fail on main, all pass on the branch.

### 8. The license hold takes the held regions' public-source measures too

- `licenseHeldRow` holds a row by its grid whatever the measure. Of 80 held rows, 27 rest on the grids' own prices and queues; 53 on EIA-930, Berkeley Lab (CC BY 4.0) and the event studies. MISO's carbon, 435.82 kg/MWh, would make it the dirtiest region.
- `tests/test_audit_reports_8.py`, passes on main. For Samuel's ruling: show these while the grids' prices and queues stay held. Default: left as it is.

### 9. What two charts and two formats draw

- The imports chart labels PJM (-3.00) and SPP (-1.11) as "0.0", both green; ERCOT's month bars are placed by order, so four incomplete months leave no gap; tonnes and MW to the hundredth.
- `tests/test_audit_reports_9.py`, passes on main. For Samuel's ruling. Default: left as it is.

## The questions of the brief, each answered

| Question | Answer |
|---|---|
| A figure with no source | none; the sentences without one are finding 4 |
| A source that does not say it | findings 3, 4, 7 |
| A date that moved | findings 6 and 3; data request 55 |
| A correlation worded as a cause | finding 3, finding 4 |
| A held grid's figure | none shown; findings 1 and 8 |
| A chart whose axis or window misleads | finding 9; the two-day window is finding 2 |
| A draft reachable by a visitor | not reachable; both pages say they are drafts |

## Not covered

- Today's live-set months for the shape premium report (data request 55). `check-values.mjs` against the live set. No build and no browser read.

## The branches

Every branch is from origin/main of 26 November and pushed: `wip/audit-reports-1` `7758998a6`, `-2` `455513d73`, `-3` `8ecdafe9d`, `-4` `34418fee1`, `-5` `85f3509db`, `-6` `ca9cc16e2`, `-7` `9b37b6927`, `-8` `b1fdd0476`, `-9` `fcdf0ec01`; `wip/audit-reports-words` `9629d8602` (1, 3, 4, 5, 7 merged; one conflict at 5, both sides kept; 90 passed, 4 skipped; both drafts drawn and read, every figure equal to main's).
