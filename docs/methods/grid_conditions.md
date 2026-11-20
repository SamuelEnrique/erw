# Grid conditions: is the grid tight, and is it congested

Chain 601, part G (session 9000, 20 November 2026). Builder: `warehouse/derived/conditions_page.py`. Page: `/conditions` (in review, in no menu). Files: `site/data/conditions/<operator>.json` for the seven grids and `index.json`; contract `docs/state/page_files_conditions.md`, section 2.

## The strips

| Strip | Grids drawn | Table | What a point is |
|---|---|---|---|
| Demand and forecast | all seven | `eia930_ba_demand_hourly` (EIA-930, the grid's balancing authority: CISO, ERCO, SWPP, MISO, PJM, NYIS, ISNE) | an hour's demand and EIA's day-ahead demand forecast; a day's peak and lowest |
| Out of service | SPP, CAISO | `generation_outages_hourly` | megawatts out in the hour; a day's mean and highest hour |
| Constraints binding | SPP, CAISO | `constraints_binding_hourly` | constraints that bound in the hour and the largest shadow price by size; a day's constraint-hours |
| Scarcity adder | ERCOT | `ercot_rtm_price_adders` (RTORPA, the online reserve adder, hourly mean) | the adder in the hour; the day's hours above zero (June 2014 to 4 December 2025) |
| Alerts | CAISO, ERCOT | `grid_all_alerts` | each notice with its date, its kind in the operator's words, start and end |
| Reserves against the requirement | none | | blank: no operator whose terms allow it publishes this over time in the files read |

## Decisions

1. **Published figures only.** The page takes a day's peak, mean, highest hour and count. No estimate.
2. **Available capacity.** No operator whose terms allow it publishes available capacity hour by hour in the files read, so "demand against what was available" is drawn as demand against EIA's day-ahead forecast, and the reserves strip is blank with its reason.
3. **Blank strips.** PJM (paid license), NYISO and ISO-NE (written permission) are held, MISO is paused, and ERCOT's outages and constraints are on paths its robots file disallows. Each strip is blank with its reason on hover. EIA's demand is public and is drawn for every grid.
4. **Hourly windows.** Hourly figures are kept for the newest 35 days and the nine events of `/events` (their own start and end days). Any other day is drawn day by day, fifteen days either side, with the chosen day's hours when a kept window holds them. Every hour of every grid since July 2018 would make about 40 MB of page files.
5. **SPP's area.** SPP's outages are its RTO balancing area (`spp:SPP`), the area of EIA's SWPP; the western area added in April 2026 (`spp:SWPW`) and SPP's total are in the table and not drawn.
6. **Days are the operator's.** A day is the operator's local day (Pacific, Central or Eastern); hourly charts mark UTC instants.
7. **First view.** ERCOT, its newest 35 days, no second operator.
