# Sessions 4220 to 4224 report: the three readers, Kansas, faults 14 and 15, landing request row 2 (chain 239, window 4)

13 November 2026, about 12:14 to 13:24 UTC. Branch `wip/4220-forecast` (built on row 1's `wip/4200-forecast`). Model spend USD 0.

- **4220 and 4221, the three readers**: an economic developer gets construction and operating output in A and B; a county assessor gets each operating year's MWh (where a production tax rests on it) and taxable value (Iowa's valuation, the reader's own rate) in the table by year; a utility siting analyst gets the taxes' present value in other states, the hover saying whether each state's property tax is counted. The model's years carry `mwh` and `value` (tested).
- **4222**: Texas's sales tax field names the Comptroller's partial exemption of generation equipment (Tax Code 151.318 as its letter rulings apply it); the statute could not be read as text (statutes.capitol.texas.gov builds its pages by script) and no share is held, so the default stays 0 as an upper bound, a ruling. **Fault 14** (the other states' runs carried the scenario's own state's defaults; found by the new chart's hover: every state had Minnesota's wind exemption) fixed with a test.
- **4223, Kansas**: K.S.A. 79-201, Eleventh, read from the Revisor of Statutes (ksrevisor.gov, robots first): wind, solar and geothermal property exempt for the 10 taxable years after construction for an application after 2016. A rule kind of its own: 0 for those years, no rule after (the life then has no total, not a misleading sum) unless the reader types a rate. The Python and Stata files follow; the replication test adds a Kansas pair; the fixture adds Kansas's JEDI rows.
- **4224**: built under the build lock (13:13 to 13:16) and read; **fault 15** found (the browser's trimmed parameters dropped the rule's `years`: Kansas read "not held"), fixed with a test that fails without the fix; read again: USD 0. check-values 78 of 78.
- **Tests**: the 179 test files that name what the stacks touch: 2,202 passed, 56 skipped, 0 failed (13:16 to 13:20). Node 24 of 24.
- **Landing request row 2** on main: `wip/4220-forecast` at `52dc1001a`, task `4220-forecast`, port 4210 (window B's gate of 13 November ran on 4200, so this window's reads moved to 4210).
- **The build lock** was held by window B's gates for most of 12:16 to 13:13; this window held it twice (12:39 to 12:42, 13:13 to 13:16).

## Decisions made without you

- A state whose property tax is not held for every operating year shows no life total (Kansas after its exemption): a sum of the held years would read as the life's.
- The siting chart counts each state's own defaults for every input the scenario does not set (its EIA cost, capacity factor, tax rates, exemptions).

## For Samuel's ruling

- **Texas's sales tax exemption for generation equipment**: the Comptroller applies the manufacturing exemption to turbines and modules but not to every item of a facility. Default: 0 exempt (the figure is an upper bound, and the field says so) until a share is read from the Comptroller's rulings or you rule one.
- **Kansas**: the exemption is granted by the Board of Tax Appeals on application. Default: assumed granted.
