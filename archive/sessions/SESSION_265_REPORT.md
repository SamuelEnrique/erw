# Session 265 report: What a datacenter pays, deep

14 October 2026, 08:29 to about 10:15 UTC, unattended, on the old laptop (a code machine), one session of the chain of 14 October (263 to 267). Worktree `erw-190`, branch `wip/265-datacenter-pack`, from `afacb21e`. Model spend USD 0. No request to any publisher; the live set read with the site's anon key only; no warehouse write.

## Read these first

- **The pack:** `docs/reviews/packs/datacenter.md`, in the nine parts of `tests/test_session262.py`, with the demo as an appendix. It replaces `docs/howitworks/datacenter.md` (removed with `git rm`); the README row of `docs/howitworks/` points at it.
- **The delivery table now states only what the tariffs state** (task 1). A line billed per kVA (it needs the load's power factor) or per meter or ESI ID (it needs the site's count of meters) is labelled "conditional" and is left out of the first total, "Total delivery, the lines with no condition": Oncor 8.81 and AEP Texas 8.39 per MWh at 100 MW; CenterPoint and Texas-New Mexico Power read "conditional" there. Session 236's totals (7.67 and 7.10) stand in the row below, labelled "Total with the conditional lines: a power factor of 1, one meter". The three lines a tariff applies only to some loads are named under the table and are in neither total. Each figure's hover names the tariff lines it sums, with schedule, rate as printed, page, date and document. The Commission's wholesale rate row says it is "not a line of a retail tariff". No new section; no number at the default moved.
- **"Will the power be there?" and "How soon?" keep today's lines** (tasks 2 and 4). Read with the anon key at 08:31 UTC: `scarcity_hours_by_grid` 0 rows, `large_load_public` 0 rows (while `ercot_rtm_price_adders` answers). After `git fetch origin`, `origin/main` is at `811328fe` (session 255's landing): session 272 has not landed. `large_load_public` stays internal, as session 255 left it. For the data machine: load `scarcity_hours_by_grid` (it is in `live_set.yaml`, under review hold); then a session can read it.
- **The cost of capital** is labelled "Cost of capital: a generator's WACC, Lazard" and stays an editable field (default 9.6). The page models no debt, so it has no coverage ratio: the 1.25 "ERW's choice" belongs to the generator and battery pages (task 3).
- **A value of the address outside its bounds** is brought inside them, as before, and the panel now says so in one line (size, hours, shares, each scenario's assumptions; a grid or region not held). A value typed into a scenario field in the browser is not covered: the field is the shared `ScenarioBlock`, the battery's too (pack, part 9, question 8).
- **The replication:** the Python mirror run and equal to the page value by value (pack, part 8); the carbon file rewritten from the live set (10,160 hours, 313.01, the page's window; it held 776 hours, 346.71). The Stata do-file has still never been run.

## What to review

- The page: https://erw-flame.vercel.app/internal/open, then https://erw-flame.vercel.app/cost-of-power (after the landing). The delivery table is under "What will it cost"; the clamped line shows on https://erw-flame.vercel.app/cost-of-power?mw=20000 and https://erw-flame.vercel.app/cost-of-power?grid=miso.
- The pack: `docs/reviews/packs/datacenter.md` (parts 4, 5 and 9 first).
- The code: `site/lib/datacenter/delivery.ts` (`conditionOf`, `held`, `assumed`), `site/app/cost-of-power/page.tsx` (`DeliveryTable`, `linesTip`, `conditionalLines`, `outsideOf`), `site/lib/datacenter/finance.ts` (the label), `site/app/cost-of-power/LoadAnswers.tsx` (one plural).

## Checks, with exit codes

Two build-and-check cycles under the mutex (08:37 to 08:46 and 09:36 to 09:44 UTC), each a fresh build of the worktree; the second is of the final code. Outputs in `C:\Users\lossa\Documents\erw\runs\session265\` (`*_c1.out`, `*_c2.out`).

| What | Exit | Notes |
|---|---|---|
| `npx tsc --noEmit` (cycle 2) | 0 | cycle 1: 2 before the build (stale `.next/types`), 0 after it |
| `npm run build` (both cycles) | 0, 0 | no "statement timeout" line |
| `check-values`, restricted to `/cost-of-power` (the three cost-of-power pages), twice a cycle | 0, 0, 0, 0 | 682 of 682 each time; the new keys (`dcd`, the utility, `held`) among them |
| `check-routes` | 0 (cycle 1), 1 (cycle 2) | cycle 2: `/shoulder` and `/shoulder?grid=caiso&month=2025-07` showed one "no data" block against production's none. Untouched by this session (no file of `/shoulder` or its reads changed); no "statement timeout" in the build log; it passed in cycle 1. Read as the live set's read at that minute; the orchestrator's full run at the landing decides |
| `check-datacenter-face.mjs` | 0, 0 | 23 of 23 |
| `check-datacenter-scenarios.mjs` | 1, 0 | cycle 1: 1 of 119 failed, this session's own check of the sum (it summed the new `held` key); fixed; cycle 2: 119 of 119 |
| `check-datacenter.mjs` | 1, 1 | stale since session 213 (session 236's report: 19 failures before any change); not a gate |
| the edge cases (`runs/session265/edges.mjs`, 19 addresses) | 0, 0 | every page 200, no "NaN", "Infinity" or "undefined"; recorded in the pack, part 5 |
| `python -m unittest` of 20 modules: 265, 262, 249, 260, 236, 138, 140, 149, 154_page, 163, 179, 186, 190, 194, 195, 196, 215, 235, 253, 257 (every module that names a file this session changed) | 0 | 371 tests, 8 skipped, under the mutex |
| `erw_2026_datacenter_replication.py` | 0 | equal to the page value by value (pack, part 8) |
| `write-datacenter-carbon.py` (anon read of the live set) | 0, 0 | 87 months, 10,160 hours |
| em dashes in the changed files | 0 | `grep` for the character |
| battery capture | not owed | no shared component, `tokens.css` or `batterystack.ts` touched |

## Decisions made without you

1. "No added assumption" read as: a conversion the tariff's unit and the reader's load (size, flat, one retail customer) give is the tariff's; a power factor and a count of meters are not, so lines resting on them are conditional. Reversible: the second total keeps session 236's figure on the page.
2. The first total is drawn only where no line rests on a condition; elsewhere it reads "conditional" with the reason on hover, rather than a sum of a few small lines that would read near 0.00.
3. The tariff lines' names appear in hovers and in the note naming the three conditional lines. Session 236's pin "no tariff line is drawn by the table" holds for the drawn cells (the hover text is built after the table, in `linesTip`); the owner's list asks for each row's source, so the hover carries it.
4. The cost of capital: the field's label only; the sentences of the scenarios still say "hurdle rate" (`check-datacenter-scenarios.mjs` reads them).
5. No coverage field: the datacenter page has no debt. The panel did not grow.
6. The clamp line lives in "Your load" (one `<p>` in `page.tsx`), not in the shared `ScenarioBlock`.
7. The carbon replication file was rewritten from the live set (anon key) by its own script, and the script's window words corrected (430 days since session 245).
8. Neither new table was wired to the page: neither is in the live set, and the brief says to keep today's line in that case.

## For Samuel's ruling

The pack's part 9, in short:

1. The delivery table's reading of "no added assumption": as built; drop the conditional total; or ask the reader for a power factor and a count of meters.
2. Texas-New Mexico Power's distribution recovery factor is in the file twice (per Meter and per ESI ID, USD 635.58 each): keep both, count one, or read the sheet again.
3. The tariff lines on hover and named under the table, or in the CSV only (the prompt of 12 October), or a row a line.
4. `scarcity_hours_by_grid`: load it on the data machine for the page to read, or keep the page's own count.
5. A flexible load at 8,760 hours a year shows USD -4.55 per MWh (it runs only in the cheapest hours): keep, cap the hours, or add a line.
6. `large_load_public`: public (session 255's questions), internal, or ERCOT's and CAISO's documents only.
7. The cost of capital: Lazard's generator WACC, or a datacenter owner's if you name a source.
8. The line for a value typed out of range in a scenario field (shared component): add it, or leave it.

## Not done, or not verified

- `check-datacenter.mjs` fails as it has since session 213 (it checks blocks that left the page; session 236's report). Not rerun as a gate.
- The Stata do-file was not run (no Stata on this machine).
- The battery capture was not owed: no shared component, `tokens.css` or `batterystack.ts` was touched.

## Files

- Changed: `site/app/cost-of-power/page.tsx`, `site/app/cost-of-power/LoadAnswers.tsx`, `site/lib/datacenter/delivery.ts`, `site/lib/datacenter/finance.ts`, `site/scripts/check-datacenter-scenarios.mjs` (the delivery rows' check, local to the datacenter), `site/scripts/write-datacenter-carbon.py` (words), `site/public/datacenter/erw_2026_datacenter_carbon.csv`, `docs/howitworks/README.md`, `tests/test_session236.py` (one pin moved, "session 265").
- New: `docs/reviews/packs/datacenter.md`, `tests/test_session265.py`, this report. Removed: `docs/howitworks/datacenter.md`.
- Notes, not in git: `C:\Users\lossa\Documents\erw\runs\session265\` (the cycle script, the edge-case reader and the pages it saved, the check outputs).

## Session 265b: "How soon?" reads large_load_public

The coordinator's follow-up, 10:26 UTC: session 272 landed (`d77571ce`, the owner's ruling of 14 October 2026: `large_load_public` public as facts with a link, no quoted text). Branch `wip/265b-how-soon` from `c4a7c83b` (batch A).

- **The live set answers:** anon read at 10:27 UTC, 341 rows; ERCOT 67, CAISO 48, NYISO 5, SPP 19, ISO-NE 0.
- **What the page says now:** one paragraph under "How soon?" (no new section), for the load's grid: how many figures public documents state (of megawatts, of a wait), from how many entities in how many documents, the newest date; the newest wait as the table writes it, with its basis, its entity, its date and its document's link and page; the newest megawatt figure, with the ERW's stage class, its entity and link. "The figures are not added." ERCOT: 67 figures (55 of megawatts, 12 of a wait) from 5 entities in 28 documents; the newest wait 60 days, expected, the Public Utility Commission of Texas, 18 September 2026; the newest megawatt figure 22,000 MW, ERCOT, 17 September 2026. ISO-NE: one line that no public document held states a figure.
- **Code:** `site/lib/datacenter/statements.ts` (new, pure: `statedOf`, `statedStat`, `leadingNumber`, `stageWords`); `site/app/cost-of-power/page.tsx` reads `largeLoadStatements()` (session 272's helper) once; `StatedLine` in `site/app/cost-of-power/LoadAnswers.tsx`. Every number under a check key `dcll|<grid>|<stat>`, recomputed by `scripts/check-values.mjs` from its own read of the table (one handler, local to the datacenter). A wait written in words ("several years") holds no number and stands as written, unkeyed. A failed read says so in its place.
- **Words changed:** for a grid without an operator report, "publishes no figure of large load waiting or energized that the warehouse holds as a public table" became "publishes no regular report of large load waiting or energized that the warehouse holds, so no operator's figure is stated here": the old words are no longer true. Scenario B's own line is unchanged (pack, part 9, question 6).
- **The pack:** parts 1, 2 (step 13), 3, 6 (item 8), 7 (question 8), 9 (question 6) and the sources.
- **Tests:** `tests/test_session265.py` gains four tests (the read through the helper; facts with a link and no document's words; the counts and the check key; the figures by node).

- **Checks, 265b:** `npx tsc --noEmit` exit 0 (10:59 UTC, under the mutex). `npm run build` did not finish: the harness stopped the background command for low memory during the build's TypeScript step (the log ends at "Running TypeScript ..."; exit 1 from the stop, not from the code). It was not restarted, as the rules say. So `check-values` (restricted, twice), `check-routes`, `check-datacenter-scenarios` and `check-datacenter-face` were **not run on 265b**. The mutex, taken at 10:59, was released by hand at 10:59. `python -m unittest tests.test_session265 tests.test_session262 tests.test_session236`: exit 0 (49 tests); after the merge of `8c86c10d`, `tests.test_session265`: exit 0 (14 tests). The statements library was run by node against the live table (anon): ERCOT 67, 5, 28, 12, 55, 22,000, 60; CAISO 48; NYISO 5; SPP 19; ISO-NE 0.
- **To finish (265b):** under the mutex, in `erw-190` on `wip/265b-how-soon`: `bash C:/Users/lossa/Documents/erw/runs/session265/cycle.sh c4 1`, then `bash C:/Users/lossa/Documents/erw/runs/session265/cycle.sh c4 2` (the build; then check-values restricted to `/cost-of-power` twice, check-routes, check-datacenter-face, check-datacenter-scenarios and the edge cases; phase 2 releases the mutex). `check-values` must match the new `dcll` keys.

## The landing

filled by the orchestrator
