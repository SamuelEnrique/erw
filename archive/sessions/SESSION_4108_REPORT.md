# Session 4108 report: the unread publishers' long tail (US federal, then foreign)

Energy Research Warehouse (ERW). Chain 229, session 9 of 50, lab-desktop third window, 13 November 2026 10:58 to 11:02 UTC. Opus 5.5. Model spend USD 0. Branch `wip/4100-licenses`.

## Read

- **US federal** (reads 1761 to 1766):
  - www.usda.gov (NRCS) and www.usace.army.mil (USACE) answered 403 to their robots files, so nothing more was asked;
  - Treasury's site policies page: read, but it states no reuse terms;
  - the Transportation Energy Data Book's citation page: read, a citation only;
  - USAspending's page is drawn by script, so it was not asked.
- **Foreign** (reads 1767 to 1772): the robots files and pages of Svenska kraftnat's data service, Latvia's CSB and E-Control.

## Verdicts (3 new; 267 publishers with a verdict)

- **Svenska kraftnat: may be public, sold or not.** "The information available on Svenska kraftnät's Data Service is covered by an open license: Creative Commons Attribution (CC BY 4.0). This means that you: may copy and share the information may modify the information may use the information even for commercial purposes [...]" (read 1770, https://data.svk.se/about)
- **Central Statistical Bureau of Latvia: may be public, sold or not.** "Data reproduction is permitted, provided Central Statistical Bureau of Latvia is quoted as source." (read 1771, https://www.csp.gov.lv/en/media)
- **E-Control: may be public; needs written permission if sold.** "Please reference E-Control as the data-source." (read 1772, https://www.e-control.at/en/statistik/e-statistik)
- **Their three tables stay internal and wait for a ruling** (never loosened): `svk_sweden_production_hourly`, `csp_latvia_electricity_monthly`, `econtrol_austria_electricity_monthly`.

## Counts

- **Agreement:** 532 agree, 51 settled by a ruling, **0 disagree**, **39 not settled** (was 71 at session 4100), 24 wait for a ruling.
- **Package record:** `build_tables.py` written again (the three tables' wording no longer says "not settled").

## Tests

- **Tests 205, 4101 and 378:** 34 passed. Test 4101's robots-first check now accepts the robots file's answering address (csp.gov.lv answered from www.csp.gov.lv).

## Decisions made without you

- **E-Control's sentence asks only for attribution,** so it is read as allowing noncommercial reuse, with a sale needing permission.
- **No verdict for a page without terms** (Treasury, the TEDB) and none for a refused host (USDA, USACE). Their tables are internal, except `usace_nid_dams`, which stays flagged public and unsettled.

## For Samuel's ruling

- **The three foreign tables** above: **default stays internal.**
