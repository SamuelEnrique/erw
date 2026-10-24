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

## The Lower 48 by month, the sum of the states (chain 091, 24 October 2026)

Chain 091 in this note (sessions 1178 to 1189): 1185 (this section; the last Decisions block written by session 1188 from its report). The energy mix panel's other changes of the chain are in `generation_mix_hourly.md`, "The energy mix panel in chain 091".

Session 1185. Until this session the energy mix panel's view by month (`mixp=month`, panel `grid_mix_us48`) said "not built for the Lower 48": `generation_mix_hourly_profile` is built for the seven ISO grids only. It now draws the Lower 48 from this note's table. Code: `site/lib/lower48.ts` (the rule, pure functions), `site/components/grid/Lower48Mix.tsx` (the view), read in `site/components/grid/MixView.tsx`.

- **Why the states.** No table of the live set holds EIA-930's Lower 48 (`eia930:US48`) by month with its mix: `eia930_all_generation` holds `eia930:US48` hour by hour for its recent window only (about 45 days, from 26 August 2026 on 24 October 2026), `carbon_intensity_monthly` holds the Lower 48's carbon intensity by month and not its generation, and `generation_mix_hourly_profile` is by ISO grid. `state_generation_mix_monthly` holds every state and DC by month since 2001, so the sum of the contiguous ones is the Lower 48's monthly mix.
- **Which locations.** The 48 contiguous states and the District of Columbia, 49 locations (`eia:AL` ... `eia:WY`, `LOWER48_STATES`). Not Alaska, Hawaii, Puerto Rico or `eia:US`.
- **Which variables.** The nine groups of the table, `net_generation_<natural_gas, coal, nuclear, wind, solar, hydro, other_renewables, oil_and_other, not_itemized>_mwh`, each summed over the 49. Their sum is the Lower 48's net generation as EIA totals each state (the groups plus `not_itemized` equal EIA's ALL, above). A group a location does not have that month (no row: nuclear in Colorado) adds nothing.
- **Which months.** The last 24 months that every one of the 49 holds, read from the 26 months before the page (the same window the grids' view reads). On 24 October 2026 that is September 2024 to August 2026, every month of them held by all 49.
- **A missing state month.** A location's month is held when it has a row of any group (the table writes a month only when EIA publishes the location's total). A month that one of the 49 does not hold is not drawn and not summed: it is left out of the chart and of the twelve months' sums, and the panel names it with the locations it misses. No month is filled or estimated.
- **The figures and their keys.** The newest month's MWh of each group and of the nine together, the group's share of the nine (percent), and each group's and the nine's MWh over the twelve calendar months to the newest, summed over the months held. A new key kind, `states_sum|state_generation_mix_monthly|<variables, comma separated>|<start>|<end>|lower48`: `site/scripts/check-values.mjs` reads the 49's rows of every variable from start to end and sums the key's variables over the months every one holds, with the page's own function (`lib/lower48.ts` `statesSum`); a share is `calc|pct|<the group's key>|<the nine's key>`. `scripts/test-lower48.mjs` recomputes every key on committed real rows.
- **What it is not.** The panel says it on its face: the sum of the states from EIA-923, not EIA-930's US48. EIA-930's US48 is the operators' hourly metered net generation, added up by balancing authority, published within days and not revised to the plant survey; EIA-923 is a survey of plants, by state, monthly, about two months behind, with its newest months preliminary. The live set holds no month that both cover (EIA-930's window starts after EIA-923's newest month), so the two are not compared here. Against EIA-923's own national figure, `eia:US` less `eia:AK` and `eia:HI`, the sum of the 49 differs by at most 0.23 percent a month from January 2024 to August 2026 (anon reads, 24 October 2026): EIA's state totals and its national total do not add up exactly.

Decisions (chain 091):

- **The sum of the states, not EIA-923's national row less Alaska and Hawaii.** The national row has no `not_itemized` group and holds the sources EIA withholds by state, so its groups differ from the states' sums (hydro in August 2026 by 62,291 MWh); but subtracting two states from a total is a figure no table holds row by row, and the chain file asked for the sum. The sum keeps every group a state reports, and `not_itemized` carries what EIA withholds.
- **A new key kind rather than `series_sum` over a list of 49 entities.** The list would write 49 entities into each of about 30 keys, and `series_sum` cannot leave out a month a state misses: the twelve months' figure would be recomputed over a partial month. `states_sum` names the group and recomputes the page's rule.
- **The view's chips and titles were kept** ("By month", the section's title "monthly mix, by grid"); the words that say what the view draws are its first paragraph and its source line, which link this section.
- **The state view below is unchanged**, and it still draws `eia:US`, the 50 states, DC and (where EIA lists it) Puerto Rico: a different area from the Lower 48.

Decisions (session 1185, the rest of its report, written by session 1188):

- **The read**: the 49's rows since the first of the month 800 days before the page (the window the grids' monthly view reads), through `series()`: about 9,200 rows in 10 requests, made only on the Lower 48's `mixp=month` address.
- **The view's method link is a second link of the mix panel** (`METHOD_MIX_US48` in `site/lib/gridAnchors.ts`, this section's id), drawn under the Lower 48's monthly view only; the panel's own link (`METHOD_MIX`) stays. This heading is therefore a link target: a rename is made with the constant, and `site/scripts/test-grid-files.mjs` and `tests/test_session1185.py` hold the link.
- **The key kind is known to the checks and to the license gate**: `site/scripts/check-methods.mjs` reads `states_sum|` as a figure of its table (`TABLE_KEY`), and `components/Num.tsx` gates it by its table, held or not as a whole table (public on 24 October 2026).
- **Its file** is `erw_grid_mix_us48_monthly.csv`, made from the view's cells as every panel's (`grid_network.md`, "Each panel's table, to download").
- **The words on the face, the national row against the sum, and the chip's and section's titles** are put to the owner (`docs/reviews/grid-rulings-2026-10-23.md`), each with a recommendation; the code stands as above until a ruling.
