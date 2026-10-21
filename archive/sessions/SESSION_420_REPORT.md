# Session 420 report: the findings pipeline and the first LinkedIn material

Night of 20 October 2026 (from 01:10 UTC on 21 October), unattended, the Fable run on the portable laptop (`portable-laptop` in `.erw/machine.json`, role data; host name Samuel). Branch `wip/findings-oct20` on GitHub, from `origin/main` at `dc4d5ba6`. No merge to main, no deploy, nothing written to Supabase or Redivis, no warehouse table written, no pull of a publisher. Model spend USD 0 (no model is called by anything built here). Session number 420: the code machine's afternoon chain holds 401 to 415 and the data machine's night chain 384 to 386; the next free number above 415 was taken, as that chain's rule says, with room left for the code machine's 416 to 419.

## The claim check, and the track

- **Track A.** `queue/next/` and the three newest reports (385, 380, 379) were searched for "findings", "Roundup chart", "/internal/findings" and "LinkedIn". The only hit is session 407 of `queue/next/015-day-20-october-code-pm.md` (ten LinkedIn posts from check-values keys, queued for the code machine, not started): it is not the findings hunt, the Roundup chart or `/internal/findings`, and no `wip/` or `task/` branch on GitHub names findings. No other machine has findings work queued or in progress, so this session took Track A. Track B (the cross-check tables) was not done.

## The ten findings, one line each (number, table, license)

In the hunt's order (strongest first; a topic the ERW has shown before ranked after the new ones). Every table is public in `warehouse/metadata/coverage.csv`; no finding reads an internal table, so none is marked internal.

1. `ercot-battery-discharge-by-month`: ERCOT's batteries discharged 770,026 MWh in September 2026, from 338,301 MWh in December 2024; up in 21 of 21 later months (`storage_daily_cycle`, public).
2. `ercot-battery-evening-share-by-month`: 85.8 percent of ERCOT's battery discharge in September 2026 fell between 5 PM and 10 PM local, from 47.6 percent in December 2024 (`eia930_all_storage`, public).
3. `caiso-curtailment-this-year`: CAISO curtailed 5,115,404 MWh of wind and solar from 1 January to 29 September 2026, the most of any such window held; 3,452,749 MWh in 2025's (`caiso_curtailment_daily`, public).
4. `pjm-queue-withdrawn-share-by-cohort`: 63.3 percent of the MW that entered PJM's queue in 2019 had withdrawn by the end of 2025, from 88.7 percent of 2010's cohort (`lbnl_interconnection_queue`, public).
5. `caiso-battery-discharge-by-month`: CAISO's batteries discharged 1,335,586 MWh in September 2026, from 1,105,004 MWh in September 2025 (`storage_daily_cycle`, public).
6. `ercot-queue-entries-record-year`: 85,405 MW entered ERCOT's queue in 2024, the most of any year LBNL records; 66,858 MW in 2023 (`lbnl_interconnection_queue`, public).
7. `caiso-queue-withdrawn-share-by-cohort`: 60.0 percent of the MW of CAISO's 2019 cohort had withdrawn by the end of 2025, from 83.4 percent of 2010's (`lbnl_interconnection_queue`, public).
8. `ercot-hb_west-negative-hours-this-year`: 15.95 percent of the West hub's 15-minute intervals from 1 January to 25 August 2026 priced below zero, the highest of the 12 such windows held; 13.49 percent in 2022's (`ercot_all_hub_prices_history`, public).
9. `caiso-curtailment-share-by-year`: 4.53 percent of CAISO's wind and solar output was curtailed in 2025, from 0.67 percent in 2015 (`caiso_curtailment_daily`, public; shown before: the hunt's draft of 13 October, block 19).
10. `ercot-peak-premium-by-year`: ERCOT's peak premium, the median evening price minus the median midday price at the hub average, was 14.52 USD per MWh in 2025, from -0.16 in 2015 (`ercot_peak_premium_annual`, public; shown before: the thesis page and the peak premium explorer).

## Files, and where they live (branch `wip/findings-oct20` on GitHub)

- `warehouse/analysis/findings/hunt_oct20.py`: the hunt (`hunt`, `check`, `state`), the three claim kinds and their tests, the families, the files and the caption.
- `warehouse/analysis/findings/brand_chart.py`: the two pictures per finding in the brand (docs/brand.md in matplotlib).
- `warehouse/analysis/fonts/`: Source Serif 4 (400, 600), IBM Plex Sans (400, 500, 600), IBM Plex Mono (400, 500), static instances built with fontTools from Google Fonts' OFL files, with the three OFL texts.
- `docs/findings/2026-10-20/index.json` and, one folder a finding, `docs/findings/2026-10-20/<slug>/`: `finding.json`, `extract.csv` (the exact rows the headline comes from), `series.csv`, `check.do`, `caption.md`, `chart_square.png` (1200 by 1200), `chart_wide.png` (1600 by 900).
- `docs/roundup/drafts/2026-W43.md`: the Roundup draft for Sunday 25 October: findings 1 to 3 as the issue, finding 1's wide chart as the chart of the week. Nothing sent. (`docs/roundup/drafts/` is new: no Roundup drafts folder existed; `roundup.py` writes the issue itself on Sunday and does not read this file.)
- `site/components/analysis/HuntReview.tsx`, `site/app/internal/findings/page.tsx` (the section added in both branches of the page), `site/app/internal/findings/local/route.ts` (the gated file route), `site/scripts/build-content.mjs` (`findings_review` in the bundle; the folders copied to `site/content/findings/`, gitignored), `site/lib/markdown.ts` (the types), `site/next.config.ts` (the trace of `content/findings/**` for the route), `site/.gitignore`.
- `docs/methods/automated_analysis_findings.md`: the section "The findings hunt of 20 October 2026".
- `tests/test_session420.py`: 18 tests (the record test on made-up series, the monthly trend, every committed finding's files, caption, do-file, chart sizes and headline, the site's wiring).
- This report. On this machine only (not in git): `runs/hunt_oct20_dry*.out`, `runs/hunt_oct20_run*.out`, `runs/s420_tsc.out`, `runs/s420_tests.out`.

## What did not hold up, and why

- Candidates: 27 claims computed, 17 passed their tests, 10 kept (the index's `candidates_list` names every one with its reason).
- Houston hub, hours below zero by year: fails "half the change remains without the first year" (2015 carries it).
- The West hub's basis to the hub average: the median 15-minute difference is 0.00 in every year but 2025; no claim.
- The day-ahead premium at the hub average: fails the change of window and the strength floor.
- The record months: CAISO's curtailment (April 2026 over May 2026) and ERCOT's and CAISO's discharge (August 2026 over the month beside it) stand under 5 percent above the previous record; the margin test fails. The monthly trends above take their place.
- The waits to operation by cohort: CAISO's cohorts hold under 15 completed projects (the sample floor); ERCOT's and PJM's changes are under one typical move.
- Henry Hub (the year's mean, days under USD 2.00, this year's window) and Brent against WTI (by year and by window): no record in 2025 or in 2026's window.
- The hub average's yearly mean price: 2025 is neither the high nor the low since 2015.
- Three hub claims that pass (the hub average's, North's and South's hours below zero by year; the hub average's intervals at USD 100 or more) and ERCOT's withdrawn share by cohort fell outside the ten, by the rules (one hub of a grid for the negative-hours story; two of a family; ten in all; shown-before topics last).
- Not run at all: large-load waits (`large_load_statements` is internal and not on this machine) and demand growth since 2018 by balancing authority (`eia930_daily_demand` is not on this machine, and its copy of `eia930_all_history` holds six months of 2018). The ERCOT price history on this machine ends on 25 August 2026 and the daily tables on 30 September; the hunt computed from the tables as this machine holds them (restored copies of 28 September to 20 October), and every file says when it was computed.

## Checks

| What | Exit | Notes |
|---|---|---|
| `scripts/precheck.py --what "session 420" --dry-run` | 0 | 6 of 6 (run late, dry: the machine was not put on duty) |
| `scripts/freeze.py status` | 0 | no freeze; no deploy was made anyway |
| `hunt_oct20.py hunt` | 0 | 27 candidates, 17 passing, 10 kept, 10 folders written |
| `hunt_oct20.py check` | 0 | every do-file's logic in Python reproduces its headline and its comparison, 10 of 10 |
| `python -m unittest tests.test_session420` | 0 | 18 tests |
| `eslint` on the six changed site files | 0 | |
| `tsc --noEmit` (site) | 0 | `runs/s420_tsc.out` |
| `python -m unittest discover -s tests` | SUITE_EXIT | SUITE_NOTE |

## What waits for Samuel, in plain words

- Open `/internal/findings` on the branch's preview (or a local build of the branch: `cd site && npm run build && npm start`, then `/internal/open`): the section "The findings hunt of 2026-10-20" lists the ten with their state, tests, pictures, caption and downloads.
- For each finding: download `extract.csv` and `check.do` into one folder, run `check.do` in Stata, compare the printed headline with the expected value in the do-file's second line, then on the branch run `python warehouse/analysis/findings/hunt_oct20.py state <slug> stata_checked` (or `approved`, or `rejected`) and commit. The page shows the committed state; it has no button, because the hunt's findings are files on a branch and not rows of the review list.
- The LinkedIn material: `chart_square.png` and `caption.md` of each approved finding. Nothing is posted by anything built here.
- The Roundup of Sunday 25 October: `docs/roundup/drafts/2026-W43.md` holds the three findings and the chart of the week; fold it into the issue, or approve finding 1 and choose it, once its do-file has run.
- Rulings: (1) whether a monthly trend whose two ends are different seasons (findings 1, 2 and 5) may be published as it stands, with the caveat sentence, or only as a same-month comparison; (2) whether a record set in 2024 (finding 6, from LBNL's 2026 edition) is news enough for a caption; (3) whether the two shown-before findings (9 and 10) go out again in this form; (4) the fonts in `warehouse/analysis/fonts/` (1.6 MB, OFL) stay in the repository, or move to the machines' font folders.

## Decisions made without you

1. **Track A**, from the claim check above.
2. **The findings are files on the branch, not rows of `public.scanner_drafts`**: the session may not write Supabase, so the states live in `finding.json` and `index.json`, changed by a command and a commit, and the page reads the committed bundle.
3. **Records and windows beside the weekly hunt's trend**, with four tests (history of 5 years or 12 months, a complete record period, no gap in the window, a 5 percent margin), and the monthly trend (the hunt's five tests over complete months) for the battery series, whose history is 23 months.
4. **The extract holds the headline period and the comparison period at the table's own grain**, not every period's rows: the West hub's extract is 45,496 15-minute rows (1.4 MB); every row the headline uses is there, and `series.csv` holds the rest of the series.
5. **The three brand fonts were fetched** (nine requests to GitHub's raw and API hosts for Google Fonts' OFL files) and instantiated as static weights: the brand names them and the machine did not have them; matplotlib cannot pick a weight from a variable font.
6. **The ERCOT queue record is 2024's**, kept because LBNL's edition ends at 2025 and the hunt counts the last two years as recent for a yearly record of an edition-based table.
7. **One light clause a family** (`TAGLINES` in `hunt_oct20.py`) is written in the module, never by a model, and states nothing causal.
8. **The session number 420**, as above.

## Anything that broke

- BROKE_NOTE

## Last two commands

`git push origin wip/findings-oct20`, then `.venv\Scripts\python.exe scripts/chain_queue.py next`.
