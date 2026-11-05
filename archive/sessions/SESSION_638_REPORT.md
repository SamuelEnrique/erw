# Session 638 report: refinery production from 2005

22 October 2026, from 06:41 UTC, on lab-desktop (the data machine), a session of `queue/done/041-morning-22-october-sources.md`. Model spend USD 0.

## Read these first

- **`eia_refinery_production_monthly` now runs from January 2005**: 326,819 rows (151,406 new), 1,488 series.
  - 2005 to 2014 is a window of its own (session 635's), so session 618's 37 saved pages of 2015 on answered again. The 31 pages of the early window came with no error from EIA.
- **Cross-checks**:
  - All 175,413 rows of 2015 on are unchanged.
  - 2005 to 2014: the PADDs against the U.S., 11,282 of 11,370 keys within 1 kbbl (the largest difference 63). PADD 2's districts against PADD 2, all 10,162 (the largest 1). PADD 3's against PADD 3, 11,045 of 11,134 (the largest 452). The larger differences fall where a part is blank.
  - U.S. finished motor gasoline: 8,157 kbbl/d in January 2005, 9,500 in July 2010, 9,898 in December 2014.
- **Written under the data lock** (06:49 UTC) with `--offline` (0 requests). The validator, coverage `--only` and the archive exited 0 (151,406 rows archived). The table's release rows were replaced; the release check exited 0.
- **Chain 040's landing deployed** (`f06826cc`, Vercel success at 06:40 UTC); s637-before against s637-after: 0 differences. The queue move (`64aa1ad2`) was rate limited.

## Pulls against their ceilings

| Host | Requests | What |
|---|---|---|
| api.eia.gov | 31 of 40 | the early window (31 pages; the count was session 635's) |

## Files

- New: this report. Changed: `docs/redivis/release-v1/{tables,variables}.csv`, coverage and the archive manifest.
