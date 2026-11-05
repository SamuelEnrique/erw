# The data machine's note of chain 035, the night of 21 to 22 October: more public sources (written 22 October 2026, about 00:57 UTC)

Energy Research Warehouse (ERW), session 606, for Samuel. The data machine's chain 035 (sessions 600 to 606, `queue/done/035-night-22-october-sources.md`), unattended on lab-desktop, from 00:21 UTC to this note's push. Model spend USD 0 in every session. Before it: [`docs/state/note_2026-10-25_sources_data.md`](note_2026-10-25_sources_data.md) (chain 033, landed as `16a76297`).

## Read these first

- **Four new tables, and petroleum supply widened: 492,627 new rows**, on the data machine and in the archive. None is in the live set, and none was uploaded to Redivis. All are held from `/data`'s catalogue and Redivis v1 until a person uploads them.

  | Session | Table | New rows | Cross-check |
  |---|---|---|---|
  | 600, 601 | `eia_petroleum_snd_monthly`, now 47 products | 253,373 | the new series equal session 556's; every earlier row unchanged |
  | 602 | `eia930_subba_demand_hourly`, the last 90 days | 186,177 | the sub-regions sum to their parents (median 0.985 to 1.0001) |
  | 603 | `eia_drilling_monthly`, 1973 on | 3,431 | onshore plus offshore equals the U.S. in 584 of 638 months |
  | 604 | `eia_gas_wells_annual`, 1989 to 2020 | 1,062 | the states equal the U.S. every year |
  | 605 | `eia_heating_fuel_prices_weekly`, 2012 on | 48,534 | residential above wholesale in 99.9% of weeks |

- **Not pulled: BOEM's offshore production by lease** (605). The files are public and the robots file allows us. But each row is a disposition under BOEM's codes, whose meanings are in yearly PDFs; it is left for a session that reads them first.
- **Petroleum supply and disposition has eleven small products left** (about 10 pages), for the next chain.
- **EIA-930's sub-region data lag**: the newest hour is 06:00 UTC on 21 October, and the hours missing are counted in the table's header, never filled (602).
- **Vercel is still rate limited** ("retry in 24 hours", since 19:29 UTC on 21 October); it should accept deploys again from about 19:30 UTC on 22 October. The pushes changed nothing visible, and the snapshots show 0 differences.

## What each session landed

All on `task/600-606-sources`, this landing: four connectors (`eia930_subba.py`, `eia_drilling.py`, `eia_gas_wells.py`, `eia_heating_fuel_prices.py`), the third and fourth product groups in `eia_petroleum_snd.py`, their tests and reports (603 and 604's pointing to 600's), every table's metadata, holds and release rows, and this note.

## Pulls against their ceilings

| Session | Used | Ceiling |
|---|---|---|
| 600 | 28 | 30 |
| 601 | 26 | 30 |
| 602 | 39 | 60 |
| 603 | 2 | 10 |
| 604 | 2 | 10 |
| 605 | 17 (5 to www.data.boem.gov, 12 to api.eia.gov) | 20 |
| 606 (the next file's routes) | 2 | none set |

## Waiting for Samuel, highest value first

Unchanged from chains 022 to 033: the daily recompute against the cards' tests first. The unit rulings (tonnage, SO2 and NOx) would open more of EIA's coal and emissions data.

## The next chain

`queue/next/037-night-22-october-sources.md` (sessions 610 to 616) was pushed to main on its own as `1c21aabd`, with snapshots (s606q-before against s606q-after, 0 differences), before this landing. The code machine had taken 036 and session 607 minutes before; 608 and 609 are left for it. It holds:

- petroleum supply's last eleven products;
- BOEM's offshore production by lease, after its PDFs;
- EIA-930's sub-region demand for 2025, in two parts;
- refinery capacity;
- the note and the queue.
