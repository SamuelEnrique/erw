# Session 2454 report: Eurostat's annual electricity balance (nrg_cb_e), 1990 to 2025 (the session's own choice)

24 October 2026, from 12:50 UTC, on lab-desktop (the data machine), the seventh session of `queue/done/118-day-18-november-data-rwanda-senegal-azerbaijan-uzbekistan.md`, unattended, beside session 2452's notes (drafted by a helper). Precheck passed (`runs/c118/pre2454.out`). Model spend USD 0. Pulls: 3 of 20 at Eurostat, 6 at EIA's API (below).

## Read these first

- **Why this source:**
  - EIA's API v2 routes were listed first. The ERW holds every electricity, natural gas and petroleum branch they offer, except the 860M inventory, which it holds from the workbooks.
  - FERC Form 714, LBNL's data sets and the federal power marketers are held too.
  - Eurostat's annual electricity balance (`nrg_cb_e`) is held by no table and taken by no chain. It complements `eurostat_electricity_production_annual` (production by fuel) and the monthly flows of `eurostat_electricity_monthly` (from 2016).
- **One public table:** `eurostat_electricity_balance_annual`, 73,062 rows, 1990 to 2025. It is written, validated, archived, in coverage (sector power), held from the live set, and listed in the release's held tables:
  - for 40 areas (the EU's members, EFTA's and the candidates, with EU27_2020; the United Kingdom, Kosovo and the euro area left out, as the gas balance does);
  - 63 balance items, from gross and net production, imports, exports and inland demand to the energy sector's own use, losses and final consumption by sector;
  - in MWh (Eurostat's GWh times 1,000).
- **No sum is made or checked but one.** The file's identities do not close:
  - other sectors' total (FC_OTH_E) is in the codelist but has no value, and the parts of final consumption fall short of it (Germany 2023: 9.5 TWh);
  - net production plus imports less exports differs from inland demand in 970 of the file's 1,419 country years.
  - The first trial checked final consumption against industry, transport and other and failed in 1,309 of 1,326 country years; that check was dropped.
  - The run now stops only if net production is ever above gross by more than 1 GWh. It never is, in all 1,328 country years.
- **License: public** (Eurostat's copyright notice, the record's verdict). `ec.europa.eu`'s robots file is the same as session 2413's (read 820).

## The cross-check (`runs/c118/s2454/cross.py`, `cross.out`; tables read past their header lines)

- **Gross production in `nrg_cb_e` against TOTAL in `nrg_bal_peh` (`eurostat_electricity_production_annual`):** the same within 1 GWh in 1,139 of 1,279 country years (EU 2023: 2,760.9 TWh in both; Germany 2023: 522.9 in both). 140 differ, by at most 509.0 GWh; France 2024 is 570.7 against 570.9 TWh. Eurostat's two data sets are kept as published.

## Pulls against their ceilings

| Host | Requests | What |
|---|---|---|
| api.eia.gov | 6 | the routes' metadata (electricity, natural gas, petroleum, total energy, densified biomass, AEO); 2 s apart |
| ec.europa.eu | 3 of 20 | robots, the data (electricity in GWh), the NRG_BAL codelist |

## Errors

- **The first trial's final-consumption check failed** in nearly every country year, the file's other-sectors total being empty. It was replaced by the production check above.

## Decisions made without you

- **Eurostat's annual electricity balance** as the session's own choice, after EIA's routes, FERC 714 and LBNL were found held.
- **Items kept as Eurostat prints them,** with no sum made.

## For Samuel's ruling

- None.

## Files

- New:
  - `warehouse/connectors/eurostat_electricity_balance.py`
  - `tests/test_session2454.py`
  - this report
- Changed:
  - `warehouse/metadata/build_coverage.py`, `warehouse/supabase/live_set.yaml`, `warehouse/redivis/release_v1.py`
  - `warehouse/metadata/license_reads.csv` (820 to 822), `license_tables.csv`, `docs/licenses.md`
  - the coverage, sources and archive manifest files, and the release lists
- On the data machine only: `runs/c118/s2454/` (the EIA route listing writes the key as `<key>`), `runs/license_reads/s2454/`.
