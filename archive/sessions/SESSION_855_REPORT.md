# Session 855 report: EIA-930's demand by sub-region, 2019, the first half of the pages

23 October 2026, from 01:56 UTC, on lab-desktop (the data machine), a session of `queue/done/046-night-22-october-data-sources-gaps.md`. Model spend USD 0.

## Read these first

- **`python warehouse/connectors/eia930_subba.py --year 2019` ran under the data lock to its ceiling and saved its pages**, as the chain plans; no table yet. January to July 2019 are read whole (July 61,000 records) and August's first pages saved. The run stopped at the connector's ceiling (89) and wrote nothing (session 612's rule). Session 856 reuses every saved page.

## Pulls against their ceilings

| Host | Requests | What |
|---|---|---|
| api.eia.gov | 89 of 90 | route `electricity/rto/region-sub-ba-data`, January to early August 2019 |

## Decisions made without you

- None.

## For Samuel's ruling

- None new.

## Files

- New: this report. On the data machine only: the saved pages under `warehouse/raw/eia930_subba/`, the run log, `runs/s855_write.out`.
