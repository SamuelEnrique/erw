# Session 2320 report: a third source of the session's own choosing (Ireland's electricity output, the Central Statistics Office)

24 October 2026, from 06:46 UTC to 07:01 UTC, on lab-desktop (the data machine), chain 106, unattended. Model spend USD 0. Pulls: 8 requests of 20 (7 by the probe, 1 by the fetch the connector reads offline).

## Read these first

- **Slovenia first, not taken:** the Statistical Office's SiStat (pxweb.stat.si) answered its robots address with HTTP 503 and a page saying the site is not available (read 525). Nothing more was asked.
- **Ireland in its place.** No ERW table held Ireland's national figures: EirGrid's data need written permission (chain 099), and the agents of chains 105 and 108 were told.
- **A new table, `cso_ireland_electricity_monthly`** (series, 644 rows, `power`): the Central Statistics Office's PxStat table MSM01, "Electricity Output". It holds:
  - gross output a month, January 1975 to December 2008 (408 months; CSO discontinued it from January 2009);
  - net output, January 2007 to August 2026 (236 months).

  CSO's note: gross output is "the amount of electricity that passes through the National Grid (excluding imports)", including what producers make and use themselves; net output leaves that out. The values are in MWh (the table's GWh times 1,000). The vintage is the answer's "updated", 2026-10-09T11:00:00Z. Written, validated (0 errors, 0 warnings), archived, held from the Redivis storage and the live set, its release rows added.
- **The license:** CC BY 4.0. CSO's Copyright and Re-use Policy (read 528): "Statistical information on this website is accessible free of charge and licensed under Creative Commons Attribution (CC BY 4.0)." This session wrote the verdict: **may be public**, sold or not.
- **Cross-checks, full years 2016 to 2025:**
  - net output over `eurostat_electricity_monthly`'s net production for Ireland: 0.967 to 1.006;
  - over `owid_ember_electricity_annual`'s demand: from 0.959 in 2016 to 0.786 in 2025. The table excludes imports, and the gap widens as Ireland's demand outgrows its own output. No value is 0 or negative.

## Requests (8 of 20)

| n | What | Outcome |
|---|---|---|
| 1 | pxweb.stat.si/robots.txt | 503: the site not available |
| 2 | ws.cso.ie/robots.txt | 404 |
| 3 | PxStat's search, its URL cut at a comma by the probe's list | 200: a parse error |
| 4 | PxStat's search for "electricity" | 200: MSM01 among 100 tables |
| 5 | www.cso.ie/robots.txt | 404 |
| 6 | CSO's home page, for the policy's link | 200 |
| 7 | CSO's Copyright and Re-use Policy | 200: CC BY 4.0 |
| 8 | MSM01 as JSON-stat 2.0 (the fetch) | 200 |

Reads recorded: 525 to 528.

## Decisions made without you

- **The gross and the net series kept as CSO gives them,** each under its own variable; the 2007 and 2008 overlap is CSO's.

## For Samuel's ruling

- None new.

## Files

- New: `warehouse/connectors/cso_ireland_electricity.py`, `tests/test_session2320.py`, this report.
- Changed: `warehouse/metadata/build_coverage.py`, `warehouse/redivis/release_v1.py`, `warehouse/supabase/live_set.yaml`, `docs/coverage.md`, `warehouse/metadata/coverage.csv`, `warehouse/metadata/sources.csv`, `warehouse/metadata/archive_manifest.csv`, `docs/redivis/release-v1/`, the license record (reads 525 to 528, one verdict).
- On the data machine only: `runs/c106/s2320/`, `warehouse/raw/cso_electricity/`, `warehouse/output/cso_ireland_electricity_monthly.csv`.
