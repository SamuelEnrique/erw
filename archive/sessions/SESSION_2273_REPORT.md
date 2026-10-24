# Session 2273 report: a second source of the session's own choosing (Finland's electricity, Statistics Finland)

24 October 2026, from 04:07 UTC, on lab-desktop (the data machine), chain 103, unattended, while session 2272's trial waited between its requests. Model spend USD 0. Pulls: 11 requests of 20 (9 by the probe, the metadata and the query by the trial; the write ran offline).

## Read these first

- **Why this source:** with chain 099's Norway and Sweden tables, Finland completes the Nordic market's national statistics. The ERW did not hold it, and chains 101 and 102 do not take it.
- **A new table, `statfi_finland_electricity_monthly`** (series, 6,350 rows, `power`): Statistics Finland's StatFin table 12su, January 1992 to June 2026, across 16 lines:
  - total consumption;
  - total generation and its sources (hydro, wind, solar, nuclear, combined heat and power and its district heating, industrial and micro kinds, conventional condensing);
  - net imports, and their parts with Norway, Sweden, Russia and Estonia.

  The values are in MWh (the table's GWh times 1,000), and only the quantity is taken. Written, validated (0 errors, 0 warnings), archived, held from the Redivis storage and the live set, its release rows added.
- **The license:** CC BY 4.0, Statistics Finland's terms of use (read 445): its "open data materials and public content of the web service are covered by the Creative Commons Attribution 4.0 International licence", with "Source: Statistics Finland". The verdict is for the licenses round (session 2271).
- **Cross-checks, full years 2016 to 2025:**
  - total generation is within 1.4 percent of Eurostat's net production for Finland (`eurostat_electricity_monthly`) every year;
  - net imports equal Eurostat's imports less exports within 3.1 percent;
  - total consumption is 0.961 to 0.972 of Ember's demand.
  - The table's six sources sum to its total generation within 2,000 MWh in all 414 months.

## Requests (11 of 20)

| n | What | Outcome |
|---|---|---|
| 1 | pxdata.stat.fi/robots.txt | 404 |
| 2 | StatFin's ehk listing | 200: table 12su |
| 3 | a wrong table address | 400 |
| 4 | table 12su's metadata | 200 |
| 5 | stat.fi/robots.txt | 200 |
| 6 | a guessed terms address | 404 |
| 7 | the PxWeb front page | 200: the terms link |
| 8 | www.stat.fi/robots.txt (redirected to stat.fi's) | 200 |
| 9 | Statistics Finland's terms of use | 200: CC BY 4.0 |
| 10, 11 | the metadata and the query (the trial) | 200 |

Reads recorded: 443 to 445.

## Decisions made without you

- **The quantity in GWh only,** the table's changes, cumulative sums and shares left out.

## For Samuel's ruling

- None new.

## Files

- New: `warehouse/connectors/statfi_electricity.py`, `tests/test_session2273.py`, this report.
- Changed: `warehouse/metadata/build_coverage.py`, `warehouse/redivis/release_v1.py`, `warehouse/supabase/live_set.yaml`, `docs/coverage.md`, `warehouse/metadata/coverage.csv`, `warehouse/metadata/sources.csv`, `warehouse/metadata/archive_manifest.csv`, `docs/redivis/release-v1/`, the license record.
- On the data machine only: `runs/c103/s2273/`, `warehouse/raw/statfi_electricity/`, `warehouse/output/statfi_finland_electricity_monthly.csv`.
