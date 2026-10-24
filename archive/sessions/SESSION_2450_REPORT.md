# Session 2450 report: Azerbaijan's electricity balance (2007 to 2025), production and plant capacity by kind (1913 to 2025)

24 October 2026, from 12:39 UTC, on lab-desktop (the data machine), the third session of `queue/done/118-day-18-november-data-rwanda-senegal-azerbaijan-uzbekistan.md`, unattended. Precheck passed (`runs/c118/pre2450.out`). Model spend USD 0. Pulls: 6 of 15 (below).

## Read these first

- **One public table:** `statsaz_azerbaijan_electricity_annual`, 1,067 rows, 56 variables. It is written, validated, archived, in coverage (sector power), held from the live set, and listed in the release's held tables. It comes from three workbooks of the State Statistical Committee's Energy section (reads 805 to 807 on this branch's numbering):
  - table 3.1.18, the electricity balance, 2007 to 2025: production by kind of plant, import, export (negative, as printed), total supply, the statistical difference, energy industries' own use, losses in transmission and distribution, and final consumption with its sectors;
  - table 5.4, production of electricity by kind of plant, 1913 to 2025;
  - table 5.3, plant capacity at the end of the year by kind of plant;
  - before 2000, single years only (1913, 1920 to 1990 by tens, 1995);
  - in MWh (million kWh times 1,000) and MW.
- **Every check holds:**
  - production is electricity plants plus CHP plants, and electricity plants are their kinds;
  - production and capacity are their kinds from 2000, within 1 GWh or 1 MW;
  - the balance's production equals table 5.4's within 1.0 GWh in every year both give.
- **License: public with the source cited.** The site's footer reads "It is necessary to refer to the information on the site..!" (read 804), and the Azerbaijani page says the same ("istinad etmək zəruridir"). New verdict: may be public. Under test 378's rule (chain 114's landing), the table is public with the citation in its header.
- **The host:** www.stat.gov.az reset the connection at its robots file (read 802). stat.gov.az answers robots.txt with its home page, so it has no robots file (read 803).

## The cross-check (`runs/c118/s2450/cross.py`, `cross.out`; tables read past their header lines)

- **Production plus imports less exports (the balance's total supply) against `owid_ember_electricity_annual`'s Azerbaijan demand:** within 0.2 to 0.8 per cent in the years compared, 2010, 2015, 2020, 2022 and 2023 (2023: 26.27 against 26.06 TWh; this line first said "from 2010 to 2023", corrected in session 2452), and 2.2 per cent above in 2024 (27.19 against 26.61 TWh).
- Exports reached 3.0 TWh in 2022 and 3.2 TWh in 2023 (as printed: -2,997.4 and -3,245.7 million kWh).

## Pulls against their ceilings

| Host | Requests | What |
|---|---|---|
| www.stat.gov.az | 1 | robots (connection reset) |
| stat.gov.az | 5 | robots (the home page), the Energy section, three workbooks, a second apart (no robots file, so no crawl delay is asked); the connector waits 2 s between them |
| total | 6 of 15 | |

## Errors

- None.

## Decisions made without you

- **The table public with the citation,** as the Committee's footer allows and test 378 requires.
- **The balance in million kWh only;** the same balance in thousand toe and terajoules is not taken.

## For Samuel's ruling

- **The Committee's figures:** now public; should they be?

## Files

- New:
  - `warehouse/connectors/statsaz_azerbaijan.py`
  - `tests/test_session2450.py`
  - this report
- Changed:
  - `warehouse/metadata/build_coverage.py`, `warehouse/supabase/live_set.yaml`, `warehouse/redivis/release_v1.py`
  - `warehouse/metadata/license_reads.csv` (802 to 807), `license_verdicts.csv` (the Committee), `license_tables.csv`, `docs/licenses.md`
  - the coverage, sources and archive manifest files, and the release lists
- On the data machine only: `runs/c118/s2450/`, `runs/license_reads/s2450/`.
