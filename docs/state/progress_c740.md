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
| Sources: taxes by state | done | 10800 to 10820 | Virginia (exemption, property classes, consumption tax), Louisiana (rebate), Iowa (exemption) read; Indiana's statute behind a script; West Virginia's code host times out (waiting) |
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
| Landing request | landed, then row 15 requested | 10810, 10821 | row 14 (`34904f82b`) landed at 14:16 UTC in landing 2; row 15 asks for the newer head |

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
| JEDI plant types the page lacks | coal done on the branch; CSP and biopower held | 10807, 10820, 10822 | data request 8 done (window A, 21:57 UTC 26 November); coal offered from EIA's case 1 and JEDI's coal model (replication 524 of 524); CSP and biopower need a capital cost and a life no published study read gives (forecast.md section 14); coal's figures appear when the live set loads the rows |
| Published IMPLAN ratios beyond Virginia | done | 10809, 10810 | Georgia (the state auditor's evaluation) and Minnesota (the Legislative Budget Office's), each its own state only |
| An equipment value schedule (a county's, typed) | done | 10809 | three fields; Loudoun's 2026 schedule reproduces its USD 9.96 million |
| Window F's browser read, rows naming `/impact` | read, five findings fixed | 10808, 10821 | `docs/reviews/browser-read-2026-11-26.md`: `/impact` with Datacenter is part C, read as it lands |
| More states, words or rules | done | 10809, 10810 | Pennsylvania and Kentucky by rule; Mississippi, Indiana and Washington as words (23 states in `datacenter_rules.json`) |
| Words-only states turned into rules where the law can be read | done | 10813 | Georgia (HB 1291 as signed, through 2031), Utah (59-12-102(111)); Illinois added as words (program paused 1 July 2026); Mississippi stays words |
| Statutes re-read | done | 10813, 10821 | Utah's code (a July 2026 version, paragraph unchanged); Florida's 212.08 and Iowa's 427A.2 in their 2026 editions (unchanged) |
| A build and read of the newest head | done | 10813, 10816 | `3fb425592` built 14:00 UTC, eleven addresses at 1280 and 390 px, check-values 1,506 of 1,506; row 14 updated |
| Minnesota's announced projects (DEED's release on Meta in Rosemount) | done | 10815, 10822 | read 02:09 UTC 27 November inside mn.gov's visit window (request 362): USD 800 million, about 100 operational jobs, at least 1,000 at peak; DEED's 2025 expansion list (363) names no datacenter; 47 rows, construction median 400.0 a billion |
| More states (part F) | done | 10813 to 10816 | by rule: Georgia, Utah, Arkansas, Oklahoma, Connecticut, Michigan (22 in all); words: Illinois, Massachusetts, Ohio, Nebraska (8 in all) |
| Electricity taxes beyond Virginia | done | 10817, 10818 | Illinois (monthly blocks), Ohio (tiers or the self-assessing schedule, the lower) |
| Wages from warehouse tables (request 7 built) | done | 10818 | `datacenter_wages.py --tables`; figures identical |
| Property ratios a datacenter shares with all property | done | 10818 | Georgia 40 percent, New Mexico one third, Ohio 35 percent building and no equipment tax |
| Build and read of 988e06dc9 | done | 10818 | thirteen addresses, check-values 1,680 of 1,680; row 14 updated |
| Equipment untaxed where the state says so | done | 10819 | Iowa, Minnesota, North Dakota, Wisconsin, Kansas (25 percent building), with Ohio |
| Assessment ratios by state | done | 10819 | South Carolina, Wyoming, Arizona, Missouri, Nevada, Alabama, Mississippi, Arkansas; rate fields to 60 percent |
| Build and read of 3e15b9395 | done | 10819 | fifteen addresses, check-values 1,680 of 1,680; row 14 updated |
| Data requests 6, 7, 9 | answered | 10820 | 6 landed (22 rows, grows when row 14 lands), 7 landed and read by the tool, 9 built on `wip/c701-tax` |
| Row 14 landed (first head) | done | 10821 | `34904f82b` at 14:16 (landing 2); newer head `6352fb2e4` requested |
| Window F's findings I1 to I5 | done | 10821 | fixed on the branch, tested, read at both widths |
| Landing row 15 (the newer head) | landed (18:36 UTC) | 10821, 10822 | `617bd736d` or later (checked 16:18 UTC: not yet on main; window F's file has no new `/impact` lines); row 14 landed at `34904f82b` |
| Window F's finding I6 (the opening scenario moved, unexplained) | done on the branch | 10822 | a line above the fields: the defaults are medians of the projects read, each count and the date; test in `test-datacenter-ui.test.mjs` |
| Row 15 | landed | 10822 | `617bd736d` in `b80148122` (18:36 UTC 26 November, task/c701-tax); the newer head goes as row 16 |
| North Dakota's announced campuses | done | 10822 | the governor's releases (requests 369 to 371): Applied Digital Ellendale a row (USD 5 billion combined); Williston and Bitzero crypto-mining, not rows (decision 19); 48 rows |
| Tennessee's sales exemption | held: refused | 10822 | www.tn.gov resets every connection (request 364), publications.tnsosfiles.com answers 403 to its robots file (366); no commercial code host taken |
| Wyoming's announced project | done | 10822 | Meta in Cheyenne (Cheyenne LEADS, request 375): USD 800 million, about 100 operational jobs, over 1,000 at peak; 49 rows, construction median 443.6 a billion |
| New Mexico's Project Jupiter | held: no document | 10822 | STACK's own PDF answered 404 (request 90); Dona Ana County's bond ordinance not found on an official host |
| Texas's first announced project | done | 10822 | Meta in El Paso (Meta's own page, request 380; the October 2025 release, 381, for the first phase): 1 GW, more than USD 10 billion, over 300 jobs, over 4,000 at peak; 50 rows; the default size moves from 1,400 to 1,000 MW |
| Arkansas's announced project | not a row | 10822 | Google's USD 4 billion (its blog, request 379) covers the data center, cloud and AI infrastructure and local programs: no figure is the data center's alone; AEDC's release gives no figure |
| Meta's campus info sheets | done | 10822 | thirteen campuses, each Meta's only one in its state (requests 384 to 408): offered in the picker, in no median (`to_date`, decision 20); first rows for Illinois, Tennessee, Idaho, New Mexico, Oregon, Nebraska; 63 rows; the parser reads "$1.5B+" |
| New Hampshire's property | done | 10822 | RSA 72:6, 72:7, 75:1 and chapter 72's list (requests 422 to 426): building at market value, equipment untaxed (decision 21); 37 states |
| California's rules | held: refused | 10822 | leginfo.legislature.ca.gov answers 403 to its robots file (request 420) |
| Colorado's property | done | 10822 | C.R.S. 39-1-104(1.9) as HB24B-1001 enacted it (request 428): 25 percent from 2027; 38 states |
| Chart axis labels cut ("00 million") | done on the branch | 10822 | found in tonight's read with El Paso picked; SeriesChart's margin widens only for a label of more than ten characters |
| Build and read of c3b81a67f | done | 10822 | 21 addresses at both widths clean, check-values 1,680 of 1,680; landing row 16 requested 02:46 UTC |
| New Jersey's property | done | 10822 | the assessors' handbook, chapter VI (request 436): equipment untaxed; 39 states |
| More announced rows | done | 10822 | U.S. Bank Chaska (Minnesota, 2016), AWS Butts and Douglas (Georgia, 2025), AWS Fayette (Ohio, 2024): 66 rows, 53 of them announcements |
| Maine, Delaware, South Dakota, Oregon property | done | 10822 | requests 440 to 449: Maine taxes a new datacenter's equipment (PL 2025, c. 768), Delaware and South Dakota none, Oregon both; 43 states |
| Rhode Island's property; Vermont | done; held | 10822 | 44-3-1 (request 452): both taxed; Vermont's statute pages are script-built (requests 454 to 457 answered one shell); 44 states |
| Crusoe's Abilene campus (Texas) | done | 10822 | Crusoe's release (request 460): 1.2 GW, USD 15 billion; 67 rows; the default size 1,100 MW. Crusoe's Wyoming campus not a row (MW only, the site since sold to Google) |
| Coal's capacity factor and rules | done on the branch | 10822 | coal.json (JEDI's 0.85); 23 plant property rules take coal (Iowa, Maryland, Montana, Georgia, South Carolina, Ohio and the general notes); replication 8,728 of 8,728; row 16 at 9841c6c1b |
| Washington's rural exemption | done | 10822 | RCW 82.08.986 from lawfilesext.leg.wa.gov (request 463; no robots file there): 35 jobs, construction before 2035, purchases through 2047, the state's rate (decision 22); 24 applied, 8 words |
| New York's and California's property | done | 10822 | ORPTS (request 467): equipment untaxed; BOE Publication 306 (469): both at cost; 46 states; left without a rule: Texas, Vermont, Hawaii, Alaska |
| Microsoft's community sheets | read, not rows | 10822 | requests 471 to 474: economic activity and jobs supported, or operating staff and construction jobs without investment or MW (Arizona 430 and 2,050; Wyoming 320 and 1,810): no ratio, no row |
| Nebraska, North Carolina, Pennsylvania property | done | 10822 | 77-201 (475); G.S. 105-274, 105-283 (477, 478); 53 Pa.C.S. 8811 (479, decision 23); 130 quotes; property rules now in every state with a rule but CT, FL, ID, IN, KY, MA, MD, MI, OK, UT, WA |
| Full suite on e07989aaf | done | 10822 | 11,107 passed, 15 failed, 346 skipped (20 min, under the lock); 12 of the 15 fail the same way on the clean main of 26 November (fail_now.txt), the other 3 (sessions 137, 143, 161, the /ask panel) on today's clean origin/main in a throwaway worktree |
| Maryland, Kentucky, Washington, Michigan, Idaho property | done | 10822 | requests 481 to 485; Florida's site serves a cookie challenge (480), not got around; 136 quotes |
