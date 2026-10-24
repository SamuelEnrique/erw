# Session 2412 report: EIA's U.S. net imports of crude oil and petroleum products by country, a month from 2010 (the session's own choice)

24 October 2026, from 10:40 UTC, on lab-desktop (the data machine), the seventh session of `queue/done/114-day-15-november-data-paraguay-panama-guatemala-namibia.md`, unattended. Precheck passed (`runs/c114/pre2412.out`). Model spend USD 0. Pulls: EIA's API, 18 of 20 (below).

## Read these first

- **Why this source:**
  - EIA's API v2 routes no connector uses were listed, and two were read first:
    - `petroleum/pri/refoth` (refiner petroleum product prices by sales type) ends in March 2022 (its metadata's end period), so it was not taken;
    - `petroleum/move/neti` (U.S. net imports by country) runs to July 2026.
  - The ERW holds crude imports by origin and petroleum exports by destination, but not EIA's own net figure by partner, which says to whom the U.S. is a net exporter. No chain has taken it, and it is not one of the countries files 115 and 117 plan.
- **One public table:** `eia_net_imports_monthly`, 65,501 rows, 530 series, January 2010 to July 2026. It is written, validated, archived, in coverage (sector oil;products), held from the live set, and listed in the release's held tables:
  - three of the route's 43 products: crude oil and petroleum products together (EP00), crude oil (EPC0) and total petroleum products (EPP0);
  - by partner: each country (`x_partner`, the ISO 3166 alpha-3 code as EIA gives it), the world (NUS-Z00) and three groups (OPEC, non-OPEC, the Persian Gulf), which overlap the countries;
  - in kbbl/d. Imports less exports, so a negative value is a net export.
- **EIA's own figures do not always add:** crude oil plus products equals the total within 1 kbbl/d in 7,822 of the 7,846 partner months that have all three. The other 24 are kept as EIA publishes them, counted in the header and listed in the run log. The first is Egypt in January 2010 (16 kbbl/d), and the largest the Bahamas in October 2017 (46 kbbl/d). The first trial stopped on them; the check now reports instead of stopping.
- **Months from 2010 only,** within the ceiling: 14 pages of 5,000 records. `--from` takes an earlier month (the route starts in 1920).
- **License: public** (EIA, verdict read 1).

## The cross-check (`runs/c114/s2412/cross.py`, `cross.out`; tables read past their header lines)

- **The world's crude oil net imports against `eia_petroleum_snd_monthly`'s U.S. crude imports less exports:** within 1 kbbl/d in all 139 months both hold (June 2025: 2,403 against 6,165 less 3,761 = 2,404).
- **The countries' sum against the world, crude oil and products:** the median gap is 6 kbbl/d and the largest 120 kbbl/d (July 2026: the world -3,608, the countries -3,488). EIA's world total is kept; the table does not say what the gap holds.
- The U.S. is a net exporter of crude oil and products together in December 2019 (-171 kbbl/d) and in July 2026 (-3,608 kbbl/d).

## Pulls against their ceilings

| Host | Requests | What |
|---|---|---|
| api.eia.gov | 18 of 20 | `refoth`'s metadata and a month (2); `neti`'s metadata and a month (2); 14 pages of the trial, reused by the write; 3 s apart |

## Errors

- **The first trial stopped on EIA's 24 partner months** whose crude oil and products do not add to the total. They are now kept and reported.

## Decisions made without you

- **EIA's net imports by country** as the session's own choice, and **refiner prices not taken** since EIA stopped them in 2022.
- **Three products and months from 2010,** within the ceiling.
- **EIA's sums kept as published** where they do not add.

## For Samuel's ruling

- None.

## Files

- New:
  - `warehouse/connectors/eia_net_imports.py`
  - `tests/test_session2412.py`
  - this report
- Changed:
  - `warehouse/metadata/build_coverage.py`, `warehouse/supabase/live_set.yaml`, `warehouse/redivis/release_v1.py`
  - `warehouse/metadata/license_tables.csv`, `docs/licenses.md`
  - the coverage, sources and archive manifest files, and the release README's held line
- On the data machine only: `runs/c114/s2412/` (the sample scripts write EIA's answers with the key replaced by `<key>`).
