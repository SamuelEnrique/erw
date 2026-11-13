# Duke Energy Carolinas, LLC (NC, SC): large-load rules

Energy Research Warehouse (ERW), research pass of session 5300 (portable laptop, window P4). Method: `../README.md`.

<!-- generated: start -->

Group `duke`. Rows in `utilities_<date>.csv`:

- **duke-01**: Large Load Tariff (LLT), with Schedule HLF: Exhibit 1 to the Agreement and Stipulation of Settlement on Large Load Tariff of 6 October 2026. Status: proposed (2026-10-06). License: public. Source: https://www.selc.org/wp-content/uploads/2026/10/2026-10-06-Duke-Energy-LLT-Settlement.pdf
  - Not published in the documents read: study_timeline, connection_timeline, queue_size.
  - Held already by window A, not repeated: threshold_mw, min_demand.
  - Overlap with window A's registries: large_load_tariffs/duke_energy_carolinas_large_load_tariff.yaml: threshold and min_demand held unchanged. contract_term: window A holds the minimum term; this adds the automatic one-year extension and the 24-month notice. collateral: window A holds the Dedicated Facilities CIAC and the network upgrade letter of credit; this adds the ratable reduction and the security equal to termination liquidated damages (cash, letter of credit or parent guarantee). exit_fee is not in window A's file. Status unchanged: proposed, no NCUC order found as of 13 November 2026.
  - Notes: Read again through the reader on 13 November 2026 (window A's copy was 12 November). No NCUC order on the settlement was found by search; the NCUC portal bars Claude's agents, so the docket itself was not read. Exhibit 1 also sets a Reliability Provision (p. 24): each ESA includes interruptibility of 95% of contract load for up to 50 hours a year for the load ramp period plus one year, or the alternative the exhibit lists. The 10-Q (same section) says: Electric service agreements entered into prior to June 1, 2026, already include similar retail customer protections. Queue leads, not values (news only): Duke's Q3 2026 earnings call coverage (Utility Dive, Earnings Whispers, 5 to 6 November 2026) reports a 15.4 GW late-stage large-load pipeline of which 7.8 GW is signed electric service agreements, company-wide, not Carolinas-only; WUNC (16 October 2026, robots bar Claude) reports Duke's Fall 2026 semiannual large-load report. FERC accepted Duke Energy Carolinas' large-load revisions to its pro forma NITSA in ER26-2691 (lead: a 75% floor for 15 years per mgrid and Utility Dive); ferc.gov answered 403 to the reader, so no row is written for it. South Carolina: see the row 'Generic docket on large load additions (SC PSC Docket 2026-138-E)'.
- **duke-03**: Generic docket on large load additions (SC PSC Docket 2026-138-E): petition for comments, no tariff proposed. Status: proposed (2026-05-27). License: public. Source: https://psc.sc.gov/sites/psc/files/Documents/PINs/2026-2027%20PINs/PIN--Docket%20No.%202026-138-E.pdf
  - Not published in the documents read: min_demand, contract_term, collateral, exit_fee, study_timeline, connection_timeline, queue_size.
  - Notes: A comment docket, not a rule: kept so that the South Carolina side's status is on record; drop it if the dataset holds rules only. Leads (news and party releases, not read as values): the docket follows commitments in Duke's 2025 South Carolina rate case settlements; S&P Global reports the SC PSC voted on 20 November 2025 to approve a separate large-load stipulation between DEP and consumer and environmental groups (Docket 2025-154-E). No Duke South Carolina large-load tariff filing was found. sierraclub.org (SSL error on robots) was not read.

Refused or blocked (not read, not retried another way):

- https://www.ferc.gov/news-events/news/commissioner-changs-dissent-duke-energy-carolinas-llc-docket-nos-er26-2691-000: HTTP 403 (FERC ER26-2691, Duke Energy Carolinas pro forma NITSA large-load provisions)
- https://ferc.gov/news-events/news/commissioner-rosners-concurrence-duke-energy-carolinas-llc-er26-2691-000-er26-2691: HTTP 403
- https://www.wunc.org/2026-10-16/new-report-shows-growing-certainty-for-incoming-data-centers-in-the-carolinas: robots.txt 200: DISALLOWED for ClaudeBot, Claude-Web, anthropic-ai; a lead only
- https://s201.q4cdn.com/583395453/files/doc_downloads/2026/Duke-Energy-2025-Annual-Report-vFINAL.pdf: robots.txt answered 403: treated as disallow all (Duke's posted investor documents)
- https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&CIK=0001326160&type=10-Q&dateb=&owner=include&count=10: robots.txt 200: DISALLOWED for all agents (the filings were reached through the Archives path instead)
- https://www.duke-energy.com/: not requested this pass: answered 403 to earlier readers (final, per the brief)
- https://starw1.ncuc.gov/: not requested this pass: the NCUC portal's robots file bars Claude's agents (final, per the brief)

<!-- generated: end -->
