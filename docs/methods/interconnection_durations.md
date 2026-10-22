# Interconnection request to operation: how long completed projects took

Two derived tables, `interconnection_durations` (one row a completed project) and `interconnection_durations_summary`
(by grid and year), built by `warehouse/derived/interconnection_durations.py` (session 671, chain 043). They are the
source of the time-to-connect column of the code machine's All grids tab. No request is made: the builder reads
`lbnl_interconnection_queue`, which the warehouse already holds.

## Input and license

`lbnl_interconnection_queue`: Lawrence Berkeley National Laboratory and GridTracker, *Queued Up: 2026 Edition* data
file (through the end of 2025), one row per interconnection request. License, in Berkeley Lab's words: "The Queued Up
data file is licensed CC BY 4.0... You may use, share, or adapt the dataset as long as you attribute it to Lawrence
Berkeley National Laboratory and GridTracker." The durations are an adaptation, public, with that attribution.

## Which projects

A request is counted when Berkeley Lab's queue status (`q_status`) is `operational` and the file gives both its
request date (`q_date`, the day it entered the queue) and its operation date (`on_date`). Of the 4,789 operational
requests in the 2026 edition, 3,098 are counted; 1,643 lack one of the two dates and 48 give an operation date before
the request date, and those are left out and counted in the table's header. Nothing is estimated for a missing date.

What the file gives differs by grid, and the tables follow it:

| Grid (Berkeley Lab's region) | Operational requests | Counted | Years of operation |
|---|---|---|---|
| CAISO | 235 | 225 | 2005 to 2025 |
| ERCOT | 613 | 470 | 2012 to 2025 |
| ISO-NE | 228 | 0 | none: the file gives no operation date for ISO-NE |
| MISO | 515 | 476 | 2001 to 2024 |
| NYISO | 215 | 83 | 2002 to 2023 |
| PJM | 1,192 | 1,181 | 2000 to 2025 |
| SPP | 299 | 272 | 2002 to 2025 |
| Southeast (outside the ISOs) | 529 | 215 | 1999 to 2025 |
| West (outside the ISOs) | 963 | 176 | 2004 to 2025 |

## The duration

`months_to_operation` = (operation date minus request date, in days) / 30.4375, to one decimal. 30.4375 is the mean
month (365.25 / 12); the unit is `month` (data standard, Decision 49). The duration runs from the request, not from the
interconnection agreement (`ia_date`), so it holds the study and the construction both.

## The project table, `interconnection_durations`

Entities shape: `entity_id` the queue table's own (`lbnl:<transmission provider>:<queue id>`), `entity_type`
`project`, `status` `operating`, `status_date` the operation date, `capacity_mw` as the file gives it. Beside them:
`queue_id`, `grid`, `state`, `county`, `utility` (the file's own utility field, blank where it names none: 888 of the
3,098), `transmission_provider` (Berkeley Lab's `entity`), `fuel` (its `type_clean`), `request_date`, `operation_date`,
`months_to_operation`, `request_year`, `operation_year`.

## The summary, `interconnection_durations_summary`

Series shape, `entity` `lbnl_durations:<grid>` (`caiso`, `ercot`, `miso`, `nyiso`, `pjm`, `spp`, `southeast`, `west`,
and `us` for every counted project), `ts_utc` 1 January of the year the projects began operating, `freq` `P1Y`:

- `median_months`, `p25_months`, `p75_months` (`month`): the median and quartiles of that year's projects;
- `projects` (`count`) and `mw` (`MW`): how many, and their capacity;
- `median_months_5y` and `projects_5y`: the median over the five years ending that year, so a grid with few completions
  in one year still has a steady figure.

For the five years to 2025: the U.S. median is 56.8 months (964 projects); ERCOT 45.6 (322), West 47.1 (50), Southeast
54.4 (139), PJM 69.1 (241), SPP 70.1 (56), CAISO 95.1 (74). MISO and NYISO have no row for 2025 (their last counted
year is 2024 and 2023), and ISO-NE none at all.

## What it does not hold

- No project still in a queue, withdrawn or suspended: a duration is known only once a project operates, so the
  figures describe what finished, not what waits now (which is longer, and rising).
- No weighting by MW; every project counts once.
- No cause of a delay, no stage durations (request to agreement, agreement to operation): the file gives the
  agreement date for some projects only.

<a id="cross-checks"></a>

## Cross-checks

Session 681 (chain 043): this table's median request-to-operation time against `iso_queue_statistics`' median wait (`wait_years_median`, from each ISO's own queue file: the queue date to the in-service date), for requests entered in 2015 and in 2017. Our months are divided by 12. No figure was moved.

| Our figure | Published figure | Source and date | Gap | Reason |
|---|---|---|---|---|
| CAISO, requests of 2015: median 8.48 years to operation (19 projects, Queued Up) | median 8.62 years (22 positions, the ISO's own queue file) | docs/methods/energy_projects.md, `iso_queue_statistics` (the warehouse's own table), 21 October 2026 | -0.14 years | Within a few weeks: the two files time the same projects |
| CAISO, requests of 2017: median 4.93 years to operation (9 projects, Queued Up) | median 4.93 years (9 positions, the ISO's own queue file) | the same | -0.00 years | Within a few weeks: the two files time the same projects |
| ERCOT, requests of 2015: median 5.53 years to operation (18 projects, Queued Up) | median 6.85 years (3 positions, the ISO's own queue file) | the same | -1.32 years | Different sets of projects: Berkeley Lab counts 18 completed requests of 2015, the ISO's file 3 positions with a wait, and their dates differ (Berkeley Lab's operation date against the ISO's in-service or commercial operation date) |
| ERCOT, requests of 2017: median 4.31 years to operation (40 projects, Queued Up) | median 3.36 years (16 positions, the ISO's own queue file) | the same | +0.95 years | Different sets of projects: Berkeley Lab counts 40 completed requests of 2017, the ISO's file 16 positions with a wait, and their dates differ (Berkeley Lab's operation date against the ISO's in-service or commercial operation date) |
| NYISO, requests of 2015: median 5.34 years to operation (4 projects, Queued Up) | median 4.34 years (6 positions, the ISO's own queue file) | the same | +1.00 years | Different sets of projects: Berkeley Lab counts 4 completed requests of 2015, the ISO's file 6 positions with a wait, and their dates differ (Berkeley Lab's operation date against the ISO's in-service or commercial operation date) |
| NYISO, requests of 2017: median 4.92 years to operation (1 projects, Queued Up) | median 6.97 years (7 positions, the ISO's own queue file) | the same | -2.05 years | Different sets of projects: Berkeley Lab counts 1 completed requests of 2017, the ISO's file 7 positions with a wait, and their dates differ (Berkeley Lab's operation date against the ISO's in-service or commercial operation date) |
| PJM, requests of 2015: median 3.83 years to operation (67 projects, Queued Up) | none: `iso_queue_statistics` holds no wait for PJM | the same | not comparable | The ISO's own queue file, as `iso_queue_statistics` reads it, gives no in-service date for PJM, so only Berkeley Lab's file times its projects |
| PJM, requests of 2017: median 4.99 years to operation (70 projects, Queued Up) | none: `iso_queue_statistics` holds no wait for PJM | the same | not comparable | The ISO's own queue file, as `iso_queue_statistics` reads it, gives no in-service date for PJM, so only Berkeley Lab's file times its projects |
| SPP, requests of 2015: median 4.4 years to operation (32 projects, Queued Up) | median 4.47 years (33 positions, the ISO's own queue file) | the same | -0.07 years | Within a few weeks: the two files time the same projects |
| SPP, requests of 2017: median 5.55 years to operation (12 projects, Queued Up) | median 8.01 years (24 positions, the ISO's own queue file) | the same | -2.46 years | Different sets of projects: Berkeley Lab counts 12 completed requests of 2017, the ISO's file 24 positions with a wait, and their dates differ (Berkeley Lab's operation date against the ISO's in-service or commercial operation date) |
| MISO, requests of 2015: median 3.88 years to operation (41 projects, Queued Up) | none: `iso_queue_statistics` holds no wait for MISO | the same | not comparable | The ISO's own queue file, as `iso_queue_statistics` reads it, gives no in-service date for MISO, so only Berkeley Lab's file times its projects |
| MISO, requests of 2017: median 3.96 years to operation (33 projects, Queued Up) | none: `iso_queue_statistics` holds no wait for MISO | the same | not comparable | The ISO's own queue file, as `iso_queue_statistics` reads it, gives no in-service date for MISO, so only Berkeley Lab's file times its projects |
