# Sessions 4255 and 4256 report: Wyoming, fault 20 (chain 240, window 4)

13 November 2026, about 14:05 to 14:16 UTC. Branch `wip/4250-forecast`. Model spend USD 0.

- **Wyoming** (the Legislature's title 39 PDF, wyoleg.gov, no robots file; request 81): the excise on producing electricity from wind, USD 1 per MWh at the point of interconnection (39-22-103 and 104), not owed until three years after a turbine first sold electricity (39-22-105(b)). Held as a production rule with exempt years that adds to the property tax: the reader's own property tax rate stays offered and is added to it, with its own tip. The Python and Stata files follow; a Wyoming replication pair passes; the fixture adds Wyoming.
- **Fault 20** (no MWh column for Wyoming: the column looked for "production" in a rule's id) fixed by the model reporting whether a production tax was applied, with tests.
- **Built and read** twice under the lock (14:07, 14:09): Wyoming's first operating year USD 0 (an exempt year), USD 14.4 million over the life; with the reader's 1.1 percent rate, USD 3.4 million the first year; the MWh column shown. check-values 785 of 785.
- **Tests**: the 180 related files 2,221 passed, 0 failed; node 28 of 28.
- **Landing row 4** moved to `3478cb30b` on main.
