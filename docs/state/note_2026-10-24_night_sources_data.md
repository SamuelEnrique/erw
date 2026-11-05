# The data machine's note of chain 031, the night of 21 to 22 October: more public sources (written 21 October 2026, about 23:28 UTC)

Energy Research Warehouse (ERW), session 561, for Samuel. The data machine's chain 031 (sessions 555 to 561, `queue/done/031-night-22-october-sources.md`), unattended on lab-desktop, from 22:24 UTC to this note's push. Model spend USD 0 in every session. Before it: [`docs/state/note_2026-10-24_sources_data.md`](note_2026-10-24_sources_data.md) (chain 030, landed as `454b4cb7`).

## Read these first

- **Six new tables, 223,152 rows**, on the data machine and in the archive. None is in the live set, and none was uploaded to Redivis. All are held from `/data`'s catalogue and Redivis v1 until a person uploads them.

  | Session | Table | Rows | Cross-check |
  |---|---|---|---|
  | 555 | `eia_petroleum_snd_monthly`, eight products, 2015 on | 100,340 | U.S. crude field production equal to session 527's on all 139 months |
  | 556 | `eia_product_supplied_monthly`, every product, 2017 on | 71,938 | the 96 series shared with 555 are equal on every row |
  | 557 | `eia_gas_balance_annual`, by state, 1997 to 2025 | 11,274 | consumption against SEDS: median 1.005; U.S. dry production equal every year |
  | 558 | `eia_wood_pellets_monthly`, 2016 on | 1,613 | the regions sum to the U.S. (a region withheld in a few months) |
  | 559 | `eia_petroleum_stocks_monthly`, 2001 on | 18,247 | about 1% above the weekly report's month-end figures |
  | 560 | `eia_energy_efficiency_state_annual`, 2013 to 2024 | 19,740 | sectors and states sum exactly |

- **Not pulled: PHMSA's pipeline incidents** (560). The host answers 403 to every automated request, including its robots file. That is an access control, not worked around.
- **Found on the way**:
  - `petroleum/stoc/ts` holds product stocks only, not crude or storage types, and its connector says so (559).
  - EIA's API answered 502s through much of the evening; sessions were reordered around them, and every page was asked again or reused, never filled (556, 557).
  - My own slip: a YAML edit missed on Windows line endings, and was caught and put right before the commit (555).
- **Vercel is still rate limited** ("retry in 24 hours", since 19:29 UTC). The pushes changed nothing visible, and the snapshots show 0 differences.

## What each session landed

All on `task/555-561-sources`, this landing: six connectors (`eia_petroleum_snd.py`, `eia_product_supplied.py`, `eia_gas_balance.py`, `eia_wood_pellets.py`, `eia_petroleum_stocks.py`, `eia_energy_efficiency.py`), their tests and reports, every table's metadata, holds and release rows, and this note.

## Pulls against their ceilings

| Session | Used | Ceiling |
|---|---|---|
| 555 | 23 | 30 |
| 556 | 19 | 20 |
| 557 | 7 | 20 |
| 558 | 7 | 20 |
| 559 | 5 | 20 |
| 560 | 4 (api.eia.gov) | 20 |

PHMSA's 2 refused requests are counted in session 554's note.

## Decisions made without you (one line each)

- 555: eight products and 2015 on, within the ceiling.
- 557: the annual form, since the monthly one repeats what the ERW holds.
- 558: one table for three routes; tonnages not taken.
- 560: EIA's energy efficiency programs in place of PHMSA.

## Waiting for Samuel, highest value first

Unchanged from chains 022 to 030: the daily recompute against the cards' tests first. `short_ton` in the vocabulary would also open wood pellets' and coal's tonnages (558).

## The next chain

`queue/next/033-night-22-october-sources.md` (sessions 570 to 576) was pushed to main on its own, with snapshots, before this landing. It was first pushed as `032-night-22-october-sources.md` with sessions 562 to 568, and renumbered within minutes: the code machine had queued its own `032-night-22-october-code-563.md`, and its `wip/562-land-023` holds sessions 562 and 563. 564 to 569 are left for the code machine. It holds:

- 570: advanced meters by state;
- 571: power plants' CO2 by state and fuel;
- 572 and 573: coal prices by rank, and coal exports' and imports' prices;
- 574: petroleum supply and disposition's other products;
- 575: wood pellets' feedstock costs;
- 576: the note and the queue.
