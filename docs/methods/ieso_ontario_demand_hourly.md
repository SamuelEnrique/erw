# Ontario's demand by the hour, a series (the IESO's Hourly Demand Report)

Energy Research Warehouse (ERW), method note written in session 2079 (chain 067) for a table first written on 23 October 2026 (session 2070).

Tables: `ieso_ontario_demand_hourly`

## Publisher and address

Independent Electricity System Operator (IESO), Ontario, Hourly Demand Report, on its public reports site: `https://reports-public.ieso.ca/public/Demand/PUB_Demand_<YEAR>.csv`, one file a year. Source id `ieso:demand`. Connector: `warehouse/connectors/ieso_demand.py` (session 2070).

## Vintage and revision

1 January 2025 to the first hour of 23 October 2026 in the IESO's Eastern Standard Time; in UTC, `ts_utc` runs from 2025-01-01T05:00:00Z to 2026-10-23T05:00:00Z. Written by run `20261023T200639Z` (23 October 2026) from two files, retrieved 2026-10-23T20:04:42Z: `PUB_Demand_2025.csv`, created 2026-01-31T12:30:13Z, and `PUB_Demand_2026.csv`, created 2026-10-23T12:30:09Z (`vintage`, the file's "Created at" time read as Eastern Standard Time and written in UTC). Session 2070's report says the trial and the write reused the saved demand files (`--offline`).

The years default to last year and this one (`--years`); this year's file is asked fresh each run, earlier years are reused from `warehouse/raw/ieso_demand/`. The table is merged, not replaced: a run's rows replace earlier rows with the same (entity, variable, ts_utc), and rows of earlier runs not in the new run are kept.

## Shape and variables

Series, 31,680 rows: two variables of 15,840 hours each, entity `ieso:ontario`, unit MW, freq PT1H, geo `CA-ON`, node `Ontario`, `market` empty. 17,518 rows come from the 2025 file (8,759 hours) and 14,162 from the 2026 file (7,081 hours: 1 January to 22 October and the first hour of 23 October).

| Variable | Meaning | Mean, MW | Lowest, MW | Highest, MW |
|---|---|---|---|---|
| ontario_demand | the load of Ontario's consumers | 16,719.2 | 11,536 (2025-06-01T07Z) | 25,646 (2026-07-14T21Z) |
| market_demand | Ontario demand plus exports | 19,121.1 | 13,055 (2025-05-01T07Z) | 27,678 (2026-07-02T21Z) |

- 2025 (Eastern Standard Time, 8,759 hours): Ontario demand 145.59 TWh, mean 16,621.5 MW, peak 24,862 MW; market demand 165.51 TWh.
- Exports by the IESO's own figures (market demand less Ontario demand): mean 2,401.9 MW, highest 4,418 MW. In 17 hours market demand is below Ontario demand, by up to 158 MW (July and August 2025, 17 August and 3 September 2026), as published.
- One hour is absent from both variables: 2025-05-01T05:00:00Z, the IESO's hour ending 1 of 1 May 2025, the first day of the market renewal. The connector drops no line of a file (it stops instead), so the 2025 file holds 8,759 hours; every other hour of the range is present.

## Reading the source

- Lines beginning `\\` are the report's own notes; the "Created at" time is read from them. The header must be `Date,Hour,Market Demand,Ontario Demand`.
- The IESO's hour is an hour ending, 1 to 24, in Eastern Standard Time all year (no daylight saving): the hour's start in UTC is the date's midnight plus the hour less one, plus five hours.
- A header not the one above, an hour outside 1 to 24, a date not `YYYY-MM-DD`, a value that is not a number, or an hour given twice stops the run. Values as the IESO publishes them; nothing is filled.
- Not taken: the Hourly Ontario Energy Price (it ends with April 2025; the Ontario zonal price that replaced it is published only as daily and hourly files) and any price, for want of a Canadian dollar unit (a standing question for the owner).
- Ceiling: one request a year's file. reports-public.ieso.ca has no robots file (read 216, HTTP 404).

## License

`license_verdicts.csv` records the IESO, read 218 (its Terms of Use): "may be public", for public and for commercial use: "you are granted a limited, non-exclusive, non-sublicensable, non-transferrable licence to use and reproduce the Content", provided each reproduction carries the IESO's copyright notice, which the table's header carries word for word. `license_tables.csv` maps the table to the IESO (the source registry), and `docs/licenses.md` gives it "may be public", flagged public, agreeing; `sources.csv` names the source's license as public.

## Cross-checks (session 2079)

- The counts above were computed from the rows, read past the header lines; they match the header's 31,680 and its range. No (entity, variable, ts_utc) is given twice, and both variables cover the same 15,840 hours.
- Session 2070's check against `eia930_all_interchange`, recomputed: the flows NYISO (`eia930:NYIS-IESO`) and MISO (`eia930:MISO-IESO`) report with the IESO, negated and summed, against Ontario's exports, 864 hours both report, 2026-09-13T00Z to 2026-10-21T23Z. Correlation 0.905 hour by hour (the report: 0.905); 0.833 and 0.839 with an hour's shift either way (the report: 0.836 and 0.830); exports average 2,486 MW and the flow into NYISO and MISO 1,482 MW (the report: the same). The U.S. flow exceeds Ontario's exports in 7 hours, all on 6 October 2026 from 12:00 to 19:00 UTC, by up to 202 MW (13:00 UTC: exports 259 MW, U.S. flow 461 MW); the report says it never does.

## What it does not hold

- Prices of any kind (the HOEP to April 2025, saved on the data machine, and the Ontario zonal price since).
- Demand by zone, flows by intertie or neighbour, and generation: Ontario-wide demand and market demand only.
- The hour ending 1 of 1 May 2025, and years before 2025 (the default reads last year and this one; `--years` reads others).
