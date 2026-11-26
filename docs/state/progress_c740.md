# Progress of chain 740 (lab-desktop, third window): datacenters in the Economic impact tool (`/impact`)

Chain file: `queue/done/740-night-26-november-desktop-window3-impact-datacenters.md`. Folder `C:\Users\Shared\Documents\erw-w3`. One line a source, a figure, a rule, a view or a request, with its state and session. States: done, waiting (and on what), not started, held (and why).

## The start

| Step | State | Session | Note |
|---|---|---|---|
| Precheck | done | 10800 | from this worktree it failed `daily_cap` (a worktree holds no cost ledger, as memory said); rerun at once from the main folder with the main folder's Python: passed, 6 of 6 (it relabelled the machine's duty from "session 10000" to this chain's, harmless) |
| Free disk, memory | done | 10800 | C: 31.7 GB free of 511 GB; memory 6.1 GB free of 15.7 GB (26 November 2026, 10:56 UTC) |
| Chain file taken by hand | done | 10800 | `b74844b6a` |
| Resume file `queue/next/741-resume-chain-740.md` | done | 10800 | pushed alone |
| This progress file | done | 10800 | |

## Part A: the ground

| Item | State | Session | Note |
|---|---|---|---|
| What the tool holds today | done | 10800 | `docs/reviews/impact-datacenter-sources-2026-11-26.md` section 1. The datacenter sales tax exemptions of the note's section 4 are prose only: no addresses, no quotes, no rows in `sales_exemptions.json`; read again |
| The method modeled on (LSU CES) | done | 10800 | section 2: LEIM is RIMS II based, a subscription; LEAP places it third of four components |
| Sources: jobs and wages | done | 10800 | CBP 518210 by state (held, public) used; QCEW refused; JLARC's figures for ranges |
| Sources: announced projects | done (first pass) | 10800 | 8 agencies' hosts readable; gov.texas.gov, michigan.gov, georgia.org, DigitalBridge refuse |
| Sources: construction cost per MW | done | 10800 | JLARC Table D-1 split (6.1, 19.6, 68.2, 6.1 percent); no public cost per MW: from part B |
| Sources: multipliers | done | 10800 | JEDI none (12 families); RIMS II USD 520 a region, USD 160 an industry (paid); IMPLAN no printed price; Virginia's JLARC tables public |
| Sources: taxes by state | in progress | 10800 | Virginia (exemption, property classes, consumption tax), Louisiana (rebate), Iowa (exemption) read; Indiana's statute behind a script; West Virginia's code host times out (waiting) |
| Verdict | done | 10800 | five lines at the top of the review |

## Part B: the evidence table of announced datacenters

| Item | State | Session | Note |
|---|---|---|---|
| Rows transcribed, every quote checked against the kept text | done | 10801 | 22 rows, 10 states (LA 2, VA 3, MS 5, NC 1, PA 1, IN 2, WV 3, KY 1, AL 3, OK 1): `warehouse/forecast/datacenter_announced_rows.json`, `datacenter_announced.py --verify-reads` |
| `site/data/forecast/datacenter_announced.json` with the defaults | done | 10801 | investment per MW: 6 rows, median USD 8.33 million (3.0 to 46.8); permanent jobs per MW: 5 rows, median 0.208 (0.05 to 0.333); permanent jobs per USD billion: 16 rows, median 56.25 (9.3 to 121.8); construction jobs (headcount as announced) per USD billion: 6 rows, median 325 (63 to 1,218) |
| Request for window A: `datacenter_announced` | requested | 10801 | row 6 of `docs/state/data_requests_forecast.md` |
| Wages by state (CBP 2023: 518210 operations; 2362 and 238 construction) | done | 10801 | `site/data/forecast/datacenter_wages.json`, 51 states; request 7 asks window A for the construction rows as a table |
