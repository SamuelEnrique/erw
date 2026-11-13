# Session 4272 report: Virginia held; Colorado and USDA not readable (chain 253, window 4)

13 November 2026, about 19:01 to 19:30 UTC. Branch `wip/4270-forecast`. Model spend USD 0. Requests 113 to 117 of `runs/w4/probe.csv`.

- **Colorado's sales tax exemption for renewable components** (39-26-724): leg.colorado.gov's robots file allows reading, but its statutes page links only to LexisNexis, which this chain does not read: not held.
- **Virginia** (law.lis.virginia.gov; its robots file, read by chain 239, asks a 10-second delay, and this was the host's first request since): Code 58.1-3660 exempts a solar project of more than 5 and less than 150 MW AC, interconnection request from 2019, from 80 percent of its assessed value in its first five years in service, 70 percent in the next five and 60 percent after (C(v), F), where the locality has no revenue share ordinance; with one, the exemption is whole and the revenue share (58.1-2636, not held) is owed (D). Held as a share of the base on the reader's own rate, with two new rule fields: a size band (`above_mw`, `below_mw`) and steps by operating year (`exempt_steps`), carried to the page's trimmed parameters, the Python file and the do-file.
- **EIA's default PV size is 150 MW**, outside the statute's band ("less than 150 megawatts"): the default Virginia solar case has no exemption, as the statute says; the tip names the band.
- **Tested**: node 37 of 37 (a Virginia test across the steps and the band; a replication pair at 100 and 160 MW, so the Python and Stata files run the steps); the fixture adds Virginia's JEDI rows (96); tsc clean; the forecast Python tests 23 passed (the trim keeps every rule field).
- **Built and read** under the build lock (waited 19:06 to 19:20 for window 2's `w2-s4011`; `origin/main` merged; built 19:21): Virginia solar at 100 MW and a 0.8 percent rate, USD 252,394 the first year (20 percent of the base); B at the default 150 MW, no exemption, USD 1.9 million; 1280 and 390 px without a sideways scroll or a console error. check-values 937 of 937 on the six addresses. The 179 related test files 2,222 passed, 0 failed.

## Decisions made without you

- Subsection F's steps are held over subsection D's flat 80 percent, as F applies "notwithstanding any provision to the contrary".

## For Samuel's ruling

- Virginia: (a) F's steps, 80, 70 and 60 percent [default]; (b) D's flat 80 percent; (c) a switch for a locality with a revenue share, the exemption whole and the revenue share held with a price path.
