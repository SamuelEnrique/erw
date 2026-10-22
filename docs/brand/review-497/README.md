# Review 497: the five-grid cards' render frames

Session 497 (21 October 2026, portable-laptop) placed the panels of the two five-grid research cards in their render frames; session 506 (the old laptop, 21 October 2026, 23:30 UTC) took the after shots on a build of `wip/506-combined`, which holds `wip/497-faults` with the rest of chain 023. Both folders were made by `shot-497.mjs` here (`node docs/brand/review-497/shot-497.mjs <base> <out dir>`); session 506 added a wait for the page's fonts before each measure and shot.

| File | Address | Frame |
|---|---|---|
| `batteries_lunch_grids_1600x900.png` | `/research/card/batteries_lunch_grids?render=1` | wide, 1600 by 900 |
| `batteries_lunch_grids_1080x1350.png` | the same | tall, 1080 by 1350 |
| `peak_hour_grids_1600x900.png` | `/research/card/peak_hour_grids?render=1` | wide |
| `peak_hour_grids_1080x1350.png` | the same | tall |

`measures.txt` in each folder gives the page height, the bottom of the last line and the bottom of the lowest chart text.

What to look at, before against after:

- **The wide frame**: the five panels side by side again; the lowest chart text moved from 959 px (below the 900 px frame) to 281 and 269 px. check-findings-grids: 163 of 163.
- **The tall frame still overlaps**: the five panels in one column end at 870 px, and the fifth (SPP) is drawn over the callouts' boxes, which begin near 830 px. Session 497's report left this case to a later session (two columns in the tall frame, the same way); it is session 588 of `queue/next/034-night-22-october-code.md`.
- No value moved; the toggle is off the picture in every frame.
