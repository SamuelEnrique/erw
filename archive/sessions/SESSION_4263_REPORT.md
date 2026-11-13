# Session 4263 report: the cross-check adds a gas plant and Wyoming's taxes (chain 240, window 4)

13 November 2026, about 17:25 to 17:50 UTC. Branch `wip/4250-forecast`. Model spend USD 0. Requests 106 and 107 of `runs/w4/probe.csv` (docs.nlr.gov, its robots answer read at request 77). Item 5 of the list asked for a gas plant and a solar project; two web searches found no statewide JEDI study of a solar project with its own numbers on a host this machine may read, and one of a gas plant.

- **NREL/TP-6A20-57411** (2013; its fact sheet 57635 read first, which gives only the two states together): a 225 MW gas plant and a 900 MW wind plant in Wyoming, JEDI with the Wyoming Infrastructure Authority's local shares, Wyoming's own jobs (Tables 6 and 7, columns reassembled from the PDF's text and checked against their totals) and taxes (Tables 2 and 3). Added to `site/scripts/forecast-crosscheck.mjs` as two studies; the script now reads a study's capacity factor, the sales tax over the build and a later operating year's property line.
- **Results** (the model at each study's MW and cost, dollars of 2012, a year the study does not state): gas construction jobs 551 against 573 (0.96), operating 0.86, Wyoming sales tax 0.90; wind construction 1.03, operating 0.70 (the study counts landowner leases in its supply chain), sales tax 0.80 (the study's 6 percent on capital goods and materials), the wind generation tax 1.01 at the study's capacity factor.
- **Written**: the method note's table and its reading, `docs/reviews/forecast-crosscheck-2026-11-13.json` (130 lines added, the earlier studies unchanged), the review pack's part 4, the note. Tests: 27 passed (packs and forecast). No page code changed: no build needed.

## Decisions made without you

- The study's dollar year is not stated; 2012, the year of its writing and of its cost estimates, is used, which moves the construction comparison by about 2 percent a year of error in that choice.

## For Samuel's ruling

- None new.
