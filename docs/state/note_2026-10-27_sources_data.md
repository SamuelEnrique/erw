# The data machine's note of chain 039, the night of 22 October: more public sources (written 22 October 2026, about 04:45 UTC)

Energy Research Warehouse (ERW), session 630, for Samuel. The data machine's chain 039 (sessions 624 to 630, `queue/done/039-night-22-october-sources.md`), unattended on lab-desktop, from 03:48 UTC to this note's push. Model spend USD 0 in every session. Before it: [`docs/state/note_2026-10-26_night_sources_data.md`](note_2026-10-26_night_sources_data.md) (chain 038, landed as `5283179e`).

## Read these first

- **Four new tables and one widened: 868,165 new rows**, on the data machine and in the archive. None is in the live set, and none was uploaded to Redivis. All are held from `/data`'s catalogue and Redivis v1 until a person uploads them.

  | Session | Table | New rows | Cross-check |
  |---|---|---|---|
  | 624 | `eia_padd_rail_barge_movements_monthly`, from 1986 | 64,560 | totals equal crude plus products on 3,931 of 3,935 early keys |
  | 625 | `eia_gas_trade_country_monthly` (new), 1973 on | 30,337 | the countries sum to the U.S. total on 1,823 of 1,856 keys |
  | 626 | `eia_gas_storage_capacity_monthly` (new), 1989 on | 23,980 | the states sum to the U.S. within 0.1% |
  | 627, 628 | `eia930_subba_demand_hourly_2023` (new) | 717,332 | six parents within 2% of FERC 714 at the median |
  | 629 | `eia_ngl_production_monthly` (new), by district | 31,956 | equal to `eia_petroleum_snd_monthly` on all 10,336 rows in common |

- **Every session kept under its ceiling**, every trial from the main checkout.
- **EIA's own figures disagree in a few places, kept as EIA gives them:**
  - four tanker and barge months of 1988 and 1989 where the parts and the total do not match (624);
  - 91 state months where working gas in storage is above the state's working capacity, Oregon in 2012 among them (626);
  - U.S. LNG exports by country against the terminal sums of `eia_lng_exports_monthly` (median 0.999, up to 1.38; 625).
- **Vercel deployed chain 038's landing** (`5283179e`, 03:47 UTC), and rate limited the push after it. Every snapshot compare shows 0 differences: every page is in review.
- **EIA-930's sub-regions now cover 2023 to 2025 whole and the last 90 days**: the same hour offset against FERC 714 in each year, and PNM's sub-regions about 1.38 to 1.39 times PNM's planning area.

## What each session landed

All on `task/624-630-sources`, this landing: four connectors (`eia_gas_trade.py`, `eia_gas_storage_capacity.py`, `eia_ngl_production.py`, and the early window of `eia_padd_movements.py`), their tests and reports, every table's metadata, holds and release rows, and this note.

## Pulls against their ceilings

| Session | Used | Ceiling |
|---|---|---|
| 624 | 16 | 25 |
| 625 | 13 | 30 |
| 626 | 7 | 15 |
| 627 | 89 | 90 |
| 628 | 65 | 90 |
| 629 | 10 | 20 |

## Waiting for Samuel, highest value first

Unchanged from chain 038: the daily recompute against the cards' tests first, then OGOR-B's dispositions and EIA-930's demand by balancing authority on the data machine.

## The next chain

`queue/next/040-night-22-october-sources.md` (sessions 631 to 637) was pushed to main on its own as `a7c86cfa`, with snapshots (s630q-before against s630q-after, 0 differences; its deploy rate limited), before this landing. It holds:

- oxygenate plant production;
- crude oil imports by origin and destination;
- EIA-930's sub-regions for 2022, in two parts;
- refinery inputs and production before 2015;
- one more source;
- the note and the queue.
