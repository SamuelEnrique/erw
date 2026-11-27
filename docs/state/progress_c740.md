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
| JEDI plant types the page lacks | done on the branch | 10807, 10820, 10822 | coal (row 16, landed), biopower (row 17, landed), the CSP trough (row 19, requested): every power plant type of nlr_jedi_multipliers; conventional hydropower and the transmission line are not in the table (economic_impact.md: hydro's saved project does not recompute from its constants, the line is per mile), marine and hydrokinetic has no state list, petroleum and the refinery models are not power plants |
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
| Connecticut's property | done on the branch | 10822 | was held (OPM 404, request 486; the certificate). www.cga.ct.gov verifies against the operating system's certificate store (a GoDaddy intermediate Python's bundle lacks; runs/c740/probe/probe_os.py, verification kept): robots 503 allows /current/pub, chapter 203 (504): 12-62a(b) 70 percent, 12-71(b) the same for personal property; 140 quotes (796690f6d) |
| AWS's state fact sheets | one row | 10822 | Oregon (request 488): USD 54.8 billion in eastern Oregon data centers 2012 to 2025, a to_date row (68 rows); Virginia and Ohio (489, 490) give no datacenter investment |
| Build and read of the newest head | waiting | 10822 | the background lock wait was stopped by Claude Code for low memory at about 04:27 UTC (not restarted, as its note asks); the lock held by window A's gate since 04:09; checked by hand in the foreground |
| Build and read of 2dc208ea7 | done | 10822 | lock taken by a foreground wait at 04:38 UTC; 28 addresses at both widths clean; check-values 1,882 of 1,882 (the Washington address included); row 16 moved to it |
| Massachusetts' property | held: by owner | 10822 | c. 59 s. 2 taxes all property (request 491); s. 5 clause Sixteenth (492) exempts or taxes a corporation's machinery by its class under chapter 63 (paragraph (2) taxes "machinery used in the conduct of the business"): the tool cannot know the owner, so no rule |
| Mississippi's exemption | done | 10822 | the Development Authority's sheet (request 493): USD 20 million, 20 jobs, equipment and construction, the state's rate (decision 24); 25 applied, 7 words |
| Build and read of 1a90adbc1 | done | 10822 | 29 addresses at both widths clean (Mississippi with its exemption added); check-values 1,882 of 1,882; row 16 moved to it |
| A review of the branch's code diff | done | 10822 | ten site files, 31 lines added: coal's branches, the chart margin (60 px when no tick), toDate, the menu and lead words; no fault found; no planned coal generator exists in EIA-860M's list (0 in the live set), so the planned list needs no coal mapping |
| Row 16 watch | waiting | 10822 | checked 05:32 UTC: still requested; window F's file has no new /impact lines |
| Row 16 in window A's gate | seen | 10822 | wip/c701-g20 (05:27 UTC) contains 1a90adbc1; the lock held by c701-gate from 05:29; the branch's later commits (9816b41a7 the menu line, 9752e6809 the note's words) wait for row 17 once row 16 lands |
| Row 16 watch | waiting | 10822 | checked 05:53 UTC: gate 20 still running, row 16 requested |
| Row 16 watch | waiting | 10822 | checked 06:15 UTC: task/c701-g20 pushed (GitHub's checks merge it on a pass); the build lock free |
| Row 16 watch | waiting | 10822 | checked 06:36 UTC: GitHub run 45948880574 (code branch, task/c701-g20) in progress since 05:57 |
| Row 16 | landed | 10822 | in 89418bdef (06:38 UTC, task/c701-g20), the branch's newest head 9752e6809 with it: nothing of the branch waits |
| Row 16 on production | read | 10822 | deployed by 06:45 UTC; eight addresses (Texas, El Paso, Washington against North Carolina, Mississippi, Prineville, coal, the page as it opens, gas against geothermal) at 1280 and 390 px clean; check-values against production 1,882 of 1,882; coal offers no figure until the live set holds its rows |
| Coal's live rows and window F | waiting | 10822 | checked 07:08 UTC: no coal rows in the live set yet; no new /impact lines in window F's file |
| Biopower, the sixth plant type | done on the branch | 10822 | EIA's AEO2020 case 13 (request 495; decision 25), JEDI's 0.8 capacity factor (biopower.json), coal's 23 rules and North Dakota's three for sources other than coal or wind; replication 606 of 606 (9,334 in all); CSP trough still held (AEO2020's case is a power tower) |
| Watch (rolling) | waiting | 10822 | last checked 21:28 UTC 27 November: nothing of the branch waits; no new /impact lines in any review; decision 27 for Samuel |
| Row 17 on production | read | 10822 | deployed by 09:30 UTC; biopower (North Dakota, and against Georgia), coal, the page as it opens and the datacenter read clean at 1280 and 390 px; check-values against production 2,354 of 2,354 with the coal and biopower addresses |
| The CSP trough, the seventh plant type | done on the branch | 10822 | NREL's parabolic trough reference plant (request 496: USD 9,861 a kW, 2Q2009 dollars, 30 years), JEDI's one construction year and 0.4175 (csp_trough.json); biopower's rules; replication 488 of 488 (9,822 in all); row 19 requested |
| Utah's property | done on the branch | 10822 | Code 59-2-103(2) (request 499, the version effective 1 July 2025): all tangible taxable property at fair market value, building and equipment at 100 percent; 138 quotes checked; replication 16,010 of 16,010 (ee0e639b7) |
| Michigan's announced project | not a row | 10822 | MEDC's Qualified Data Centers Jobs Creation Report (request 302, 12 December 2025) gives a statewide count only (2,972 jobs since 2016), no project; michigan.gov refuses |
| Oklahoma's property | held: refused | 10822 | www.oscn.net's robots file disallows every path for every agent (request 253's reading, confirmed 27 November) |
| Maryland's announced project | not a row | 10822 | Quantum Frederick's figures are the Maryland Tech Council's study, not a developer's announcement; Commerce's 2021 release is a land purchase; MEDC's 2025 and 2026 releases hold no data center project (Michigan) |
| Indiana's property | done on the branch | 10822 | DLGF's memo of 23 May 2025 (request 501): business personal property exempt only below USD 2 million a county from 2026, no 30 percent floor after 1 January 2025 outside older TIF areas; building and equipment at 100 percent, cost an upper bound; 139 quotes; replication 16,010 of 16,010 (a2e8c6cb1); DLGF's Level II course (500) holds no general rule |
| Statutes re-read: Illinois | done on the branch | 10822 | ilga.gov through the OS certificate store (robots 505, crawl delay 10 s honoured): 20 ILCS 605/605-1025 (506) lets certificates issue until 1 July 2029; DCEO stopped on 1 July 2026 by the Governor's directive; no exemption applied, the tip names both; 141 quotes |
| Statutes re-read: Connecticut | done on the branch | 10822 | General Statutes 32-286 (chapter 588n, request 507): USD 50 or 200 million, 20 years, 200 or 400 million for 30, as DECD's page; (d) also exempts services and all electricity from sales tax (no Connecticut electricity tax held); (e) the property exemption with a host fee, left to the abatement input; the compiled history names PA 21-1 only (PA 26-122 not read); 142 quotes (da5f0e8a7) |
| Texas's announced projects | done on the branch | 10822 | Vantage's Frontier (its release, request 513): 1.4GW, over USD 25 billion; 69 rows; the datacenter defaults 1,200 MW and USD 11.0 million a MW (4822dd23d); statutes.capitol.texas.gov's /Docs/ files serve the script shell (request 305), so Texas's rule stays held |
| Hawaii's property | held: no statement | 10822 | the Tax Review Commission's 2021 memo (request 511) says the counties alone tax real property; no current official page read says personal property is untaxed |
| Michigan's announced project | done on the branch | 10822 | OpenAI's Stargate Michigan (its announcement, request 515): more than one gigawatt, more than 2,500 union construction jobs, no investment; 70 rows, the MW median 1,100 (14); the parser reads 'one gigawatt' (tested) |
| Stargate sites (Texas, Wisconsin) | done on the branch | 10822 | Milam County (OpenAI, request 516: 1.2 GW, MW only); Port Washington (Vantage, 518: close to a gigawatt, USD 15 billion or more, 4,000 construction, 1,000 long-term jobs); the five-site release (517) gives combined capacity only (Lordstown, Doña Ana not rows); 72 rows (47abf48a4) |
| Pennsylvania's second project | done on the branch | 10822 | CoreWeave Lancaster (its investor release, request 521, crawl delay 10 s honoured): 100 MW, 70 roles at launch; USD 6 billion to equip, not taken (Nevada's precedent); 73 rows (b64b599d6, after gate 26's copy: a later row) |
| Louisiana's Amazon update | done on the branch | 10822 | Amazon's page as updated 18 August 2026 (request 524): USD 18 billion, three campuses, 750 full-time and 2,250 construction jobs; a second row beside February's (the Richland precedent); 74 rows |
| Meta's New Albany and Fort Worth | done on the branch | 10822 | info sheets (526, 528): to date, no median; 76 rows |
| Meta's Altoona and Stanton Springs | done on the branch | 10822 | info sheets (530, 533): to date, no median; 78 rows (e7a6ae1f5) |
| Meta's Temple and Jeffersonville | done on the branch | 10822 | from the US locations page (382; no sheets): to date, no median; every campus on that page now has a row; 80 rows (ecd0c9986) |
| Google's Iowa page | not a row | 10822 | request 536 (www.google.com redirected to datacenters.google, whose robots file, read at request 412, allows every path): "invested more than $20 billion in Iowa", Google's whole investment in the state, not a data center's (unlike Meta's "Data center investment" and AWS's "data center infrastructure"), so the earlier ruling on Google's state pages stands; www.google.com's robots file names ClaudeBot in its own group, which allows /about/datacenters |
| Virginia's Vantage VA4 | done on the branch | 10822 | VEDP's release (537): USD 2 billion, 50 jobs; 81 rows. Microsoft's 2019 Mecklenburg expansion (538) names no investment: not a row |
| Microsoft's Mecklenburg expansions | done on the branch | 10822 | VEDP (539, 540): 2015 and 2016; 83 rows |
| Searched, no row | noted | 10822 | VEDP's 2011 Microsoft release answers 404 (541); 2013 and 2014 phases only in the 2016 release's list; Georgia's governor has no data center release (gov.georgia.gov searched); Microsoft's Atlanta Fairwater post gives no figures |
| Alabama's Google Jackson County | done on the branch | 10822 | Alabama Commerce (542): USD 600 million, up to 100 jobs; 84 rows |
| Meta's Huntsville expansion | done on the branch | 10822 | Meta's post of 9 June 2022 (543): to date, no median; 85 rows |
| Meta's Tulsa announcement | done on the branch | 10822 | 'Hello, Tulsa!' (544): more than USD 1 billion, 1,000 at peak, about 100 jobs; enters the ranges beside the info sheet's to-date row; 86 rows |
| Meta's five announcement posts | done on the branch | 10822 | 545 to 549 (Jeffersonville, Beaver Dam, Temple, Kuna, Mesa); 91 rows; construction default 590.5 a billion, permanent per billion 63.6 (decision 27, for Samuel's ruling) |
| Meta's Gallatin and Kansas City posts | done on the branch | 10822 | 550, 551; 93 rows; construction default 833.3 a billion: decision 27 states the possible overstatement and stops further Meta posts until Samuel rules |
| Tennessee's xAI Colossus | not a row | 10822 | the Greater Memphis Chamber's pages give "up to 500" jobs and no investment or MW (searched); nothing enters a median |
| Shared chart: figure and axis collisions | done on the branch | 10822 | SeriesChart.tsx: a bar's figure gives way at the same height ("10,00010,000"), the last column labelled only with room (2047 and 2048 at 390 px); test file; read on /impact and four other chart pages, 86 reads clean |
| Landing row 20 | requested | 10822 | 20e315ad2: rows 72 to 93, the chart fixes; built and read 13:28 UTC, check-values 2,470 of 2,470 |
| Row 19 on production | read | 10822 | deployed by 13:52 UTC; the CSP trough (Arizona; North Dakota against Arizona), Utah's, Indiana's and Connecticut's datacenter pages, Frontier picked in Texas, coal and the opening page clean at 1280 and 390 px; check-values against production 2,470 of 2,470 with the trough's address |
| Row 20 on production | read | 10822 | deployed by 17:21 UTC (93 in the list); Utah's datacenter page, Port Washington, CoreWeave and Meta's Tulsa announcement picked, the trough, the opening page, /attention, /cost-of-power/battery and /explore/interconnection clean at 1280 and 390 px; the jobs chart writes one 10,000; check-values against production 2,470 of 2,470. Every row this window requested is on main and read on production |
| Window A's review of 27 November | read | 10822 | docs/reviews/readers-c701-2026-11-27.md (34ea83df5): five readers on /equities and the large-load rules; none names /impact; nothing for this window |
