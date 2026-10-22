# Session 588: the tall render frame of the five-grid cards in two columns

Draft, written while the build lock was held by session 581; the measures and checks follow once the build is made.

## What was done

- `site/app/research/card/render.css`: in the tall frame (1080 by 1350, `max-aspect-ratio: 3/2`) the five panels of the small multiples stand in two columns (three rows, SPP alone in the last), and the box is as tall as its panels (`height: auto`), so the callouts begin under the lowest axis label. The wide frame, session 182's box heights and the card page are untouched.
- `site/components/svgchart.tsx` (the shared category chart): an area's base is held between the plot's top and floor, so on an axis whose floor is above zero (the right scale of the five-grid cards, 12k on CAISO's) the shading no longer runs below the axis and out of its panel. The line, the points and `data-points` are the series' own: no value moves.
- `site/scripts/check-findings-grids.mjs`: a new check in every render frame (four cards, two frames: eight checks) that the lowest chart text ends above the callouts' top (the paragraph's on a card without callouts).
- `tests/test_session588.py`: the rules held in the files.
