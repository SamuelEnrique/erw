# Session 2495 report: the licenses' forty-second round (EWA, ZIMSTAT and NSO Malawi need written permission; the Fiji Bureau of Statistics may be public)

24 October 2026, about 15:12 UTC, on lab-desktop (the data machine), chain 121, unattended. Precheck passed (`runs/c121/pre2495.out`). Model spend USD 0. Pulls: 1 request of 20 (NSO Malawi's home page). The other verdicts rest on pages this chain's source sessions already read.

## Read these first

- **`license_verdicts.csv` was read first:** none of this chain's publishers had a verdict.
- **Four verdicts,** each sentence cut by code from the page as it was saved (`runs/c121/s2495/verdicts.py`), never typed:
  - **Electricity and Water Authority, Bahrain (EWA)** (read 816, the terms of use): "This website contains materials which are owned by or licensed to us. ... Reproduction is prohibited other than in accordance with the copyright notice, which forms part of these terms and conditions." **Needs written permission,** sold or not. `ewa_bahrain_electricity_annual` stays internal.
  - **Zimbabwe National Statistics Agency (ZIMSTAT)** (read 825, the copyright page): "Unless otherwise stated, the material or information published within the Zimbabwe National Statistics Agency Website is ZIMSTAT copyright". **Needs written permission.** `zimstat_zimbabwe_generation_monthly` stays internal.
  - **Fiji Bureau of Statistics (FBoS)** (read 831, Electricity 2024's page ii): "Any table or material published in this Report may be reproduced and published without the Fiji Bureau of Statistics' prior approval. However, the source of information should always be identified and acknowledged in all modes of presentation." **May be public,** sold or not. `fbos_fiji_electricity_annual` is public with the citation in its header.
  - **National Statistical Office of Malawi (NSO)** (read 838, this session's request): the home page's footer, "Copyright © 2026 National Statistical Office of Malawi. All Rights Reserved". The year book states no terms. **Needs written permission.** `nso_malawi_electricity_sales_annual` stays internal.
- **Not given a verdict:** Kahramaa and Qatar's Planning and Statistics Authority (their hosts refused or did not answer, reads 810 to 812), ZERA, ZPC, MERA and EGENCO (no terms page read; the ERW holds no table of theirs).
- **The record:** `licenses.py write` and `check`: 537 tables, 162 publishers with a verdict, 836 requests, 0 problems. Tests 205, 207, 887 and 888 pass. Test 205's bound did not need raising. The four tables join the record's table list when their writes run `licenses.py tables` (sessions 2490 to 2493).
- Sessions 2496 and 2497 come after this one. Their publishers' verdicts are written in their own sessions where a terms page is read.

## Requests (1 of 20)

| n | What | Outcome |
|---|---|---|
| 1 | www.nsomalawi.mw (the home page) | 200: the footer's copyright line; no terms page linked |

Read recorded: 838 (on this branch).

## Decisions made without you

- **A copyright line with no reuse statement read as needs written permission,** as the record reads EEHC's and EEP's.
- **EWA's sentence read as a reservation over the site's materials,** its statistical books among them, though the sentence lists design and layout first.

## For Samuel's ruling

- **Consent from EWA, ZIMSTAT or NSO Malawi,** if their tables are wanted public.

## Files

- Changed: `warehouse/metadata/license_verdicts.csv` (four rows), `warehouse/metadata/license_reads.csv` (read 838), `docs/licenses.md`. New: this report.
- On the data machine only: `runs/c121/s2495/`.
