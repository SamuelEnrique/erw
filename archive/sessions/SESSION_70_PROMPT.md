# Session 70 prompt: battery game v4, three rule fixes

Energy Research Warehouse (ERW), session 70. A short follow-up to session 66, in the same worktree and on the same branch. Read archive/sessions/SESSION_66_REPORT.md and docs/methods/battery_game.md first.

**Expected model spend: USD 0.00. Hard cap: USD 0.00.** No paid service, no pulls, no force push. Expected wall time about 1 hour; no time cap.

## Where this runs

Exactly as session 66: only in `C:\Users\samen\Documents\erw-game`, on `wip/066-battery-game-v4`. Never read, write or run git in `C:\Users\samen\Documents\erw` (other sessions are running there); you may only call its Python interpreter by path. Push only to the wip branch, never to main or any `task/` branch. No Supabase writes, do not apply migration 019, do not take the data lock, do not run the finish step.

Version 4 has not been released, so these changes are still version 4: no new rules version, no new migration.

## Fix 1: the lights-out charge is Texas's official value of lost load, not "6 times the cap"

Session 66 priced unserved house energy at 6 times the USD 5,000/MWh cap, a number found by search. Replace it with a real, citable one: **USD 35,000 per MWh, the value of lost load the Public Utility Commission of Texas approved in August 2024** (Project No. 55837; ERCOT's study by The Brattle Group found a one-hour, system-wide value of USD 35,685 per MWh).

- Verify both figures against the source documents (the PUC's order or announcement and the Brattle final report) before citing them. If you cannot open a source, cite it as given here and flag it in the report.
- On the page and in the methods doc: it is a game rule; the figure and its source; that it is the system-wide value and that the same study found a lower value for residential customers alone (state that residential figure only if you verified it); and that the game applies the Texas figure on California days too.
- Remove the multiple-finding logic and its test. Keep the required result as a test (Fix 2).

## Fix 2: going dark costs the whole outage

Session 66's report notes that with a much larger inverter the perfect battery can still choose the dark for the outage's last minutes, because the charge counted only the time left. New rule: **if the lights go out at any point in the outage, the house is charged for the unserved energy of the whole outage** (1.5 kW for all of it, less what a roof supplies if the add-on is on), at Fix 1's price. The round still ends there. One sentence on the page, written for a high school student.

**Required result, as a test:** the perfect battery does not end in lights out on any of the 7 famous days, on today's level, on any toy day where the lights can be kept on, or under the larger-inverter presets session 66 identified. If any case still fails, do not tune the price: report the case exactly and leave the rule as specified.

The DP, `simulate` and the server scorer stay one code path; the DP still equals brute force on the toy days under every preset.

## Fix 3: the roof stops exporting at negative prices

Session 66 had the rooftop array sell at the interval's price even when it is negative, so the roof paid to export. A real system curtails. New rule: when the price is below zero and the battery is not charging, the roof's output is curtailed and earns nothing. The page's add-on text says so. Update the DP, the scorer and the tests.

## Checks

`site/scripts/test-battery.mjs`, `check-scorer.mjs`, the Python tests (main folder's interpreter by path), `tsc --noEmit`, `npm run build`, eslint on the files touched, and check-routes on the local build. In a browser on the local site: play Hard on 2021-02-15 and let the lights go out, and confirm the charge, the sentence and the end screen read correctly.

## Report: `archive/sessions/SESSION_70_REPORT.md`

"To finish" first: session 66's finish steps, restated in full and corrected for anything this session changed, so this report alone is enough to finish version 4. Then "In plain words"; the table of the perfect battery on the 7 famous days (Hard and Normal) under the new rules, with how each ends and what keeping the lights on costs against session 66's figures; the sources as verified; test results; errors and decisions; "For Samuel" with only what needs a person. No em dashes anywhere. Commit after every working step, push the wip branch, reply "REPORT READY" and stop.
