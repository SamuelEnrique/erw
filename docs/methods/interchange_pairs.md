# Who trades with whom (`interchange_pair_daily`, `interchange_pair_monthly`, `ba_trade_partners`, `interchange_event_pairs`)

Session 8002, chain 501 part C, 19 November 2026. Builder: `warehouse/derived/interchange_pairs.py`. Page file: `site/data/regions/trade_matrix.json` (its shape: `docs/state/page_files_regions.md`, section 7).

These tables describe: sums of what each side reported, the mean of the two reports, their gap, counts of hours and ranks. They hold no model, no estimate and no statement of cause.

## Inputs

- `eia930_ba_interchange_hourly_2018` to `_2026`: every tie between two balancing authorities, hour by hour, each side's report its own row, positive when the reporting authority sends power to its neighbour, as filed in EIA's six-month files (`docs/methods/eia930_region_hourly.md`).
- `eia930_region_pair_hourly`: each pair of EIA's regions, the first region's reports about the second summed and the second's about the first summed, turned to the same direction.
- `eia930_ba_supply_hourly` (each authority's total interchange) and `eia930_ba_demand_hourly` (its demand), for the share of demand met by net imports.

## The pair rule

For a pair A-B, A is the one whose code comes first. A's report is power from A to B as A filed it; B's report of the same tie is turned to the same direction. Over a day, a month or an event's window:

| Column | Meaning |
|---|---|
| `x_a_report_mwh`, `x_hours_a` | the sum of A's reported hours, and how many |
| `x_b_report_mwh`, `x_hours_b` | the same for B's |
| `x_hours_both` | the hours both reported |
| `x_gap_mwh` | over the hours both reported, A's report less B's |
| `value` | over the hours both reported, the mean of the two (`x_basis` `mean`); where no hour has both, the side that reported (`x_basis` `a` or `b`) |
| `x_direction` | `a_to_b` when `value` is above zero, `b_to_a` below, `none` at zero |
| `x_level` | `ba` for two balancing authorities, `region` for two regions |

For region pairs the first and second reports of `eia930_region_pair_hourly` are A's and B's. Neighbours outside the lower 48 (`CAN`, `MEX`, and Canadian and Mexican authorities) are kept as EIA lists them.

Days and months are Eastern (America/New_York), as in `ba_supply_monthly`.

## `ba_trade_partners`

For each balancing authority and Eastern year, from its own reports only (one row a partner, `entity` `eia930:<authority>-<partner>`, with `x_ba` and `x_partner`): with each partner, the gross exchange (the sum of the absolute hourly flows) and the net imports (the same flows signed, positive when it received power), and each partner's rank within the year by gross and by net (net ranked by size, whichever direction). `x_hours` is how many hours it reported for that tie.

`net_import_share_of_demand_pct` (`entity` `eia930:<authority>`): the authority's total interchange with its sign turned, summed over the hours it holds both that and its demand, over its demand in the same hours, percent. Below zero, the authority sent out more than it took in over those hours. It is a ratio of two sums the authority reported, not a measure of what any import displaced.

## `interchange_event_pairs`

The nine events of `/events` (their dates in `warehouse/derived/event_window.py`). For each event, the window runs from midnight of its first day in Eastern time to midnight after its last day in Pacific time, so every region's local days are inside it. Each pair's sums over that window (`x_role` `event`) stand beside the same calendar dates in every other year the tables hold, July 2018 to November 2026 (`x_role` `other_year`, `x_year` the year). A window the tables do not reach (before July 2018, after the newest hour) is not written; a window they reach in part is summed over the hours held, and the hour counts say how many.

## The first build (19 November 2026)

| Table | Rows |
|---|---|
| `interchange_pair_daily` | 552,751 |
| `interchange_pair_monthly` | 18,284 |
| `ba_trade_partners` | 5,987 |
| `interchange_event_pairs` | 13,574 |

A check against the region pair table: the Carolinas and the Southeast in August 2025 read -501,753 MWh by the Carolinas' reports and -506,389 by the Southeast's, a gap of 2,226 MWh over the 720 hours both held, the same figures `site/data/regions/trade/car.json` carries with the Carolinas' import sign.

## Build

    python warehouse/lock.py run --task pairs -- <python> warehouse/derived/interchange_pairs.py

The data machine's daily run calls it after the EIA-930 tables are brought to the newest hour.
