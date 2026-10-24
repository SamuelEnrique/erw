# Session 2225 report: Europe's monthly electricity supply (Eurostat)

24 October 2026, from 02:05 UTC, on lab-desktop (the data machine), chain 099, unattended. Model spend USD 0. Pulls: 5 requests of 15 (the robots file, the two data sets and the two codelists; the trial and the write ran offline).

## Read these first

- **`nrg_cb_em` alone does not hold what the chain file asks.** It is electricity's flows only (imports, imports from the EU, exports, exports to the EU, the supply available for the internal market AIM, distribution losses, and TI_EHG_EPS). Net production by fuel is Eurostat's companion data set `nrg_cb_pem`, so the session took both, through the same SDMX 2.1 API session 2123 used for `nrg_inf_epcrw`.
- **A new table, `eurostat_electricity_monthly`** (series, 130,025 rows, `power`):
  - 39 European countries and the EU27_2020 aggregate, January 2016 to August 2026;
  - net production by SIEC fuel (`net_production:<code>`, each as published, no sum made here) and the flows (`flow:<code>`);
  - in MWh (Eurostat's GWh times 1,000).
  - Written, validated (0 errors, 0 warnings), archived, held from the Redivis storage and the live set, its release rows added. Public under Eurostat's verdict.
- **The country rule of chain 079's connector, reused from its own constants:** the EU, EFTA, the official candidates and Eurostat's aggregates. The United Kingdom and Kosovo are left out (Eurostat's notice bars commercial reuse of other countries' data) and named in the header. `nrg_cb_pem`'s percent shares are not taken.
- **Cross-checks:**
  - The 27 member states' net production, summed, equals Eurostat's own EU27_2020 row in every one of the 127 months, to six decimals of the ratio.
  - Against `owid_ember_electricity_annual`'s demand (chain 079), in 359 full country-years 2016 to 2025:
    - Eurostat's supply available for the internal market is a median 0.896 of Ember's demand, 0.825 to 0.969 between the 10th and 90th percentiles;
    - net production a median 0.915, 0.649 to 1.075, wider, as importers and exporters should be.
    - The furthest are Moldova (0.55 in 2021 and 0.59 in 2023) and Montenegro (2.97 in 2016 and 3.09 in 2017), not explained here.

## Requests (5 of 15)

| n | What | Outcome |
|---|---|---|
| 1 | ec.europa.eu/robots.txt | 200: the API path not disallowed |
| 2 | nrg_cb_em from 2016-01 | 200, 2.6 MB |
| 3 | nrg_cb_pem from 2016-01 | 200, 14.0 MB |
| 4 | the NRG_BAL codelist | 200 |
| 5 | the SIEC codelist | 200 |

Read recorded: 346.

## Decisions made without you

- **Both monthly data sets in one table,** since the chain file asks for production by fuel and the flows together.
- **No sum made by the ERW:** Eurostat's TOTAL and its aggregates are kept as published.

## For Samuel's ruling

- None new.

## Files

- New: `warehouse/connectors/eurostat_electricity_monthly.py`, `tests/test_session2225.py`, this report.
- Changed: `warehouse/metadata/build_coverage.py`, `warehouse/redivis/release_v1.py`, `warehouse/supabase/live_set.yaml`, `docs/coverage.md`, `warehouse/metadata/coverage.csv`, `warehouse/metadata/sources.csv`, `warehouse/metadata/archive_manifest.csv`, `docs/redivis/release-v1/`, the license record.
- On the data machine only: `runs/c099/s2225/`, `warehouse/raw/eurostat_cb_em/`, `warehouse/output/eurostat_electricity_monthly.csv`.
