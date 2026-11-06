# Session 3180 report: the rest of the US tables, the second part: what is not drafted (chain 166)

6 November 2026, about 14:25 UTC, on lab-desktop, second window, chain 166, unattended. Model spend USD 0. Pulls: none.

## Read these first

- **No draft this session.** Session 3179 asked the questions of these tables that the hunt's tests can carry. The other US tables were read, and are not drafted, for these reasons:
  - **ONRR's federal revenue** (`onrr_revenue_monthly`): royalties follow the prices of oil and gas month by month, so a change by year would restate the prices already drafted (session 3003).
  - **The forecasts** (`eia_steo_forecasts`, `eia_aeo_electricity`): a forecast against its outturn is a level and an error, not a change over years. It needs a test the hunt does not have, the error by vintage, which a later chain can write.
  - **Buildings and households** (CBECS, RECS): surveys of a few years each (2012 and 2018; 2015 and 2020), which the window test cannot carry.
  - **Transit and transport** (`ntd_transit_energy_annual`, `ornl_tedb_transportation_annual`): ORNL's table is internal, and the transit table's energy by mode is a level by agency.
- **The rest of the US family is marked "hunted" in the plan,** with these reasons beside it.

## Decisions made without you

- **A table whose shape needs another test is named, not drafted.**

## For Samuel's ruling

- None new.
