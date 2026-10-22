# Session 635 report: refinery inputs from 2005 (production before 2015 left)

22 October 2026, from 06:00 UTC, on lab-desktop (the data machine), a session of `queue/done/040-night-22-october-sources.md`. Model spend USD 0.

## Read these first

- **`eia_refinery_inputs_monthly` now runs from January 2005**: 216,010 rows (93,610 new), 1,056 series.
  - 2005 to 2014 is a window of its own (`SPLIT`, `EARLY_END`, as session 619 did for refinery capacity), so session 615's pages of 2015 on answered again.
  - The first trial stopped at offset 65,000 of the early window (HTTP 504, then 502). The second reused its 13 saved pages and asked for the last 6.
- **Refinery production before 2015 was not pulled.** Its early window is 151,406 records (31 pages), and the inputs used 24 of the session's 40 requests. The chain file put the inputs first. `eia_refinery_production.py` has the same early window, ready for a session of its own.
- **Cross-checks**:
  - All 122,400 rows of 2015 on are unchanged.
  - 2005 to 2014: the PADDs against the U.S., 7,175 of 7,226 keys within 1 kbbl (the largest difference 30). PADD 3's districts against PADD 3, 6,538 of 6,584 (the largest 7).
  - U.S. crude oil input: 15,254 kbbl/d in January 2005, 13,666 in January 2010, 16,469 in December 2014.
- **Written under the data lock** (06:14 UTC) with `--offline` (0 requests). The validator, coverage `--only` and the archive exited 0 (93,610 rows archived). The table's release rows were replaced; the release check exited 0. Tests: `tests/test_session635.py`, 3.

## Pulls against their ceilings

| Host | Requests | What |
|---|---|---|
| api.eia.gov | 24 of 40 | the two early windows' counts, the first trial (16: 13 answered, 3 answered with errors), the second (6) |

## Files

- New: `tests/test_session635.py`, this report. Changed: `warehouse/connectors/eia_refinery_inputs.py`, `warehouse/connectors/eia_refinery_production.py` (both the early window and a ceiling of 37), `docs/redivis/release-v1/{tables,variables}.csv`, coverage and the archive manifest.
