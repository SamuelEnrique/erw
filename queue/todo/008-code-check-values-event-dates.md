---
role: code
spend_cap_usd: 3
timeout_minutes: 120
permission_mode: auto
---
# check-values: name the date of every event-page key, so like is compared with like

Source: PRIORITIES.md layer 2, order 2 (gates: number checks); session 58's open question 0, which session 59 settled as no error.

On `/events/caiso-heat-2022`, `site/scripts/check-values.mjs` reported keys for 2022-09-01: `demand_max_mw` at 46,868 MW and `demand_max_pct_vs_baseline` at 34.74 percent. The page's own headline names 2022-09-06 at 51,104 MW. Both are right:
- 09-06 is the window's highest hour;
- 09-01 is the day with the largest rise against its baseline.

But the check's output let a session believe the page was wrong. That is a defect in the gate, not the page.

Do this:

1. Read `site/scripts/check-values.mjs` and the event pages' code: `site/app/events/`, and the `pickOf` helper or whatever else chooses the day each figure is taken from.
2. Change the check:
   - every key it reports for an event page names the date (or the hour) the figure belongs to;
   - a key is compared only with the table row for that same date: the highest-MW figure with the highest-MW row, the largest-rise figure with the largest-rise row.
3. Add a test with real rows copied from the tables: in the style of the site's existing script tests (`site/scripts/test-*.mjs`), or in `tests/` if the logic is reachable from Python.
   - The September 2022 case must pass.
   - A deliberately swapped date must fail.
4. Run the check against the built site for the event pages (`npm run build`, `npm start`, then `node scripts/check-values.mjs`), and against `SITE_URL`. Paste the event pages' lines into the final report.

Commit after each unit of work. No data writes; no em dashes.
