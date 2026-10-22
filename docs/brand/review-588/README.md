# Review 588: the five-grid cards' tall render frame in two columns

Session 588 (22 October 2026, the old laptop) placed the five panels of the two five-grid research cards in two columns in the tall render frame (1080 by 1350), as session 497 placed them side by side in the wide frame (1600 by 900). `before/` is production (erw-flame.vercel.app, the internal view, main after chain 023 landed); `after/` is a build of `wip/588-s` served on port 3588. The five-grid shots are `docs/brand/review-497/shot-497.mjs` (`measures.txt`); the two one-chart cards and the other seven cards' measures are `shot-588.mjs` here (`node docs/brand/review-588/shot-588.mjs <base> <out dir> <id>...`, `measures-588.txt` and `measures-588-other-cards.txt`, the same measures plus the callouts' top). `page/` holds the card page `/research/card/batteries_lunch_grids` at 1280 and 390, before and after.

| Frame | Before: lowest chart text / callouts' top | After |
|---|---|---|
| batteries_lunch_grids 1080 x 1350 | 870 / 637 px (SPP over the callouts) | 581 / 639 px |
| peak_hour_grids 1080 x 1350 | 870 / 827 px | 581 / 639 px |
| batteries_curtailment_hourly 1600 x 900 | 511 / 407 px | 432 / 447 px |
| batteries_curtailment 1600 x 900 | 514 / 387 px | 435 / 447 px |
| the seven other cards, 1600 x 900 | 506 to 518 / 387 to 407 px | 428 to 438 / 447 to 467 px |

What to look at, before against after:

- **The tall frame**: the five panels in two columns, three rows (SPP alone in the last), the box as tall as its panels; the callouts begin under the lowest axis label. The timeline's labels are 9 px in these half-width panels (at 11 px they ran into each other). On the peak hour card the picture now ends at 1103 of 1350 px, with white below the foot.
- **The shading**: CAISO's and ISO-NE's shaded fleet no longer runs below the panel's axis (the right scale's floor is above zero); the line and every value are as before, in the frame and on the card page.
- **The wide frame of every one-chart card** (the new check's finding): the 420 px drawing stood in a 280 px box and its foot ran about 120 px over the callouts on all nine one-chart cards. It is now scaled whole to 340 px in a box as tall as it; the last line of the lowest card ends at 867 of 900 px.
- **Not changed**: the wide frame of the five-grid cards (session 497's), where the peak hour card's eight year labels print over each other in panels some 20 px wide; listed for Samuel in the session's report.
