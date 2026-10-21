# The data machine's note of chain 029, the night of 21 to 22 October: more public sources (written 21 October 2026, about 21:57 UTC)

Energy Research Warehouse (ERW), session 547, for Samuel. The data machine's chain 029 (sessions 530 and 543 to 547, `queue/done/029-night-22-october-sources.md`), unattended on lab-desktop, from 21:28 UTC to this note's push. Model spend USD 0 in every session. Before it: [`docs/state/note_2026-10-23_night_sources_data.md`](note_2026-10-23_night_sources_data.md) (chain 028, landed as `e0132d9f`).

## Read these first

- **Four new tables, and SEDS widened: 220,001 rows written**, on the data machine and in the archive. None is in the live set, and none was uploaded to Redivis. All are held from `/data`'s catalogue and Redivis v1 until a person uploads them.

  | Session | Table | Rows | Cross-check |
  |---|---|---|---|
  | 530 | `eia_co2_state_annual`, 1970 to 2022 | 66,144 | GHGRP's power plants by state: median 1.009 |
  | 543 | `eia_refinery_weekly`, 2010 on | 50,753 | three shared series equal `eia_petroleum_supply_weekly` on all 875 weeks |
  | 544 | `eia_state_source_disposition_annual`, 1990 to 2024 | 37,738 | generation equal to the monthly table, all within 1% |
  | 545 | `eia_net_metering_state_annual`, 2013 to 2024 | 16,226 | sectors and states sum exactly (no other table measures it) |
  | 546 | `eia_seds_state_energy`, now 27 series | 49,140 | gas by sector: 0.994 to 1.012; electricity by sector: 1.0000 |

- **Nothing in this chain needed a ruling, and nothing failed a check.**
- **Vercel is still rate limited** ("retry in 24 hours", since 19:29 UTC). Every push changed nothing visible, and the snapshots show 0 differences.

## What each session landed

All on `task/530-547-sources`, this landing:

| Session | What |
|---|---|
| 530 | `warehouse/connectors/eia_co2_state.py` and tests |
| 543 | `warehouse/connectors/eia_refinery_weekly.py` and tests |
| 544 | `warehouse/connectors/eia_state_disposition.py` and tests |
| 545 | `warehouse/connectors/eia_net_metering.py` and tests |
| 546 | `eia_seds.py`'s 14 new series and its page reuse; a test |
| 547 | this note and the next file |

Every table's metadata, holds and release rows are in the same landing.

## Pulls against their ceilings

| Session | Used | Ceiling |
|---|---|---|
| 530 | 18 | 20 |
| 543 | 12 | 20 |
| 544 | 2 | 20 |
| 545 | 4 | 10 |
| 546 | 11 | 20 |
| 547 (the routes checked for the next file) | 4 | none set |

All requests were to api.eia.gov.

## Decisions made without you (one line each)

- 543: refinery weeks from 2010, within the ceiling.
- 545: no cross-check against behind-the-meter sales, which measure something else.

## Waiting for Samuel, highest value first

Chains 022, 026 and 027's lists stand unchanged, the daily recompute against the cards' tests first.

## The next chain

`queue/next/030-night-22-october-sources.md` (sessions 548 to 554, free in every queue file and branch) was pushed to main on its own, with snapshots, before this landing. It holds:

- 548 and 549: nuclear outages by reactor;
- 550: interstate natural gas movements;
- 551 and 552: crude oil and natural gas proved reserves by state;
- 553: coal receipts' prices at power plants;
- 554: the note and the queue.
