# Session 2329 report: Europe's monthly gas balance (Eurostat, nrg_cb_gasm), the second source of the session's own choosing

24 October 2026, from 07:25 UTC, on lab-desktop (the data machine), the eighth session of `queue/done/108-day-10-november-data-malaysia-thailand-ecuador-kenya.md`, unattended. Precheck passed (`runs/c108/pre2329.out`). Model spend USD 0. Pulls: 3 of 20 (below).

## Read these first

- **One public table:** `eurostat_gas_balance_monthly`, Eurostat's supply, transformation and consumption of natural gas, a month, 2015 to September 2026. It is written, validated, archived, in coverage (sector gas), and held from the live set and the release.
  - 53,214 rows, 38 areas (the EU's members, Norway, the candidates in the file, EU27_2020 and EA21; the file holds no EA20, and the United Kingdom and Kosovo are left out; session 2331 corrected "40 areas ... and EA20"), 16 balance items: production, imports, exports, stock changes, inland consumption (calculated and observed), gas for power and heat, industry and other final use, losses, bunkers, flaring, venting and statistical differences.
  - In MWh, from Eurostat's terajoules of gross calorific value; the million cubic metres are not taken.
- **Why this one:** the ERW holds Eurostat's gas imports by partner (chain 098) but not the balance they feed. Europe's monthly demand, storage draws and gas burn are what the United States' LNG serves.
- **Zeros kept:** 18,211 zeros are written as Eurostat prints them, since in a balance a zero says an item is nil. The imports table leaves its zeros out, because 97 per cent of its partner cells are zero. 292 blanks have no row.
- **Eurostat's sign of stock changes:** positive when gas goes into storage. The EU's is positive from April to October 2024 and negative in winter; January 2024 is -190.5 TWh. The docstring first said the opposite and was corrected before the write.
- **License:** Eurostat's copyright notice, already on record (public with acknowledgement). ec.europa.eu's robots file disallows only the old SDMX path and the search pages, and names no AI agent (read 535).

## The cross-check (`runs/c108/s2329/cross.py`, `cross.out`)

- **MOS GAS's identity:** inland consumption calculated equals production plus imports minus exports minus the stock change in 3,866 of 4,494 area-months within 0.5 per cent, and in 4,078 with transfers from other sources added. Inland consumption calculated equals observed plus statistical differences in 4,219 of 4,868. Of the 628 misses, 225 are months whose consumption and gap are both 0 (which a relative test cannot pass), and 373 of the other 403 carry transfers from other sources. (Session 2331: this replaces "the rest are cells Eurostat leaves blank or marks confidential", which the test, taking only months with every item, cannot meet; `cross.py` is now saved in the form that printed these figures.)
- **Against `eurostat_gas_imports_monthly`:** the balance's imports equal the TOTAL partner of the imports table in 4,422 of 4,431 area-months within 0.1 per cent; 5 differ by more than 5 per cent.
- **The EU's year, TWh** (complete years only):
  - Inland consumption: 3,855.6 (2015), 4,401.3 (2021), 3,807.0 (2022), 3,535.3 (2023), 3,555.2 (2024), 3,644.9 (2025).
  - Production: 927.3 (2015) falling to 334.8 (2025).
  - The EU's imports (4,747.2 to 7,319.0 TWh; 6,220 to 7,319 to 2022, then 5,135.3, 4,747.2 and 5,144.9) are larger than its consumption because the aggregate counts the members' trade with each other. (Session 2331 corrected the range.)

## Pulls against their ceilings

| Host | Requests | What |
|---|---|---|
| ec.europa.eu | 3 of 20 | robots, the data set (9.2 MB), the NRG_BAL codelist (for the items' names); 3 s or more apart |

## Errors

- **The docstring first gave the stock change's sign the wrong way;** the cross-check showed it, and it was corrected before the write.

## Decisions made without you

- **Eurostat's gas balance chosen,** as the companion of the imports table the ERW holds.
- **Zeros kept; energy units only.**

## For Samuel's ruling

- None new.

## Files

- New:
  - `warehouse/connectors/eurostat_gas_balance.py`
  - `tests/test_session2329.py`
  - this report
- Changed:
  - `warehouse/metadata/build_coverage.py`, `warehouse/redivis/release_v1.py`, `warehouse/supabase/live_set.yaml`
  - `warehouse/metadata/license_reads.csv` (535), `license_tables.csv`, `docs/licenses.md`
  - `docs/redivis/release-v1/`
  - the coverage, sources and archive manifest files
- On the data machine only: `runs/c108/s2329/`, `runs/license_reads/s2329/`, `runs/s2329*`.
