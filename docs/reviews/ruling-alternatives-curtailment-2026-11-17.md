# Ruling alternatives: /curtailment (17 November 2026)

Session 7631 (portable-laptop, code role). The three lines of `docs/reviews/ruling-impact-curtailment-2026-11-17.md`. Two are built, each on its own branch from origin/main with a test that pins it; the third moves no figure on today's file. **No branch asks to land; no default on main changed; no request to ERCOT.** Model spend USD 0.

- **Build:** the worktree `erw-alt` (3,072 and 3,336 MB free before the two builds), served on port 3320 with the repository's `.env` and no model key, read cache-free with the internal cookie at 1280 px.
- **Tests:** the new test of each branch and every test file that names a changed file: 166 passed, 10 skipped, 251 subtests (both branches).

| # | Line | Branch | Figure before (origin/main) | Figure after (the other choice) | Files touched | Test | Screenshot |
|---|---|---|---|---|---|---|---|
| 2 | One line in the battery section with the battery page's revenue for the same hub and duration | `wip/alt-curtailment-1` (`3feea6ebc`) | `?grid=caiso&period=2026-09`, "A battery of 4 hours, against what the fleet charged": no revenue | **"What the battery page says the same battery earned at SP15 in September 2026: USD 6.84 per kW of power with perfect foresight, USD 6.32 on the day-ahead schedule"**, with the battery page's link (a figure added a month: May to October 2026 7.50, 5.73, 7.02, 10.87, 6.84, 7.74 with perfect foresight; 6.99, 5.57, 4.95, 6.97, 6.32, 7.53 day-ahead). Read server side from the live set's `battery_stack_monthly`, the rows the battery page reads; follows the duration chosen | `site/app/curtailment/page.tsx`, `site/app/curtailment/Sections.tsx`, `tests/test_session7631_alt_curtailment_battery_revenue.py` | The live set's figures, May to September the impact file's exactly; the page reads them for CAISO and draws the line for a month chosen | `docs/reviews/ruling-alternatives/curtailment-1-battery-revenue-1280.png` |
| 3 | ERCOT's view: only the head's share of output below the limit, not shares over more than one span | `wip/alt-curtailment-2` (`afe8188ad`) | `?grid=ercot`: 6.23 percent over the 47 whole days (the head and the Texas table), and October 2026's 6.05 percent (the head's third number, the line under the complete months, the Texas table's month row) | **The head's 6.23 percent alone**; October's 6.05 leaves the view in all three places (the months' MWh stay; the share cell says it is given over the head's days only). The impact file's 5.91 (a third span) is not on the page of 15 November's file | `site/app/curtailment/page.tsx`, `site/app/curtailment/Sections.tsx`, `tests/test_session7631_alt_curtailment_one_span.py` | `ercot.json`: 47 days at 6.23, October at 6.05; the code draws no month's share | `docs/reviews/ruling-alternatives/curtailment-2-one-span-1280.png` |

## Line not built

- **Line 1, the hour of 1 November 2026 whose wind limit reads twice its neighbours:** on the page's file of 15 November that hour is already not among the day's hours held (it lacks a solar limit), so the day already reads 15,423.9 MWh and leaving the hour out changes nothing (0). Reading the posting again would need a saved copy (none is kept) or a request to ERCOT's MIS, which ruling 2 does not allow.

## Decisions made without you

- **Line 2 is drawn for a month, not a year:** the battery page's figure is monthly; for a year chosen the line is not drawn (a year's sum would be a figure the battery page does not print for a calendar year in this form).
- **Line 2 reads the live set at the page's build**, as the battery page does, so it follows the battery page's own figure on the same day.
