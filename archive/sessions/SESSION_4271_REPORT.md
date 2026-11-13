# Session 4271 report: Maryland held, Idaho and California read (chain 253, window 4)

13 November 2026, from about 17:52 UTC. Branch `wip/4270-forecast` (from `wip/4250-forecast`'s head). Model spend USD 0. Requests 108 to 112 of `runs/w4/probe.csv` (the probe's ceiling raised from 120 to 170 for chain 253).

- **California** (Revenue and Taxation Code 73, the solar new construction exclusion): leginfo.legislature.ca.gov answered a challenge page (HTTP 403) to the robots request itself. A refusal, honoured; no other request.
- **Maryland** (mgaleg.maryland.gov, no robots file; request 110): machinery and equipment used to generate electricity for sale is exempt from property tax, except that counties and municipalities tax 50 percent of its value (Tax-Property 7-237(a) and (b)). Held for every technology as a share of the base on the reader's own rate. Not modeled: land and buildings, section 7-514 (not read), small community solar (subsection (c)).
- **Idaho** (legislature.idaho.gov; robots read, ClaudeBot named only in a commented line; request 112): 3 percent of gross energy earnings for wind and geothermal, 3.5 percent for solar (63-3502B). Not held: the tool has no sale price (a ruling).
- **Tested**: node 36 of 36 (a Maryland test, all four technologies); tsc clean; forecast Python tests 23 passed.
- **The build** waits for the lock (`c227-gate2`, from 17:54).

## Decisions made without you

- Maryland's 50 percent is applied to the whole capital cost, as North Carolina's and Florida's shares are; the tip says land and buildings are taxed in full.

## For Samuel's ruling

- Idaho's tax on gross earnings: (a) not held [default]; (b) a sale price input with no default, the tax shown only when the reader types one.
