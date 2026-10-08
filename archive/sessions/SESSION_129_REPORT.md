# Session 129 report: demand growth without weather, finished

## To finish

**The freeze is on.** This session pushed `wip/129-demand-weather-finished` only, deployed nothing and loaded nothing into the live set. **This branch is not from main alone: it builds on `wip/126-demand-weather`** (session 126's tables, page and method are not on main), with main merged in. Landing it lands sessions 125 and 126 too, so it replaces their "To finish". When `python scripts/freeze.py status` exits 0:

```bash
git checkout wip/129-demand-weather-finished && git fetch origin && git merge origin/main
node site/scripts/snapshot-live.mjs take before-129
git push origin wip/129-demand-weather-finished && git push origin wip/129-demand-weather-finished:task/129-demand-weather-finished
python runs/session118/watch_run.py task/129-demand-weather-finished 15
node site/scripts/snapshot-live.mjs take after-129 && node site/scripts/snapshot-live.mjs compare before-129 after-129
cd site && node --import ./scripts/alias-loader.mjs scripts/check-demand-weather.mjs https://erw-flame.vercel.app && cd ..
git push origin --delete wip/129-demand-weather-finished wip/126-demand-weather wip/125-contracts wip/124-network-v3
```

- **What the comparison should show on the three open pages: nothing but the clock.** The page is `review`; its six tables are under `catalogue_hold` and their sources under `sources_hold`; it is not in the menu.
- **If the merge conflicts**, it is in the generated metadata the daily run rewrites. Take main's copy and run, under the lock, `build_coverage.py --only` and `archive.py --tables ... write` for `'^(census_metro_population|noaa_station_weather_hourly|noaa_grid_weather_(stations|hourly|daily)|eia930_demand_weather|ferc_eqr_(contracts_history|contract_terms|party_mw|quarter_changes))$'`.

## Verdict: ready to open, once three things are ruled

The work asked for is done: the weights are the Census Bureau's, dew point is in the fit because it earned its place, the stations' hours are a warehouse table, and the page and method are rebuilt. What is left is yours, not code:

1. **New England's rule**: all five stations, or four of five. Both sets of figures are below and on the page.
2. **NOAA's and the Census Bureau's terms.** Neither states a license in so many words on the pages I read; both tables are registered `public` and cite their source. A person should confirm.
3. **Keeping it current.** The tables end on 28 September 2026. A refresh asks NOAA for about 560,000 rows each time, which is a standing pull and needs your approval and a budget.

Smaller, and not blocking: New York's fifth station (point 2 below), and a look at the page on a phone.

## Read these first

1. **The stated weights were close, and the findings did not rest on them.** No stated twentieth was more than 0.030 from the Census Bureau's share. Across all 136 figures both builds hold, the year's energy not explained moves by 0.26 points on average and by at most 1.0 (California, 2026). Four figures change their reading, all of them peaks or California's overnight figure (table below).
2. **By the Census Bureau's counts the rule picks one area I hold no station for.** New York's fifth most populous area is Kiryas Joel-Poughkeepsie-Newburgh (698,330), not Syracuse (662,063). This session's approved pull was the Census Bureau's, not NOAA's, so I did not pull a station for it. Syracuse stays, at a weight of 0.039. One station's pull (about 75,000 rows) would put the rule's fifth in its place; it would move New York's figures very little.
3. **Dew point is in the fit.** The rule was set before the numbers were read: in for every grid if the seven grids' mean error on an hour left out falls and no grid's rises by more than 0.05 points. It fell from 4.61 to 4.47 percent and no grid got worse. The gain is in New England (5.54 to 5.10), New York (4.17 to 3.94) and PJM (3.77 to 3.61); MISO and SPP do not move.
4. **California is still the weak grid** (6.97 percent on an hour left out with dew point, against 3.6 to 5.1 elsewhere). Its figures need sunshine, not humidity.

## The pull

| | |
|---|---|
| Source | U.S. Census Bureau, Population Estimates Program, metropolitan and micropolitan areas, vintage 2025 (`cbsa-est2025-alldata.csv`) |
| Rows in the file | **2,806** of the 5,000 allowed, USD 0. Before the pull the file's size was read from its first 20,000 bytes (63 rows, twice) to be sure it was under the ceiling |
| Used | the estimates base of 1 April 2020, for 387 metropolitan areas, whole and by state part (the sum of each area's counties, which the connector checks against the area's own total) |
| Table | `census_metro_population`, 1,650 rows |

**The Census Bureau's terms, quoted** (its page "Citing our Data, Tools, Technical Documents and Research", read 6 October 2026):

> Proper citation ensures that Census Bureau statistical products and research can be discovered, reused, replicated for verification, and credited for recognition to measure usage and impact. Data users who create their own estimates using data from disseminated tables and other data should cite the Census Bureau as the source of the original data only. Conclusions drawn from any analysis of these data are the sole responsibility of the performing party.

The file came from the Bureau's public file server, not its API, so the API's terms (which ask for the notice "This product uses the Census Bureau Data API but is not endorsed or certified by the Census Bureau") do not apply to it. Neither page states a license in so many words. A weight computed here is the ERW's, not the Bureau's.

## The weights

| Grid | Station | The Census Bureau's area | People, 1 April 2020 | Weight | Stated by session 126 |
|---|---|---|---|---|---|
| ERCOT | DFW | Dallas-Fort Worth-Arlington, TX | 7,638,294 | 0.373 | 0.35 |
| ERCOT | IAH | Houston-Pasadena-The Woodlands, TX | 7,150,227 | 0.349 | 0.35 |
| ERCOT | SAT | San Antonio-New Braunfels, TX | 2,558,389 | 0.125 | 0.15 |
| ERCOT | AUS | Austin-Round Rock-San Marcos, TX | 2,283,391 | 0.111 | 0.10 |
| ERCOT | MFE | McAllen-Edinburg-Mission, TX | 870,788 | 0.043 | 0.05 |
| CAISO | LAX | Los Angeles-Long Beach-Anaheim, CA | 13,204,693 | 0.474 | 0.50 |
| CAISO | SFO | San Francisco-Oakland-Fremont, CA | 4,753,651 | 0.171 | 0.15 |
| CAISO | ONT | Riverside-San Bernardino-Ontario, CA | 4,601,615 | 0.165 | 0.15 |
| CAISO | SAN | San Diego-Chula Vista-Carlsbad, CA | 3,298,648 | 0.118 | 0.10 |
| CAISO | SJC | San Jose-Sunnyvale-Santa Clara, CA | 2,000,479 | 0.072 | 0.10 |
| NYISO | LGA | New York-Newark-Jersey City, NY-NJ (the part in New York State) | 13,167,758 | 0.776 | 0.80 |
| NYISO | BUF | Buffalo-Cheektowaga, NY | 1,166,897 | 0.069 | 0.05 |
| NYISO | ROC | Rochester, NY | 1,065,373 | 0.063 | 0.05 |
| NYISO | ALB | Albany-Schenectady-Troy, NY | 899,223 | 0.053 | 0.05 |
| NYISO | SYR | Syracuse, NY | 662,063 | 0.039 | 0.05 |
| ISO-NE | BOS | Boston-Cambridge-Newton, MA-NH | 4,944,719 | 0.516 | 0.50 |
| ISO-NE | PVD | Providence-Warwick, RI-MA | 1,676,652 | 0.175 | 0.15 |
| ISO-NE | BDL | Hartford-West Hartford-East Hartford, CT | 1,151,912 | 0.120 | 0.15 |
| ISO-NE | ORH | Worcester, MA | 862,093 | 0.090 | 0.10 |
| ISO-NE | BDR | Bridgeport-Stamford-Danbury, CT | 946,700 | 0.099 | 0.10 |
| PJM | ORD | Chicago-Naperville-Elgin, IL-IN | 9,454,432 | 0.346 | 0.35 |
| PJM | DCA | Washington-Arlington-Alexandria, DC-VA-MD-WV | 6,278,627 | 0.230 | 0.25 |
| PJM | PHL | Philadelphia-Camden-Wilmington, PA-NJ-DE-MD | 6,245,056 | 0.229 | 0.20 |
| PJM | BWI | Baltimore-Columbia-Towson, MD | 2,848,898 | 0.104 | 0.10 |
| PJM | PIT | Pittsburgh, PA | 2,456,916 | 0.090 | 0.10 |
| MISO | DTW | Detroit-Warren-Dearborn, MI | 4,392,378 | 0.301 | 0.30 |
| MISO | MSP | Minneapolis-St. Paul-Bloomington, MN-WI | 3,690,272 | 0.253 | 0.25 |
| MISO | STL | St. Louis, MO-IL | 2,820,862 | 0.194 | 0.20 |
| MISO | IND | Indianapolis-Carmel-Greenwood, IN | 2,089,651 | 0.143 | 0.15 |
| MISO | MKE | Milwaukee-Waukesha, WI | 1,574,759 | 0.108 | 0.10 |
| SPP | MCI | Kansas City, MO-KS | 2,192,063 | 0.351 | 0.35 |
| SPP | OKC | Oklahoma City, OK | 1,425,730 | 0.228 | 0.25 |
| SPP | TUL | Tulsa, OK | 1,015,330 | 0.163 | 0.15 |
| SPP | OMA | Omaha, NE-IA | 967,604 | 0.155 | 0.15 |
| SPP | ICT | Wichita, KS | 647,632 | 0.104 | 0.10 |

New York's area is counted by its part in New York State (13,167,758 of 20,083,400): the New Jersey part is PJM's.

## Dew point, tried

Mean absolute error on an hour left out of the fit, percent:

| Grid | Without dew point | With |
|---|---|---|
| ERCOT | 4.19 | 4.12 |
| CAISO | 6.99 | 6.97 |
| PJM | 3.77 | 3.61 |
| MISO | 3.84 | 3.83 |
| SPP | 3.74 | 3.72 |
| NYISO | 4.17 | 3.94 |
| ISO-NE | 5.54 | 5.10 |
| Mean of the seven | 4.61 | 4.47 |

The term: how far the grid's dew point stands above 60 F in an hour that has cooling degrees, and its mean over the 24 hours before. An hour with no dew point held is not fitted; nothing is made up for it.

## The stations' hours, as a table

`noaa_station_weather_hourly`: **4,714,333 rows** of a ceiling of 5,000,000. Every station's measured temperature and dew point by the hour, and nothing else: an hour NOAA holds no value for has no row, and no interpolated value is written.

- **Weights can now change without this machine.** `python warehouse/connectors/noaa_grid_weather.py --from-table` rebuilds the grid tables from it. A test rebuilds Texas's and New England's hourly temperature from the table alone and finds them equal to the grid table as built, hour for hour.
- Validator pass, in coverage, archived (4,714,333 rows to the bucket), in the Redivis draft (count equal).

## New England under two rules, for your ruling

The rule in the tables: a grid's hour is used only when all five stations hold it. The trial: an hour is used when at least four do, each figure the weighted mean over the stations held, their weights restated to add to one. New England then holds 67,739 of 67,862 hours (328 of them on four stations), against 67,411 under the rule of five.

Growth not explained by temperature, percent (bold is a finding):

| Figure | Rule | 2022 | 2023 | 2024 | 2025 | 2026 |
|---|---|---|---|---|---|---|
| The year's energy | all five | -0.1, give or take 1.7 | **-2.6**, give or take 1.7 | **-1.7**, give or take 1.7 | -1.1, give or take 1.7 | -0.4, give or take 2.0 |
| | four of five | -0.0, give or take 1.7 | **-2.6**, give or take 1.7 | -1.7, give or take 1.7 | -1.0, give or take 1.7 | -0.5, give or take 2.0 |
| The summer peak | all five | -0.0, give or take 7.1 | +3.5, give or take 7.1 | +2.1, give or take 7.1 | not held | -1.6, give or take 7.1 |
| | four of five | -0.1, give or take 7.2 | +3.5, give or take 7.2 | +2.1, give or take 7.2 | +0.3, give or take 7.2 | -1.4, give or take 7.2 |
| The winter peak | all five | -3.0, give or take 5.1 | **-7.4**, give or take 5.1 | -0.9, give or take 5.1 | +2.9, give or take 5.1 | not held |
| | four of five | -3.0, give or take 5.1 | **-7.4**, give or take 5.1 | -0.8, give or take 5.1 | +2.9, give or take 5.1 | +2.9, give or take 5.1 |
| The overnight minimum | all five | **+2.0**, give or take 1.5 | +0.4, give or take 1.5 | **+3.1**, give or take 1.5 | not held | not held |
| | four of five | **+2.0**, give or take 1.5 | +0.3, give or take 1.5 | **+3.0**, give or take 1.5 | **+3.6**, give or take 1.5 | **+6.4**, give or take 1.7 |

- Where both rules hold a figure they differ by at most 0.21 points (the summer peak, 2026).
- The second rule holds the four figures the first does not.
- What it costs: in an hour held on four stations the grid's weather is that of four cities, so a figure's meaning shifts a little with which station is missing. That is the whole of the trade.

## What moved from session 126's figures

136 figures are held by both builds. The year's energy not explained moves by 0.26 points on average, at most 1.0 (California 2026: +6.0 to +5.0). Any figure by at most 4.7 (New England's 2026 summer peak: -6.3 to -1.6, where dew point explains a humid summer the temperature alone did not).

Four change their reading:

| Grid | Year | Figure | Session 126 | Now | Give or take, now | Reading |
|---|---|---|---|---|---|---|
| CAISO | 2025 | the overnight minimum | +4.4 | +4.4 | 4.5 | no longer a finding |
| CAISO | 2026 | the overnight minimum | +4.9 | +4.6 | 4.9 | no longer a finding |
| PJM | 2023 | the summer peak | -4.3 | -4.4 | 3.6 | now a finding |
| ISO-NE | 2023 | the summer peak | +6.9 | +3.5 | 7.1 | no longer a finding |

## Growth explained and not explained, by grid and year

Percent of the mean of 2019 to 2021. Each cell: growth = the part temperature and dew point explain, and the part they do not. **Bold** is a finding (larger than its uncertainty). 2026 is 1 January to 27 September. "(beyond)": the peak hour was hotter or colder than any hour of 2019 to 2021, and the figure is not called a finding.

**The year's energy**

| Grid | Give or take | 2022 | 2023 | 2024 | 2025 | 2026 |
|---|---|---|---|---|---|---|
| ERCOT | 4.0; 3.7 for 2026 | +11.8 = +3.9 and **+7.8** | +16.0 = +2.8 and **+13.2** | +20.1 = +2.1 and **+18.0** | +26.5 = +2.4 and **+24.2** | +32.9 = +3.9 and **+29.0** |
| CAISO | 3.2; 3.8 for 2026 | +3.1 = +1.0 and +2.0 | +0.5 = -1.5 and +2.0 | +3.0 = -1.9 and **+4.9** | +2.9 = -1.7 and **+4.6** | +8.6 = +3.7 and **+5.0** |
| PJM | 2.5; 3.0 for 2026 | +2.8 = +0.7 and +2.1 | -0.4 = -2.7 and +2.3 | +3.1 = -0.8 and **+3.9** | +7.2 = +0.6 and **+6.6** | +10.1 = +1.3 and **+8.8** |
| MISO | 2.6; 2.7 for 2026 | +2.4 = +1.0 and +1.3 | +0.4 = -1.2 and +1.6 | +1.0 = -0.8 and +1.8 | +4.1 = +0.6 and **+3.5** | +6.8 = +1.0 and **+5.8** |
| SPP | 1.5; 1.3 for 2026 | +6.1 = +2.4 and **+3.7** | +5.4 = -0.3 and **+5.7** | +8.7 = -0.2 and **+8.9** | +12.7 = +0.2 and **+12.5** | +17.5 = +2.8 and **+14.7** |
| NYISO | 3.0; 3.6 for 2026 | +0.1 = -0.1 and +0.2 | -3.6 = -2.2 and -1.4 | -1.3 = -1.1 and -0.2 | -0.5 = -0.5 and -0.0 | -1.2 = +0.9 and -2.2 |
| ISO-NE | 1.7; 2.0 for 2026 | +0.0 = +0.1 and -0.1 | -4.2 = -1.7 and **-2.6** | -2.4 = -0.7 and **-1.7** | -1.3 = -0.2 and -1.1 | +0.5 = +0.9 and -0.4 |

**The overnight minimum**

| Grid | Give or take | 2022 | 2023 | 2024 | 2025 | 2026 |
|---|---|---|---|---|---|---|
| ERCOT | 4.7; 4.2 for 2026 | +13.5 = +3.6 and **+9.9** | +18.3 = +1.7 and **+16.6** | +23.3 = +1.1 and **+22.2** | +30.9 = +1.4 and **+29.5** | +38.4 = +3.1 and **+35.3** |
| CAISO | 4.5; 4.9 for 2026 | +5.1 = +1.1 and +4.0 | +4.9 = -0.4 and **+5.4** | +4.2 = -1.1 and **+5.3** | +3.5 = -0.8 and +4.4 | +6.7 = +2.0 and +4.6 |
| PJM | 2.2; 2.8 for 2026 | +4.3 = +0.9 and **+3.4** | +1.1 = -3.0 and **+4.2** | +4.5 = -1.5 and **+6.1** | +10.0 = +0.8 and **+9.2** | +13.7 = +1.2 and **+12.5** |
| MISO | 2.4; 2.6 for 2026 | +3.6 = +1.0 and **+2.6** | +1.2 = -1.7 and **+2.9** | +2.2 = -1.6 and **+3.8** | +5.3 = +0.6 and **+4.7** | +8.5 = +0.7 and **+7.8** |
| SPP | 2.3; 2.0 for 2026 | +6.6 = +2.0 and **+4.6** | +5.6 = -1.0 and **+6.6** | +9.6 = -1.2 and **+10.7** | +15.5 = -0.2 and **+15.6** | +20.4 = +1.4 and **+19.0** |
| NYISO | 1.8; 2.2 for 2026 | +1.8 = +0.0 and +1.7 | -1.6 = -2.2 and +0.6 | +1.6 = -1.4 and **+2.9** | +3.8 = -0.5 and **+4.3** | +4.1 = +1.1 and **+3.0** |
| ISO-NE | 1.5 | +2.0 = -0.0 and **+2.0** | -1.5 = -1.9 and +0.4 | +2.2 = -0.8 and **+3.1** | not held | not held |

**The summer peak**

| Grid | Give or take | 2022 | 2023 | 2024 | 2025 | 2026 |
|---|---|---|---|---|---|---|
| ERCOT | 6.2 | +7.8 = +6.3 and +1.5 (beyond) | +15.4 = +11.2 and +4.2 (beyond) | +15.5 = +3.8 and +11.7 (beyond) | +12.9 = +0.0 and **+12.9** | +23.0 = +7.0 and +16.0 (beyond) |
| CAISO | 12.7 | +14.3 = +17.7 and -3.4 | -1.6 = -3.8 and +2.2 | +6.4 = +1.0 and +5.4 | -1.9 = -4.8 and +2.9 | +11.8 = +14.1 and -2.3 |
| PJM | 3.6 | -0.4 = -2.9 and +2.5 | -1.0 = +3.4 and **-4.4** | +2.7 = +1.7 and +1.0 | +7.7 = +8.6 and -1.0 (beyond) | +9.1 = +10.2 and -1.1 (beyond) |
| MISO | 3.8 | +1.6 = -0.8 and +2.4 (beyond) | +5.4 = -0.9 and **+6.3** | +3.5 = -0.8 and +4.3 (beyond) | +5.0 = +3.9 and +1.1 | +6.0 = +2.5 and +3.6 (beyond) |
| SPP | 3.7 | +6.0 = +2.5 and +3.5 (beyond) | +12.0 = +5.6 and +6.4 (beyond) | +8.5 = +1.9 and **+6.6** | +8.8 = -0.3 and **+9.0** | +15.9 = +6.9 and +9.0 (beyond) |
| NYISO | 3.9 | -0.5 = -1.6 and +1.1 | -1.5 = -3.3 and +1.8 | -5.4 = -3.4 and -2.1 | +3.9 = +0.7 and +3.2 (beyond) | +1.4 = +9.3 and **-7.8** |
| ISO-NE | 7.1 | -1.5 = -1.4 and -0.0 | -4.5 = -8.1 and +3.5 | -1.4 = -3.4 and +2.1 | not held | +2.8 = +4.5 and -1.6 (beyond) |

**The winter peak**

| Grid | Give or take | 2022 | 2023 | 2024 | 2025 | 2026 |
|---|---|---|---|---|---|---|
| ERCOT | 37.8 | +9.8 = -8.5 and +18.4 | +18.0 = +6.0 and +12.1 | +24.7 = +5.7 and +19.0 | +27.9 = -1.6 and +29.5 | +20.6 = -1.4 and +22.0 |
| CAISO | 7.0 | +4.2 = +1.6 and +2.6 | +0.3 = -7.5 and **+7.8** | -3.5 = -15.8 and **+12.3** | +0.0 = -4.5 and +4.5 | +2.8 = +1.6 and +1.1 |
| PJM | 7.5 | +8.5 = +2.0 and +6.5 | +13.0 = +12.1 and +1.0 | +11.9 = +8.1 and +3.8 | +20.6 = +13.4 and +7.3 | +16.5 = +9.4 and +7.1 |
| MISO | 5.4 | +0.1 = +0.5 and -0.3 | +6.2 = +4.5 and +1.7 | +7.4 = +5.6 and +1.8 | +9.3 = +3.6 and **+5.7** | +5.7 = +6.9 and -1.2 |
| SPP | 8.4 | -0.3 = -6.2 and +6.0 | +14.0 = +2.5 and **+11.5** | +23.7 = +4.5 and **+19.2** | +16.2 = +1.6 and **+14.6** | +21.0 = -1.5 and **+22.5** |
| NYISO | 3.9 | +1.5 = +3.8 and -2.3 | +2.1 = +6.8 and **-4.7** | -0.8 = -0.3 and -0.5 | +2.7 = +4.9 and -2.2 | +6.2 = +7.7 and -1.5 |
| ISO-NE | 5.1 | +4.2 = +7.2 and -3.0 | +3.6 = +11.0 and **-7.4** | -2.8 = -2.0 and -0.9 | +4.1 = +1.2 and +2.9 | not held |

62 of the 136 figures held are findings. Four of New England's are not held under the rule of five (above).

## The five strongest findings

1. **Texas: +24.2 percent in 2025 that weather does not explain, give or take 4.0.** Demand averaged 55,666 MW against 43,988 MW in 2019 to 2021: growth of 26.5 percent, of which weather explains 2.4. In 2026 to 27 September: +29.0, give or take 3.7.
2. **SPP: +12.5 percent in 2025, give or take 1.5**, the firmest figure in the table against its uncertainty (8.6 times). Weather explains 0.2 of 12.7. In 2026 so far: +14.7, give or take 1.3.
3. **PJM turned in 2024 and is still rising.** +2.1 and +2.3 in 2022 and 2023, neither a finding at 2.5. Then +3.9, **+6.6 in 2025**, and +8.8 in 2026 so far (give or take 3.0).
4. **The overnight minimum rose more than the year's energy in every grid that grew.** In 2025: Texas +29.5 (give or take 4.7) against +24.2; SPP +15.6 (2.3) against +12.5; PJM +9.2 (2.2) against +6.6; MISO +4.7 (2.4) against +3.5. **New York: +4.3 at night, give or take 1.8, while its year's energy is flat** (-0.0, give or take 3.0). Load that never switches off would read this way; so would rooftop solar holding the day down while nights grow. The table cannot tell which.
5. **New York's 2026 summer peak fell short of its weather: -7.8 percent, give or take 3.9.** A hot and humid summer explains a peak 9 percent above the base; the metered peak was 1.4 percent above. With dew point in the fit this is firmer than session 126's -5.4. It is the one large figure that is a shortfall.

**What the remainder is not.** It is growth weather does not explain. Population, electrification, industry and datacenters are in it together, and so are rooftop solar, efficiency and prices. The warehouse cannot split them, and no figure here is a count of datacenters.

**Not findings:** New York's and New England's energy in 2025; every Texas winter peak (uncertainty 37.8 points, because of February 2021); every California summer peak (give or take 12.7).

## Checks

- Tests: `tests/test_session129.py`, 22 tests, on the Census Bureau's own rows for New York State's areas and on session 126's samples: the Bureau's counts and the parts by state; counties that do not add to their area stop the build; New York's weights are the Bureau's shares; the rule says where counts and stations part; four of five restates the weights and three is not held; a stored value turns back to NOAA's tenth exactly; the table holds measured hours only; the rule of adoption for dew point; the grid table rebuilt from the station table. Session 126's tests, updated where their truths changed (weights are shares, not twentieths).
- Full suite: 1,318 passed, 19 skipped, exit 0.
- Site build exit 0. Route check exit 0: 8 live pages and 119 in review, 0 failed. The page's check: 65 of 65.
- All six tables: validator pass, coverage, archive, Redivis draft with counts equal. Nothing released; nothing loaded into the live set.

## Decisions made without you

- **The estimates base of 1 April 2020**, not the newest estimate: it sits inside the fit's years.
- **Weights not rounded.**
- **New York by its in-state part**, as session 126 stated; every other area whole.
- **Syracuse kept** (point 2).
- **The rule for dew point set before the numbers**, and one answer for all seven grids.
- **The tables keep the rule of five**; four of five is shown beside it and changes nothing until you rule.
- **The station table holds measured values only**, in degrees Fahrenheit, because the data standard's units hold no Celsius.

## Errors, and what caught them

| What | Caught by | Now |
|---|---|---|
| My first Census pull kept a header request's empty answer under the file's address, and read it as the file | the pull's own failure ("no columns") | the size estimate is made before the raw capture opens; the empty file removed |
| A grid none of whose hours can be fitted crashed the build | a test with a sample that holds no dew point | no figure is written for such a grid, and none is made up |
| A test of mine dated its hours a day before the seam | the test | corrected |

## What is left

1. Your three rulings (the verdict).
2. A NOAA pull of one station for Kiryas Joel-Poughkeepsie-Newburgh, if you want the rule followed to the letter.
3. Sunshine or behind-the-meter solar, for California.
4. The page on a phone.
