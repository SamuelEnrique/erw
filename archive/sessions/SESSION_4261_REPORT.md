# Session 4261 report: Wisconsin held (chain 240, window 4)

13 November 2026, about 15:32 to 16:15 UTC. Branch `wip/4250-forecast`. Model spend USD 0. Requests 100 to 103 of `runs/w4/probe.csv`.

- **Wisconsin** (docs.legis.wisconsin.gov; robots read first, no crawl delay, requests a few seconds apart; a first address in the statutes path answered 404 and the site's document address was used): the property of a light, heat and power company taxed under s. 76.28 is exempt from the general property tax (70.112(4)(a)); in its place the state pays the plant's municipality and county USD 2,000 per MW between them (79.04(6)(b) and (c)) and, for a plant on an alternative energy resource built after 2003, USD 1,500 per MW more to each since 2024 (79.04(7)(c)1). Held as a capacity rule of USD 5,000 per MW a year for wind, solar and geothermal of 1 MW or more; gas not held (its baseload payment rests on a definition not read).
- **Tested**: node 34 of 34 (a new test: wind, solar, under 1 MW, gas); tsc clean; the forecast Python tests 23 passed.
- **Built and read** under the build lock (waited 15:34 to 16:07 for window 2's `w2-s4008`; built 16:08): Wisconsin wind USD 1,000,000 a year (200 MW), solar USD 750,000 (150 MW), USD 25.0 and 26.3 million over the lives; 1280 and 390 px without a sideways scroll or a console error. check-values 937 of 937 on the six `/impact` addresses.
- **After merging `origin/main`**: the 179 related test files 2,218 passed, 56 skipped, 0 failed.

## Decisions made without you

- Wisconsin's payments are a state payment to the county and municipality, not a tax the plant pays; they are held on the property tax line, with the tip saying so, as what the localities receive in place of the plant's property tax.

## For Samuel's ruling

- Whether Wisconsin's shared revenue belongs on the property tax line [held there, with its tip], and whether the caps per resident (79.04(6)(d)) should be an input [not modeled].
