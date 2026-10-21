# The data machine's note of chain 027, the night of 21 to 22 October: more public sources (written 21 October 2026, about 20:31 UTC)

Energy Research Warehouse (ERW), session 522, for Samuel. The data machine's chain 027 (sessions 516 to 522, `queue/done/027-night-22-october-sources.md`), unattended on lab-desktop, from 19:51 UTC to this note's push. Model spend USD 0 in every session. Before it: [`docs/state/note_2026-10-22_night_sources_data.md`](note_2026-10-22_night_sources_data.md) (chain 026, landed as `15c84fb5`).

## Read these first

- **Four new tables, and one table extended: 1,845,179 new rows**, on the data machine and in the archive. None is in the live set, and none was uploaded to Redivis. All are held from `/data`'s catalogue and Redivis v1 until a person uploads them.

  | Session | Source | Table | Rows | Cross-check |
  |---|---|---|---|---|
  | 516 | EIA's nuclear outages by plant, daily 2015 to 2026 | `eia_nuclear_outages_facility_daily` | 741,501 | the plants' sums equal EIA's U.S. total on all 4,312 days |
  | 517 | EIA's natural gas prices by state, monthly 2001 to 2026 | `eia_gas_prices_state_monthly` | 72,550 | electric power price against plants' gas cost: median 0.997 |
  | 518 | EIA's natural gas consumption by state, monthly 2001 to 2026 | `eia_gas_consumption_state_monthly` | 63,420 | U.S. total against SEDS: 0.999 to 1.014 |
  | 519 | EIA's coal market sales price, annual 2001 to 2024 | `eia_coal_prices_annual` | 2,781 | order of magnitude only (mine prices include metallurgical coal) |
  | 520 | EIA-861M, now 2017 to 2026 | `eia861m_utility_sales_monthly` | 1,145,088 (964,927 new) | every year's median 1.0000 against the annual form |

- **The EIA-861M gaps are explained** (521). The utilities under customer choice report only bundled sales monthly; against the annual form's part A alone they agree (97.8% within 2%). Behind-the-meter owners and parts B and D explain most of the rest. 13 utility-states remain unexplained, and no table changed.
- **Coal production by mine is not pulled.** Its short tons are not in the unit vocabulary (519, item 2 below).
- **Faults found and fixed on the way**:
  - EIA's `total` for the plants' outages counts more rows than the data hold. The connector now reads until a short page and checks for missing days (516).
  - My own `runs/finish_table.sh` dropped another session's uncommitted release rows. It now keeps the working copy (518).
- **Vercel is still rate limited** (since 19:29 UTC; "retry in 24 hours"). The landing of chain 026 and every push since changed nothing visible, and the snapshots show 0 differences.

## What each session landed

All on `task/516-522-sources`, this landing:

| Session | What |
|---|---|
| 516 | `warehouse/connectors/eia_nuclear_outages_facility.py` and tests |
| 517 | `warehouse/connectors/eia_gas_prices_state.py` and tests |
| 518 | `warehouse/connectors/eia_gas_consumption_state.py` and tests |
| 519 | `warehouse/connectors/eia_coal_prices.py` and tests |
| 520 | `eia861m_sales.py` reads the 2017 to 2020 files; a test |
| 521 | its report |
| 522 | this note and the next file |

Every table's metadata, holds and release rows are in the same landing.

## Pulls against their ceilings

| Session | Host | Used | Ceiling |
|---|---|---|---|
| 516 | api.eia.gov | 53 | 100 |
| 517 | api.eia.gov | 20 | 30 |
| 518 | api.eia.gov | 14 | 30 |
| 519 | api.eia.gov | 5 | 20 (6 for the price) |
| 520 | www.eia.gov | 9 | 10 |
| 521 | none | 0 | 0 |

## Decisions made without you (one line each; the reasons are in each report)

- 516: 2015 on, within the ceiling; completeness by day order and no missing day.
- 517, 518: EIA's USD/Mcf and MMcf kept; consumption's smaller fuels left in the U.S. total.
- 519: coal prices in place of production.
- 521: no table changed.

## Waiting for Samuel, highest value first

1. Chains 022 and 026's lists stand. First: the daily recompute against the cards' tests; FERC 714's license.
2. **`short_ton` in the unit vocabulary**: coal production by mine, coal sales and AEO's coal rows (490, 519).

## The next chain

`queue/next/028-night-22-october-sources.md` (sessions 523 to 529; 530 is free, and 531 on is the old laptop's) was pushed to main on its own, with snapshots, before this landing. It holds:

- 523: nuclear outages by plant, 2007 to 2014;
- 524: EIA-923's back years;
- 525: natural gas storage by state;
- 526: the state electricity profiles' capacity;
- 527: crude oil production by state;
- 528: natural gas production by state;
- 529: the note and the queue.
