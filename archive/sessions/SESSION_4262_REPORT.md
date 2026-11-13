# Session 4262 report: Nevada held (chain 240, window 4)

13 November 2026, about 16:15 to 17:25 UTC. Branch `wip/4250-forecast`. Model spend USD 0. Requests 104 and 105 of `runs/w4/probe.csv`.

- **Nevada** (leg.state.nv.us; robots read first, NRS pages allowed): where the Office of Energy's Director approves an application, a renewable energy facility's property tax is abated by 55 percent for the 20 fiscal years after approval (NRS 701A.370(1)(a)); approval needs construction jobs (50 or 75), a capital investment (USD 3 or 10 million) and wages (110 and 175 percent of the state's average), and the county may deny it within 30 days, else it is deemed approved (701A.365, the version in force through 30 June 2032; the page also prints the version from 1 July 2032, with the same tests). Held behind the local option's switch (off by default), on the reader's own rate: 45 percent of the tax charged for 20 years counted from the first construction year. The local sales and use tax abatement above 0.6 percent for 3 years is not modeled.
- **Code**: an own-rate exclusion can now need the option and last a number of years from the first construction year (model, Python, Stata).
- **Tested**: node 35 of 35 (a new test and a Nevada replication pair, solar and geothermal); the fixture adds Nevada's JEDI rows (96); tsc clean; forecast Python tests 23 passed.
- **Built and read** under the build lock (waited 16:19 to 17:14 for window 2's `w2-s4009` and a chain's `c227-gate`; built 17:15): Nevada solar with the abatement and a 1.1 percent rate, USD 1.25 million the first year (45 percent of the tax); B, Nevada wind without it, the whole rate; 1280 and 390 px without a sideways scroll or a console error. check-values 937 of 937 on the six addresses.
- **The review pack** names the statutes of sessions 4260 to 4262.
- **After merging `origin/main`**: the 179 related test files 2,222 passed, 56 skipped, 0 failed.

## Decisions made without you

- The 20 fiscal years after approval are counted from the first construction year (approval comes before the build).

## For Samuel's ruling

- None new.
