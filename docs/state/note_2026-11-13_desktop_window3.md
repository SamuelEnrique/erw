# Note: the licensing sweep, 13 November 2026 (chain 229, lab-desktop third window)

Energy Research Warehouse (ERW). Written by session 4148 of chain 229 (`queue/done/229-day-13-november-desktop-window3-licenses.md`), roadmap item 5. Sessions 4100 to 4115 did the chain's work, 09:27 to about 11:55 UTC. The plan's later numbers (4116 to 4147) were not needed: the sweep, the letters, the costs, the FRED requests, the two tests and the page and note checks were done, so the note and the next file follow at once. Model spend USD 0 (no model call). Nothing sent, nothing posted, no warehouse write, no site build. Reports: `archive/sessions/SESSION_4100_REPORT.md` to `SESSION_4115_REPORT.md` and `SESSION_4148_REPORT.md`.

## Verdict counts, before and after (`docs/licenses.md`)

| | Before (session 4100, main at `ed0634ecc`) | After (session 4148, `wip/4115-licenses`) |
|---|---:|---|
| Tables | 648 | 648 |
| Flag and verdict agree | 528 | 544 |
| Settled by a ruling | 47 | 52 (49 "license needed", 2 kept internal, 1 public by the owner's ruling) |
| Disagree | 0 | 0 |
| Not settled (a publisher not read) | 71 | 26 |
| Flagged internal, the sentence allowing them: wait for the owner's ruling | (counted as disagreeing: 0 then) | 24 |
| Internal by the ERW's own choice | 2 | 2 |
| ERW verdict: public / internal / unsettled | 476 / 115 / 57 | 479 / 115 / 54 |
| Publishers with a verdict | 259 | 279 |
| Publishers confirmed on their current page | 0 | 37 (none with its sentence gone) |
| Tables resting on a read older than 30 days | 362 | 36 (MISO paused; CFTC, Bloomberg, DCD, Hart Energy, Heatmap, Reuters, Meta, Equinix refuse by robots; the FT's page is 404) |
| Requests in the record | 1,649 | 1,805 (156 this chain: robots files and current pages) |

## Every flag changed

- **`coverage.csv`:** no flag changed and none edited by hand.
- **`warehouse/metadata/sources.csv`:** needed no change. Every table whose verdict now asks more than its public flag declares `License: public` in its own header, so the owner's ruling of 12 October (hold it "license needed") is the rule, not a flag change.
- **Held "license needed"** (`license_status.csv`, 45 to 49), each because a publisher's page asks permission:
  - `policy_actions`, `policy_action_tags` and `policy_reads` (the PUCT's link policy, read 1689);
  - `impact_tax_rules` (the Louisiana Department of Revenue's terms, read 1696).
- **Out of Redivis release v1** (139 to 133 in v1): those four, plus `large_load_rules` and `large_load_rule_reads`. `release_v1.py`'s plan now holds out any table whose verdict is unsettled.
- **Ruled public in the record:** `large_load_public` (the owner's ruling of 14 October, session 272, which `licenses.py` did not know).
- **Settled public:** `ferc714_forecast_growth` and `ferc714_planning_area_forecasts` (flagged public by the owner's ruling of 6 November; PUDL's CC BY 4.0 now read).
- **Never loosened:** 24 internal tables whose sentences allow public stay internal and wait for a ruling. They are the 21 FERC 714 tables (PUDL), Svenska kraftnat's, Latvia's and E-Control's.

## The letters (`docs/reviews/licenses/`, nothing sent)

- **What each letter now holds:** a current draft on top, the session 378 draft kept below, the sentence confirmed on 13 November, the contact from the publisher's own page, the stated use (an open, citable research warehouse at Stanford, derived figures on a site in review), and an appendix of the exact tables and fields.
- **NYISO** (31 tables): its address and switchboard. The page names no legal or data contact.
- **SPP** (33): communication@spp.org. Needed only if the ERW sells anything.
- **PJM** (2): its General Counsel's address, from its legal page.
- **MISO** (26): the address is left to a person, since MISO is paused.
- **Waiting for you:** your surname, role and email, and MISO's address.

## The costs found (`docs/licenses_costs.md`)

- **PJM membership** (read 1707):
  - associate member USD 2,500 a year, no application fee;
  - voting member USD 5,000 a year, plus USD 2,000 application and USD 1,500 risk review for market participants;
  - ex officio and special members USD 500.
  - Its data license lets "Members" republish. Whether an associate member counts is the PJM letter's question.
- **ICE 2027 fees** (read 1709):
  - redistribution license for ICE Futures U.S. commodities USD 30,000 a year (non-member), USD 25,000 (member);
  - public display USD 3,000;
  - end-of-day derived data USD 10,000 per product.
- **CME:** its fee list is not readable (the connection is refused).
- **No price stated** by NYISO, ISO-NE, MISO, SPP, the news outlets or the data center companies.

## What else the chain built

- **`scripts/license_confirm.py`:** robots first, the sentence found by code, cuts by index, `--start` and `--end`, `--pick none`. Its record is `warehouse/metadata/license_confirmations.csv`.
- **`scripts/licenses.py` gains:** the stale count, the confirmations section, `RULED_PUBLIC`, the "waits for a ruling" standing, and two `CANON` names (CENCE and VMME, whose verdicts the document could not see).
- **`tests/test_session4101_licenses.py`:** the flag and the verdict agree; a confirmation never loosens; robots are read first.
- **`tests/test_session4109_public_site.py`:** no table reaches the public site while its verdict is not public (the live set, downloads, release v1, the findings cards, the held grids' public files).
- **The page and the notes:** `/data/licenses`' two lines and 13 method notes' license lines brought in step.
- **`docs/state/unsettled_licenses_2026-11-13.md`:** the 26 tables still not settled.
- **`docs/state/data_requests_licenses.md`:** 15 requests of window A: the outlet-name dash; FRED's series mapped to their primary sources (six already read from EIA, the Board and the IMF; three IMF codes and seven BLS indexes requested); three fetches of hosts whose robots refuse Anthropic's agents.

## Landing

- **Row 1** (`wip/4100-licenses`, sessions 4100 to 4109) and **row 2** (`wip/4110-licenses`, to 4114; it holds row 1) are in `docs/state/landing_request_desktop_w3.md` on main for window B.
- Neither had landed at 11:50 UTC.
- `wip/4115-licenses` (sessions 4115 and 4148) waits for the next file's landing row.

## The rulings waiting, each with the default taken

- **The held grids' public files:** 138 files of NYISO's and ISO-NE's prices under `site/public/` (`board/s`, `board/h`, `seller/prices`), served by address past the review curtain (every extension but `.rsc`, even after session 5101's fix) and in the public repository. **Default: left as they are.** The test fails on any new one.
  - **For chain 234's security list:** this is the same class of fault as its row 1, and it is not on that list.
- **Three findings cards built from internal tables** (`gas_sets_price` from ISO-NE's prices; `siting_flexible` and `siting_gigawatt` from the PUCT's transmission matrices), their files also served by address. **Default: left as they are;** the test keeps `/` and `/research` from opening while they wait.
- **The policy monitor held** by the PUCT's news releases. **Default: held,** until the PUCT's rows leave the tables or the PUCT grants permission.
- **`impact_tax_rules` held** by the Louisiana Department of Revenue's terms (the table holds statutes and rule citations). **Default: held.**
- **The 24 internal tables whose sentences allow public** (FERC 714 by PUDL; Sweden, Latvia, Austria). **Default: stay internal.**
- **The 26 tables not settled** (`docs/state/unsettled_licenses_2026-11-13.md`). **Default: internal ones stay internal; public-flagged ones unchanged** (two out of v1, three held from Redivis).
- **CFTC's site refuses Anthropic's agents;** window A is asked to stop reading www.cftc.gov. **Default:** its verdict stays as read in October.
- **The letters:** send or not. **Default: not sent.** Any purchase (PJM membership, an ICE license): **default: none.**
