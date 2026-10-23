# Session 1134 report: the board's freshness, kept

23 October 2026, 20:05 to 20:10 UTC, on samueloldlaptop, unattended, on `wip/1134-board` (cut from `wip/1132-ask`). Chain `queue/done/076-day-24-october-code-ask-board-2.md`. Model spend USD 0.

## What was done

- **The stale rule by the publisher's calendar** (`staleDays`, `POWER_GROUPS` in `site/lib/board.ts`): a power market posts every day, weekends and holidays included, so a daily row of the power groups is stale past 3 days; EIA's daily fuel closes keep session 304's 10 days; weekly 17, monthly 132, as session 1116 set them. Measured first on the file of 23 October: the power rows were 0 to 4 days old (the 4-day ones ISO-NE's and NYISO's, held), the fuels 2 to 3. With the rule, 60 rows shown are marked stale: SPP's 14 ancillary rows (3 October), 10 crude rows and 34 plant-fuel rows of monthly series a publisher stopped, CARB's 2 weekly credit rows.
- **ERCOT's day-ahead gap of 15 October** (roadmap v4, item 6) checked again on the file: the row holds every day of its last 30, 23 September to 22 October. It is filled.
- The method note says both.

## Checks

- `node --import ./scripts/alias-register.mjs scripts/test-board-1116.mjs`: exit 0, 5 of 5 (a market's daily price stale past 3 days, its words); `test-board.mjs`: exit 0; `tests.test_session1116`, 132, 240, 304: exit 0.
- Em dashes: 0.

## Decisions made without you

1. **3 days for a market's daily price**: a day-ahead price is posted the day before its day, every day; three days late is a fault of the pull, not of the calendar. Reversible: one constant.

## For Samuel's ruling

- None new.
