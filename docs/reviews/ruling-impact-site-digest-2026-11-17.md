# Ruling impact: Site-wide, the Digest and the Roundup (17 November 2026)

Session 7612 (portable-laptop). The one line marked "Changes a figure" under "Site-wide: the Digest and the Roundup" in `docs/reviews/rulings-for-samuel-2026-11-17.md` (branch `wip/7560-six-reads`): the figure under the default and under the other choice, the page and cell it moves, and the change in units and percent. No page, no default and nothing of the Digest was changed (the Digest is paused this week; this is a reading of the tables only).

- **Script:** `runs/ruling_impact/site-digest_impact.py`, its printout beside it (`site-digest_impact.out`). It recomputes the Digest's line as `warehouse/news/brief.py` (`demand_lines`) writes it: the highest hour of the Lower 48's demand on the day before the issue, and its change against the same weekday a week before. It reads `eia930_all_demand` (entity `eia930:US48`, variable `demand_mw`; EIA Form EIA-930, `eia:electricity/rto/region-data`, retrieved 2026-11-16 14:34 UTC) from the live set, read-only.
- **The window:** the live set holds 824 hours, 12 October 16:00 UTC to 15 November 23:00 UTC: 33 days whole under every clock (13 October to 14 November) and 26 with a whole day a week before. The note's own count (9 of 70 days with the peak at 23:00 UTC) was taken on a longer copy; here it is 10 of 33. A longer span would need the warehouse's whole hourly table (Redivis), not read here.
- **No model call** (spend USD 0).

| # | Line (the question) | Page and cell | Default | Other choice | Change |
|---|---|---|---|---|---|
| 1 | Should the Digest's US48 day stay the UTC day, which splits the US evening peak? | Each weekday Digest (`/digest`, `docs/digest/`): the line "US48 demand, yesterday: peaked at X MW in the hour starting ... UTC", its change against the week (or year) before, and the "Physical" row of the numbers block | The UTC day | A US day (the Eastern day; the Central day gives the same figures on every day here) | **The peak moves on 14 of 33 days** (42 percent), and its hour on the same 14. On each of them the UTC day's highest hour is 00:00 UTC, which is the evening peak of the US day before (19:00 or 20:00 Eastern): the Digest gives yesterday's figure the evening of the day before. Largest: 17 October, **495,806 MW to 448,936 MW, -46,870 MW, -9.45 percent**; then 16 October 540,657 to 514,073 (-4.92 percent), 7 November 480,282 to 459,651 (-4.30 percent), 14 November 492,216 to 472,195 (-4.07 percent). Over the 14 days the peak falls by 11,387 MW on average (-2.29 percent); it never rises. **The change against a week before** (written to one decimal) moves on 12 of 26 days and turns sign on 3; largest, 24 October: -4.8 percent to +2.6 percent (+7.4 points) |

## What a ruling would also have to fix

- Which US day: Eastern and Central give the same peaks over these 33 days (the evening peak falls between 23:00 and 01:00 UTC either way); a Pacific day would not, and was not computed.
- The hour as written: the Digest writes the hour in UTC; a US day would read better with the hour in that day's own clock.
- The Roundup's weekly peak cuts its weeks at UTC midnight too; the same shift touches at most the evening at each end of a week. Not computed here.
- Nothing here needs a model call, a license not held, or data not held. The year-before change the Digest prefers needs last year's hours, which the live set does not hold; the data machine's copy does.
