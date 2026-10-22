# The data machine's note of chain 038, the night of 22 October: more public sources (written 22 October 2026, about 03:30 UTC)

Energy Research Warehouse (ERW), session 623, for Samuel. The data machine's chain 038 (sessions 617 to 623, `queue/done/038-night-22-october-sources.md`), unattended on lab-desktop, from 02:29 UTC to this note's push. Model spend USD 0 in every session. Before it: [`docs/state/note_2026-10-26_sources_data.md`](note_2026-10-26_sources_data.md) (chain 037, landed as `95224f02`).

## Read these first

- **Three new tables and three widened: 2,143,059 new rows**, on the data machine and in the archive. None is in the live set, and none was uploaded to Redivis. All are held from `/data`'s catalogue and Redivis v1 until a person uploads them.

  | Session | Table | New rows | Cross-check |
  |---|---|---|---|
  | 617 | `eia_petroleum_snd_monthly`, now all 58 products | 47,966 | earlier rows unchanged; equal to `eia_product_supplied_monthly` on 8,112 rows |
  | 618 | `eia_refinery_production_monthly` (new), by district | 175,413 | equal to `eia_petroleum_snd_monthly` on all 56,926 rows in common |
  | 619 | `eia_refinery_capacity_annual`, from 1982 | 11,300 | the PADDs equal the U.S. every year |
  | 619 | `boem_ogor_lease_production_monthly`, from 1996 | 885,852 | 2005 on within 0.5% of EIA for oil |
  | 620, 621 | `eia930_subba_demand_hourly_2024` (new) | 726,716 | six parents within 2% of FERC 714 at the median |
  | 622 | `eia_padd_rail_barge_movements_monthly` (new), 2010 on | 56,182 | totals equal crude plus products on every key |

- **Every session kept under its ceiling.** Every trial ran from the main checkout, the rule chain 038 added after session 610.
- **Chain 037's landing deployed on Vercel** (`95224f02`, 02:30:45 UTC), the first deploy since 19:29 UTC on 21 October. The next push was rate limited again. Every snapshot compare shows 0 differences: every page is in review.
- **A metadata patch can carry main's older row of a table the branch widened** (622 met session 617's row). A plain union would keep both. The resolver used keeps the branch's lines and adds only the new table's (`runs/s622/resolve_ours_plus.py`).
- **BOEM's 2009 file repeats one line in every field** (619). The connector keeps such a line once and counts it in the header.

## What each session landed

All on `task/617-623-sources`, this landing: two connectors (`eia_refinery_production.py`, `eia_padd_movements.py`), early windows and request ceilings in `eia_refinery_capacity.py` and `boem_ogor.py`, the lower ceiling of `eia_petroleum_snd.py`, their tests and reports, every table's metadata, holds and release rows, and this note.

## Pulls against their ceilings

| Session | Used | Ceiling |
|---|---|---|
| 617 | 10 | 15 |
| 618 | 38 | 40 |
| 619 | 3 (api.eia.gov), 20 (www.data.boem.gov) | 5, 22 |
| 620 | 89 | 90 |
| 621 | 65 | 90 |
| 622 | 15 | 20 |
| 623 (the next file's routes) | 3 | none set |

## Waiting for Samuel, highest value first

Unchanged from chain 037: the daily recompute against the cards' tests first, then OGOR-B's dispositions and EIA-930's demand by balancing authority on the data machine.

## The next chain

`queue/next/039-night-22-october-sources.md` (sessions 624 to 630) was pushed to main on its own as `38bebe26`, with snapshots (s623q-before against s623q-after, 0 differences), before this landing. It holds:

- tanker and barge movements before 2010;
- natural gas exports and imports by country;
- underground gas storage capacity;
- EIA-930's sub-regions for 2023, in two parts;
- one more source;
- the note and the queue.
