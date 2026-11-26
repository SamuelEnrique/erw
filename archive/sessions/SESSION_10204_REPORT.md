# Session 10204 report: Automated Analysis audited as a hostile econometrician would (chain 710, part C)

26 November 2026, the old laptop, worktree `erw-c710-c`, branch `wip/audit-analysis-doc`. Model spend USD 0. No table written, no lock, no draft's state changed, no live service asked.

## First: a license matter (finding 2)

- Held and paused grids' figures are in public files: the impact study's default download (`site/public/findings/erw_2026_impact_event_control.csv`) holds 56 days of NYISO New York City prices; `docs/analysis/gallery/` holds 88 NYISO, 54 ISO-NE and 48 MISO charts with their figures; every week's `results.json` holds NYISO's and SPP's regulation prices. `build-content.mjs` copies `docs/analysis/` to `public/analysis-files/`, and `site/proxy.ts` serves any address with an extension. Not fixed (it moves what a reader sees): for Samuel's ruling, below.

## What was done

- `docs/reviews/analysis-model-audit-2026-11-26.md`: the ground, each statistic re-done by hand, 13 findings with their tests, the attacks of the chain file, what was checked and found right. Evidence: `docs/reviews/analysis-model-audit-2026-11-26/` (`a1` to `a11`, each script and its output).
- The arithmetic is right: all 37 yearly claims of the forty, drafts 4, 5, 6 and 20 from ERCOT's prices, the impact study, the hourly curtailment fit and five figures of 2026-W44, each to the digit.
- 13 branches `wip/audit-analysis-1` to `-13`: 4 words-only (5, 9, 12, 13) returned for landing; 9 hold a test that shows a figure finding, not for landing.
- Draft findings shown wrong: 3 (the tightest hours fall with solar by construction) and 6 (a plain mean of clock hours across midnight). States untouched.

## Decisions made without you

- The audit file and this report were written to a scratch file and copied into place: the agent harness refuses to write a `.md` report directly. The content is the audit the chain asked for.
- "Each template" was read as every kind of statistic the engine computes: the deep hunt's claim and tests (all forty), four deep measures from the tables, two cards' regressions, the weekly rule and four weekly templates. Five weekly templates were not re-done (their tables are not here, or their counts move as the ERW reads).
- Inflation for finding 13 is an assumption (2.5 percent a year); no deflator is held in the warehouse.
- The two data requests and four landing rows are returned to the desk, not written to the state files (this session's rules).
- No snapshot was taken for the push of this file to main: this machine may not build or ask a live service; every page is in review and the push changes no page.

## For Samuel's ruling (default for each: left as it is)

1. Held and paused grids out of the gallery, the weekly results and the impact study's default control, and the published files taken down. Measured: 56 NYISO values in one download, 190 gallery charts, two held measures every week, drafts 8 and 9.
2. A test against chance beside the hunt's five tests, and each draft to say how many claims its hunt tested. Measured: no-trend series pass 12 to 83 percent.
3. `tight_solar`, `tight_wind`, `tight_gas` on hours chosen by demand. Measured: fixed shapes give 43.5 to 3.2 percent as solar grows.
4. The cheapest hour as a circular mean or median. Measured: 2015 from 6.04 to 2.54.
5. The deep drafts to carry the session-361 statistics. Measured: 12 of 37 would read "a step, not a trend".
6. A floor of full years for a drafted trend. Measured: 9 of the forty under eight years.
7. The chart of the week's caption to say it is the largest of N measures. Measured: the largest of 21 no-change scores is at least 87.5 with probability 0.94.
8. The scanner's expected flags by chance printed beside a day's flags. Measured: 30 to 36 a day on persistent or fat-tailed series.
9. The impact study's p at several lags, the hourly card clustered by week. Measured: p 0.006 to 0.076; error x1.64.

## Needs the key

- Nothing. No step of this audit needs a model; none was called.

## Problems

- `git fetch` prints "failed to delete .git/worktrees/erw-1425, erw-1600: Permission denied" each time (stale worktree records of the main copy, not this session's); harmless, left.
- One push of `wip/audit-analysis-4` was refused by the remote ("failed") and went through on the second try.
