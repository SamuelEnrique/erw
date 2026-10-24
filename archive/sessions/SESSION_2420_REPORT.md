# Session 2420 report: queue file 117 first; Zambia's electricity from ERB's Statistical Bulletin

24 October 2026, from 10:35 UTC, on lab-desktop (the data machine), the first session of `queue/done/115-day-16-november-data-zambia-botswana-mongolia-cambodia.md`, unattended. Precheck passed, run from the main checkout (`runs/c110/precheck_2420.out`). Model spend USD 0.

Pulls: 8 requests of 15, all to www.erb.org.zm:
- its robots file, alone;
- `wp-sitemap.xml` (HTTP 404);
- the home page;
- `/statistics`;
- the 2025 Statistical Bulletin;
- the 2025 Energy Sector Report (for peak demand: none);
- the 2022 and 2020 bulletins (to check one column).

The trial and the write ran offline.

## Read these first

- **Queue file 117 written first and pushed to main alone** (`d96de185`, with snapshots on both sides; the site answers 402 on both):
  - `117-day-17-november-data-tunisia-egypt-armenia-nepal.md`, sessions 2434 to 2447.
  - Its rules are file 115's, with the hosts chain 114 closed added (NamPower, www.ecb.org.na, cnd.enee.hn, www.ut.com.sv, CND Panama's key).
  - 117 was the next free number (115 taken, 116 the code machine's). 2434 to 2447 were free on main and on every branch.
  - The four countries are neither in `sources.csv` nor planned in any queue file on main or the running chains' branches.
  - Chains 113's and 114's agents were told.
- **Chain 115 itself:** taken at 10:34 UTC by chain 057's agent when chain 110 landed (`1db31cbf`), beside chains 113 and 114. Branch `wip/2420-2433-data`, worktree `erw-c115`.
- **Zambia is taken from the Energy Regulation Board** (not held; no chain planned it).
  - **Table:** `erb_zambia_electricity_annual`, 515 figures, internal.
  - **Contents:**
    - generation by power station, 2013 to 2025: ZESCO's three large hydro, six mini hydro and seven diesel plants, and 14 independent power producers;
    - each group's printed total;
    - consumption by 11 economic sectors and the total, 2015 to 2025;
    - exports by exporter and ZESCO's imports, 2024 and 2025;
    - installed capacity by technology, 2025.
  - **Unit:** MWh (ERB's GWh times 1,000); capacity in MW.
  - **Source:** one PDF (the bulletin's tables 12 to 19 and 26), read with pdfplumber. Table 16's 14 columns are taken from its table extraction, and the header must match ERB's exactly.
- **Checks in the connector:**
  - **Totals:** every table's rows add to its printed total within 0.1 GWh. The four groups' 2025 totals equal table 12's national total, 14,560.23 GWh.
  - **Two flaws in ERB's tables, recorded in the header:**
    - **Consumption for 2019 is not taken.** In table 19 the 2019 column equals the 2021 column in every sector (12,831.30 GWh in all). The 2022 bulletin gives these figures as 2021's (12,831,360.78 MWh), so 2019's own figures are missing. The 2020 bulletin is a mid-year issue with no annual 2019. The connector leaves 2019 out only while the two columns are equal.
    - **Table 17's power traders' total for 2025** (544.17 GWh) is 12.96 GWh under its rows, which is Africa GreenCo's exports. The grand total still adds up. The connector allows that one gap and stops on any other.
  - **Table 12's IPP line** (5,873.17) is 2.50 GWh under table 16's IPP total, the CEC emergency generators' output. Table 12 is used as a check only.
- **Against `owid_ember_electricity_annual`'s Zambia demand** (that table holds demand, not generation, for Zambia):
  - **2013 to 2023:** ERB's generation is 0.89 to 1.20 times Ember's demand, as for a net exporter (1.18 and 1.20 in 2022 and 2023).
  - **2024, the drought year:** generation less exports plus ZESCO's imports is 13,478 GWh against Ember's 16,600, 19 percent under. Ember's figure is not ERB's, and the power traders' imports (charted in the bulletin's figure 6, not tabled) are not in ERB's import table.
  - **2025:** consumption (15,471 GWh) exceeds generation less exports plus ZESCO's imports (14,445 GWh). That points to the traders' imports too. Ember has no 2025 figure.
- **Not in the bulletin:** the system's peak demand. The 2025 Energy Sector Report gives maximum-demand tariffs and customer counts, not a system peak.
- **License: internal.** ERB's site footer reads "Copyright 2026 All Rights Reserved", and no page read states terms of reuse. This follows KPX's verdict (read 547: "all rights reserved", needs written permission; its table internal).
- **Registered:**
  - the sector rule (`power`), the live-set hold;
  - the license tables (licenses check: 516 tables, 0 problems);
  - the test, `tests/test_session2420.py` (4 tests).

## Errors

- **The connector's first run stopped at table 17's traders' total.** The gap was found to be exactly Africa GreenCo's row, and the rule was written for that one case.
- **The test's first stop case was a valid input:** a gap equal to GreenCo's figure, which the rule allows. Corrected.

## Decisions made without you

- **ERB taken over ZESCO,** since ERB's bulletin holds every producer's generation, not only ZESCO's.
- **Internal, not closed,** for an "All Rights Reserved" footer, as for KPX. Chain 114 closed NamPower for the same footer; ERB's statistics page publishes the bulletins for users, and the table stays off every public surface until a ruling.
- **2019 consumption left out** rather than written as a copy of 2021.
- **One year's bulletin only** (2025, covering 2013 to 2025 for generation). Earlier bulletins were read only to check one column.

## For Samuel's ruling

- **ERB's terms:** a word from the Energy Regulation Board on reuse would settle whether `erb_zambia_electricity_annual` can be public. Not asked.

## Files

- New: `warehouse/connectors/erb_zambia.py`, `tests/test_session2420.py`, this report.
- Changed:
  - `warehouse/metadata/build_coverage.py`, `warehouse/supabase/live_set.yaml`;
  - `docs/coverage.md`, `coverage.csv`, `sources.csv`, `archive_manifest.csv`, `license_tables.csv`, `docs/licenses.md`.
- On main: `queue/next/117-day-17-november-data-tunisia-egypt-armenia-nepal.md`.
- On the data machine only: `runs/c115/`, `runs/license_reads/s2420/`, `warehouse/raw/erb_zambia/`.
