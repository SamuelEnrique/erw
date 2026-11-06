# Session 619 report: refinery capacity from 1982, and BOEM's lease production from 1996

22 October 2026, from 02:41 UTC, on lab-desktop (the data machine), a session of `queue/done/038-night-22-october-sources.md`. Model spend USD 0.

## Read these first

- **`eia_refinery_capacity_annual` now runs from 1982**: 62,804 rows (11,300 new, 1982 to 1994).
  - All 65,350 of EIA's records from 1982 are read, as session 616 counted.
  - 1982 to 1994 is a window of its own (`SPLIT`), so session 614's 11 saved pages of 1995 on answered again; 3 requests were made.
  - **Cross-checks**: the PADDs equal the U.S. on all 1,482 keys, and all 51,504 rows of 1995 on are unchanged.
  - U.S. operable distillation capacity reads 17,890 kbbl/d (calendar day) on 1 January 1982 and 15,034 on 1 January 1994.
- **`boem_ogor_lease_production_monthly` now runs from January 1996**: 1,131,562 rows (885,852 new), 4,654 leases.
  - 19 more yearly files (1996 to 2014), and the 2015 on files reused.
  - **2009's file repeats one line in every field** (lease G13367, completion 003, August 2009, all zeros). The connector now keeps a line repeated in every field once and counts it in the header (1). A key given twice with any field different still stops the run.
  - **Cross-checks**: all 245,710 rows from 2015 on are unchanged. BOEM over EIA's Federal Offshore Gulf of America (EIA's series in the ERW start in 2001):

    | Years | Months | Oil, median (min to max) | Gas, median (min to max) |
    |---|---|---|---|
    | 2001 to 2004 | 48 | 1.0004 (0.960 to 1.033) | 1.0037 (0.986 to 1.011) |
    | 2005 to 2014 | 120 | 1.0001 (1.000 to 1.005) | 1.0048 (0.979 to 1.031) |
    | 2015 to 2024 | 120 | 1.0003 (1.000 to 1.004) | 1.0031 (0.999 to 1.006) |

- **Both written under the data lock** (02:42 and 02:50 UTC) with `--offline` (0 requests). The validator, coverage `--only` and the archive exited 0 each time. Both tables' release rows were replaced, and the release check exited 0.
- BOEM's robots file was read again: unchanged since session 611.

## Decisions made without you

- **Ceilings counted as requests.** BOEM's connector counted files (15 a run). A run from 1996 opens 31 files but asks for only those not saved, so the ceiling now counts requests (21 a run). The refinery capacity connector's ceiling is now 5, as only the early window is asked for.
- **A repeated line kept once**, as above. Dropping it changes no sum, since it is zero, and a run no longer stops on a line BOEM gives twice.

## Pulls against their ceilings

| Host | Requests | What |
|---|---|---|
| api.eia.gov | 3 of 5 | refinery capacity, 1982 to 1994 |
| www.data.boem.gov | 20 of 22 | the robots file, the 1996 to 2014 files (14 in the first trial, which stopped at 2009's repeated line; 5 in the second) |

## Files

- New: this report. Changed: `warehouse/connectors/eia_refinery_capacity.py`, `warehouse/connectors/boem_ogor.py`, `tests/test_session611.py`, `docs/redivis/release-v1/{tables,variables}.csv`, coverage and the archive manifest.
