# Session 274 report: the Roundup's motion video

14 October 2026, 10:06 to 10:30 UTC, unattended, on lab-desktop (the data machine), the fourth session of the overnight chain of 14 October, built in a worktree (`../erw-274`) while session 273's pull of CAISO's history ran, and landed before it. Branch `task/274-motion`. Model spend USD 0: no model call. Pulls: npm (Remotion 4.0.535 and React 19.3.0), Remotion's headless Chrome (one download, 120 MB, from Google's public storage), and the three font families from Google Fonts at render time. No warehouse table, no page and no load changed. **Nothing was posted anywhere.**

## Read these first

- **A pipeline that turns a chart's own rows into a silent 10 to 20 second video, in the brand, at 1080x1350 and 1080x1080:** `motion/` (Remotion). `node specs.mjs` reads the chart files and writes a spec; `node render.mjs` renders each spec in both sizes with a still of its last frame. About 15 seconds a video on this machine.
- **The four motion types, chosen by the chart's kind:** draw-on (line charts), count-up (a scatter's fitted effect), roll call (stacked percent bars), reorder (ranked bars). A kind with no motion type stops the builder by name.
- **Fourteen proofs in `docs/research/motion/`** with a README: this week's chart (the newest chart of the week, 2026-W41: the Roundup of 18 October has not run) and the four strongest findings, plus two extra proofs so that each motion type is shown at least once. 11 MB in all.
- **"The four strongest" is a rule I wrote, for your ruling:** the findings with an effect table, ranked by the p-value of its first specification, one card a finding. It gives `batteries_curtailment_hourly`, `batteries_curtailment`, `batteries_lunch` and `impact_study`.
- **No permission prompt appeared.** npm 11 held back esbuild's install script (a default, not a prompt); esbuild's Windows binary came with the package and works, so nothing was approved.

## What to review

- `docs/research/motion/README.md`, then the stills: `chart_of_the_week_2026-W41_1080x1350_last.png`, `batteries_lunch_1080x1350_last.png`, `batteries_curtailment_1080x1350_last.png`, `who_rescues_whom_1080x1080_last.png`, `queue_divorce_1080x1350_last.png`. Then any `.mp4` beside them.

## The proofs

| Proof | Motion type | Seconds | MB (1080x1350, 1080x1080) |
|---|---|---|---|
| `chart_of_the_week_2026-W41` | draw-on | 15 | 0.54, 0.50 |
| `batteries_curtailment_hourly` | draw-on | 15 | 0.45, 0.45 |
| `batteries_curtailment` | count-up | 11 | 0.61, 0.54 |
| `batteries_lunch` | draw-on | 15 | 0.47, 0.45 |
| `impact_study` | draw-on | 15 | 0.49, 0.51 |
| `who_rescues_whom` (extra) | reorder | 14 | about 1.0 each |
| `queue_divorce` (extra) | roll call | 14.2 | 0.77, 0.75 |

## Checks

| What | Exit | Notes |
|---|---|---|
| `python scripts/precheck.py --what "session 274"` | 0 | six of six |
| `npm install --save-exact ...` | 0 | |
| `npx remotion browser ensure` | 0 | |
| `node specs.mjs`, `node render.mjs` | 0, 0 | fourteen videos, fourteen stills; the stills were looked at and three faults fixed (the top tick, the date labels, a bar chart's zero line) |
| `python -m unittest tests.test_session274` | 0 | 6 tests: every number of a spec is the source's, the rule's four, both sizes on disk, exact versions, no host asked by the code |

## Decisions made without you

1. **This week's chart is 2026-W41's,** the newest written (11 October); W42's is written on Sunday 18 October.
2. **A scatter becomes a count-up of its fitted effect:** the effect table's fullest specification (its last row), with the finding's own sentence beneath it.
3. **One series is left out of one video:** `batteries_lunch`'s hours at or above USD 1,000, a bar series on a third scale; the fleet keeps a right axis of its own. The spec names what it left out.
4. **The titles keep the cards' capitals,** as the findings write them.
5. **The pipeline is in `motion/` at the root,** beside `site/`, with its own `package.json` and `.gitignore`; nothing of it is in the site's build.
6. **Landed before session 273,** whose pull was still running: the two touch no common file.

## For Samuel's ruling

1. Where the videos go (the Roundup's email, a post), and on what schedule. Nothing posts today.
2. The rule for "strongest", or another.
3. The titles in capitals, or as sentences, in a video.

## Files

- New: `motion/` (`package.json`, `package-lock.json`, `.gitignore`, `specs.mjs`, `render.mjs`, `src/*.ts*`, `specs/*.json`), `docs/research/motion/` (the README, 14 videos, 14 stills), `tests/test_session274.py`, this report.

## The landing

- In session 273's report.
