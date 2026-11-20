# The four problem sets on the whole country: the done line (chain 507, 19 November 2026)

Energy Research Warehouse (ERW). Chain 507, part E, on samueloldlaptop. The sets are on `wip/8901-problem-sets` (landing row 56 of `docs/state/landing_request_oldlaptop.md`), built in session 8901; their report is `docs/reviews/problem-sets-country-2026-11-19.md` on that branch. The done line is the form the five tools reached on 14 November (`queue/done/303-night-16-november-portable-trackers-done-line.md`): a complete method note, a replication that reproduces every figure, a cross-check against published figures, a decisions block, and a one-page summary for a reader. Each cell says done, waiting (for what) or not done (why).

| Set (address after landing) | Method note | Replication | Cross-check against published figures | Decisions block | One-page summary |
|---|---|---|---|---|---|
| Who trades with whom (`https://erw-flame.vercel.app/learn/problems/who-trades-with-whom`) | done: `docs/methods/problem_sets.md`, "The whole country", on the branch | done: `replication/problem_sets/replicate_country.py` (every answer from `site/data/regions/trade/ten.json` and `trade_matrix.json`; 0 of 113 figures differ across the four sets); `replicate_country.do` read, not run (no Stata here) | waiting: the trade figures are EIA-930's as each side reports them; a publisher's own monthly table to set them against is the next web read when the session's search allowance refills | done: the set's choices in the decisions fold, each with its default and source on hover (`page-file` and its own) | done: the table below |
| A storm across the country (`.../storm-across-the-country`) | done (as above) | done (as above) | in part: the set's figures are the event pages' own (browser read 433 sets question 1 beside Elliott's page); ERCOT's and TVA's own published peaks to stand beside them wait for the search allowance | done | done |
| What is under the ground and in the wind (`.../under-the-ground-and-in-the-wind`) | done | done | in part: each figure is the legend or summary the publisher's own file carries (`site/data/resources/manifest.json` names the NREL and other sources); browser read 434 sets the legends beside the map | done | done |
| Where energy goes (`.../where-energy-goes`) | done | done | waiting: EIA's MECS and Monthly Energy Review tables the file is read from, to be set beside it when the allowance refills | done | done |
| Your own balancing authority | not done: its files (`site/data/regions/authority/`) are not on main; the set waits, as the chain says | | | | |

## The one-page summary, for a teacher

- **Four sets, 27 questions and four worked examples**, for an introductory energy class, in plain words with no advice and no view. Each opens with a worked example by the method of one question, then six or seven questions from the easiest.
- **Every figure is read from the file the site's own page draws**, with a key that the site's value check recomputes (`pf|<file>|<path>`), and its file and path on hover. No number is typed.
- **Who trades with whom:** a region's imports by neighbour and month (Tennessee, October 2026), where the two sides' reports of one flow disagree and why that matters for a number you quote, and how many hours each side reported.
- **A storm across the country:** Winter Storm Elliott in Tennessee and the Carolinas beside Winter Storm Uri in Texas: the highest hour against the baseline, what ran, and what moved between regions.
- **What is under the ground and in the wind:** the resource map's layers and their units (sunlight, wind, geothermal, dams, biomass), and why a resource is not a power plant (a capacity is not an energy; a legend's top is a cell's mean).
- **Where energy goes:** energy by industry, by fuel and by state, from EIA's manufacturing survey and monthly review.
- **Not yet:** a dated edition with the students' and teacher's copies (data request 561); the cross-checks against publishers' own tables (the web reads resume when the search allowance refills).
