# Method: generation mix by state and grid operator

Energy Research Warehouse (ERW), session 18. Tables: `eia_state_generation_monthly` (EIA, series, public), `state_generation_mix_monthly` (derived, series, public) and `eia930_generation_latest` (EIA, series snapshot, public). Code: `warehouse/connectors/eia_series.py`, `warehouse/derived/generation_mix.py`, `warehouse/connectors/eia930.py`. The page that reads them: the site's `/mix` (platform tool 21, the energy mix explorer).

## Two sources, two geographies

| Question | Source | Geography | Time | Table |
|---|---|---|---|---|
| What generated the power, month by month since 2001 | EIA Form EIA-923, "Electric power operational data" (API route `electricity/electric-power-operational-data`) | states, DC, Puerto Rico, EIA's census regions, US | monthly, 2001-01 to about two months ago | `eia_state_generation_monthly`, grouped in `state_generation_mix_monthly` |
| What is generating it this week | EIA Form EIA-930, the Hourly Electric Grid Monitor | the seven ISOs (balancing authorities) and the Lower 48 | hourly | `eia930_<ba>_generation` (complete UTC days), `eia930_generation_latest` (the latest complete hours) |

EIA-923 reports by state and EIA-930 by balancing authority. An ISO's footprint crosses state lines (MISO, SPP and PJM each span many states; ERCOT covers most of Texas but not El Paso or the Panhandle), so the ERW does not add states up into ISOs or split ISOs into states. The page selects the two separately.

## eia_state_generation_monthly

Net generation, all sectors (`sectorid` 99), for these EIA energy sources (`fueltypeid`): ALL (all fuels), COW (all coal products), PET (petroleum), NG (natural gas), OOG (other gases), NUC (nuclear), HYC (conventional hydroelectric), HPS (pumped storage, usually negative), WND (wind), SUN (utility-scale solar), GEO (geothermal), BIO (biomass), OTH (other), and DPV (EIA's estimate of small-scale solar, which is not part of ALL).

- EIA publishes thousand megawatthours. The ERW writes MWh: value x 1000, exact.
- `entity` is `eia:generation:<location>:<fueltypeid>`; `geo` is `US-<state>`, `US`, or empty for a census region.
- A month EIA lists without a value (withheld to protect a plant's data) is left out and counted in the run log.
- The twelve sources COW through OTH partition ALL. For Texas, July 2026, they add up to ALL to the published digit (63,541,838.25 MWh). Over every state and month, 254 of 19,348 state-months differ from ALL by more than 0.1%, where EIA withheld a source.

## state_generation_mix_monthly (derived)

| Group | EIA sources |
|---|---|
| coal | COW |
| natural_gas | NG |
| nuclear | NUC |
| hydro | HYC |
| wind | WND |
| solar | SUN (utility scale) |
| other_renewables | GEO, BIO |
| oil_and_other | PET, OOG, HPS, OTH |
| not_itemized | ALL minus the groups above |

- A group is the exact decimal sum of its sources that EIA published for the month. A withheld source adds nothing.
- `not_itemized` is written only when it is at least 0.5 MWh either way. It is the part of EIA's total that EIA does not assign to a source.
- The groups plus `not_itemized` equal EIA's ALL for every location and month. The largest difference over the whole table is 0.09 MWh, which is rounding to three decimals.
- Locations: the 50 states, DC, Puerto Rico (where EIA lists it) and US. The census regions are left out. A location's month is written only if EIA publishes ALL for it.
- Small-scale solar (DPV) is not in any group. The page says so.
- Why a derived table: the site reads Supabase, whose free tier is limited to 500 MB. The grouped table has about half the rows of the EIA table, and a short `source_url` per row (this document) instead of a paged API URL. The EIA table stays whole in the CSV and on Redivis.

## eia930_generation_latest

The EIA-930 generation tables hold only complete UTC days (session 16), so the hours of the current day are not in them. `eia930_generation_latest` is a snapshot of the last 48 hours for each of the eight balancing authorities, rewritten on every run. An hour of a BA is written only when its `net_generation_mw` and every energy source the BA reports anywhere in the window have a value for it. Any other hour is left out, never filled. EIA publishes fuel data a day or more after the hour, so the latest complete day is often yesterday. The page names the date and the last hour.

## On the page

- **Today so far**: the latest UTC day in `eia930_generation_latest` for the selected grid operator. It shows the hours it holds, the net generation in MWh (the sum of hourly MW), and the share by fuel group, grouped as on `/grid`.
- **Hourly mix, last 7 days**: the 7 latest complete UTC days of `eia930_<ba>_generation`, stacked by fuel group. Negative values (storage charging) are not stacked.
- **Monthly mix since 2001**: `state_generation_mix_monthly` for the selected state, stacked. The fuel-share table gives each group's share of net generation for whole calendar years (2001, 2010, 2020 and the latest full year) and the latest 12 months, and each group's MWh in the latest month.

## On the Grid tool's Mix tab (chain 077, 23 October 2026)

The page these blocks stood on is now the Mix tab of `/grid` ("Now and by state", session 133 and session 299). Chain 077 changed three things about them; the rules are in `generation_mix_hourly.md`, section "The Mix tab's energy mix, keyed, hourly and by month".

- **The hourly mix on the Mix tab reads `eia930_all_generation`**, the live set's table of EIA-930 generation by balancing authority (nine days of its 35-day window), and it opens with a keyed panel, `grid_mix_<grid>`: the 24 hours that end with the newest hour held, their net generation, each fuel group's MWh and share, the peak demand hour and the newest hour's age.
- **Negative values are now stacked below zero.** Storage charging is drawn as a band under the axis, each band from the running sum of its own side of zero (session 1152's fix in `site/components/TimeChart.tsx`); the line above, "Negative values (storage charging) are not stacked", described the chart before that session, which drew the band after storage from storage's negative value. A stack of positive values draws as before.
- **A second view by month by grid** (`mixp=month`): `generation_mix_hourly_profile`, the seven ISO grids' last 24 months. The monthly mix by state below it (`state_generation_mix_monthly`) is unchanged, and it is the Lower 48's only monthly view: the profile table is by grid.

Decisions (chain 077):

- **The state monthly view was kept as it was**, below the grid's monthly view, rather than replaced: a state and a grid are different areas (the note's "Two sources, two geographies"), and the owner's rule that no default figure moves holds for it. The owner may ask for one of the two to be dropped.
- **The line about negative values was left as written and corrected here**, as this note's form keeps what the page said; the page now draws what this section says.
