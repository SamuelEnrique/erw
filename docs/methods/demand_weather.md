# Demand growth with the weather taken out

Table `eia930_demand_weather`, built by `warehouse/derived/demand_weather.py` from EIA-930 hourly demand and
`noaa_grid_weather_hourly`. The weather tables (`noaa_grid_weather_stations`, `noaa_grid_weather_hourly`,
`noaa_grid_weather_daily`) are built by `warehouse/connectors/noaa_grid_weather.py`. Page: `/demand/weather`, in review.
Session 126. Every figure below is the build's own (run of 2026-10-05); this document is written from its summary.

## What it answers

The demand page ([demand growth](demand_growth.md)) shows which grids use more power than they did, and says above
everything else that weather is not removed. This table removes it, as far as temperature goes. For each of the seven
grid operators and each year after 2021 it gives the growth of demand against the average of 2019 to 2021, the part of
that growth the year's temperatures explain, and the part they do not, each with an uncertainty.

## What the remainder is not

The remainder is growth that temperature does not explain. It is not a count of datacenters. Population,
electrification, new industry and datacenters raise it together; rooftop solar behind the meter, efficiency and a
weak economy lower it; humidity, wind and cloud, which are not in the fit, move it either way. The warehouse cannot
split these, and neither this table nor its page says which one a figure is.

## The weather

**Source.** NOAA National Centers for Environmental Information (NCEI), hourly observations at 35 airport stations,
five a grid, from 1 January 2019 to 2026-09-28 (the newest hour every station reaches). Two products, because
the first one ended:

| Hours | Product | Access |
|---|---|---|
| to 31 July 2025 | ISD-Lite, the hourly cut of the Integrated Surface Database: one file per station and year, one row per hour, temperature and dew point in tenths of a degree Celsius | `https://www.ncei.noaa.gov/pub/data/noaa/isd-lite/<year>/<USAF>-<WBAN>-<year>.gz` |
| from 1 August 2025 | Local Climatological Data, version 2: every report of the station, in degrees Celsius, dated in local standard time | NCEI's Access Data Service, `dataset=local-climatological-data-v2`, `dataTypes=HourlyDryBulbTemperature,HourlyDewPointTemperature` |

NOAA's Integrated Surface Database stopped on 27 August 2025: its station list gives that day (or one or two days
before) as the last of every one of these stations, the 2025 files were last written on 29 August 2025, and there is no
file for 2026. The Local Climatological Data carries the same stations on. Its times are moved from local standard time
to UTC, and ISD-Lite's own rule for an hour is applied to its reports: an hour takes the report made from ten minutes
before the hour up to the hour, the one closest to it. So an hour means the same thing on both sides of 1 August 2025:
the reading taken just before it.

**The seam, checked.** Both products were read for 1 July 2025 to the end of ISD-Lite (about eight weeks, 1,304 to 1,368 shared hours a station) and compared hour by hour before anything was written.
Outside the eight synoptic hours of the day, every station agrees to a tenth of a degree Celsius in at least 99.89 percent of hours.
At the synoptic hours (00, 03, ... 21 UTC) ISD-Lite takes the synoptic report filed on the hour where a station files one, and the
second product does not carry that report for every station: there 34 of the 35 stations agree in more than 99 percent of hours, and the least is
AUS (Austin-Bergstrom Intl Airport) at 28.6 percent, where ISD-Lite reads +0.099 C higher on average over all shared hours.
A station whose hours outside the synoptic ones agree in under 90 percent stops the build. None did.

**The service's short answers.** The Access Data Service twice answered HTTP 200 with a body that was not the data asked for:
once with nothing (Omaha), once with a file that stopped at 1 January 2026 (Ontario, California; 4,896 rows). The connector
now tests every answer (it begins with the header, and its newest report is within 21 days of the last day asked for),
counts a short answer's rows against the ceiling, does not use it, and asks again.

**Minneapolis-St. Paul, the one exception.** 2020-04-01 to 2022-11-30 read from the Local Climatological Data (125,199 rows): 23,365 hours held there against 12,464 in ISD-Lite; over the 12,456 hours both hold they agree to a tenth of a degree C in 99.82%.
ISD-Lite keeps, for that station in the warm months of 2020 to 2022, little more than the synoptic hours (one hour in six on 14 July
2020), while the second product holds the station's hourly report for every one of those hours. The stretch is read from the second
product for that station only, under the same rule for an hour.

**The pull.** 2,770,528 rows read from NOAA, of the approved ceiling of 3,000,000, at no cost. A row is a data row of a file or of a
response; the session's trial reads (29,558 rows, made to choose the product), the short answer above and the probes that explained it are counted.

### NOAA's terms, quoted

NCEI's record for the Integrated Surface Database (`gov.noaa.ncdc:C00532`, read 5 October 2026) names no license. Under
"Use Constraints" it says:

> Cite as: NOAA National Centers for Environmental Information (2001): Global Surface Hourly [indicate subset used]. NOAA National Centers for Environmental Information. [access date]
>
> Use liability: NOAA and NCEI cannot provide any warranty as to the accuracy, reliability, or completeness of furnished data. Users assume responsibility to determine the usability of these data. The user is responsible for the results of any application of this data for other than its intended purpose.

and under "Access Constraints":

> Distribution liability: NOAA and NCEI make no warranty, expressed or implied, regarding these data, nor does the fact of distribution constitute such a warranty. NOAA and NCEI cannot assume liability for any damages caused by any errors or omissions in these data.

The record for the Local Climatological Data, version 2 (`gov.noaa.ncdc:C01689`) carries the same two statements of liability and its own citation:

> Cite as: Kantor, Diana; Casey, Nancy W.; Menne, Matthew J.; Buddenberg, Andrew. 2023. Local Climatological Data (LCD), Version 2. [indicate subset used]. NOAA National Centers for Environmental Information. https://doi.org/10.25921/96dw-mb77. [access date]

The one restriction either states is in the database's readme (`https://www.ncei.noaa.gov/pub/data/noaa/readme.txt`):

> IMPORTANT NOTE:  The non-U.S. data in ISD are subject to WMO Resolution 40 restrictions, and cannot be redistributed to other users or customers.

All 35 stations are in the United States. The words "public domain" are the National Weather Service's, about its own pages
(`https://www.weather.gov/disclaimer`): "The information on National Weather Service (NWS) Web pages are in the public domain, unless
specifically noted otherwise, and may be used without charge for any lawful purpose". NCEI's two records do not use those words. The
registry holds both sources as `public`, as it has held `noaa:isd_global_hourly` since session 49, and the tables carry both citations.
A person should confirm that reading before the page opens.

### The stations and their weights

**The rule.** For each grid, the five most populous metropolitan areas whose principal city the grid operator serves; for each, the
principal airport's station; the weight is the area's share of the five areas' population, to the nearest twentieth (largest
remainders first, so the five add to one).

**The populations were not retrieved.** The warehouse holds no population table, and the session's one approved pull was NOAA's. The
twentieths below are therefore a stated parameter of the method, as session 60 stated California's three (0.30, 0.20, 0.50), set from the
2020 Census counts of metropolitan areas as generally known. No population figure is written to any table. They are rounded this
coarsely so that a count wrong by a few percent gives the same weight. A person should check them against the Census Bureau's table of
metropolitan areas before the page opens; replacing them by retrieved figures needs an approved pull of that one file.
What rests on them: with five equal weights a grid in their place, the year's energy not explained moves by at most 1.2 points in any grid and year
(CAISO, 2026); a peak moves by up to 7.2 points (NYISO, 2024,
where equal weights put four fifths of the weight outside the city that holds most of the load). The energy figures do not rest on the weights; the peaks do.

| Grid | Airport | NOAA station (USAF-WBAN), NOAA's name | Stands for | Weight | Hours measured | Interpolated | Missing | Longest gap, hours |
|---|---|---|---|---|---|---|---|---|
| ERCOT | DFW | 722590-03927 Dallas/Ft Worth International Ap | Dallas-Fort Worth-Arlington | 0.35 | 67,680 | 80 | 102 | 91 |
| ERCOT | IAH | 722430-12960 G Bush Intercontinental Ap/Houston Ap | Houston-The Woodlands-Sugar Land | 0.35 | 67,720 | 45 | 97 | 90 |
| ERCOT | SAT | 722530-12921 San Antonio International Airport | San Antonio-New Braunfels | 0.15 | 67,699 | 40 | 123 | 90 |
| ERCOT | AUS | 722540-13904 Austin-Bergstrom Intl Airport | Austin-Round Rock-Georgetown | 0.10 | 67,637 | 117 | 108 | 91 |
| ERCOT | MFE | 722506-12959 Mc Allen Miller Intl Arpt | McAllen-Edinburg-Mission | 0.05 | 67,573 | 109 | 180 | 91 |
| CAISO | LAX | 722950-23174 Los Angeles International Airport | Los Angeles-Long Beach-Anaheim | 0.50 | 67,695 | 60 | 107 | 90 |
| CAISO | SFO | 724940-23234 San Francisco International Airport | San Francisco-Oakland-Berkeley | 0.15 | 67,670 | 60 | 132 | 90 |
| CAISO | ONT | 747040-03102 Ontario International Arpt | Riverside-San Bernardino-Ontario | 0.15 | 67,673 | 69 | 120 | 91 |
| CAISO | SAN | 722900-23188 San Diego International Airport | San Diego-Chula Vista-Carlsbad | 0.10 | 67,678 | 58 | 126 | 90 |
| CAISO | SJC | 724945-23293 N Y. Mineta Sn Jo Intl Apt | San Jose-Sunnyvale-Santa Clara | 0.10 | 67,610 | 87 | 165 | 90 |
| NYISO | LGA | 725030-14732 La Guardia Airport | New York-Newark-Jersey City (the part in New York State) | 0.80 | 67,700 | 61 | 101 | 90 |
| NYISO | BUF | 725280-14733 Buffalo Niagara International Airpor | Buffalo-Cheektowaga | 0.05 | 64,280 | 3,485 | 97 | 90 |
| NYISO | ROC | 725290-14768 Greater Rochester International Ap | Rochester | 0.05 | 64,319 | 3,425 | 118 | 90 |
| NYISO | ALB | 725180-14735 Albany International Airport | Albany-Schenectady-Troy | 0.05 | 67,690 | 71 | 101 | 90 |
| NYISO | SYR | 725190-14771 Syracuse Hancock International Ap | Syracuse | 0.05 | 67,680 | 61 | 121 | 90 |
| ISO-NE | BOS | 725090-14739 Gen E L Logan International Airport | Boston-Cambridge-Newton | 0.50 | 67,611 | 154 | 97 | 90 |
| ISO-NE | PVD | 725070-14765 Theodore F Green State Airport | Providence-Warwick | 0.15 | 67,579 | 128 | 155 | 90 |
| ISO-NE | BDL | 725080-14740 Bradley International Airport | Hartford-East Hartford-Middletown | 0.15 | 67,697 | 64 | 101 | 90 |
| ISO-NE | ORH | 725100-94746 Worcester Regional Airport | Worcester | 0.10 | 67,571 | 102 | 189 | 90 |
| ISO-NE | BDR | 725040-94702 Igor I Sikorsky Memorial Airport | Bridgeport-Stamford-Norwalk | 0.10 | 67,388 | 147 | 327 | 90 |
| PJM | ORD | 725300-94846 Chicago O'Hare International Airport | Chicago-Naperville-Elgin | 0.35 | 67,687 | 62 | 113 | 90 |
| PJM | DCA | 724050-13743 Ronald Reagan Washington Natl Ap | Washington-Arlington-Alexandria | 0.25 | 67,687 | 72 | 103 | 90 |
| PJM | PHL | 724080-13739 Philadelphia International Airport | Philadelphia-Camden-Wilmington | 0.20 | 67,684 | 58 | 120 | 90 |
| PJM | BWI | 724060-93721 Baltimore-Washington Intl Airport | Baltimore-Columbia-Towson | 0.10 | 67,718 | 47 | 97 | 90 |
| PJM | PIT | 725200-94823 Pittsburgh International Airport | Pittsburgh | 0.10 | 67,710 | 45 | 107 | 90 |
| MISO | DTW | 725370-94847 Detroit Metro Wayne County Airport | Detroit-Warren-Dearborn | 0.30 | 63,829 | 3,918 | 115 | 91 |
| MISO | MSP | 726580-14922 Minneapolis-St Paul International Ap | Minneapolis-St. Paul-Bloomington | 0.25 | 67,600 | 129 | 133 | 90 |
| MISO | STL | 724340-13994 Lambert-St Louis International Ap | St. Louis | 0.20 | 67,627 | 113 | 122 | 90 |
| MISO | IND | 724380-93819 Indianapolis International Airport | Indianapolis-Carmel-Anderson | 0.15 | 67,715 | 50 | 97 | 90 |
| MISO | MKE | 726400-14839 General Mitchell International Ap | Milwaukee-Waukesha | 0.10 | 67,688 | 61 | 113 | 90 |
| SPP | MCI | 724460-03947 Kansas City International Airport | Kansas City | 0.35 | 67,701 | 53 | 108 | 91 |
| SPP | OKC | 723530-13967 Will Rogers World Airport | Oklahoma City | 0.25 | 67,686 | 53 | 123 | 90 |
| SPP | TUL | 723560-13968 Tulsa International Airport | Tulsa | 0.15 | 67,670 | 70 | 122 | 90 |
| SPP | OMA | 725500-14942 Eppley Airfield Airport | Omaha-Council Bluffs | 0.15 | 67,557 | 183 | 122 | 90 |
| SPP | ICT | 724500-03928 Wichita Eisenhower National | Wichita | 0.10 | 67,655 | 79 | 128 | 90 |

Of 67,862 hours from 1 January 2019 to 2026-09-28 13:00 UTC. Station names and positions are NOAA's (`isd-history.csv`).

Left out by the rule, and worth knowing: the New Jersey half of the New York area (PJM's, but the area's principal city is NYISO's);
Sacramento (its city utility is its own balancing area); MISO's southern states (New Orleans would be sixth); west Texas, where much
of ERCOT's new load is.

### Missing hours

A station's hour with no temperature is counted (the table above). A run of one, two or three missing hours between two measured hours is
interpolated on a straight line and counted as interpolated; a longer run stays missing, and nothing else is filled. Buffalo, Rochester and
Detroit lack an hour or a few on most days in ISD-Lite, at the same hours of the clock (Detroit in the cold months): those are the interpolated
thousands. Every station lacks about 90 hours from 30 August to 2 September 2025: the Local Climatological Data holds no report for
any of them over those four days, the first after NOAA's database ended. No grid has weather for those hours.

A grid's hour is written only when all five of its stations hold a temperature, measured or interpolated across at most three hours;
`x_interpolated` counts the interpolated ones. A grid's day is written only when every hour of its local day is.

| Grid | Hours held | Of | Share | Hours with a station interpolated | Whole local days |
|---|---|---|---|---|---|
| ERCOT | 67,667 | 67,862 | 99.71 percent | 226 | 2,805 |
| CAISO | 67,663 | 67,862 | 99.71 percent | 152 | 2,806 |
| PJM | 67,734 | 67,862 | 99.81 percent | 129 | 2,817 |
| MISO | 67,720 | 67,862 | 99.79 percent | 4,095 | 2,814 |
| SPP | 67,703 | 67,862 | 99.77 percent | 276 | 2,814 |
| NYISO | 67,736 | 67,862 | 99.81 percent | 3,967 | 2,817 |
| ISO-NE | 67,411 | 67,862 | 99.34 percent | 414 | 2,765 |

**Degrees.** `heating_degrees_f` is the weighted mean over the stations of max(65 - T, 0), `cooling_degrees_f` of max(T - 65, 0), with T in
degrees Fahrenheit: taken at each station and then weighted, so a grid whose cities sit either side of 65 has both. A day's degree days
are the sum of its hours' degrees over 24.

## The fit

Demand is EIA-930's hourly demand as [demand growth](demand_growth.md) reads it (EIA's Adjusted demand; California's late hours set back). An
hour is used only when it passes the rule for impossible values ([impossible hours](impossible_hours.md), session 118): held, above zero,
within a quarter of the median of the four hours around it, and within the grid's own range.

For each grid, on the local years 2019 to 2021, one least-squares line for each of 48 kinds of hour (24 hours of the local day, weekday or
weekend):

    demand = a + b1 HD + b2 HD^2 + b3 CD + b4 CD^2 + b5 HD24 + b6 CD24

HD and CD are the grid's heating and cooling degrees of the hour; HD24 and CD24 are their means over the 24 hours before (at least 18
of them held). Heating and cooling have their own terms, and every kind of hour its own seven numbers. There is no trend, no month and
no holiday in the fit: whatever repeats every year by the calendar is carried by the temperature it travels with.

Texas's hours of 15 to 19 February 2021 are left out of the fit (120 hours): ERCOT was shedding load, so the meter did not record what
customers would have used. The dates are a stated choice of the method. Those hours stay in the year's own figures.

**The fit's error, by grid.** Mean absolute error, percent of the hour's (or the day's) demand. "Left out": each of 2019, 2020 and 2021 predicted by a fit
made on the other two. The last column is the same 48 lines with heating and cooling degrees only, to show what the squares and the day before buy.

| Grid | Hours in the fit | On an hour left out | On a day left out | On the hours it was fitted to | 2019 left out | 2020 | 2021 | With HD and CD only |
|---|---|---|---|---|---|---|---|---|
| ERCOT | 26,119 | 4.21 | 3.80 | 3.48 | 3.72 | 3.73 | 5.21 | 4.97 |
| CAISO | 26,236 | 7.06 | 6.24 | 6.57 | 7.49 | 7.20 | 6.48 | 7.69 |
| PJM | 26,285 | 3.77 | 3.30 | 3.47 | 3.17 | 4.54 | 3.61 | 4.83 |
| MISO | 26,286 | 3.83 | 3.43 | 3.49 | 3.66 | 4.57 | 3.26 | 4.62 |
| SPP | 26,287 | 3.72 | 3.21 | 3.57 | 3.71 | 4.26 | 3.19 | 4.63 |
| NYISO | 26,290 | 4.20 | 3.78 | 3.87 | 4.11 | 4.81 | 3.68 | 5.07 |
| ISO-NE | 26,192 | 5.50 | 4.58 | 5.22 | 5.13 | 6.22 | 5.14 | 6.58 |

California's fit is the weakest by a wide margin. Its demand as the grid meters it depends on sunshine on rooftops, which temperature at
five airports does not carry, and three of its five airports sit on the coast.

## The figures

| Figure | What it is |
|---|---|
| energy | the mean of the year's hours |
| summer_peak | the highest hour of June to September |
| winter_peak | the highest hour of December of the year before to February (a winter is named by its January) |
| overnight_min | the mean over the year's days of the lowest hour from midnight to 6 am, local time, on days whose six hours are all used |

With A the figure from metered demand and P the same figure from the fit's hours (what the customers of 2019 to 2021 would have used in
that year's weather), and A0 and P0 their means over the years of 2019 to 2021 that hold the figure:

    growth                 A / A0 - 1
    explained by weather   P / P0 - 1
    not explained          the first minus the second

Both figures of a year come from the same hours: those where demand passes the rule and the fit's terms are held. A figure is written when
at least 95 percent of its hours (or days) are. The winter of 2019 is not: its December is before the weather begins, so the winter peak's
base is 2020 and 2021. The newest year is partial (through 2026-09-27): its energy and its overnight minimum are compared over the
same days of 2019 to 2021; its summer is whole but for the last days of September.

**Not held.** ISO-NE 2025, the summer peak; ISO-NE 2025, the overnight minimum; ISO-NE 2026, the winter peak; ISO-NE 2026, the overnight minimum. New England's hours fall just under 95 percent for these: Bridgeport's
station lacks hours in 2025 and 2026, and a grid's hour needs all five stations. They are left not held; the bar was not lowered to admit them.

## The uncertainty

It comes from years the fit has not seen. Each of 2019, 2020 and 2021 is left out in turn; the fit is made on the other two and the left-out
year's "not explained" is computed against them. The uncertainty of a figure is the largest of those misses, in absolute value. A peak is a
single hour, so its uncertainty is never taken as less than the fit's error on an hour left out (the table above).

A figure is a finding (`x_finding` yes) only when it is larger than its uncertainty **and**, for a peak, when the peak's hour was not hotter
(summer) or colder (winter) than every hour of 2019 to 2021: there the fit reaches past what it was made on, and the row says `beyond`.

This uncertainty is deliberately wide. A left-out year's miss holds the fit's error and whatever really changed that year, and 2020 holds
the lockdowns. With three years to leave out it is also a rough number: three misses, and the largest of them.

## The check: years the fit had not seen

A grid whose customers did not change should come back near zero. Growth not explained by temperature in the year left out, percent:

**The year's energy**

| Grid | 2019 left out | 2020 left out | 2021 left out | The uncertainty used |
|---|---|---|---|---|
| ERCOT | -2.5 | -1.4 | +4.1 | 4.1 |
| CAISO | -2.0 | -0.6 | +3.0 | 3.0 |
| PJM | +0.9 | -2.6 | +1.6 | 2.6 |
| MISO | +2.3 | -2.6 | +0.2 | 2.6 |
| SPP | +0.6 | -1.5 | +0.8 | 1.5 |
| NYISO | +2.8 | -2.7 | -0.2 | 2.8 |
| ISO-NE | +1.1 | -0.9 | -0.4 | 1.1 |

**The summer peak**

| Grid | 2019 left out | 2020 left out | 2021 left out | The uncertainty used |
|---|---|---|---|---|
| ERCOT | -1.6 | -4.7 | +6.6 | 6.6 |
| CAISO | +2.9 | -9.5 | +9.9 | 9.9 |
| PJM | +1.8 | -4.4 | +3.8 | 4.4 |
| MISO | +0.7 | -1.2 | +0.3 | 3.8 |
| SPP | -3.3 | +2.9 | -0.5 | 3.7 |
| NYISO | +0.2 | -1.7 | -0.3 | 4.2 |
| ISO-NE | -1.7 | -0.3 | +1.1 | 5.5 |

**The winter peak**

| Grid | 2019 left out | 2020 left out | 2021 left out | The uncertainty used |
|---|---|---|---|---|
| ERCOT | not held | +19.9 | -36.7 | 36.7 |
| CAISO | not held | -6.5 | +4.5 | 7.1 |
| PJM | not held | +6.4 | -7.6 | 7.6 |
| MISO | not held | -5.5 | +5.1 | 5.5 |
| SPP | not held | +3.4 | -8.7 | 8.7 |
| NYISO | not held | +3.5 | -3.4 | 4.2 |
| ISO-NE | not held | +4.2 | -4.6 | 5.5 |

**The overnight minimum**

| Grid | 2019 left out | 2020 left out | 2021 left out | The uncertainty used |
|---|---|---|---|---|
| ERCOT | -3.1 | -1.5 | +4.8 | 4.8 |
| CAISO | -3.5 | +0.2 | +4.3 | 4.3 |
| PJM | +0.0 | -2.3 | +2.2 | 2.3 |
| MISO | +1.2 | -2.3 | +1.0 | 2.3 |
| SPP | +0.8 | -2.3 | +1.5 | 2.3 |
| NYISO | +1.0 | -1.9 | +0.8 | 1.9 |
| ISO-NE | +0.4 | -1.2 | +0.7 | 1.2 |

Read for the year's energy: ISO-NE comes back within 1.1 points in each of the three years and SPP within 1.5;
2020 comes back below zero in all seven grids (-2.7 to -0.6), the year of the lockdowns; Texas's 2021 comes back at +4.1,
which reads as growth already under way inside the fit's own years. The base of 2019 to 2021 is not a still one, least of all for Texas, and a later figure is growth on top of it.

Texas's winter peak is the method's plain failure: the winter left out that holds February 2021 misses by 37 points, because the grid was shedding load at the
coldest hours while the fit, made on the mild winter before, reaches far past it. No Texas winter peak is a finding.

## California across December 2025

EIA dated California's hours one hour late until 2025-12-02 and changed its generation series on 2025-12-16 ([the break](eia930_caiso_break.md)).

**Comparable across the change:** every figure of this table. They rest on demand, a different series from generation, which the demand method's
own check found does not step at the change, and on hours dated right: the late hours are set back before anything is computed (`caiso_join.true_hours`).

**Not comparable, and not used here:** California's generation by source in EIA's series either side of the change.

**A check the weather allows.** If demand sat on the wrong hour, the fit would match it clearly better moved by an hour. The fit's mean absolute error,
percent, with demand an hour early, as read, and an hour late; and how far metered demand stood above the fit:

| Window | From | An hour early | As read | An hour late | Metered against the fit |
|---|---|---|---|---|---|
| the eight weeks before the hours were dated right | 2025-10-07 | 8.44 | 7.10 | 6.98 | +2.86 |
| the eight weeks from the change in EIA's generation series | 2025-12-16 | 9.49 | 8.75 | 8.86 | +6.32 |
| the eight weeks before the hours were dated right, a year earlier | 2024-10-07 | 7.89 | 7.02 | 7.17 | +4.61 |
| the eight weeks from the change in EIA's generation series, a year earlier | 2024-12-16 | 7.62 | 7.18 | 8.00 | +6.16 |

In 3 of the 4 windows the error is smallest as read; in the other the smallest is 0.12 points under it, with demand an hour late, against 1.34 points worse an hour early.
That is too little to read as a misdated hour, and too coarse to rule one out: demand follows temperature with a lag, so moving it later costs the fit
little. The last column rises from autumn to winter in both years. What this check can say is that nothing as large as an hour's shift shows at the change;
it cannot see a step of a point or two in the level.

## What is not in it

- A cause for the remainder (above).
- Humidity, wind, cloud and sunlight. Dew point is in the weather tables and not in the fit.
- Weather the fit never saw: a peak beyond every hour of 2019 to 2021 is marked and is not a finding.
- A still base: 2019 to 2021 holds the lockdowns of 2020 and, in Texas, growth already under way.
- The parts of a grid away from its five largest cities.
- Demand served behind the meter.
- The station hours themselves as a table: the grid tables are built from NOAA's files kept on the data machine (`warehouse/raw/noaa_grid_weather/`), each with its URL in a manifest.

