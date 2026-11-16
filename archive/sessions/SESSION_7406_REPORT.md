# Session 7406 report: the deal tracker's cross-check, its do-file and its faults

Energy Research Warehouse (ERW). Chain 303, portable-laptop, 16 November 2026, about 10:00 to 10:10 UTC. Model spend: USD 0.

## What was done

- **The cross-check** (`docs/methods/crosschecks/deal_tracker.md`), in two parts. No figure adjusted.
  - **Counts and megawatts by year and kind beside published tallies.** CEBA (17 March 2026): 27.3 GW contracted by US companies in 2025. BloombergNEF (19 February 2026): 29.5 GW in the United States, 55.9 GW worldwide; Meta and Amazon 20.4 GW. The tracker: 3 power purchases dated 2025, none stating megawatts; 36 dated 2026, 14 stating 11,990.5 MW. LevelTen's public page gives price changes in percent only, and no deal held states a price, so there is no price to set beside one.
  - **The twenty largest AI-power rows against their stories' headlines**, as the lists stand today (they are not the twenty of 5 November: the capital deals left the dollar list, and four megawatt rows are new). **17 of 20 figures are in a headline of the row's own story**; 3 megawatt rows of 11 and 13 November could not be checked on this machine (their stories are not in its copy).
- **What the tables say:** the tracker is a reading of the news, not a tally of the market; where a row states a figure, the figure is its headline's; its weakness is what a row is (a pledge kept as a deal, a funding round tagged AI power).
- **Web reads** (rule 9): each host's robots file first, about 10:00 UTC; CEBA's crawl delay of 10 seconds kept. Facts with links, no quoted text. Not read: LevelTen's report (behind a form), S&P Global's tallies (behind a login).
- **The do-file** (`replication/deals/replicate.do`): six headline lines and the table by year and kind, expected values at its top (585 deals; 39 stating 43,119 MW; 298 stating US dollars; 217 tagged AI power; 0 stating a price). Not run: Stata is not on this machine. Its Python mirror, `replicate.py --headline`, prints the same lines.
- **The faults file** (`docs/reviews/deals-faults-2026-11-11.md`), rows 22 to 29: three rulings (22, 23, 28), four for the data machine (24 to 27), one open for a session with a build (29). The three `ruling` rows of 11 November restated in plain words with their defaults.

## The faults, in one line each

- 22: the table and the three views read a deal's grid two ways (ruling).
- 23: a folded pair drops a figure only the folded row states: 433 MW (ruling).
- 24: the capital view's file says 529 rows; the table holds 590 (data machine).
- 25: three of the ten largest dollar rows are a pledge, a plan or a bet (data machine; needs the key).
- 26: two compute contracts are still "other" and "offtake" (data machine).
- 27: a step toward a power purchase is kept as one, 1,200 MW (data machine; needs the key).
- 28: the energy-asset rule is written nowhere (ruling).
- 29: the first tab lists both rows of a folded pair (open: needs a build, because the value check reads the built page).

## Needs the key

- Rows 25 and 27, with the second reading of session 7405's report (USD 3.0 to 10.6).

## For Samuel's ruling

- Rows 22, 23 and 28, each with its default, and the three of 11 November: the method note's section 12.

## Decisions made without you

- All twenty rows of today's lists were read, not only "the ones that changed": session 1851's own list is on another machine, and the lists themselves changed.
- BloombergNEF's release is on its own site, whose robots file allows every path; Bloomberg's news pages, whose terms the license log holds as needing permission, were not read.

## Commit

- `wip/7400-trackers`: this session's commit, named in the progress file.
