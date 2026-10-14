# The Roundup's motion video: proofs

Energy Research Warehouse (ERW), session 274 (14 October 2026). Silent videos of 10 to 20 seconds, drawn from the rows that draw a chart, in the brand of `docs/brand.md` (Source Serif 4 for the title and the headline number, IBM Plex Sans for text, IBM Plex Mono for figures, cardinal the only accent, on white). Two sizes each: 1080x1350 and 1080x1080. **Nothing here is posted anywhere.**

## The proofs

| Video (each at 1080x1350 and 1080x1080) | Drawn from | Chart kind | Motion type | Length |
|---|---|---|---|---|
| `chart_of_the_week_2026-W41` | `docs/analysis/2026-W41/chart_of_the_week.json`, its `chart` (the newest chart of the week: the Roundup of 18 October has not run) | line | draw-on | 15 s |
| `batteries_curtailment_hourly` | `site/data/findings/batteries_curtailment_hourly.json` | lines | draw-on | 15 s |
| `batteries_curtailment` | `site/data/findings/batteries_curtailment.json`, its effect table | scatter | count-up | 11 s |
| `batteries_lunch` | `site/data/findings/batteries_lunch.json` | line with the fleet | draw-on | 15 s |
| `impact_study` | `site/data/findings/impact_study.json` | line with a marked window | draw-on | 15 s |
| `who_rescues_whom` (extra proof) | `site/data/findings/who_rescues_whom.json` | bars | reorder | 14 s |
| `queue_divorce` (extra proof) | `site/data/findings/queue_divorce.json` | stacked bars, percent | roll call | 14 s |

- Each video has a still of its last frame beside it (`<name>_last.png`): the quickest look.
- **"The four strongest findings"** is a rule, written in `motion/specs.mjs`: of the committed findings, those with a tested effect (an effect table), ranked by the p-value of the table's first specification, smallest first, one card a finding. Today: `batteries_curtailment_hourly` (1.5e-74), `batteries_curtailment` (1.7e-19), `batteries_lunch` (1.4e-5), `impact_study` (0.07). The other findings have no effect table and no p-value to rank by.
- **The two extra proofs** are there because the five above use only two of the four motion types; they show the other two on findings whose chart kind calls for them.

## The four motion types, and how one is chosen

The chart's own kind chooses (`KIND` in `motion/specs.mjs`):

| Motion type | What moves | Chart kinds |
|---|---|---|
| draw-on | the chart is drawn along its x axis; the lead series' newest value rides the head; each series is named at its end when the drawing is done | `line`, `lines`, `line_with_fleet`, `flag_line` |
| count-up | the headline number counts from zero to its value, then the finding's own sentence | `scatter`: a scatter's message is its fitted effect, the effect table's last (fullest) specification |
| roll call | each row takes the frame in turn while the list scrolls behind it | `stacked_bar_pct`: each category with the first series' share |
| reorder | ranked bars move from one ranking to another as their values change | `bars_free` (the first series, then the second), `grouped_bar` (the first year, then the last) |

A kind with no motion type (`multiples`) stops the builder with its name: nothing is drawn in a form not decided.

## Every number is the chart's

- `motion/specs.mjs` copies the values, labels, units and source line from the file; it rounds nothing beyond the chart's own decimals and fills nothing. The count-up's number is the effect table's coefficient, shown to the units its sentence uses.
- **One series is left out of one video:** `batteries_lunch`'s "Hours at or above USD 1,000/MWh", a bar series on a third scale of its own (`leftOut` in its spec). The fleet, on the chart's right scale, keeps a right axis of its own.

## Running it

```bash
cd motion
npm install                       # Remotion 4.0.535, React 19.3.0 (exact versions in package.json)
npx remotion browser ensure       # Remotion's own headless Chrome, once a machine
node specs.mjs                    # specs/<id>.json from the chart files
node render.mjs                   # docs/research/motion/<id>_<w>x<h>.mp4 and _last.png
```

- About 15 seconds of rendering a video on lab-desktop; the fourteen took 3.5 minutes.
- The fonts come from Google Fonts at render time (`@remotion/google-fonts`), each under the SIL Open Font License.
- npm 11 held back esbuild's install script; esbuild's own Windows binary came with the package and works without it, so nothing was approved.

## For a ruling

- Where the videos go (the Roundup's email, a social post) is not decided here: nothing posts.
- Whether a finding's title stays in capitals in a video (the cards are set that way).
- The rule for "strongest", or another.
