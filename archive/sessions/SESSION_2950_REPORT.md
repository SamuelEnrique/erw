# Session 2950 report: FERC-714 forecast growth (with session 2949)

6 November 2026, about 08:16 UTC, on lab-desktop (the data machine), chain 157 (the owner's), unattended. Model spend USD 0. Pulls: none.

## Read these first

- **`ferc714_forecast_growth` not derived: its input is not held.** The chain's rule: "from held tables only (`coverage.csv` read first; a table not held is not pulled, the session says so and derives from what is)".
  - The warehouse holds FERC-714's Part 3 Schedule 1, the hourly planning-area demand (`ferc714_area_demand_2006` to `_2025`, internal), and the respondents (`ferc714_respondents`, 219, internal).
  - It does not hold Part 3, Schedule 2, the ten-year forecasts of summer peak, winter peak and net energy that the revisions would be computed from. No table or raw file under `warehouse/raw/` holds them (session 2946's inventory).
- **What the held tables can give instead** is each planning area's actual peak and energy by year (from the hourly demand). That is not a forecast and not the datacenter signal the chain names, so it was not derived under the forecast table's name.
- **For chain 162's session 2988:** the table once Schedule 2 is held.

## Decisions made without you

- **No substitute table under the forecast's name.**

## For Samuel's ruling

- **Whether FERC-714 Part 3 Schedule 2 may be pulled** (FERC's Form 714 data, the same publisher and license as the hourly tables, internal).
