# How clean, and when: the carbon-free share of each grid's generation

> **Session 133 (6 October 2026).** California's months from October 2019 to August 2020 (the hydro gap) are now read from CAISO's own supply by fuel, so their carbon-free share is held; no carbon figure is made for them, because EIA's carbon intensity of those hours still divides by a total without hydro. The page is a view of `/mix` (`/mix?view=clean`); what stood on its face is in this note. Details: `generation_mix_hourly.md`, "Session 133".

Energy Research Warehouse (ERW), session 122 (5 October 2026). Tables: `clean_energy_hourly`,
`clean_energy_summary`. Code: `warehouse/derived/mix_clean.py`. Page: `/mix/clean` (in review).

## What the figures are, and are not

1. **Generation inside the grid, not imports.** Each figure is what the grid's own plants put out, hour by hour. It is
   not what the grid's customers used: power the grid imported is not in it, and power it exported is. A grid that
   imports clean power looks dirtier here than its customers' supply, and one that imports coal power looks cleaner.
2. **Average, not marginal.** A carbon figure is the hour's CO2 over the hour's generation. It does not say what one
   more MWh of load would have emitted, which depends on the plant that would have met it. Moving load between hours
   changes the average figure by the amounts below; the marginal effect can be larger or smaller, in either direction.
3. **A flat load is an arithmetic device.** "A load that draws the same power every hour" is a yardstick, not a
   customer.

## The hours

The hours are the energy mix's ([`generation_mix_hourly.md`](generation_mix_hourly.md), `mix_profile.hours_of`):
EIA-930's hourly net generation by energy source for the seven ISO grids, from January 2019.

- **California from the join** (16 December 2025, [`eia930_caiso_break.md`](eia930_caiso_break.md)) is the California
  ISO's own supply by fuel. Before it, EIA's hours, with the late ones set back. The two are not one series: in the
  months both hold, EIA's California gas output was 251.7 GWh a day against CAISO's own 178.3. The step between the
  last year on EIA's data and the first on CAISO's is partly the change of source. The month of the join is not
  written.
- **The hydro gap.** EIA's file holds no hydro for California from October 2019 to mid August 2020. Those hours are
  not held (a main source is blank), so they are in no figure, and California's first year here is 2021.
- **Session 118's rule** ([`impossible_hours.md`](impossible_hours.md)): an impossible hour of demand is a blank in
  the mix's hours; here the same rule is also put to the hour's net generation, and an hour it leaves out is not held.
- **Nuclear under another name (found by this session).** In stretches from October 2021 (3,147 held hours), EIA's
  file has New York's nuclear output at nothing while its "other" stands higher by about as much: from 13 March to 1 May
  2023 nuclear is 12 MW on average against 2,671 in the same weeks of 2022, and "other" 3,080 against 899. New
  York's four reactors do not stop together for seven weeks. The hour's carbon-free share cannot be told, so it is
  not held. The test: nuclear under a quarter of its usual output while "other" is above its usual level by at least
  half of nuclear's usual output, "usual" being the median over the hours nuclear runs. A fleet that is truly off
  leaves "other" where it was and is kept: SPP's two plants from 6 October to 15 November 2022 (975 hours), and
  California's in October 2020. The test also leaves out 24 hours of California's. New York loses 2022 and 2023 as
  whole years to this. It is not yet in the register of known faults.
- An hour that is not held is used for nothing. A day is complete when every hour of the local day is held. A month
  is written when at least 90 percent of its days are complete, over those days. A year is written when at most one
  of its months is missing. Nothing is filled.

## Carbon-free

Nuclear, wind, solar and hydro. Generation is those plus natural gas, coal and "other" (oil, geothermal, biomass
and what EIA does not name). "Other" is counted as not carbon-free because EIA's file does not always separate
geothermal and biomass from oil. Where a grid has geothermal, its carbon-free share is understated by it. Storage is
not a source: what a battery puts out was generated before and is counted there.

## The share

- `carbon_free_share_pct`: carbon-free MWh over generation MWh.
- `carbon_free_share_flat_pct`: the mean of the hours' shares. This is the share a load of constant power meets. It
  differs from the first because a grid generates more in some hours than in others.
- `cf_share_pct_hHH`: the month's average day, the share in local hour HH. `cleanest_hour_1` to `_4`: the four hours
  with the highest share.
- `year_hours_cf_ge50_pct`, `_ge75_pct`, `_ge90_pct`: the share of the year's held hours at or above that level.

## Annual against hourly matching

A flat load of 1 MW buys clean energy equal to p percent of its year's use (p: 50, 100, 150). The purchase is
delivered in the shape of the grid's own generation of a kind, hour by hour, scaled so that the year's total is the
purchase: `mix` (all the grid's carbon-free generation), `solar`, `wind`.

- `year_match_<shape>_<p>_energy_pct`: the sum over hours of the smaller of the delivery and the load, over the
  load's energy. What arrives beyond the load's use in an hour is not counted, and nothing is stored.
- `year_match_<shape>_<p>_hours_pct`: the share of hours in which the delivery covers the whole load.

"Annual matching" would report p. The difference between p and the first figure is energy an annual claim calls
clean that was served, in its own hour, by something else.

## Moving load into the cleanest hours

A flat load of 1 MW. Each day, s percent of the day's energy (s: 10, 20) is taken evenly from every hour and put,
in equal parts, into the hours of that day that are among the month's four cleanest. The day's energy is unchanged.

- The schedule is the month's own average day, known only afterwards. It is what a load that knew the month's
  pattern could do, not a forecast, and it is the same every day of the month.
- **Carbon**: each hour's load times `carbon_intensity_hourly`'s `intensity_generation`. California's hours before
  the join are set back as `caiso_join.true_hours` sets them.
- **Cost**: each hour's load times the grid's day-ahead hub price. ERCOT from 2019; California, New England, New
  York and SPP from September 2024. No hub price of PJM is held. MISO's prices are not used while MISO is paused
  and its terms are under review ([`miso_pause.md`](miso_pause.md)); MISO's generation is EIA's file and is shown.
- A day counts only when every one of its hours has the figure. `shift_days` and `cost_days` say how many did.

## What it leaves out

Imports and exports. The marginal plant. Geothermal and biomass as carbon-free. Any storage of surplus clean energy
by the buyer. Prices at a load's own node or zone. PJM's and MISO's cost.

## As built on 5 October 2026

- `clean_energy_hourly`: 463,459 held hours of the seven grids, January 2019 to 4 October 2026.
  `clean_energy_summary`: 27,012 rows.
- Left out beyond the mix's own tests: 7 hours by session 118's rule on net generation (California 6, New England
  1); 3,171 because nuclear is under "other" (New York 3,147, California 24).
- Carbon-free share of generation in 2025: California 54.7 percent (EIA's series; 11 months), Texas 45.8, SPP 45.6,
  New York 44.3, PJM 39.3, New England 36.9, MISO 34.9. California's 2026 to September, on CAISO's own data, is
  71.6: not comparable with the years before it.
- A purchase of 100 percent of a flat load's year, delivered as the grid's own carbon-free plants ran, covered in its
  own hour, in 2025: PJM 95.2 percent of the load's energy, New England 94.5, New York 94.0, MISO 89.6, SPP 84.9,
  Texas 84.6, California 78.5. Delivered as the grid's solar it covered 41 to 51 percent, whatever was bought.
- Moving 20 percent of each day's energy into the month's four cleanest hours, 2025: carbon down 4.2 percent in
  Texas, 3.6 in California, 2.0 in SPP, 1.4 in New England, 1.1 in MISO, 1.0 in PJM, 0.8 in New York. Cost at the
  day-ahead hub price down 11.5 percent in California, 9.8 in SPP, 8.2 in Texas, 3.7 in New York, 3.5 in New
  England.
