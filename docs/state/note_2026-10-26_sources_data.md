# The data machine's note of chain 037, the night of 22 October: more public sources (written 22 October 2026, about 02:15 UTC)

Energy Research Warehouse (ERW), session 616, for Samuel. The data machine's chain 037 (sessions 610 to 616, `queue/done/037-night-22-october-sources.md`), unattended on lab-desktop, from 01:18 UTC to this note's push. Model spend USD 0 in every session. Before it: [`docs/state/note_2026-10-25_night_sources_data.md`](note_2026-10-25_night_sources_data.md) (chain 035, landed as `3887785f`).

## Read these first

- **Session 610 broke its pull ceiling: 29 requests to api.eia.gov against 15, and wrote nothing.**
  - The cause was mine. I ran the trial from the worktree, where the connector finds no saved pages. It asked again for 29 pages of a product group the ERW already holds.
  - Sessions 555 to 601 ran trials from the main checkout, and every later session of this chain did so.
  - The fifth product group (eleven small products) is defined in the connector and moves to the next chain.
- **Four new tables: 1,143,231 rows**, on the data machine and in the archive. None is in the live set, and none was uploaded to Redivis. All are held from `/data`'s catalogue and Redivis v1 until a person uploads them.

  | Session | Table | Rows | Cross-check |
  |---|---|---|---|
  | 611 | `boem_ogor_lease_production_monthly`, 2015 on, 1,491 leases | 245,710 | equal to EIA's Federal Gulf to 2024 within 0.4% (oil) and 0.6% (gas) |
  | 612, 613 | `eia930_subba_demand_hourly_2025`, 83 sub-regions | 723,617 | five parents within 2% of FERC 714 at the median |
  | 614 | `eia_refinery_capacity_annual`, 1995 on | 51,504 | the PADDs and the states equal the U.S. to the barrel |
  | 615 | `eia_refinery_inputs_monthly`, 2015 on | 122,400 | the same series as `eia_petroleum_snd_monthly` equal on all 29,990 rows |

- **BOEM's lease production comes from OGOR-A, not OGOR-B** (611). BOEM names OGOR-B's 48 disposition codes but nowhere says which of them make a lease's production, so a sum of them would be my reading. OGOR-A gives each completion's production as BOEM defines it. OGOR-B is under "For Samuel's ruling".
- **The hours of EIA-930 and FERC 714 do not line up the same way for every parent** (613). FERC's hours fit one hour earlier for ERCO, ISNE, NYIS and PJM, and one hour later for CISO. The ERW holds no 2025 EIA-930 demand by balancing authority on this machine to settle it.
- **Vercel is still rate limited** (since 19:29 UTC on 21 October); the pushes changed nothing visible, and the snapshots show 0 differences.

## What each session landed

All on `task/610-616-sources`, this landing: three connectors (`boem_ogor.py`, `eia_refinery_capacity.py`, `eia_refinery_inputs.py`), the year mode of `eia930_subba.py`, the fifth product group of `eia_petroleum_snd.py`, their tests and reports, every table's metadata, holds and release rows, and this note.

## Pulls against their ceilings

| Session | Used | Ceiling |
|---|---|---|
| 610 | 29 | 15 (broken) |
| 611 | 20 (www.data.boem.gov) | 25 |
| 612 | 89 | 90 |
| 613 | 62 | 90 |
| 614 | 14 | 15 |
| 615 | 29 | 30 |

## Waiting for Samuel, highest value first

Unchanged from chains 022 to 035, the daily recompute against the cards' tests first. Added by this chain:

- OGOR-B's dispositions (611);
- EIA-930's 2025 demand by balancing authority on the data machine, for the year tables' checks (613).

## The next chain

`queue/next/038-night-22-october-sources.md` (sessions 617 to 623) was pushed to main on its own as `a3043fe1`, with snapshots (s616q-before against s616q-after, 0 differences), before this landing. It holds:

- the fifth product group;
- refinery capacity's early years with refinery production by district;
- BOEM's OGOR-A from 1996 to 2014;
- EIA-930's sub-regions for 2024, in two parts;
- one more source;
- the note and the queue.
