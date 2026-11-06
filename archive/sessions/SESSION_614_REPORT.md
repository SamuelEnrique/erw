# Session 614 report: EIA's refinery capacity, a year, from 1995

22 October 2026, from 02:01 UTC, on lab-desktop (the data machine), a session of `queue/done/037-night-22-october-sources.md`. Model spend USD 0.

## Read these first

- **New table `eia_refinery_capacity_annual`: 51,504 rows, 2,009 series, 1995 to 2026.** From EIA's Refinery Capacity Report (route `petroleum/pnp/cap1`), as of January 1 each year, by state, PADD, the U.S. and three territories.
  - Capacity of 34 processes: atmospheric and vacuum distillation, catalytic cracking, hydrocracking, reforming, hydrotreating and desulfurization, coking, thermal cracking, solvent deasphalting.
  - Capacity is in `kbbl/d`, per calendar day (`capacity_per_calendar_day`, EIA's B/CD) or per stream day (`capacity_per_stream_day`, B/SD). There are also counts of operable, operating and idle refineries (`refineries`, `count`).
  - EIA's 53,594 records gave 51,504 rows; the 2,090 blanks have no row.
  - The U.S.'s operable atmospheric distillation capacity on 1 January 2025 reads 18,423 kbbl/d per calendar day.
- **From 1995, not 1982.** The route holds 65,350 records from 1982: 14 pages, where 12 requests were left after the probes. 1982 to 1994 (about 13,800 records, 3 pages) is left for a later session.
- **Cross-checks**:
  - The five PADDs sum to the U.S. on all 1,154 process, unit and year keys, to the barrel.
  - The states, territories excluded, sum to the U.S. on all 1,152.
  - **January's U.S. operable distillation capacity against the weekly table** (`eia_refinery_weekly`, series WOCLEUS2, the year's first two weeks), 2010 to 2026: from 0.976 (2013) to 1.024 (2012), and 1.000 in 2026. The weekly series takes the annual survey's figure late, sometimes a year late.
- **Written under the data lock** (02:04 UTC) with `--offline` (0 requests). The validator, coverage `--only` and the archive exited 0. Release rows added; `licenses.py check` 0 problems (279 tables). **Held** from `/data` and Redivis v1. Sector rule (`products`). Tests: `tests/test_session614.py`, 5.

## Decisions made without you

- **Variables named by EIA's unit, the process in the entity.** `capacity_per_calendar_day`, `capacity_per_stream_day` and `refineries`; the process and area are in EIA's series id (the entity) and its name (the node), rather than 34 process words of the ERW's own.
- **Territories' geo**: `US-PR`, `US-GU` and `US-VI` (ISO 3166-2).

## Pulls against their ceilings

| Host | Requests | What |
|---|---|---|
| api.eia.gov | 14 of 15 | the process facet, a 2025 page, the count from 1982, the trial (11) |

## Files

- New: `warehouse/connectors/eia_refinery_capacity.py`, `tests/test_session614.py`, this report. Changed: the sector rule, both holds, the release package, coverage and the archive manifest.
