# The data machine's note of chain 033, the night of 21 to 22 October: more public sources (written 22 October 2026, about 00:02 UTC)

Energy Research Warehouse (ERW), session 576, for Samuel. The data machine's chain 033 (sessions 570 to 576, `queue/done/033-night-22-october-sources.md`), unattended on lab-desktop, from 23:35 UTC on 21 October to this note's push. Model spend USD 0 in every session. Before it: [`docs/state/note_2026-10-24_night_sources_data.md`](note_2026-10-24_night_sources_data.md) (chain 031, landed as `ffa9ddbd`).

## Read these first

- **Four new tables, and two widened: 169,317 new rows**, on the data machine and in the archive. None is in the live set, and none was uploaded to Redivis. All are held from `/data`'s catalogue and Redivis v1 until a person uploads them.

  | Session | Table | New rows | Cross-check |
  |---|---|---|---|
  | 570 | `eia_meters_state_annual`, 2013 to 2024 | 8,578 | the kinds sum to all meters; residential meters a median 1.015 of EIA-861's customers |
  | 571 | `eia_power_co2_state_annual`, 1990 to 2024 | 10,640 | a median 5% above session 530's electric power sector (CHP plants included) |
  | 572 | `eia_coal_price_rank_annual`, 2001 to 2024 | 2,843 | all ranks equal all markets in 93.7% of area-years |
  | 573 | `eia_coal_trade_price_annual`, 2000 to 2025 | 24,623 | exports about 4 times the mine price (an order of magnitude) |
  | 574 | `eia_petroleum_snd_monthly`, now twenty products | 122,156 | the new series equal session 556's; session 555's rows unchanged |
  | 575 | `eia_wood_pellets_monthly`, with feedstock costs | 477 | the dearest feedstock below the pellet price every month |

- **This chain's numbers were changed once, before it ran**: it was first pushed as `032-night-22-october-sources.md` with sessions 562 to 568. The code machine had already queued its own 032 holding 562 and 563, so this chain became `033` with 570 to 576. Its code chain 034 holds 577 to 589, so the next file starts at 600.
- **Vercel is still rate limited** ("retry in 24 hours", since 19:29 UTC on 21 October). The pushes changed nothing visible, and the snapshots show 0 differences.

## What each session landed

All on `task/570-576-sources`, this landing: four connectors (`eia_meters.py`, `eia_power_co2_state.py`, `eia_coal_price_rank.py`, `eia_coal_trade_price.py`), product groups in `eia_petroleum_snd.py`, a feedstock route in `eia_wood_pellets.py`, their tests and reports (571 to 573's pointing to 570's), every table's metadata, holds and release rows, and this note.

## Pulls against their ceilings

| Session | Used | Ceiling |
|---|---|---|
| 570 | 4 | 10 |
| 571 | 4 | 10 |
| 572 | 2 | 10 |
| 573 | 8 | 20 |
| 574 | 26 | 30 |
| 575 | 3 | 10 |
| 576 (the next file's routes) | 3 | none set |

All requests were to api.eia.gov.

## Waiting for Samuel, highest value first

1. Unchanged from chains 022 to 031: the daily recompute against the cards' tests first.
2. **SO2 and NOx units** (short tons, pounds per MWh), for power plants' emissions (571), beside the tonnage ruling already asked.

## The next chain

`queue/next/035-night-22-october-sources.md` (sessions 600 to 606) was pushed to main on its own, with snapshots, before this landing. It holds:

- 600 and 601: petroleum supply and disposition's last products;
- 602: EIA-930's demand by sub-region, hourly, the last 90 days;
- 603: drilling activity;
- 604: natural gas wells by state;
- 605: one more source;
- 606: the note and the queue.
