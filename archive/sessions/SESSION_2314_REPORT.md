# Session 2314 report: a source of the session's own choosing (Latvia's electricity, the Central Statistical Bureau)

24 October 2026, from 06:29 UTC to 06:34 UTC, on lab-desktop (the data machine), chain 106, unattended. Model spend USD 0. Pulls: 7 requests of 20 (5 by the probe, the metadata and the query by the trial; the write ran offline).

## Read these first

- **Why this source:** with session 2278's Estonia and session 2273's Finland, Latvia completes the Baltic states' and Finland's national statistics but Lithuania's (session 2315). No ERW table held it, and the agents of chains 105 and 108 were told before any request.
- **A new table, `csp_latvia_electricity_monthly`** (series, 2,039 rows, `power`): the Central Statistical Bureau of Latvia's table ENB010m, January 2006 to August 2026. It holds ten indicators:
  - total gross production and its sources (hydro, combined heat and power, wind, solar from 2023);
  - total net production;
  - the battery storage line (from October 2025);
  - imports, exports, and the electricity available for the internal market.

  The values are in MWh (the table's million kWh times 1,000). The vintage is the answer's "updated", 2026-09-25. Written, validated (0 errors, 0 warnings), archived, held from the Redivis storage and the live set.
- **The license is not read.** data.stat.gov.lv has no robots file, and its portal page carries no licence or terms text (read 504). CSP's own site, stat.gov.lv, answered HTTP 403 to its robots file (read 503) and was not asked again. The table is `internal` until a read settles it.
- **Cross-checks, full years 2016 to 2025, against `eurostat_electricity_monthly` (Latvia):**
  - net production 0.999 to 1.000 of Eurostat's;
  - imports and exports 1.000 in every year;
  - wind 1.000 to 1.048.
  - The internal-market line is 0.943 to 0.975 of Ember's demand (`owid_ember_electricity_annual`).
- **Checks within the table:**
  - the four sources sum to gross production within 1,000 MWh (the table's rounding) in all 248 months;
  - net production plus imports less exports equals the internal-market line within 1,000 MWh, but for:
    - three months, by 11 GWh (August 2011), 8 GWh (September 2011) and 2 GWh (September 2012), unexplained;
    - December 2025 to August 2026, where the line equals that sum plus the battery line.

## Requests (7 of 20)

| n | What | Outcome |
|---|---|---|
| 1 | data.stat.gov.lv/robots.txt | 404 |
| 2 | the database's search for "electricity" | 200: ENB010m among 40 tables |
| 3 | table ENB010m's metadata | 200 |
| 4 | stat.gov.lv/robots.txt | 403 |
| 5 | the portal's database page | 200: no licence text |
| 6, 7 | the metadata and the query (the trial) | 200 |

Reads recorded: 502 to 504. `tests/test_session205.py`'s bound raised by 40 (463 later reads against 462 allowed before it).

## Decisions made without you

- **`internal` until the terms are read,** as for SingStat.
- **The battery line kept as CSP gives it,** with the internal-market identity it implies stated here.

## For Samuel's ruling

- None new.

## Files

- New: `warehouse/connectors/csp_latvia_electricity.py`, `tests/test_session2314.py`, this report.
- Changed: `warehouse/metadata/build_coverage.py`, `warehouse/redivis/release_v1.py`, `warehouse/supabase/live_set.yaml`, `tests/test_session205.py`, `docs/coverage.md`, `warehouse/metadata/coverage.csv`, `warehouse/metadata/sources.csv`, `warehouse/metadata/archive_manifest.csv`, the license record (reads 502 to 504).
- On the data machine only: `runs/c106/s2314/`, `warehouse/raw/csp_latvia_electricity/`, `warehouse/output/csp_latvia_electricity_monthly.csv`.
