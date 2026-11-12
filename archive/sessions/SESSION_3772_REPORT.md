# Session 3772 report: the pages checked

Energy Research Warehouse (ERW). Chain 211, session 23 of 24, data machine (lab-desktop), 12 November 2026 12:27 to 12:52 UTC. Opus 5.5. Model spend USD 0. Requests: none to any publisher; production read only by the snapshots.

- **The local build of `wip/c211-code`** at `094148cc3`, the gate's own build (`runs/land_check/094148cc3...txt`):
  - **check-values:** 3 failures, all three known floors of main (`/deals`, `/learn/problems/know-your-grid`, `/digest`), 0 new (`cv_diff`). The ten "license needed" floors were met.
  - **check-routes:** 1 live page and 225 in review, 0 failed. **check-cross-checks:** 92 of 92. **check-csp:** 97 pages, 0 violations.
  - The same build, served again for the hand reads:
    - **`check-links.mjs`** over the pages this chain's tables feed (`/cost-of-power?view=allgrids`, `/datacenter`, `/board`, `/internal/health`, `/internal/findings`, `/ask`): 2,074 links, 1,802 addresses, 1 finding, 3 aliases.
    - **The All grids tab at 1280 and 390** with the internal cookie (`runs/s3764/shots/allgrids_1280.png`, `allgrids_390.png`). Outside ERCOT the Transmission and 4CP cell shows a filed figure where the row's utility files one (CAISO NP15 and ZP26: PG&E's $11.03/kW-mo, its filing on hover) and "not held" where it does not (SP15). The rendered tab holds 10 "licensed source needed" cells. Inputs left, results right; the 390 view keeps its layout.
- **The link finding:** `/datacenter#content` ("Skip to content") answers 404 on the local build, because `/datacenter` itself answers 404 there. Not a link of this chain's code; it goes to the note.
- **AccessLint was not run.** Its live audit cannot carry the internal view's cookie (the pages are in review, so a visitor's read is the in-review page), and its HTML audit takes the page as a string: the tab's HTML is 1.9 MB.
  - This chain's change to the tab is text inside the tab's existing tooltip component (`Tp`, `role="tooltip"`), with no new control or structure.
  - Carried to chain 212 as an audit through a browser the session drives with the cookie.
- **The two known floors read by hand,** as the state report says:
  - `/digest`: no issue since 6 November, until today's run writes one.
  - `/deals`: one checked number and one held by a license, the floor 10.
  - Both are known on main and moved by the catch-up run, not by this chain's code.

## Decisions made without you

- **No accessibility claim without an audit.** The report says it was not run, and why, rather than inferring the result.
- **The link finding goes to the note, unfixed:** the page that 404s is not this chain's.

## For Samuel's ruling

- None new.
