# Session 3701 report: Research's replication a reader can run

Energy Research Warehouse (ERW). Chain 208, session 2 of 20, portable laptop, 6 November 2026, about 21:50 to 22:02 UTC. Branch `wip/3701-sellable` (worktree `Documents\erw-3701`, cut from `origin/main` at `0f544a79d`), head `29f9038ea`.

- **`replication/analysis/`**, in chain 158's form:
  - `figures_of_the_page.py` writes `page_figures.json` and `.csv`: the 78 figures `/research` prints (the twelve current cards' callouts, each with its Num check key, and the four figures of the weekly chart's finding sentence). It reads the cards' own files, as `check-values.mjs` does, and refuses when a callout's text is not the card figure `FIELDS` names.
  - `replicate.py` (standard library and pandas; the regressions' algebra is written out, no numpy import) recomputes them from the public CSVs and the week's chart file. **65 of 66 computed figures inside the tolerance**, 1 known difference, 10 "license needed", 2 not in a download.
  - The known difference: the weekly score, 87.25 against the page's 87.5, because `chart_of_the_week.json` holds 104 weeks, 102 earlier changes, and the rule ranked the change among 104.
  - Not in a download: `siting_gigawatt`'s months to connect (read from `interconnection_durations` by the All grids tab).
  - `replicate.do` covers the same card figures in the owner's Stata rules. Not run: no Stata here.
  - `assumptions.json` (35 assumptions, each with its default, unit, source and how to change it) and `assumptions.csv` (the numeric ones, with Stata names).
- **Test:** `tests/test_session3701.py`, 8 tests, OK in 10 s.
  - It builds the figures afresh from the cards, so a card the data machine recomputes never turns main red by itself.
  - The committed file is checked only for cards whose `computed_at` it recorded.
- **Read and not changed:** the cards, their CSVs, `site/lib/findings.ts`, `site/lib/license.ts`, the Roundup of W44 (the rule's pick, WTI).

## Decisions made without you

- "The page's keyed figures" are read from the cards' JSON (the files `check-values.mjs` holds the page to), not from a build. A build needs about 3 GB and is the landing's step.
- The ten callouts naming NYISO or ISO-NE are "license needed" on the page (`licenseHeldGrids`: ISO-NE, MISO, NYISO), so the replication prints those words and computes nothing for them.
- The weekly chart's figures are in `replicate.py` only. Its file is JSON, which Stata reads only with a package.
- Today's chart (the Digest's) and the five "also moved" sentences are not replicated: no download of `/research` holds their rows.

## For Samuel's ruling

- Four of the public CSVs hold rows of grids whose figures the page prints as "license needed": NYISO in `erw_2026_grids_spikes_batteries.csv` and `erw_2026_grids_peak_hour_solar.csv`, ISO-NE in `erw_2026_gas_share_hours.csv`, NYISO New York City in `erw_2026_impact_event_control.csv`, and MISO in `erw_2026_event_interchange_flips.csv`. Should those rows leave the downloads while the hold lasts? The files are the findings chain's.
