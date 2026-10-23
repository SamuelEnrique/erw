# Session 697 report: EIA-930's demand by sub-region, 2020, the first half of the pages

23 October 2026, from 00:48 UTC, on lab-desktop (the data machine), a session of `queue/done/045-evening-22-october-data-resumed.md`. Model spend USD 0.

## Read these first

- **`python warehouse/connectors/eia930_subba.py --year 2020` ran under the data lock to its ceiling and saved its pages, as the chain plans; no table is written yet.** January to July 2020 are read whole (each month 57,068 to 61,008 records, pages of 5,000) and August's first pages saved, in `warehouse/raw/eia930_subba/20261023T004839Z/`. The run stopped at the connector's ceiling ("the ceiling of 89 requests is reached") and wrote nothing, as the connector does (session 612). Session 698 reuses every saved page and asks only for the rest.

## Pulls against their ceilings

| Host | Requests | What |
|---|---|---|
| api.eia.gov | 89 of 90 | route `electricity/rto/region-sub-ba-data`, January to early August 2020 |

## Decisions made without you

- The pull ran through `runs/c045/write_table.sh` (the lock, then the validator, coverage and archive once the table exists), so session 698 runs the same command.

## For Samuel's ruling

- None new.

## Files

- New: this report. On the data machine only: the saved pages, the run log `warehouse/output/logs/eia930_subba_20261023T004839Z.log`, `runs/s697_write.out`.
