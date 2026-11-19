# Session 8203 report (chain 502, lab-desktop second window)

19 November 2026, 11:19 to 11:27 UTC. Opus 5.5. Model spend: USD 0. Parts B and C checked at the start: both still waiting.

## Family 3, demand against temperature: 15 drafts

- `docs/findings/weather/`, loaded in state draft; second pass 15 of 15 reproduce; 15 of 15 do-files hold.
- Described, not modeled: no fit and no weather adjustment. For each of the thirteen regions: the demand in the year's 50 coldest and 50 hottest hours (MW and against the mean hour), the temperature of the 100 highest hours of demand, the hours at or below 20 F and at or above 95 F, each season's mean temperature, the year's coldest and hottest hour. Temperature from `region_weather_hourly`, demand summed from the authorities.
- 143 claims, 15 pass all five tests: a year's extreme hours move with its weather, and the tests reject most of them, as they should.
- The three strongest by consequence:
  - Texas's demand in its 50 hottest hours: 83,437 MW in 2024 against 72,017 MW in 2019 (7.1 typical yearly moves).
  - Texas's demand in its 50 coldest hours: 72,548 MW in 2024 against 53,077 MW in 2019.
  - The Midwest's demand in its 50 hottest hours: 122,280 MW in 2025 against 115,622 MW in 2019.
- Texas and the Northwest end at 2024 because 2025 is not a full year in `region_weather_hourly` for them (counted by `runs/c502/wx_hours.py`): Texas has no hour from late August to December 2025 (5,084 hours in 2025), the Northwest few in November and December 2025 (7,360), and the Carolinas none after September 2025 and none in 2026 (5,843 in 2025). A region's hour is written only when every one of its chosen stations holds one, so one station's gap empties the region. Written for the data machine in the plan's faults section.

## Code

- `warehouse/analysis/findings/deep/weather.py` on `wip/8202-findings`.

## Needs the key

- Nothing.
