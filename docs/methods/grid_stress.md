# How hard the system works: evening ramp, lowest net load, the tightest hours, dark and calm stretches

> **Session 133 (6 October 2026).** Installed capacity is now read from every retired unit EIA lists (`eia860m_retired_generators_all`), so the share of capacity in the tightest hours is given for natural gas, coal, nuclear, and hydro and storage from 2019, not from 2025 only. The page is a view of `/mix` (`/mix?view=stress`); what stood on its face is in this note. Details: `generation_mix_hourly.md`, "Session 133".

Energy Research Warehouse (ERW), session 123 (5 October 2026). Table: `grid_stress_yearly`. Code:
`warehouse/derived/mix_stress.py`. Page: `/mix/stress` (in review).

## The definitions, as computed

Local time is the grid's own. A year is the local calendar year.

| Term | Definition |
|---|---|
| Net load | Demand less wind less solar, MW, hour by hour |
| The evening ramp | For each day, the largest rise of net load from one hour to the next between the hours starting 14:00 and 22:00 local (eight steps), in MW in one hour; and the largest rise over three hours in the same window. Only steps between hours that are both used and next to each other |
| A spike, not a ramp | A one-hour rise that the next hour takes back by more than half is not counted. (PJM, 1 December 2019: demand 86,378 MW, then 103,428, then 89,476) |
| The lowest net load | The hour of the year with the least net load |
| The tightest hours | The 100 used hours of the year with the highest net load |
| A fuel in those hours | Its mean output over the 100 hours, over its installed capacity in each hour's month |
| Dark and calm | An hour in which wind and solar together put out less than 10 percent of their installed capacity of that month |
| A stretch | A run of dark, calm hours, each used and each next to the last. An hour that is not used ends it. It belongs to the year it begins in |
| The energy missing | Over a stretch: the year's average output of wind and solar (MW, over the year's used hours) less what they put out, summed, MWh |
| Hours of the battery fleet | That energy over the fleet's power (MW) in the stretch's first month: the hours the whole fleet would have to discharge at full power. Beside it, the energy over the fleet's energy (MWh): how many times it would have to be emptied |

Shares "of peak" are of the same year's peak hourly demand, so a grid that grew is compared with itself.

## The hours

The hours are the energy mix's ([`generation_mix_hourly.md`](generation_mix_hourly.md), `mix_profile.hours_of`):
EIA-930's hourly demand and net generation by source for the seven ISO grids from January 2019, an impossible hour
of demand a blank by session 118's rule ([`impossible_hours.md`](impossible_hours.md)). California from the join (16
December 2025, [`eia930_caiso_break.md`](eia930_caiso_break.md)) takes its wind and solar from the California ISO's
own supply by fuel, which runs higher than EIA's did; its demand stays EIA's. California is two series, and a step
across the join is partly the change of source.

Every figure here is a record or rests on a few hours, so hours that are in the file and do not describe the grid
are not used:

1. **EIA's own balance does not close.** Demand differs from net generation less total interchange by more than a
   fifth of demand (the mix's own test for its records). Where EIA's interchange is blank the balance cannot be
   taken, and the hour is used only when its demand stands to its net generation as in the grid's hours that do
   close (inside the middle 99 percent of their ratio). California, 8 March 2025, interchange blank: demand 13,710
   MW against net generation 25,095; that hour would have been the year's lowest net load, at minus 5,099 MW.
   CAISO's own hours are not put to this test.
2. **A stale report.** An hour that repeats the hour before to the MW in net generation, wind and solar. SPP has
   2,568 of them, in runs: on 6 December 2023 the same three figures stand for four hours while wind then doubles.
3. **Wind or solar blank** in a year that reports it. Taken as zero, a blank would be a jump in net load.

**A source the file does not report.** New York's solar is zero or blank in every hour of every year. A source like
that is no part of that year's net load or of the installed capacity in the dark, calm measure, and the page says
so. New York's net load is therefore demand less wind only.

A year is written when it holds at least nine tenths of its hours to date. The newest year is not a whole year.

## Installed capacity, and what the inventory cannot give

Installed capacity is EIA's monthly generator inventory (`eia860m_operating_generators`, and the units retired since
January 2025 from `eia860m_retired_generators`): nameplate MW by the balancing authority EIA gives each unit, month
by month from each unit's first month of operation.

The inventory read lists the units operating now and those retired since January 2025. A unit retired before 2025
is in neither. So the capacity of a fuel that lost plants before then is understated for the earlier years, and its
output would look like a larger share of capacity than it was. Therefore:

- for **wind and solar** the share of installed capacity is written for every year (few have retired);
- for **natural gas, coal, nuclear, and hydro and storage together** it is written for 2025 and later only.

**Hydro and storage are one line against capacity.** The inventory counts pumped storage with storage; the grids do
not all report it that way. PJM's hydro output in its tightest hours of 2025 is 157 percent of its conventional
hydro capacity, and MISO's 106 percent: their pumped storage is in their "hydro". So each one's output is written,
and the share is of the two together: hydro and storage output over conventional hydro, pumped storage, batteries
and flywheels.

A fuel the file does not report in a year (storage before EIA itemized it) has no figure, never a zero.

The battery fleet in the dark, calm measure is `storage_buildout_monthly`'s operating batteries (MW and MWh).

## What the figures are not

- **Not what a plant could do.** A plant below its capacity in a tight hour may have been in reserve, on outage,
  out of fuel or not needed. The share is what the fleet did.
- **Not a reliability study.** The tightest hours are tight by net load. Outages, transmission limits and reserves
  are not in the file.
- **Not a sizing of storage.** "Hours of the battery fleet" sets the energy missing against today's fleet to show
  its scale. Batteries hold a few hours; the gap was filled by other plants and imports.
- **The definition of dark and calm is one line.** At night solar is zero whatever is installed, so the measure
  asks whether wind alone reaches a tenth of wind and solar capacity together. A grid with much solar and little
  wind (New England) is below the line most nights. It is the definition asked for, computed as stated.

## As built on 5 October 2026

- 2,002 rows: 7 grids, 2019 to 2026 to date. Not written: California 2019 and 2020 (the hydro gap takes their
  hours), SPP 2019 and 2026 (stale reports).
- Hours not used, of the held hours with a demand: California 127 for the balance and 20 stale; Texas 22 and 0; New
  England 1 and 0; MISO 0 and 19; New York 0 and 4; PJM 8 and 35; SPP 60 and 2,568.
- The largest one-hour evening ramp as a share of the year's peak demand, 2019 to 2025: Texas 7.9 to 19.1 percent
  (15,940 MW, starting 16:00 on 19 January 2025); MISO 4.0 to 10.0; New England 6.1 to 9.4; New York 4.1 to 5.4; PJM
  4.9 to 5.9. California 19.1 percent in 2021 and 23.7 in 2025; over three hours, 37.4 and 47.1.
- The lowest net load as a share of peak demand, 2025: California 3.1 percent, SPP 8.1, Texas 11.5, New England
  18.9, MISO 27.5, New York 32.5, PJM 33.8.
- Solar in Texas's 100 tightest hours: 71.1 percent of its installed capacity in 2019, 33.1 in 2024, 5.0 in 2025. The
  tightest hours moved from summer afternoons to hours after dark as solar grew.
- In the tightest hours of 2025: nuclear 85.5 to 96.1 percent of capacity; natural gas 53.5 to 72.8; wind 11.1 to
  31.6; hydro and storage together 19.7 (California, on EIA's file, which itemized no battery output there) to 68.3
  (New York); Texas 31.7, and 39.9 in 2026 to date.
- The longest dark, calm stretch of 2025: Texas 18 hours (322,188 MWh missing; 37.8 hours of its battery fleet at
  full power), California 18 hours, MISO 16, PJM 20, SPP 15, New England 62, New York 101 (wind only).

## Three different "tight" hours on the Grid tool (chain 077, 23 October 2026)

Chain 077 put two more measures of a hard hour on the Mix tab of `/grid`, beside this note's. They are not the same hours, and the page does not mix them:

- **The tightest hours (this note):** the 100 used hours of a year with the highest net load (demand less wind less solar), in `grid_stress_yearly`, drawn by the view "How hard the system works".
- **The peak demand hour (session 1152):** in the energy mix panel `grid_mix_<grid>`, the hour of highest EIA-930 demand (`eia930_all_demand`, `demand_mw`) in the 24 hours that end with the newest hour held, keyed `series_max|eia930_all_demand|demand_mw|<start>|<end>|eia930:<BA>` and marked on the hourly chart. Demand, not net load: wind and solar are not taken off. `generation_mix_hourly.md` gives the rule.
- **The scarcity hours (session 1154):** in the panel `grid_scarcity_<grid>`, the hours of the latest 30 days `scarcity_hours_by_grid` holds in which the hub's price reached USD 1,000 per MWh or the grid's own scarcity signal was in force (ERCOT and CAISO only). A price and a notice, not a load. `scarcity_hours_by_grid.md` gives the rule.

Decisions (chain 077):

- **The panel's peak is demand's, not net load's**, as a trader reads a peak (prices, reserves and the four coincident peaks key off demand); this note's net load stays the measure of the tightest hours. The owner may ask the panel to name the net load peak beside it; that would be a new key, and no figure of this note would move.
- **No figure of this note was changed by the chain**; the section only says which of the three a figure on the page is.

## The views' figures, keyed from the committed files (chain 078, 24 October 2026)

Session 1166 keyed the figures this note's tables put on the Grid tool's Mix tab (`components/mix/views.tsx`, the view
"How hard the system works" and the tightest hours of "Availability by source"). The page reads the site's copy of
`grid_stress_yearly`, `site/data/stress/<grid>.json` (`warehouse/derived/mix_stress.py`); each figure is keyed
`fmt|<form>|file|stress/<grid>.json|years.<year>.<variable>`: `site/scripts/check-values.mjs` reads the committed file
in the repository, follows the path (`site/scripts/check-file.mjs`), holds the page's text to that value written in its
form (`n0` whole, `n1` one decimal: `site/scripts/check-format.mjs`), and then compares the file's value with the row of
`grid_stress_yearly` it was built from (entity `iso:<grid>`, the variable, `<year>-01-01`), on a line of its own
("same" within the rounding of the less precise of the two, "DIFF" else).

The variables keyed, each a `grid_stress_yearly` variable as the table writes it: `peak_demand_mw`,
`evening_ramp_max_mw_per_h`, `evening_ramp_max_share_of_peak_pct`, `evening_ramp_3h_max_mw`,
`evening_ramp_3h_max_share_of_peak_pct`, `net_load_min_mw`, `net_load_min_share_of_peak_pct`, `hours_held` (the
table "the evening ramp and the lowest net load, by year", every year), the five shares of "The seven grids"
(`evening_ramp_max_share_of_peak_pct`, `evening_ramp_3h_max_share_of_peak_pct`, `net_load_min_share_of_peak_pct`,
`tight_wind_share_of_capacity_pct`, `tight_solar_share_of_capacity_pct`), and the tightest hours by source of
"Availability by source", `tight_<natural_gas, coal, nuclear, wind, solar, hydro_storage>_share_of_capacity_pct`.
On 24 October 2026 the 272 such figures the two views draw for ERCOT and CAISO were the same in the file and in the table.

Not keyed, and why: the hours of each record ("When it started", "When", "It began": a time, written by the grid's
clock, not a value), the tightest hours' fuel table (mean MW, capacity, share; the dark and calm stretches' table): left
for a later pass, a table of up to ten columns a year; "The longest" stretch, written in words (`stress.span`).

Decisions (chain 078):

- **A figure of a committed file is recomputed from the file, and the file from the table**, as two lines: the page
  reads the file, so the first check is the page's own reading; the second says whether the file still matches the
  live set. A "DIFF" is counted apart and does not fail the run: the files are rebuilt by hand
  (`mix_stress.py --snapshot`), the table by its job, and a difference says the file is behind, which is a finding for
  the owner, not a page fault. The owner may make it a failure.
- **The form is part of the key** (`fmt|n1|...`), so the text is recomputed exactly, not only the number; no figure's
  text moved.
