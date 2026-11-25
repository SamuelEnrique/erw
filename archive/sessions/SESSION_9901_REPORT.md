# Session 9901: ERW video posts, batch 2 (nine posts, two options each, three shapes)

Desktop, unattended, 25 November 2026, 07:25 to 08:10 UTC. Worktree `C:\Users\Shared\Documents\erw-w-9901`, branch `wip/linkedin-posts-2026-11-25` (from `origin/wip/linkedin-posts-2026-11-24`, `af4deceef`). Not merged. Nothing posted, published or deployed; main, the site, `site/lib/release.ts`, Supabase and Redivis untouched; no force push. Model and API spend USD 0 (no Claude API call, no paid service).

## Read first

- **Not finished: 32 of the 54 videos are not rendered.** Claude Code stopped the background render at 08:06 UTC because the machine ran low on memory, and its rule is not to restart such a job unasked. Every still is done and checked; the commands are under "To finish".
- Review page: `docs/reviews/linkedin/posts-2026-11-25.md` (comparison image a post, every number with its table and source, status).
- Comparison images, all nine posts: `docs/reviews/linkedin/img/batch_2026-11-25/<post>_options.png`.

## What was built

- Section 2 first: `motion/src/Jensen.tsx` and `motion/specs/posts/nvidia_energy_blocks.json` copied byte for byte from the prompt's code blocks by script; `Root.tsx` routes `blocks` and `ladder`. First commit right after.
- Regression check: NVIDIA's last frame at 1080 x 1080 and 1080 x 1350 (scale 2) opened; every item in section 2d matches. The NVIDIA post was not re-rendered or re-published.
- `motion/src/Batch2.tsx`: the approved look, header and title visible from frame 0 (`Shell2`), ten chart types: columns, year line or area, weekly line, clock shift, day curves, fill block, flow band, staircase, 100-square grid, ladder, proportional blocks.
- `Root.tsx`: routes the Batch2 types; `canvasHeight` puts the 1080 x 1350 layout on a 1080 x 1920 fog canvas 200 px down (Instagram).
- `motion/batch_9901.mjs`: stills at chosen frames, and videos in the three shapes at scale 2 with a last-frame thumbnail.
- Data: one file a post in `docs/research/motion/posts/batch_2026-11-25/data/`, written by `scripts/build_9901.py` from the ERW tables and the saved reproduce runs.
- Videos done (24 + 2): posts 1 to 4 complete (A and B, three shapes, thumbnails); post 5 option A in X and LinkedIn. All 26 probed: H.264, 450 frames, 30 fps, the right size.

## Status by post

| # | Post | Stills | Videos | Status |
|---|---|---|---|---|
| 1 | thanksgiving_peak_hour | done | done | A ready, B needs ruling |
| 2 | thanksgiving_gasoline | done | done | ready |
| 3 | caiso_battery_peak | done | done | ready |
| 4 | canada_new_york_flow | done | done | ready |
| 5 | dominion_mean_hour | done | A x, A linkedin only | ready, videos to finish |
| 6 | ercot_solar_tight_hours | done | none | ready, videos to finish |
| 7 | texas_cold_peak | done | none | ready, videos to finish |
| 8 | uranium_us_origin | done | none | ready, videos to finish |
| 9 | us_share_world_oil | done | none | ready, videos to finish |

## Numbers

- Every reproduce script rerun on today's tables (sections 1, 3, 8, 10, 21, 24, 37): every value equals the 24 November runs. Post 1: `thanksgiving_peaks.py` rerun, summary identical.
- Numbers that differ from section 5: none. Post 1 as given (9, 7, 7, 5, 4, 3, 0 hours). Post 2 as given ($2.10, $3.40, $3.65, $3.29, $3.04, $3.06, $3.64 from 3.642); 2022 is 3.648, so nothing says record. The old spec's $3.81 (16 November) is replaced.
- Post 2's week of 23 November 2026 is from EIA's API (read 07:29:55Z): the ERW table on this machine ends at 16 November. All 359 overlapping weeks equal the table.
- New numbers, not in section 5: post 1 B (PJM average day, 94,247 MW at 7 pm and 86,132 MW at noon) and post 9 A (2025 production by country). Both from ERW tables, in the data files.

## Checks

- Final frame of all 18 options opened in each of the three shapes; frames 0, 110, 220, 330 of each option opened (square). Fixed after looking: three titles on three lines (posts 3, 5, 8), a year range broken at its hyphen, touching labels (MW columns, staircase total, first labels on line charts), a missing 2026 label, two labels past the right margin, the ladder label over the title, a figure shown before its fill ended (post 8 A).
- Every still now: title two lines, source at most three, nothing clipped or spilling, one cardinal element, figures equal to the data files.
- Text-size exceptions (under 15 px at 1080 scale): none. Smallest is 18 px (axis ticks, clock-time labels).
- Line charts not starting at zero: none.
- Dashes: none in any file written (checked by grep).

## Instagram safe area (an assumption, not measured)

- The 1080 x 1350 layout sits on the 1080 x 1920 canvas from y = 200 to 1550, as the prompt says. That Instagram's buttons and caption leave this band clear is a design assumption.

## Skipped or blocked

- No post blocked for its numbers.
- 32 videos and their thumbnails not rendered (memory stop, above).
- Post 8 A uses the prompt's fallback (100 squares): the ERW table holds no country of origin.

## To finish

Run in a terminal (not as a background job), one line at a time; each spec takes about 2 minutes (three shapes):

```
cd C:\Users\Shared\Documents\erw-w-9901\motion
node batch_9901.mjs video ../docs/research/motion/posts/batch_2026-11-25 ig specs/posts/batch2/dominion_mean_hour_a.json
node batch_9901.mjs video ../docs/research/motion/posts/batch_2026-11-25 x,linkedin,ig specs/posts/batch2/dominion_mean_hour_b.json specs/posts/batch2/ercot_solar_tight_hours_a.json specs/posts/batch2/ercot_solar_tight_hours_b.json
node batch_9901.mjs video ../docs/research/motion/posts/batch_2026-11-25 x,linkedin,ig specs/posts/batch2/texas_cold_peak_a.json specs/posts/batch2/texas_cold_peak_b.json specs/posts/batch2/uranium_us_origin_a.json
node batch_9901.mjs video ../docs/research/motion/posts/batch_2026-11-25 x,linkedin,ig specs/posts/batch2/uranium_us_origin_b.json specs/posts/batch2/us_share_world_oil_a.json specs/posts/batch2/us_share_world_oil_b.json
cd ..
C:\Users\Shared\Documents\erw\.venv\Scripts\python.exe docs/research/motion/posts/batch_2026-11-25/scripts/options_image.py
git add docs/research/motion/posts/batch_2026-11-25 docs/reviews/linkedin/img/batch_2026-11-25
git commit -m "Session 9901: the remaining videos"
git push
```

- `batch_9901.mjs` renders with `concurrency: 6`; if memory is short, set it to 2 (slower).
- The python line rebuilds the comparison images from the thumbnails (the same final frames).

## Open questions for Samuel

- Post 1 B averages the 21 normal Thursdays and 7 Thanksgivings for PJM (marked needs ruling); the plan said one Thursday. One pair of days is a one-line change.
- Post 2: is a value from EIA's API (the table's own source) acceptable before the ERW table holds it, or should the post wait for the table?
- Post 8 A and post 6 A share a chart type (100 squares), because the fallback forces it. An alternative from the table: two proportional blocks, U.S. origin 3.4 million lb against foreign origin 43.5 million lb.
- Posts 8 A and 9 A show the latest year under a title that spans the period (each says 2025 in the chart). Keep, or give A its own title?
- Titles changed from the proposals: post 3 "California's battery power vs peak-day demand, 2019-2025"; post 5 "Power demand in Dominion's Virginia zone, 2019-2025"; post 8 "U.S.-origin share of uranium for U.S. reactors, 2003-2025".
- Post 1 A and B have different source lines (B is one grid's average day); every other post shares one.
- Post 5 A: steps rounded one by one sum to 3,715 against a total of 3,716 (the source line says so). Prefer steps from rounded levels (2023 would read +158)?
- Post 7 A: the counter shows passing values while the column rises (as the NVIDIA block counted up); it stops on 75,599 MW.
- `Shell2` copies Jensen's `Shell` without the header fade, so `Jensen.tsx` stays verbatim; fold them into one later.
- The proportional blocks (post 9 A) keep the NVIDIA chart's 2 px inset a side, which takes a thin constant strip from every box.
