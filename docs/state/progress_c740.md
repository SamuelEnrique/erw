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

## Part C: the model

| Item | State | Session | Note |
|---|---|---|---|
| The four plant types pinned before the first edit | done | 10802 | `site/scripts/test-impact-pins.test.mjs`, `tests/fixtures/forecast/plant_pins.json` (32 technology-state runs, 16 figures each), branch `wip/c740-impact-datacenter` |
| `site/data/forecast/datacenter_rules.json` | done | 10802 | JLARC's split, refresh (5 years), build (18 months), Virginia multipliers; Virginia, Louisiana, Iowa rules; 14 quotes verified against the kept text |
| `site/lib/dcimpact.ts` (first written to `site/lib/datacenter.ts`, which is `/cost-of-power`'s library: overwritten on the wip branch only, restored byte for byte in session 10803, never on main) | done | 10802, 10803 | on-site jobs and earnings, Virginia's chain, property (building, equipment), sales before, forgone and paid, income, electricity (Virginia), present values, check keys |
| Tests: three announced projects, tax lines by hand | done | 10802 | `site/scripts/test-datacenter.test.mjs` (12 tests by session 10805), `tests/test_session10802_datacenter.py` |

## Part D: the page and the notes

| Item | State | Session | Note |
|---|---|---|---|
| "Datacenter" in the project types: fields, announced projects to pick, A and B, years, other states, CSV, Python, Stata | done (code) | 10803 | `site/lib/dcui.ts`, `site/app/impact/Datacenter.tsx`, `site/app/impact/Forecast.tsx`, `site/lib/dcfiles.ts`; tsc clean for these files; 109 tests touching `/impact` pass |
| check-values: `datacenter|` keys, two new addresses | done | 10803 | `site/scripts/check-values.mjs` |
| `forecast.md` section 13 with its decisions block | done | 10804 | pushed to main |
| Cross-check | done | 10804 | JLARC's exemption value reproduced (9.04 to 15.52 against "about $9 million to $15.5 million"); Huntsville and LED beside the model, differences stated |
| Replication `replication/impact/datacenter/` | done | 10804, 10805 | `replicate.py` 4,460 of 4,460 figures of 18 cases; `replicate_datacenter.do` (not run: no Stata) |
| Local build, seen at 1280 and 390 px, five readers' cases | done | 10808 | three builds under the lock (12:15 to 12:29 UTC); six addresses at both widths, no overflow, no console error; check-values 1,506 of 1,506; four faults fixed; `docs/reviews/impact-datacenter-readers-2026-11-26.md` |
| Landing request | requested | 10810 | row 14 of `docs/state/landing_request_desktop_w3.md`, head `34904f82b`, port 3740 (13:08 UTC) |

## Part E: more states

| State | Sales exemption | Session | Note |
|---|---|---|---|
| Minnesota, South Carolina, Missouri, North Dakota, Maryland, Florida, Idaho | done | 10805 | thresholds and terms from each statute, tests by hand |
| Nevada | done (words only) | 10805 | NRS 360.754 is an abatement the Office may approve: never applied |
| Washington | held: refused | 10805 | app.leg.wa.gov's robots file disallows every path (`Disallow: /`, behind a byte order mark my first reading missed; no page was read) |
| New York | held: refused | 10805 | www.nysenate.gov answered HTTP 403 |
| Texas | held: not readable | 10805 | statutes.capitol.texas.gov serves a script-built page; gov.texas.gov disallows ClaudeBot; comptroller.texas.gov disallows `/*/` |
| Kansas, Arizona, North Carolina | done | 10806 | K.S.A. 74-50,332; A.R.S. 41-1519; G.S. 105-164.3(201) |
| Utah (words), Wisconsin (done), Georgia (words) | done | 10806 | Utah's threshold is in 59-12-102 (not read); Wisconsin 238.40; Georgia's code behind LexisNexis, the auditor's evaluation read |
| Montana | done | 10806 | class seventeen property, 0.9 percent of market value |

## Part F

| Item | State | Session | Note |
|---|---|---|---|
| More announced projects | done (first pass) | 10807 | 25 rows (Hut 8 River Bend, Amazon Caddo and Bossier, Applied Digital Delta Forge 1 added); defaults recomputed and dated |
| JEDI plant types the page lacks | requested | 10807 | data request 8 for window A |
| Published IMPLAN ratios beyond Virginia | done | 10809, 10810 | Georgia (the state auditor's evaluation) and Minnesota (the Legislative Budget Office's), each its own state only |
| An equipment value schedule (a county's, typed) | done | 10809 | three fields; Loudoun's 2026 schedule reproduces its USD 9.96 million |
| Window F's browser read, rows naming `/impact` | none yet | 10808 | `docs/reviews/browser-read-2026-11-26.md`: `/impact` with Datacenter is part C, read as it lands |
| More states, words or rules | done | 10809, 10810 | Pennsylvania and Kentucky by rule; Mississippi, Indiana and Washington as words (23 states in `datacenter_rules.json`) |
| Words-only states turned into rules where the law can be read | done | 10813 | Georgia (HB 1291 as signed, through 2031), Utah (59-12-102(111)); Illinois added as words (program paused 1 July 2026); Mississippi stays words |
| Statutes re-read | done | 10813 | Utah's code showed a version effective 1 July 2026, read; paragraph unchanged |
| A build and read of the newest head | waiting | 10813 | the build lock was held by window A's gate at 13:25 UTC |
| Minnesota's announced projects (DEED's release on Meta in Rosemount) | waiting | 10815 | mn.gov's robots file sets Visit-time 0000-1200; read after 00:00 UTC |
