# The storms that take power lines down, an event (NOAA NCEI's Storm Events Database)

Energy Research Warehouse (ERW), method note written in session 2052 (chain 059) for a table first written on 23 October 2026 (session 2042).

Tables: `noaa_ncei_storm_events`

## Publisher and address

NOAA's National Centers for Environmental Information (NCEI), Storm Events Database (`https://www.ncei.noaa.gov/stormevents/`), the National Weather Service's Storm Data as NCEI publishes them. Read from the bulk directory's yearly details files, `https://www.ncei.noaa.gov/pub/data/swdi/stormevents/csvfiles/StormEvents_details-ftp_v1.0_d<YEAR>_c<YYYYMMDD>.csv.gz`, the newest file of each year from 2015 (`--first-year`) that the directory's listing names. Source id `noaa:storm_events`. Connector: `warehouse/connectors/noaa_storm_events.py` (session 2042).

## Vintage and revision

1 January 2015 to 30 June 2026 in NCEI's local times (`x_begin_local`); in UTC, `event_date` runs from 2015-01-01T06:00:00Z to 2026-07-01T05:49:00Z. Written by run `20261023T183046Z` (23 October 2026) from twelve files: 2015, 2016, 2018 to 2021 and 2023 created 23 March 2026; 2017 19 May; 2022 25 June; 2024 28 July; 2025 19 August; 2026 18 September (it ends with June). Session 2042's report says the write reused the saved files (`--offline`) and the probe's saved listing.

The table is a snapshot: each run writes it whole and replaces the file, so an event NCEI drops leaves it. The listing is asked fresh each run; a year's file is named by its creation date, so a revised file is a new name and is fetched, and an unchanged one is reused from `warehouse/raw/noaa_storm_events/`.

## Shape and variables

Events, 411,139 rows, one an event: `event_id` `noaa_storm:<EVENT_ID>`, NCEI's own; `event_date` the begin time in UTC; `event_type` NCEI's `EVENT_TYPE` in snake case, its words in `x_noaa_event_type`; `parties`, `entity_ids`, `mw`, `price`, `currency` and `status` empty in every row. 67,749 episodes (`x_episode_id`).

| Type | Events | Type | Events |
|---|---|---|---|
| thunderstorm_wind | 206,586 | cold_wind_chill | 7,360 |
| high_wind | 43,770 | blizzard | 6,182 |
| winter_storm | 33,217 | wildfire | 4,039 |
| heavy_snow | 24,870 | lightning | 3,458 |
| heat | 18,695 | tropical_storm | 3,190 |
| tornado | 17,479 | ice_storm | 2,662 |
| excessive_heat | 15,469 | storm_surge_tide | 494 |
| strong_wind | 12,448 | hurricane_typhoon | 379 |
| extreme_cold_wind_chill | 10,601 | tropical_depression | 239 |
| | | hurricane | 1 |

By the year of the local begin time: 2015 28,713; 2016 28,563; 2017 30,129; 2018 31,047; 2019 37,776; 2020 34,045; 2021 33,260; 2022 39,500; 2023 42,677; 2024 40,680; 2025 42,466; 2026 (to June) 22,283.

- Time: NCEI gives `BEGIN_YEARMONTH`, `BEGIN_DAY`, `BEGIN_TIME` in the zone `CZ_TIMEZONE` names; the connector subtracts the zone's own hours (`CST-6` adds six). Zones: CST-6 185,196; EST-5 146,724; MST-7 53,114; PST-8 22,328; AKST-9 2,369; AST-4 545; HST-10 374; PDT-7 290; SST-11 77; GST10 68; EDT-4 47; CDT-5 7. The 344 rows in PDT-7, EDT-4 and CDT-5 are in a daylight zone by NCEI's own label, converted by its offset.
- Place: `x_geo` the state's ISO 3166-2 code from NCEI's `STATE_FIPS`: the FIPS codes of the 50 states and DC, and NCEI's own codes for the territories, Puerto Rico 99 (519 rows), American Samoa 97 (77), Guam 98 (68) and the Virgin Islands 96 (26). It is filled in every row. (This note's first draft found those 690 rows empty, the map holding the territories' FIPS codes, 60 to 78; session 2052 corrected the map and wrote the table again, its rows otherwise unchanged.) `x_cz_type` C (county) 227,675, Z (forecast zone) 183,462, and `5` in two Arizona high wind rows of 2026, as published.
- Damage: `x_damage_property_usd` and `x_damage_crops_usd`, NCEI's `K`, `M` and `B` read as dollars; `K` alone is 0 (206,638 property rows at 0); an empty cell stays empty (property 89,007, crops 92,372). Property sums to USD 142,800,427,380, crops USD 9,148,692,310; the largest property figure is USD 17,000,000,000, California's wildfire beginning 8 November 2018 (`noaa_storm:788675`). By type, hurricane_typhoon USD 69.4 billion, wildfire 30.3 billion, tornado 13.4 billion.
- People: 5,336 direct and 2,252 indirect deaths, 15,599 direct injuries; excessive heat (1,608) and heat (1,168) lead the direct deaths.
- Tornadoes: `x_tor_f_scale` EF0 7,131, EF1 6,625, EFU 1,774, EF2 1,535, EF3 360, EF4 53, EF5 1 (the 17,479 tornadoes).

## Reading the source

- Only the 19 types in `TYPES` are kept; hail, floods, marine events and the rest, and both narratives, are not.
- A heading not in the connector's map (or one it needs missing), an event id that is not a number, a zone not of the form `EST-5`, a time not in NCEI's form, a damage figure not in NCEI's form, a file that is not gzip, or an event id given twice stops the run.
- Values as NCEI publishes them, whitespace collapsed; a blank stays blank.
- Ceiling: one request for the listing and one for each year's file not already saved.

## License

`license_tables.csv` lists the table under NOAA NCEI. `license_verdicts.csv` records NOAA NCEI, read 9: "may be public", for public and for commercial use; its one restriction is on ISD's non-U.S. stations (WMO Resolution 40). The connector and the header cite the National Weather Service's notice (read 8, also "may be public"): free for any lawful purpose, so long as it is not claimed as one's own, no endorsement is implied, and a modified copy is not presented as official. `docs/licenses.md` lists the table as may be public, flagged public, agreeing.

## Cross-checks (session 2052)

- The counts above were computed from the rows, read past the header lines. The 19 types sum to the header's 411,139 and each matches its header count. No `event_id` is given twice; the rows are in (event_date, event_id) order.
- `event_date` equals `x_begin_local` less the zone's offset in all 411,139 rows, and `x_end_utc` equals `x_end_local` less it; no event ends before it begins.
- Session 2042's report checked ice storms and hurricanes against `doe_oe417_events` by state and day, a day either side: 42 of 48 hurricane state-days and 45 of 334 ice storm state-days (2016 to 2025) have a DOE-417 weather event; the other way, 867 of 878 DOE-417 weather events naming a state have one of these storms there within a day.

## What it does not hold

- Hail, floods, marine and NCEI's other types; the episode and event narratives; the begin and end locations' range and azimuth.
- Years before 2015, and months NCEI has not yet published (the 2026 file ends with June).
- Session 2042's report first listed `hurricane` (1) and `hurricane_typhoon` (379) as "hurricane 380"; the table keeps them apart, and the report now does too.
