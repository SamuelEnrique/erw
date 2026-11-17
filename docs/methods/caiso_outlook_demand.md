# caiso_outlook_demand: CAISO's demand, 5-minute, on the days asked

Energy Research Warehouse (ERW). Written by session 7052 (chain 370, the data machine, 17 November 2026) for done-line
request 201: the warehouse held CAISO's Today's Outlook supply by fuel by the hour and its batteries every 5 minutes,
and no 5-minute demand, so the minutes after a Flex Alert could not be read.

## Source

CAISO's public Today's Outlook history file for each day, `https://www.caiso.com/outlook/history/YYYYMMDD/demand.csv`:
columns Time (Pacific wall-clock time, the interval's start), Day ahead forecast, Hour ahead forecast, Current demand
and Demand response (1 in an interval CAISO marks, else blank). The file ends with the next day's 00:00 row, which is
that day's first interval and is dropped. CAISO's robots file (read 17 November 2026) disallows `/resources/*` only.
License: public, with credit to the California ISO (its terms of use).

## Shape

Series, entity `caiso:ISO`, freq `PT5M`, `ts_utc` the interval start: `demand_mw` (Current demand),
`demand_forecast_day_ahead_mw`, `demand_forecast_hour_ahead_mw` (MW) and `demand_response_marked` (count: 1 in an
interval CAISO marks; no row where the column is blank). Written by `warehouse/connectors/caiso_outlook_demand.py`.

## The days

By default the 39 Flex Alert days of 2018 to 2024 that `docs/methods/flex_alert_scorecard.md` names ("The result"),
2021-07-12 included (the scorecard leaves it out for incomplete EIA-930 data; CAISO's file holds it whole). `--days`
asks other Pacific days. On 17 November 2026: 39 of 39 days written, 33,927 rows.

## Completeness

A day is written only when the three MW columns hold every 5-minute interval of the Pacific day (288, or 276 and 300 on
the clock-change days); a day short of one is logged and not written, and nothing is filled. Each run merges into the
table.

## What it lets a reader see

On 6 September 2022, the day of the text alert, CAISO's demand read 50,403 MW in the interval starting 17:50 Pacific,
49,194 MW at 17:55 and 47,635 MW at 18:30. The table gives the minutes; it says nothing of what caused them.

## Registrations

Sector `power` (`warehouse/metadata/build_coverage.py`); license from the source registry (`caiso:todays_outlook_demand`,
public); held out of the Redivis v1 package as a table written after it was prepared (`warehouse/redivis/release_v1.py`);
on the public Redivis draft (uploaded 17 November 2026, nothing released). Not in the live set and not on a page.
