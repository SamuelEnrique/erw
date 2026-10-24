# Session 2278 report: a third source of the session's own choosing (Estonia's electricity, Statistics Estonia)

24 October 2026, from 05:00 UTC to 05:08 UTC, on lab-desktop (the data machine), chain 103, unattended. Model spend USD 0. Pulls: 13 requests of 20 (11 by the probe, the metadata and the query by the trial; the write ran offline).

## Read these first

- **Why this source:** with chain 099's Norway and Sweden and session 2273's Finland, Estonia completes the Nordic and Baltic neighbours of the Nordic market's statistics. No ERW table held it, and chains 101, 102 and 104 do not take it; their agents were told before any request.
- **Elering first, not taken.** Elering's dashboard (`dashboard.elering.ee`) is the grid operator's own data. Its robots file disallows every path for every reader (read 448), so nothing more was asked there.
- **A new table, `statee_estonia_electricity_monthly`** (series, 1,344 rows, `power`): Statistics Estonia's table KE21, January 2005 to August 2026, six indicators:
  - total electricity production;
  - production from hydro, wind and solar (solar from January 2023, 44 months);
  - imports and exports.

  The values are in MWh (the table's GWh times 1,000). The table's two shares of sold electricity (percent) are not taken. Written, validated (0 errors, 0 warnings), archived, held from the Redivis storage and the live set, its release rows added.
- **The answer's "updated" is 9999-12-31T21:59:59Z,** a placeholder, so the connector writes no vintage and the header says why. The table listing gives KE21's last update as 2026-09-29.
- **The license:** CC BY-SA 4.0. Statistics Estonia's principles for disseminating official statistics (read 451): "Statistics Estonia's open data can be shared under Creative Common (CC) licence BY-SA 4.0." This session wrote the verdict, **may be public**, sold or not (commercial use is allowed). Any copy or adaptation must carry the same license, and the header says so.
- **Cross-checks, full years 2016 to 2025:**
  - against `eurostat_electricity_monthly` (Estonia): imports and exports equal Eurostat's (1.000) in every year but 2017 (imports 1.051, exports 1.004) and 2024 (imports 0.997); wind is within 2 percent;
  - total production is 1.115 to 1.176 times Eurostat's net production. The table does not say whether its production is gross or net;
  - production plus imports less exports is 0.954 to 1.010 of Ember's demand (`owid_ember_electricity_annual`).

## Requests (13 of 20)

| n | What | Outcome |
|---|---|---|
| 1 | dashboard.elering.ee/robots.txt | 200: `Disallow: /` |
| 2 | andmed.stat.ee/robots.txt | 404 |
| 3 to 7 | the database's listings, root to the short-term energy tables | 200: tables KE20 to KE23 |
| 8 | table KE21's metadata | 200 |
| 9 | www.stat.ee/robots.txt | 200: Drupal's own paths only |
| 10 | www.stat.ee/en, for the terms link | 200 |
| 11 | the principles for disseminating official statistics | 200: CC BY-SA 4.0 |
| 12, 13 | the metadata and the query (the trial) | 200 |

Reads recorded: 448 to 451.

## Decisions made without you

- **The indicators in GWh only,** the two percent shares left out.
- **A share-alike license read as "may be public",** the first in the record. CC BY-SA 4.0 allows redistribution and commercial use with credit, on the condition that copies carry the same license.

## For Samuel's ruling

- **Share-alike in the release:** whether version 1 on Redivis may carry a table under CC BY-SA 4.0 beside CC BY and public domain tables (each table keeps its own license in its header). Until you rule, the table is public in the record like any other.

## Files

- New: `warehouse/connectors/statee_electricity.py`, `tests/test_session2278.py`, this report.
- Changed: `warehouse/metadata/build_coverage.py`, `warehouse/redivis/release_v1.py`, `warehouse/supabase/live_set.yaml`, `docs/coverage.md`, `warehouse/metadata/coverage.csv`, `warehouse/metadata/sources.csv`, `warehouse/metadata/archive_manifest.csv`, `docs/redivis/release-v1/`, the license record (reads 448 to 451, one verdict).
- On the data machine only: `runs/c103/s2278/`, `warehouse/raw/statee_electricity/`, `warehouse/output/statee_estonia_electricity_monthly.csv`.
