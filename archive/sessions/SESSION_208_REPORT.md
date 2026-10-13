# Session 208 report: the battery page on three questions, with the rulings of 12 October

12 to 13 October 2026, from 23:25 UTC, unattended, on the old laptop (`samueloldlaptop`, a code machine). Branch `wip/203-brand-battery`, pushed, **not landed**: Samuel approves from the screenshots. Model spend USD 0. Pulls: none; five published reports read on the web (each host's robots file first). No data lock, no warehouse table written. No em dash in anything written.

## Read these first

- **The page asks three questions now, nothing folded**: "What did it earn?" (the headline, the three numbers, the year chart, the income table: every number unchanged), "Is it worth building?" (scenarios A and B, with the contract's share and price as two more assumptions, 0 by default, and the results table), "What matters most" (the NPV sensitivity chart with one line on how to read it). Screenshots before and after, 1280 and 390 px: `docs/brand/review-208/`.
- **The defaults are the rulings'**: hurdle rate 12 percent (Lazard's cost of equity) on the battery and on the generator page, 9.6 kept on the datacenter; the battery's debt share 20 percent (Lazard's storage cases). The default case now reads: debt payments USD 2,261,119 a year, coverage 2.63 times, NPV USD -69.78 million, IRR -8.8 percent, breakeven toll USD 4.19 per kW-month. Every default is in grey under its field with its source, editable, with a Reset (as before).
- **At a contract share of 0 every number that stays is what it was.** Opened at the old defaults, the restructured page's 51 checked numbers are identical to session 203's page in key, raw value and shown text, in the same order; the results table is identical row for row; check-values: 254 of 254 values match Supabase. The 330 keys that left the page are the monthly rows (now the CSV) and the stress days (the public table). At the new defaults only the coverage and the debt payments move.
- **The cross-check says the negative NPV is credible, plainly.** The default case's revenue (USD 148 per kW in 2024, 87 in 2025, 81.40 over the last twelve months, an upper bound) sits above every published ERCOT figure: Modo Energy's fleet average of 55 in 2024 and about 29 in 2025, E3's modeled 2-hour battery at 127 in 2024, Tyba's first-half-2025 median of USD 2.13 per kW-month. Revenue would have to be about USD 190 per kW a year, every year, for the NPV to reach zero at the defaults; ERCOT paid that only in 2021 to 2023. The table, with each gap and its reason, is the last section of `docs/methods/battery_earns_algorithm.md`.
- **One thing I found and fixed outside the ruling:** removing the contract panel removed the sentence "sent or stored", which was what had silenced the site's usage counter on this page (`components/Usage.tsx` reads the page's text for that promise). The page now carries `data-no-usage` outright; the browser check holds every change to no request (85 of 85).
- **The generator page's hurdle rate changed too** (ruling 1 names it), on this wip branch: `site/lib/seller/finance.ts`, its script and tests. Its page was not rebuilt or screenshotted here. Decision 2.

## What to review

1. The screenshots: https://github.com/SamuelEnrique/erw/tree/wip/203-brand-battery/docs/brand/review-208 (`battery_before_1280.png` against `battery_after_1280.png`, then the two at 390 px; `README.md` says what to look at).
2. The numbers before and after: `docs/brand/review-208/numbers_before_after.txt` on the same branch.
3. The cross-check table and the paragraph "Is the negative NPV at the defaults credible?": https://github.com/SamuelEnrique/erw/blob/wip/203-brand-battery/docs/methods/battery_earns_algorithm.md#cross-checks
4. To see it live on the old laptop: `git switch wip/203-brand-battery`, `cd site`, `npm run build`, `npx next start -p 3208`, open http://localhost:3208/internal/open, then http://localhost:3208/cost-of-power/battery . The CSV: http://localhost:3208/cost-of-power/battery/months.csv .

## Part A: the rulings

1. **Defaults.** `lib/battery/finance.ts`: `HURDLE = 12`, `SHARE = 20`, `defaultsOf` reads both; the sources under the fields quote Lazard's storage sentence ("20% debt at an 8% interest rate and 80% equity at a 12% cost"). `lib/batterystack.ts`: `DEBT.share = 0.2`, so the panel's note and the page's own default debt payment agree with scenario A to the dollar (2,261,119). `lib/seller/finance.ts`: `HURDLE = 12`; its debt share stays 60 (Lazard's generation structure; the ruling names only the battery's). `lib/datacenter/finance.ts`: untouched, 9.6.
2. **The fold "What this model cannot see" is gone.** Under the income table one sentence stays: "Energy is priced at ERCOT's HB_HUBAVG hub, not the battery's own node; reserves are paid for being held and are assumed never called", with a link to the list in the methods note (section 4.11, anchor `cannot-see`).
3. **The cross-check.** Five rows added to the note's table (our number, theirs, gap, reason), the credibility verdict, and the "Debt share" row that had asked the question now records the ruling. The page's source line says "Checked against: 14 published figures". What was read, after each host's robots file: Modo Energy (two posts; robots allow everything; its website terms of service forbid redistributing its analysis, so one figure is quoted per post, with its source, as a citation; see ruling 4), E3's 2024 ERCOT Market Update (PDF), Tyba's H1 2025 page, and Potomac Economics' 2024 State of the Market Report (PDF, 1.9 MB), whose net revenue analysis covers gas, wind and solar and gives no storage net revenue, which the table says. Enverus's newsroom answered 403 and is not used; Gridmatic publishes no 4-hour ERCOT figure.

| Our figure, ERCOT 100 MW 4-hour, perfect foresight (day-ahead schedule) | Theirs | Gap | Likely reason |
|---|---|---|---|
| 2024: USD 148 per kW (127) | Modo Energy, the fleet average, 2024: 55 | +93 (+72) | an upper bound for one price-taking battery at the hub, reserves never called, against a fleet settled at its nodes, mostly 1 and 2 hours; the model takes 5.66 times the fleet's day-ahead reserve awards |
| 2025: 87 (78) | Modo Energy, the fleet, 2025: 26.0 through November, about 29.4 for the year (a nowcast) | +58 (+49) | the same; the ratio of ours to theirs is about 3 in both years, which an upper bound on the same prices should give |
| 2024: 148 (127); 2023: 530 (459) | E3, a modeled 2-hour battery at ERCOT North: about 127 in 2024, up to about 475 in 2023 | 2024: +21 (0); 2023: +55 (-16) | the closest method to ours (an optimization over the real prices); 2 hours at the North hub against 4 at the hub average |
| H1 2025, a month: 7.3 | Tyba, the fleet's median asset: USD 2.13 per kW-month; the best asset 6.19 | +5.2 against the median; +1.1 against the best | ours sits above the best asset by the margin perfect foresight and uncalled reserves give |
| (none) | ERCOT's market monitor, 2024 report: no net revenue for a storage resource | none | its net revenue analysis is gas, wind and solar |

## Part B: the restructure

4. **The order.** `page.tsx` draws three `ToolSection`s inside `data-question` wrappers. Section 1 holds the headline (`BatteryHeadline`), the chart, an `h3` "Income by stream", the table, the awards line, the one sentence, and the line "Every month, CSV" (with the stress table's download for ERCOT). Section 2 (`id="scenarios"`, the panel's link still works) holds `Scenarios`, which hands the shared block `chart={null}`. Section 3 holds `BatterySensitivity`, which draws the shared block's `Sensitivity` (now exported: one `export` keyword added to `components/decisions/ScenarioBlock.tsx`, nothing else in that file changed).
5. **Gone:** the panel "Your contract (optional)" and the section "With your contract" (`Contract.tsx` stays on disk with a note, imported by nothing; `contractResult` stays in the library); the "Other grids" table (one line under the grid picker, `data-other-grids`); the folds "Every month", "Stress days" and "What this model cannot see". **The monthly rows are a download:** `/cost-of-power/battery/months.csv` with the page's own four parameters and scenario A's, served by a route handler from the same read as the page (`read.ts`, new, shared by both) and the same library, with the provenance in `#` lines (the source table, when it was read, the fixed O&M and the debt payments the coverage column uses, the 90 percent rule), 113 lines for ERCOT. The proxy never sees a path with an extension, so the route applies the page's status itself: a visitor gets a 404 "in review" line while the page is in review; the internal view gets the file.
6. **The contract as assumptions.** `lib/battery/finance.ts`: two more keys, `cshare` (percent of the battery's power, letter `n`) and `cprice` (USD per kW-month, letter `p`), bounds 0 to 100, steps 10 points and USD 1; `contractYear`, `merchantShare`, `incomeInYear`; the flows read the contract for the debt's years and the market after; coverage reads it; the toll and the tail do not. A missing key is read as 0, so every older address and every older set of assumptions is a merchant case. The headline reads A's contract: the summary sentence names it, the coverage is A's own and drops its check key (the table holds no contract); at a share of 0 the key is back. The results row "Debt coverage" names the contract in its note.

## Checks, with exit codes

None piped; outputs under `runs/session208/`.

| Command | Exit | Result |
|---|---|---|
| `scripts/precheck.py` | 0 | 6 of 6; on duty until 13 October 15:25 UTC |
| `npx tsc --noEmit`, four times (the last after the merge of `main`) | 0 | |
| `npm run build`, three times (the tip for the before screenshots; the restructure; the audit fixes) | 0, 0, 0 | no "statement timeout" line |
| `node scripts/test-battery-finance.mjs` (pins moved; the contract's checks added) | 0 | 61 assertions |
| `node scripts/test-decisions-195.mjs`, `test-seller-finance.mjs` (pins moved) | 0, 0 | |
| `CHECK_VALUES_PAGES=/cost-of-power/battery node scripts/check-values.mjs` on the restructure | 0 | 254 of 254 values match Supabase (the first run was mangled by MSYS path conversion of the variable: `MSYS_NO_PATHCONV=1`) |
| `node scripts/check-battery-scenarios.mjs` on the final build (rewritten section 11: the contract as assumptions; the chart read from the document) | 0 | 85 of 85 |
| `runs/session208/capture.mjs` before and after, and the comparison (`docs/brand/review-208/numbers_before_after.txt`) | 0 | 51 kept keys identical at the old defaults; 330 removed, all monthly or stress-day rows; the results table identical (43 numbers) |
| `impeccable detect --json` on the five changed files | 0 | 0 findings |
| Impeccable's audit (the playbook, run once; `runs/session208/impeccable_audit.md`) | | 16 of 20: two fixes made (controls 32 px tall; a zero-size bar reads "USD 0"), three P3 left for the ruling |
| `npx eslint` on the changed files | 1 | one error, pre-existing and not of this session: `react-hooks/immutability` on the memo in `Scenarios.tsx` (session 179's lines, unchanged); the build does not lint |
| `python -m unittest` on the 29 modules that read the battery page, before the pins were moved | 1 | 17 failures, every one a pin of the old defaults or of a section that left the page |
| the same ten modules after the pins were moved; then the 29 again after the merge (`tests5.out`) | 0 | see "To finish" if the last run was not read before this report was committed |
| `scripts/freeze.py status` | 0 | no freeze (not needed: nothing landed) |
| Whole suite in a clean copy | not run | no landing in this session; the wip branch carries the changed tests. Run it before the landing |

The CSV was fetched three ways in the internal view (the bare address; ERCOT day-ahead at 50 MW with a typed capital cost; CAISO 2 hours), each 200 with its header lines, and as a visitor (404 after the gate was added; it was 200 before it, which is why the gate exists).

## Decisions made without you

1. **The generator page's hurdle rate moved to 12 with the battery's**, since ruling 1 names "battery and generator"; its debt share stays 60. Its note has a session 208 paragraph; its worked figures below stay as the record. Reversible: one constant.
2. **The seller page was not rebuilt or screenshotted**; this session is the battery page's. Its own browser check (`check-seller-scenarios.mjs`) still expects "9.6 percent" in two sentences and will say so until it is moved; listed under "To finish".
3. **`Contract.tsx` is kept on disk**, undrawn, with a note (CLAUDE.md rule 3 against deleting; the ruling asks for the panel and the section to go, which they have).
4. **The monthly rows are a route handler**, not a file: a code machine writes no warehouse data, and the rows depend on the address (grid, duration, strategy, size, scenario A's costs). The stress days are not on the page at all: the ruling lists the fold among what goes, and the table is public (`/api/download?table=battery_stack_stress_daily`, linked under the CSV line for ERCOT). The page no longer reads `battery_stack_stress_daily`, so the source line no longer names it.
5. **The contract runs for the debt's years**, as the row "Merchant tail after the contract" already assumed (section 11.1 of the note: "the toll is taken to run as long as the debt"); the contract price is paid flat, not degraded. The headline reads A's contract (ruling 6: the headline uses scenario A), unkeyed when contracted.
6. **The replication files keep 60 percent debt** (`site/public/battery/erw_2026_battery_replication.py` and the do-file, written by the data machine's export, pinned by `tests/test_session178.py`); that test now reads the page's library at the export's own debt payment, and the note says the files carry the old share until the next export. Ruling 2.
7. **The screenshots were taken before `main` was merged into the branch**, so their header is session 203's menu as the wip branch had it; the merge changed only reports and one script.
8. **Modo Energy was read** (session 196 had not: it could not find the terms). This session found them (`/website-terms-of-service`): no sentence on automated access; "you may not recirculate, redistribute or publish the analysis". One figure per post is quoted with its source, as a citation. Ruling 4.
9. **`data-no-usage` on the page's wrapper** (above). The alternative, keeping a promise sentence on the page, would have been a sentence written for a counter.
10. **The CSV route answers 404 to a visitor** while the page is in review, by `statusOf` in the route. Without it the file was public (the proxy's matcher skips paths with an extension); the table is public anyway, but the page's status should govern its download.

## For Samuel's ruling

1. The page: approve from the screenshots, or say what to change. Then the landing (a `task/` branch from this wip branch, the whole suite in a clean copy, the snapshot).
2. The replication files (section 7 of the note) still say 60 percent debt and coverage 0.88. The data machine's exporter (`warehouse/derived/battery_dispatch_export.py`) writes them: change its scalars to 20 percent at the next export, or keep the export as it is and let the note explain.
3. The seller page's browser check and its own worked figures at 9.6 (its note's examples): move them in a seller session.
4. Modo Energy's two rows in the cross-check: keep them (a quoted figure with its source), or take them out under their terms sentence.
5. Impeccable's three P3 findings: the charts' colors as literals (waits for the brand's approval), the chart titles as spans not headings (the shared `ChartFrame`), the grid list's five greyed grids beside the one line.
6. The pre-existing eslint error on `Scenarios.tsx` (session 179's memo): fix it in a tooling session, or turn the rule down for the file.

## To finish

- `runs/session208/tests5.out` (the 29 modules after the merge): read its last line; if it is not `OK`, the failure is new since this report.
- The landing, when approved: `git switch -c task/20N-battery-three-questions wip/203-brand-battery`, `git merge origin/main`, the whole suite in a clean worktree, `npm run build`, `node site/scripts/snapshot-live.mjs take <before>` as its own command, `git push`, then `take <after>` and `compare`.

## The prompt

Chain of 12 October, sessions 208 and 209, code machine, unattended. Session 208: "the battery page, on branch wip/203-brand-battery. Do NOT land on main: Samuel approves from screenshots. Long end 5:00. Model spend cap USD 0. Pulls: none (reading published reports on the web is allowed)." Part A, rulings 1 to 3 (defaults, the fold, the cross-check); Part B, the restructure, 4 to 6 (the order, what goes, every number at contract share 0 identical); "Then run Impeccable's audit on the page once, fix what it flags, and save before and after screenshots (1280 and 390 wide) to docs/brand/review-208/."
