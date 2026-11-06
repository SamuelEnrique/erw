# The reactor fleet

Energy Research Warehouse (ERW), method note written in session 2955 (chain 157, 6 November 2026) for the table first
written that day.

Table: `nuclear_fleet_status` (series, public). Builder: `warehouse/derived/nuclear_fleet_status.py`.

## Sources

- `eia_nuclear_outages_generator_daily`: EIA's Status of U.S. Nuclear Outages by reactor, each day's capacity and outage
  (MW), EIA's estimates from the NRC's daily power reactor status reports, 1 January 2007 to 21 October 2026.
- `eia860m_operating_generators` (vintage 2026-09): a reactor's grid is its plant's balancing authority among EIA-860M's
  operating generators with energy source NUC. A plant EIA-860M no longer lists (a retired one) is under "none".

No request is made.

## What a row is

- **A reactor and year** (`nuclear_fleet:<facility>:<generator>`, EIA's plant and reactor ids):
  - `capacity_mw`: the year's highest daily capacity;
  - `outage_share`: outage MW-days over capacity MW-days;
  - `full_outage_days`: days 99 percent out or more;
  - `long_outages`: runs of 14 or more such days, the refuelings and long outages; the cadence is their spacing;
  - `available_mwh`: (capacity less outage) x 24, summed over the days;
  - `days_held`;
  - `capacity_change_mw`: `capacity_mw` less the year before's, an uprate or a derate.
  `x_first` and `x_last` are the reactor's first and last days held: a restart is a first day after 2007, a retirement a
  last day before 21 October 2026. A year with fewer than 300 days held gets `days_held` only, except a reactor's first
  and last years, whose figures are its own.
- **The fleet by grid and year** (`nuclear_fleet:grid:<BA>`) **and the US** (`nuclear_fleet:US`): `capacity_mw` and
  `available_mwh` summed, `reactors` counted, `outage_share` as the fleet's outage MW-days over its capacity MW-days.

## Checks

- **Available energy against EIA-923's nuclear net generation** (`eia923_plant_fuel_annual`, the plants' NUC rows):
  2023, 769.5 TWh available against 774.9 TWh generated; 2024, 775.1 against 781.9. Within 1 percent, as expected:
  the outages are EIA's estimates of capacity out, and a reactor can run slightly above its rated capacity.
- **The fleet:** 93 reactors and 98.0 GW in 2024; 94 and 99.2 GW in 2025; 95 and 100.1 GW in 2026 to 21 October (the
  year's newest days).
- **Uprates** show as `capacity_change_mw`: Turkey Point 3 and 4, 109 MW each (2012, 2013); R. E. Ginna 81.7 MW (2008).

## License

Public: EIA's data are works of the U.S. government.
