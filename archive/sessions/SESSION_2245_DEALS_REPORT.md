# Session 2245 (chain 156, deals and datacenters) report: the timeline

6 November 2026, from about 10:41 UTC (while session 2242's gate ran), portable-laptop (code role), unattended. Worktree `erw-2245` on `wip/2245-deals`, cut from `wip/2244-deals`. Model spend **USD 0**. Nothing deployed; no warehouse data written.

- **`site/lib/dcrollups.ts`**: `timeline` (the facilities whose sources state both the first story's date and the year the facility is to be energized or come online; the wait the difference of the two years), `timelineCells` (by grid and by year of first report: the count, and the median from three), `timeKey` (`dctime|<count|median>|<grid|year>|<value>`).
- **`site/app/datacenters/Timeline.tsx`** (new), on the facilities view under the rollups; with no facility of both dates (today: the energized year is a field of session 2236, and the stored rows predate it) it says so in one line.
- **`site/scripts/check-values.mjs`**: the `dctime|` keys with the page's function.
- **`tests/test_session2245_deals.py`** (4 tests); with 2243 and 2244: 13 passed.

## Decisions made without you

1. **The wait is in whole years**: the energized date the stories state is a year ("go live in mid-2026" is 2026), so a wait in months would claim a precision no source gives.
2. **"Announced" is the first story's date**, named "first reported" on the page: the tracker holds when the news first reported a facility, not when its owner announced it.

## For Samuel's ruling

- None new.
