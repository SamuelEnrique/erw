# Session 4111 report: the paused, the refused and the reserved

Energy Research Warehouse (ERW). Chain 229, session 12 of 50, lab-desktop third window, 13 November 2026 11:27 to 11:33 UTC. Opus 5.5. Model spend USD 0. Branch `wip/4110-licenses`.

## Verdicts (3 new; 270 publishers with a verdict)

- **Georgia Public Service Commission: needs written permission.** The site's footer: "All rights reserved." (read 1775, https://psc.ga.gov/about-the-psc/, 13 November 2026; no robots file, read 1774). The site names no terms of reuse.
- **Virginia State Corporation Commission: needs written permission, no page asked.**
  - Paused since 10 October: its robots file disallows every automated request, and by the owner's ruling of 9 October only the commission's written permission lifts the pause.
  - Recorded as "not asked: paused" (read 1773).
- **CME Group (NYMEX): needs written permission, no page readable.** www.cmegroup.com refused the connection on 12 October and 13 November (reads 49 and 1704).
- **Their tables are all internal,** so nothing moves on the site: `large_load_rules_internal` (still waiting for PUCO) and `eia_all_futures_prices`.

## Counts

- **Agreement:** 533 agree, 52 settled by a ruling (45 "license needed" of October, 4 of this chain, 2 kept internal, 1 public), **0 disagree**, **37 not settled** (71 at session 4100), 24 waiting for a ruling.
- **Package record and catalogue:** `build_tables.py` written again (0 differences after); `build_llms.py`, `release_v1.py --check` agree.

## Searched, no page with terms found

- PUCO, Grant PUD, TNMP: no page with terms found by search; not asked.

## Tests

- **Tests 205, 4101 and 4109:** 37 passed.

## Decisions made without you

- **A publisher whose site cannot be read** (refused or paused) and whose tables are internal gets "needs written permission" with a note beginning "NOT READ", as Electrek's did. It settles the document and loosens nothing.
- **US federal agencies are not treated that way:** USDA, USACE, FERC and Treasury stay "not settled". Their works are public domain by statute (17 U.S.C. 105), and a "permission" verdict would misstate that.

## For Samuel's ruling

- **USACE's National Inventory of Dams** (`usace_nid_dams`, flagged public, unsettled: www.usace.army.mil refuses its robots file). **Default: unchanged.**
