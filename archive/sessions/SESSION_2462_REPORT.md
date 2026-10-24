# Session 2462 report: queue file 120 first; Kyrgyzstan's electricity from the National Statistical Committee

24 October 2026, from 12:45 UTC, on lab-desktop (the data machine), the first session of `queue/done/119-day-19-november-data-kyrgyzstan-cote-divoire-jamaica-laos.md`, unattended. Precheck passed (`runs/c119_precheck_2462.out`). Model spend USD 0.

Pulls: 6 requests of 15, all to www.stat.gov.kg:
- its robots address (HTTP 404: none);
- the English home page;
- the open data page (its licence);
- the manufacturing section;
- two Excel files.

The trial and the write ran offline.

## Read these first

- **Queue file 120 written first and pushed to main alone** (`e39aaaeb`, with snapshots on both sides; the site answers 402 on both):
  - `120-day-20-november-data-ethiopia-mozambique-bhutan-trinidad.md`, sessions 2476 to 2489.
  - Its rules are file 119's; its Stanford session names chain 114's three newly public tables.
  - 120 was the next free number; 2476 to 2489 were free on main and every branch.
  - The four countries are neither in `sources.csv` nor planned in any queue file on main or the running chains' branches.
  - Chains 117's and 118's agents were told.
- **Chain 119 itself:** taken at 12:45 UTC by chain 057's agent when chain 115 landed (`9406de92`), beside chains 117 and 118. Branch `wip/2462-2475-data`, worktree `erw-c119`.
- **Kyrgyzstan from the National Statistical Committee** (not held; no chain took it). Chain 117's session 2436 read the committee's open data, which gives electricity only for 2015 to 2019, and did not open these tables.
  - **Table:** `nsc_kyrgyzstan_electricity_annual`, 478 figures, public with the committee's citation.
  - **Two dynamic tables:** 1.05.01.03, generation by kind of station, 1992 to 2025: hydro, thermal, and other (2025 only, 17.1 GWh). 1.05.01.02, the electricity balance, 1990 to 2025: produced, imports, consumption by branch, network losses, exports.
  - **Unit:** MWh (the committee's million kWh times 1,000).
  - **Sheets:** each file has two, the old classification (to 2013) and GKED-3 (from 2011). The years before 2011 come from the old one and those from 2011 from GKED-3. The overlap, 2011 to 2013, agrees.
- **The committee's footnotes** (in its Kyrgyz and Russian columns, carried into the header):
  - **Imports** "actually including flows" (transit).
  - **Manufacturing** includes, from 2007, the electricity distributed for communal and household needs and to the population. So households' supply sits in `consumption_manufacturing` from 2007, and "public utilities" ends in 2006.
- **The checks:**
  - **Generation:** the kinds add to it.
  - **Consumption:** the branches and the losses add to it.
  - **The balance:** produced and imports equal consumption and exports, within 0.15 million kWh. The years 1990 to 2002 are printed in whole million kWh and are checked to 1.05.
  - **One failure,** the committee's own: 2001, where produced and imports exceed consumption and exports by 55 million kWh. Kept as published and named in the header.
  - **Produced against generation:** the balance's "produced" and the stations' "generation" differ by up to 0.3 million kWh in 2003, 2004 and 2010; both are kept.
- **Against `owid_ember_electricity_annual`'s Kyrgyzstan demand:** the committee's consumption is 0.957 (2024) to 1.021 (2018) times Ember's over 2015 to 2024, and 1.000 in 2020 and 2021.
- **License:** the committee's open data page says its open data is "published under the terms of the Creative Commons Attribution-NonCommercial-ShareAlike license 4.0", "Based on data from the official website of the NSC KR www.stat.kg".
  - **Chain 117's verdict** (read 797 on its branch; the same publisher key): may be public as the ERW is today; written permission if it sells anything.
  - **The table is public with that citation in its header,** by test 378's rule. Until chain 117 lands, this branch's license record lists it as "not settled", flag public.
- **Registered:**
  - the sector rule (`power`), the live-set hold;
  - the release package's held list and its rows (the release check passes);
  - the license tables (licenses check: 534 tables, 0 problems);
  - the test, `tests/test_session2462.py` (4 tests).

## Errors

- **The first parse stopped at 1997:** the balance missed by 1.0 in the years printed in whole million kWh. The rounding is now allowed for those years only.
- **A first header line named "public utilities" to 2010;** it ends in 2006. Corrected before the trial.

## Decisions made without you

- **Both classifications kept** under one set of names where they match (manufacturing, agriculture, transport, construction). The branches only one has keep their own names.
- **The share-alike licence treated as chain 117 judged it:** public today, a question if the ERW ever sells. Share-alike in version 1 stays a standing question (chain 103's note).

## For Samuel's ruling

- **CC BY-NC-SA in the release:** this table is under a noncommercial share-alike licence; the standing question of share-alike in version 1 covers it.

## Files

- New: `warehouse/connectors/nsc_kyrgyzstan.py`, `tests/test_session2462.py`, this report.
- Changed:
  - `warehouse/metadata/build_coverage.py`, `warehouse/supabase/live_set.yaml`, `warehouse/redivis/release_v1.py`;
  - `docs/redivis/release-v1/`;
  - `docs/coverage.md`, `coverage.csv`, `sources.csv`, `archive_manifest.csv`, `license_tables.csv`, `docs/licenses.md`.
- On main: `queue/next/120-day-20-november-data-ethiopia-mozambique-bhutan-trinidad.md`.
- On the data machine only: `runs/c119/`, `runs/license_reads/s2462/`, `warehouse/raw/nsc_kyrgyzstan/`.
