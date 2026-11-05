# The data machine's note of chain 040, the morning of 22 October: more public sources (written 22 October 2026, about 06:22 UTC)

Energy Research Warehouse (ERW), session 637, for Samuel. The data machine's chain 040 (sessions 631 to 637, `queue/done/040-night-22-october-sources.md`), unattended on lab-desktop, from 05:04 UTC to this note's push. Model spend USD 0 in every session. Before it: [`docs/state/note_2026-10-27_sources_data.md`](note_2026-10-27_sources_data.md) (chain 039, landed as `5ff2fad5`).

## Read these first

- **Three new tables and one widened: 967,226 new rows**, on the data machine and in the archive. None is in the live set, and none was uploaded to Redivis. All are held from `/data`'s catalogue and Redivis v1 until a person uploads them.

  | Session | Table | New rows | Cross-check |
  |---|---|---|---|
  | 631 | `eia_oxygenate_production_monthly` (new), 1981 on | 6,006 | U.S. fuel ethanol equal to `eia_petroleum_snd_monthly` in all 139 months |
  | 632, 636 | `eia_crude_imports_detail_monthly` (new), 2011 on | 154,779 | the U.S. total equal to `eia_crude_imports_by_country` at the median |
  | 633, 634 | `eia930_subba_demand_hourly_2022` (new) | 712,831 | six parents within 2% of FERC 714 at the median |
  | 635 | `eia_refinery_inputs_monthly`, from 2005 | 93,610 | the PADDs and districts sum to their whole on about 99% of keys |

- **Every session kept under its ceiling.** EIA answered HTTP 502 and 504 often this morning; each was asked once more, and two runs stopped and finished from their saved pages.
- **Session 632 stopped at EIA's errors** with 29 pages saved, and session 636 (the chain's open session) finished the table from them.
- **EIA's crude imports route counts more records than its pages hold** (160,665 against 154,779, every month there). The connector takes such a read only when every month is present.
- **Refinery production before 2015 was not pulled** (31 pages beyond session 635's ceiling); its connector is ready.
- **Vercel deployed chain 039's landing** (`5ff2fad5`, 05:03 UTC), and rate limited the push after it. Every snapshot compare shows 0 differences: every page is in review.

## What each session landed

All on `task/631-637-sources`, this landing: two connectors (`eia_oxygenate_production.py`, `eia_crude_imports_detail.py`), early windows in `eia_refinery_inputs.py` and `eia_refinery_production.py`, their tests and reports, every table's metadata, holds and release rows, and this note.

## Pulls against their ceilings

| Session | Used | Ceiling |
|---|---|---|
| 631 | 4 | 10 |
| 632 | 35 | 40 |
| 633 | 89 | 90 |
| 634 | 63 | 90 |
| 635 | 24 | 40 |
| 636 | 2 | 20 |

## Waiting for Samuel, highest value first

Unchanged from chain 039: the daily recompute against the cards' tests first, then OGOR-B's dispositions and EIA-930's demand by balancing authority on the data machine.

## The next chain

`queue/next/041-morning-22-october-sources.md` (sessions 638 to 644) was pushed to main on its own as `2a4a10e9`, with snapshots (s637q-before against s637q-after, 0 differences; its deploy rate limited), before this landing. It holds:

- refinery production before 2015;
- the early years of crude imports and of natural gas liquids;
- EIA-930's sub-regions for 2021, in two parts;
- two more sources;
- the note and the queue.
