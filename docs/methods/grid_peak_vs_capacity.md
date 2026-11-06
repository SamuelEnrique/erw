# Each grid's peak demand against its installed capacity

One derived table, `grid_peak_vs_capacity`, built by `warehouse/derived/grid_peak_vs_capacity.py` (session 672, chain
043): the All grids tab's headroom column. No request is made: both inputs are tables the warehouse holds. It is the
second half of session 672; the first half, NERC's reserve margins, was not pulled because NERC's terms could not be
read (session 666).

## Inputs and license

- **Peak:** `eia930_demand_growth`'s `peak_demand_mw` for the grid's balancing authority (CISO, ERCO, ISNE, MISO,
  NYIS, PJM, SWPP), the last whole year it holds (2025 when written): the highest hour of EIA-930's demand that passes
  that table's test for faulty hours (`docs/methods/demand_growth.md`). `x_at` is the hour's start, UTC.
- **Capacity:** `eia860m_operating_generators` (EIA-860M, vintage 2026-08 when written): every operating generator's
  net summer capacity (`net_summer_mw`) and its balancing authority (`balancing_authority`), as EIA gives them.

Both are works of the U.S. government: public.

## No state is mapped to a grid

EIA-860M names each generator's balancing authority, so a grid's capacity is the sum over its own generators, not over
states assigned to it. The states the grid's generators stand in are in `x_states`; a state with more than 1 percent of
its capacity in another balancing authority is named in `x_split_states` (Texas is split between ERCOT, SPP, MISO and El
Paso Electric; New Jersey between PJM and NYISO's generators there; and so on). The chain asked for a state mapping;
the balancing authority field makes one unnecessary and avoids splitting a state's capacity by guess.

## Variables

`entity` `grid_peak_vs_capacity:<grid>`; `ts_utc` 1 January of the peak's year; `freq` `P1Y`.

| Variable | Unit | What |
|---|---|---|
| `peak_demand_mw` | MW | the year's peak hour |
| `capacity_mw` | MW | net summer capacity of the listed generators that began operating by the end of the peak's year |
| `capacity_mw_listed` | MW | every operating generator in the list, whatever its first year (`x_vintage` the list's month) |
| `capacity_solar_mw`, `capacity_wind_mw`, `capacity_storage_mw` | MW | the parts of `capacity_mw` whose energy source is SUN, WND and MWH |
| `peak_to_capacity` | ratio | `peak_demand_mw / capacity_mw` |
| `capacity_over_peak_pct` | pct | `(capacity_mw - peak_demand_mw) / peak_demand_mw * 100` |

When written (2025 peaks, the 2026-08 list): CAISO 0.49, ERCOT 0.51, SPP 0.56, MISO 0.62, ISO-NE 0.73, NYISO 0.74,
PJM 0.76.

## What it is not

- **Not a reserve margin.** Net summer capacity counts solar, wind and storage at their summer ratings, not at what they
  give in the peak hour, and counts no imports or demand response. A planner's anticipated reserve margin (NERC's)
  discounts them; that is why CAISO and ERCOT, with the most solar and storage, show the most capacity over peak.
- **Not the year's own fleet.** `capacity_mw` is read back from today's list: a generator retired since the peak's
  year is not in it, so the figure can be below what stood that year.
- **One hour.** The peak is one hour of one year; a hotter or colder year moves it.

<a id="cross-checks"></a>

## Cross-checks

Session 681 (chain 043): this table's peak hour against the peak the site's demand pages draw (the Grid and demand tools' copy of `eia930_demand_growth`, `site/data/demand_growth.json`). A check that the table and the pages agree, not against a publisher's own peak: EIA-930 is the source of both. No figure was moved.

| Our figure | Published figure | Source and date | Gap | Reason |
|---|---|---|---|---|
| CAISO: 2025 peak 43,860 MW at 2025-08-22 01:00 UTC | 43,860 MW at 2025-08-22 01:00 UTC | docs/methods/demand_growth.md, the site's copy `site/data/demand_growth.json`, built 2026-10-05 | 0 MW, the same hour | The peak the demand pages show, built on 5 October, is this table's input as rebuilt on 21 October, hour for hour |
| ERCOT: 2025 peak 83,597 MW at 2025-08-18 22:00 UTC | 83,597 MW at 2025-08-18 22:00 UTC | the same | 0 MW, the same hour | The peak the demand pages show, built on 5 October, is this table's input as rebuilt on 21 October, hour for hour |
| ISONE: 2025 peak 25,898 MW at 2025-06-24 22:00 UTC | 25,898 MW at 2025-06-24 22:00 UTC | the same | 0 MW, the same hour | The peak the demand pages show, built on 5 October, is this table's input as rebuilt on 21 October, hour for hour |
| MISO: 2025 peak 120,343 MW at 2025-07-24 20:00 UTC | 120,343 MW at 2025-07-24 20:00 UTC | the same | 0 MW, the same hour | The peak the demand pages show, built on 5 October, is this table's input as rebuilt on 21 October, hour for hour |
| NYISO: 2025 peak 31,857 MW at 2025-06-24 22:00 UTC | 31,857 MW at 2025-06-24 22:00 UTC | the same | 0 MW, the same hour | The peak the demand pages show, built on 5 October, is this table's input as rebuilt on 21 October, hour for hour |
| PJM: 2025 peak 160,560 MW at 2025-06-23 21:00 UTC | 160,560 MW at 2025-06-23 21:00 UTC | the same | 0 MW, the same hour | The peak the demand pages show, built on 5 October, is this table's input as rebuilt on 21 October, hour for hour |
| SPP: 2025 peak 54,411 MW at 2025-07-29 21:00 UTC | 54,411 MW at 2025-07-29 21:00 UTC | the same | 0 MW, the same hour | The peak the demand pages show, built on 5 October, is this table's input as rebuilt on 21 October, hour for hour |
