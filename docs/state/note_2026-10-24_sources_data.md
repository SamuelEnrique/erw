# The data machine's note of chain 030, the night of 21 to 22 October: more public sources (written 21 October 2026, about 22:38 UTC)

Energy Research Warehouse (ERW), session 554, for Samuel. The data machine's chain 030 (sessions 548 to 554, `queue/done/030-night-22-october-sources.md`), unattended on lab-desktop, from 22:02 UTC to this note's push. Model spend USD 0 in every session. Before it: [`docs/state/note_2026-10-23_late_sources_data.md`](note_2026-10-23_late_sources_data.md) (chain 029, landed as `17d0020f`).

## Read these first

- **Five new tables, on the data machine and in the archive.** None is in the live set, and none was uploaded to Redivis. All are held from `/data`'s catalogue and Redivis v1 until a person uploads them.

  | Session | Table | Rows | Cross-check |
  |---|---|---|---|
  | 548, 549 | `eia_nuclear_outages_generator_daily`, by reactor | 2,141,406, 2007 to 2026 | the reactors sum to each plant on all 437,624 plant-days |
  | 550 | `eia_gas_interstate_annual`, 1997 to 2024 | 29,470 | net receipts against consumption less production: correlation 0.991 |
  | 551 | `eia_crude_reserves_annual`, 1977 to 2021 | 13,931 | the Lower 48 and Alaska equal the U.S. every year |
  | 552 | `eia_gas_reserves_annual`, 1977 to 2021 | 19,232 | the same |
  | 553 | `eia_coal_delivered_price_annual`, 2000 to 2025 | 3,213 | the plants' coal cost by state: median 1.000 |

- **Not pulled: coal receipts by plant and mine** (553). EIA's records repeat every field it gives with two prices, so they have no key; a weighted average would be my figure, not EIA's. A ruling is listed below.
- **Answered: session 516's puzzle.** EIA's "total" for the plant route counted reactors, as the reactor route's 413,039 records from 2015 show (548).
- **A repeat in EIA's data, handled**: one Louisiana series under two ids with one value, kept once (550).
- **Vercel is still rate limited** ("retry in 24 hours", since 19:29 UTC). Every push changed nothing visible, and the snapshots show 0 differences.

## What each session landed

All on `task/548-554-sources`, this landing:

| Session | What |
|---|---|
| 548, 549 | `warehouse/connectors/eia_nuclear_outages_generator.py` and tests |
| 550 | `warehouse/connectors/eia_gas_interstate.py` and tests |
| 551, 552 | `warehouse/connectors/eia_crude_reserves.py` and `eia_gas_reserves.py`, with tests |
| 553 | `warehouse/connectors/eia_coal_delivered_price.py` and tests |
| 554 | this note and the next file |

Every table's metadata, holds and release rows are in the same landing.

## Pulls against their ceilings

| Session | Used | Ceiling |
|---|---|---|
| 548 | 83 | 100 |
| 549 | 63 | 100 |
| 550 | 7 | 20 |
| 551 | 4 | 10 |
| 552 | 6 | 10 |
| 553 | 6 | 30 |
| 554 (routes for the next file; 555's probe; PHMSA, refused, for 560) | 8 | none set |

All requests were to api.eia.gov.

## Waiting for Samuel, highest value first

1. Chains 022, 026 and 027's lists stand, the daily recompute against the cards' tests first.
2. **Coal receipts by plant and mine**: wanted with EIA's repeated records kept as given (a row number in the key), or not at all (553).

## The next chain

`queue/next/031-night-22-october-sources.md` (sessions 555 to 561) was pushed to main on its own, with snapshots, before this landing. It holds:

- 555: petroleum supply and disposition; its probe found 3,949 records a month, so it must narrow by product or period;
- 556: products supplied;
- 557: natural gas supply and disposition;
- 558: wood pellets;
- 559: petroleum stocks by type;
- 560: one more source;
- 561: the note and the queue.
