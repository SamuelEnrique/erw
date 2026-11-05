# The data machine's note of chain 041, finished by chain 044 (written 22 October 2026, about 10:55 UTC)

Energy Research Warehouse (ERW), session 686, for Samuel. Chain 041 (`queue/done/041-morning-22-october-sources.md`, sessions 638 to 644) ran on lab-desktop from 06:41 UTC and stopped after session 640 (07:12 UTC), with its session 641 started and not finished. The owner's chain 043 ran next; its successor, chain 044 (`queue/done/044-night-24-october-data.md`), did chain 041's remaining work in sessions 684 and 685 and lands it here. Model spend USD 0 in every session. Before it: [`note_2026-10-27_night_sources_data.md`](note_2026-10-27_night_sources_data.md) (chain 040).

## Read these first

- **Three tables widened and two new: 1,104,616 new rows**, on the data machine and in the archive. None is in the live set or on Redivis; each is held from `/data`'s catalogue and Redivis v1 like the tables before it.

  | Session | Table | New rows | Cross-check |
  |---|---|---|---|
  | 638 | `eia_refinery_production_monthly`, from 2005 | 151,406 | the PADDs against the U.S. within 1 kbbl on 11,282 of 11,370 keys; 2015 on unchanged |
  | 639 | `eia_crude_imports_detail_monthly`, from 2009 | 28,614 | 1.017 to 1.049 times the country table's U.S. total in 2009 and 2010 (two EIA forms); 2011 on unchanged |
  | 639 | `eia_ngl_production_monthly`, from 1973 | 78,940 | the later rows unchanged |
  | 640, 641, 684 | `eia930_subba_demand_hourly_2021` (new) | 710,831 | six parents within 2% of FERC 714 at the median |
  | 685 | `eia_coal_production_annual` (new), 2001 to 2024 | 22,630 | the states 99.75 to 99.95 percent of the U.S. every year |

- **A new unit, `short_ton`** (Decision 50), for coal production.
- **Session 641's run** (07:12 to about 07:48 UTC) saved 2021's August to December pages and wrote nothing; session 684 wrote the year from them with no request.

## Pulls against their ceilings

| Session | Used | Ceiling |
|---|---|---|
| 638 | 31 | 40 |
| 639 | reported in its report | 25 |
| 640 | 89 | 90 |
| 641 | not recorded (no report) | 90 |
| 684 | 0 | 90 |
| 685 | 4 | 20 |

## Waiting for Samuel

Unchanged from chain 043's note (`note_2026-10-24_data.md`): the Redivis click on the Stanford dataset, its daily target, the caps, an OpenEI key, HIFLD's successor and NERC's terms.

## The landing

`wip/638-644-sources` merged with origin/main (chain 043 landed first), the whole suite, `scripts/freeze.py status`, rule 8's snapshots and `task/638-644-sources`; session 686's report holds the lines.
