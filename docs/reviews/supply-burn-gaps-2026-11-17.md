# The fuel burn's missing weeks, hour by hour (session 7052, chain 370; done-line requests 150 and 151)

Energy Research Warehouse (ERW), the data machine, 17 November 2026. The burn rows of `site/data/supply.json`
(`warehouse/derived/supply_page.py`) count a week only when its seven local days are whole in the energy mix's held
hours (`warehouse/derived/mix_profile.py`): an hour is held when EIA-930's net generation is positive, no main source is
blank, and the sources add up to the net generation within the mix's tolerance. California is read from CAISO's own
Today's Outlook supply by fuel from January 2026 (`caiso_fuel_supply`), every other grid from EIA-930's balancing
authority workbooks (downloaded 2026-11-16 17:58 UTC, the newest on this machine).

## Pulled in this session

- CAISO, `caiso_fuel_supply`: 2026-10-15, 2026-11-05, 2026-11-06, 2026-11-07 and 2026-11-08 were not in the table (CAISO's
  robots file read first: it disallows `/resources/*` only). Five days, 1,560 rows, from
  `https://www.caiso.com/outlook/history/YYYYMMDD/fuelsource.csv`. California's weeks ending 2026-10-16 and 2026-11-13
  are whole now.

## Not held, and why (the weeks still missing from 2025-11-07 to 2026-11-13)

| Grid | Days | Why |
|---|---|---|
| CAISO | 2026-08-21 | CAISO's file holds 0 of the day's 288 five-minute intervals |
| CAISO | 2026-09-22 | CAISO's file holds 287 of 288 intervals; a short day is never filled |
| CAISO | 2026-11-01 | the clock-change day: the Today's Outlook connectors refuse a day whose local times do not convert (request 162) |
| CAISO | 2025-12-02 (EIA-930 side) | EIA's workbook holds 23 of the day's 24 hours |
| ERCOT | 2025-12-05 to 2025-12-14 | 2025-12-05 blank in EIA's workbook (24 hours); 3 to 9 hours a day after it where EIA's sources miss its net generation by more than the tolerance |
| ISO-NE | 2026-09-11 (1 hour), 2026-10-14 (2 hours) | 2026-10-14: coal blank in EIA's workbook; 2026-09-11: sources off net generation |
| NYISO | 2026-05-04 (9 hours) | sources off net generation in EIA's workbook |
| PJM | 2025-11-02 04:00 UTC; 2026-06-01 to 06-03 (11, 14, 9 hours); 2026-11-02 04:00 UTC | the two clock-change hours are blank in EIA's workbook (every column); June: sources off net generation |
| SPP | 2026-02-18, 02-26, 02-27, 05-07, 05-19 to 05-25, 06-03, 07-21, 09-15 (1 to 7 hours a day) | sources off net generation in EIA's workbook |

None of these hours is held by EIA-930 in a form the mix's rule accepts, so nothing was filled. "The seven grids
together" stand at the week ending 2026-10-30: the week ending 2026-11-06 lacks CAISO's and PJM's clock-change hours.
