# Session 9901: ERW video posts, batch 2 (nine posts, two options each, three shapes)

Desktop, unattended, 25 November 2026, 07:25 to about 08:40 UTC. Worktree `C:\Users\Shared\Documents\erw-w-9901`, branch `wip/linkedin-posts-2026-11-25` (from `origin/wip/linkedin-posts-2026-11-24`, `af4deceef`). Not merged. Nothing posted, published or deployed; main, the site, `site/lib/release.ts`, Supabase and Redivis untouched. Model and API spend USD 0 (no Claude API call, no paid service).

## Read first

- Review page: `docs/reviews/linkedin/posts-2026-11-25.md` (one comparison image a post, every number with its table and source, status).
- Comparison images: `docs/reviews/linkedin/img/batch_2026-11-25/<post>_options.png`.

## What was built

- Section 2 in place first: `motion/src/Jensen.tsx` and `motion/specs/posts/nvidia_energy_blocks.json` extracted byte for byte from the prompt's code blocks; `Root.tsx` routes `blocks` and `ladder`.
- Regression check: NVIDIA's last frame at 1080 x 1080 and 1080 x 1350 (scale 2) opened and read; every item in section 2d matches (header, two-line title, cardinal block with $952B, nine grey blocks with their values and counts, no percentages, three-line source). The NVIDIA post was not re-rendered as a deliverable.
- `motion/src/Batch2.tsx`: the approved look with header and title visible from frame 0 (`Shell2`), and ten chart types: columns, year line or area, weekly line, clock shift, day curves, fill block, flow band, staircase, 100-square grid, ladder, proportional blocks.
- `Root.tsx`: routes the Batch2 types; `canvasHeight` places the 1080 x 1350 layout on a 1080 x 1920 fog canvas, 200 px down, for Instagram.
- `motion/batch_9901.mjs`: stills at chosen frames and videos in the three shapes, scale 2, thumbnail = last frame.
- All nine posts, options A and B, three shapes: 54 videos (H.264, 450 frames at 30 fps; 2160 x 2700, 2160 x 2160, 2160 x 3840) and 54 thumbnails in `docs/research/motion/posts/batch_2026-11-25/<post>/`.
- Data: one file a post in `docs/research/motion/posts/batch_2026-11-25/data/`, written by `scripts/build_9901.py` from the ERW tables and the reproduce runs saved beside them.

## Numbers

- Every reproduce script rerun on today's tables (sections 1, 3, 8, 10, 21, 24, 37): every value equals the 24 November runs. Post 1 rerun of `thanksgiving_peaks.py`: summary identical.
- Numbers that differ from section 5: none. Post 1: Plains 9, Midwest 7, Mid-Atlantic 7, New York 5, Texas 4, New England 3, California 0 hours, as given. Post 2: $2.10, $3.40, $3.65, $3.29, $3.04, $3.06, $3.64 (3.642), as given; 2022 is 3.648, so nothing says record. The old spec's 2026 value ($3.81, 16 November) is replaced.
- Post 2's week of 23 November 2026 comes from EIA's API (read 07:29:55Z): the ERW table on this machine ends at 16 November. All 359 overlapping weeks equal the table.
- New numbers not in section 5: post 1 B (PJM average day: 94,247 MW at 7 pm, 86,132 MW at noon) and post 9 A (2025 production by country). Both from ERW tables, in their data files.

## Checks

- Final frame of all 18 options opened in each of the three shapes; four evenly spaced frames (0, 110, 220, 330) of each option opened in square. Fixed after looking: three titles on three lines (posts 3, 5, 8), a year range broken at its hyphen, touching labels (columns in MW, staircase total, line-chart first labels), a missing 2026 label, two labels past the right margin, the ladder's label over the title, a figure shown before its fill finished (post 8 A).
- Every still now: title two lines, source at most three lines, nothing clipped or spilling, one cardinal element, figures equal to the data files.
- Text-size exceptions (under 15 px at 1080 scale): none. Smallest text is 18 px (axis ticks, clock-time labels, the "MW" under column figures is 19 px).
- Line charts that do not start at zero: none. Every axis starts at zero.
- Videos probed with ffprobe: (filled in below).

## Instagram safe area (an assumption, not measured)

- The 1080 x 1350 layout sits on a 1080 x 1920 fog canvas from y = 200 to y = 1550, as the prompt asks; that Instagram's buttons and caption leave this band clear is a design assumption.

## Skipped or blocked

- Nothing blocked. Post 8 A uses the prompt's fallback (100 squares) because the ERW table holds no country of origin.

## Open questions for Samuel

- Post 1 B averages the 21 normal Thursdays and 7 Thanksgivings for PJM (marked needs ruling); the plan said one Thursday. A single pair of days is a one-line change.
- Post 2: is a value read from EIA's API (the table's own source) acceptable before the ERW table holds it, or should the post wait for the table?
- Post 8 A and post 6 A share a chart type (100 squares) because the fallback forces it. An alternative from the table: two proportional blocks, U.S. origin 3.4 million lb against foreign origin 43.5 million lb.
- Posts 8 A and 9 A show the latest year under a title that spans the period (each says "2025" in the chart). Keep, or give A its own title?
- Titles changed from the proposals: post 3 "California's battery power vs peak-day demand, 2019-2025"; post 5 "Power demand in Dominion's Virginia zone, 2019-2025"; post 8 "U.S.-origin share of uranium for U.S. reactors, 2003-2025".
- Post 5 A: steps rounded one by one sum to 3,715 against a total of 3,716 (said in the source line). Prefer steps from rounded levels (2023 would read +158)?
- Post 7 A: the counter shows passing values while the column rises (as the NVIDIA lead counted up); it stops on 75,599 MW.
- `Shell2` is a copy of Jensen's `Shell` without the header fade, so `Jensen.tsx` stays verbatim; fold them into one when convenient.
- The proportional blocks (post 9 A) keep the NVIDIA chart's 2 px inset a side, which takes a constant strip from every box.
