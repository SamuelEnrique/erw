# Session 806 report: the Roundup's five numbers and its chart

22 October 2026, 10:26 to about 10:36 UTC (the landing later, below), unattended, on portable-laptop (the code machine), in the worktree `C:\Users\samen\Documents\erw-806` on `wip/806-periodicals` (cut from `wip/805-periodicals`). Chain `queue/done/060-night-23-october-code-periodicals.md`, session 806. Model Fable 5.1. Precheck 0. Model spend USD 0 (the regeneration ran with `--no-model`). No warehouse data written, no web request, no past issue rewritten, nothing under `docs/roundup/` touched.

## Read these first

- **The Roundup opens with "The week in five numbers"** (`roundup.five_numbers`, after the line under the title): the week's biggest price move in percent among the main hubs' weekly means (both weeks complete, not held, not paused) and EIA's closes a week apart, with both values; the US48 peak with its hour; the week's largest deal by US dollars from `energy_deals` (by MW when no deal states dollars), with its parties, asset, type, date and row id; the largest new datacenter load first reported in the week from `datacenter_projects` (the policy actions carry no MW or price figure, so the queue or policy figure the chain asks for is the week's largest new load, said as such); and the headline figure of the week's chart from `docs/analysis/<week>/chart_of_the_week.json`. A number the warehouse does not hold is said missing.
- **Each of the five traces.** `scripts/check_roundup.py` reads the five lines (`five_checks`): the hub's two weekly means and the change, the two closes, the US48 hour, the deal's dollars or MW by its row id, the load's MW by its entity id, the chart's headline value from its record. The checker and the Roundup write a sum the same way (`usd_words`: "USD 12 billion", "USD 4.3 billion", half up) and a chart figure the same way (`chart_figure`: a count whole).
- **The chart of the week says where the week's stories point** (`roundup.chart_relevance`, through session 805's `daily_chart.relevance` over the rule's pick and the measures that also moved in the week's record): when the pick is the most related it says so; when another measure is, the section keeps the rendered picture (the rule's, drawn once a week on the data machine) and names the related measure with its finding and a link to `/research`. Fix 3's division rule stays his.
- **The real-time maximum says its interval length** ("a 15-minute interval", "an hourly interval") and that the grids' series differ in it, so the figure is the highest interval value held, not one measure across grids.
- **Each numbered list starts at one** (`brief.drop_repeated_items` restarts at a heading): since session 470 the Roundup's five would have been numbered 4 to 8 after the weekend's three.
- **Proved on W40 and W41 regenerated without the model** on this machine's tables (`docs/reviews/periodicals-roundup-regen-2026-10-23.md`): the five numbers of each week, the weekend and the five of the week before and after (with the "also" lines of session 802), and every line of the numbers and chart sections that differs. The price tables here end in late September, so W41's hub means and W40's are "not in the warehouse"; the week's price move came from EIA's closes; the deals, loads and charts are the committed tables and records.

## What to review

- `/roundup` after Sunday's issue: the five numbers under the title, the sentence under the chart, the interval words on the real-time line.
- `docs/reviews/periodicals-roundup-regen-2026-10-23.md`.

## Checks

| Check | Exit | Result |
|---|---|---|
| `scripts/precheck.py --what "session 806"` | 0 | on duty |
| `tests.test_session806` (14 tests) with 498, 470, 577, 192, 170, 802, 805 | 0 | 135 tests OK (skipped 2) |
| `runs/periodicals/s806_proof.py` (W40 and W41, `--no-model`, `--out` under `runs/`) | 0 | both written; the review file above |
| em and en dashes | 0 | none |

## The landing

**Not landed by this chain.** The branches land together through `wip/811-periodicals` (sessions 801 to 811 over `origin/main` at 11:13 UTC), gated by session 818 of the next chain after 16:15 UTC. The gate ran twice on `wip/807-periodicals` (sessions 801 to 807): the suite in a clean worktree passed (5,965 tests, 21 minutes), the build passed (173 s), and check-values read 12,412 of 12,423 values equal to the live set, with 13 failures: the ten license-hold floors of session 408's list (a pass by rule), `/digest`'s floor (the page carries no number until the day's issue is written, about 15:45 UTC), and two pages whose fetch timed out on the slow database (`/roundup`, `/cost-of-power?view=allgrids&profile=flexible`); 16 pages were not read in the 45-minute limit. The exact commands are under "To finish" in `docs/state/review_2026-10-24_portable.md`.

## Decisions made without you

1. **The queue or policy figure is the week's largest new datacenter load** (`capacity_mw` of `datacenter_projects`), since the policy actions table holds no MW or price in any of its 1,836 rows; the line says what it is.
2. **The deal is ranked by dollars first, MW second**, and the line says which.
3. **The rendered chart stays the rule's**; a more related measure is named, not drawn (drawing needs the data machine's tables and `run.py`).
4. **A held grid is not the price move of the week** (the board's rule, as session 804's movers).
5. **Sums print in the voice's form** ("USD 12 billion") and the checker reproduces it rather than the raw figure.

## For Samuel's ruling

- Whether the chart of the week should be re-drawn for the measure the stories point to (a change to `warehouse/analysis/run.py` on the data machine, which renders once a week), or stay the rule's with the sentence.

## Files

- Changed: `warehouse/news/roundup.py` (`chart_relevance`, `chart_of_the_week`, `interval_words`, `numbers` with `facts`, `usd_words`, `chart_figure`, `FIVE_HEADING`, `five_numbers`, `main`), `warehouse/news/brief.py` (`drop_repeated_items`), `scripts/check_roundup.py` (`FIVE*`, `usd_words`, `chart_figure`, `event_row`, `five_section`, `five_checks`, `checks`).
- New: `tests/test_session806.py`, `docs/reviews/periodicals-roundup-regen-2026-10-23.md`, this report. Not in git: `runs/periodicals/s806/` (the two regenerated issues).
