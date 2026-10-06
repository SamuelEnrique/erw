# Demand growth with the weather taken out

Table `eia930_demand_weather`, built by `warehouse/derived/demand_weather.py` from EIA-930 hourly demand and
`noaa_grid_weather_hourly`. The weather tables (`noaa_grid_weather_stations`, `noaa_grid_weather_hourly`,
`noaa_grid_weather_daily`) are built by `warehouse/connectors/noaa_grid_weather.py`. Page: `/demand/weather`, in review.
Sessions 126 and 129. Every figure below is the build's own (run of 2026-10-06); this document is written from its summary.

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
principal airport's station; the weight is the area's population over the sum of the grid's five.

**The populations are the Census Bureau's** (session 129): `census_metro_population`, from the Population Estimates Program's file of
metropolitan areas, vintage 2025, the estimates base of 1 April 2020 (`cbsa-est2025-alldata.csv`, 2,806 rows of a ceiling of 5,000). A weight
is not rounded. New York's area is counted by its part in New York State, the sum of its New York counties as the file lists them: its
New Jersey part is PJM's. Session 126 had no population table and stated the shares to the nearest twentieth; no stated share was more
than 0.030 from the Bureau's.

**Where the counts and the stations part.** NYISO: Kiryas Joel-Poughkeepsie-Newburgh, NY (698,330) is more populous than Syracuse, NY (662,063), whose station SYR is held; no station is held for it. Session 129's approved pull was the Census Bureau's and not NOAA's, so the
station held stays, at a weight of 0.039. A pull of that one station would put the rule's fifth area in its place.

**The Census Bureau's terms, quoted** (its page "Citing our Data, Tools, Technical Documents and Research", read 6 October 2026):

> Proper citation ensures that Census Bureau statistical products and research can be discovered, reused, replicated for verification, and credited for recognition to measure usage and impact. Data users who create their own estimates using data from disseminated tables and other data should cite the Census Bureau as the source of the original data only. Conclusions drawn from any analysis of these data are the sole responsibility of the performing party.

The file was taken from the Bureau's public file server, not through its API, so the API's terms of service (which ask for the notice "This
product uses the Census Bureau Data API but is not endorsed or certified by the Census Bureau") do not apply to it. Neither page I read
states a license in so many words; the table is registered `public`, as the Bureau's gazetteer already is, and cites the
Bureau as the source. A weight computed here is the ERW's, not the Bureau's.
What rests on them: with five equal weights a grid in their place, the year's energy not explained moves by at most 1.8 points in any grid and year
(CAISO, 2026); a peak moves by up to 6.0 points (CAISO, 2025,
where equal weights put four fifths of the weight outside the city that holds most of the load). The energy figures do not rest on the weights; the peaks do.

| Grid | Airport | NOAA station (USAF-WBAN), NOAA's name | The Census Bureau's area | People, 1 April 2020 | Weight | Stated by session 126 | Hours measured | Interpolated | Missing | Longest gap, hours |
|---|---|---|---|---|---|---|---|---|---|---|
| ERCOT | DFW | 722590-03927 Dallas/Ft Worth International Ap | Dallas-Fort Worth-Arlington, TX | 7,638,294 | 0.3726 | 0.35 | 67,680 | 80 | 102 | 91 |
| ERCOT | IAH | 722430-12960 G Bush Intercontinental Ap/Houston Ap | Houston-Pasadena-The Woodlands, TX | 7,150,227 | 0.3488 | 0.35 | 67,720 | 45 | 97 | 90 |
| ERCOT | SAT | 722530-12921 San Antonio International Airport | San Antonio-New Braunfels, TX | 2,558,389 | 0.1248 | 0.15 | 67,699 | 40 | 123 | 90 |
| ERCOT | AUS | 722540-13904 Austin-Bergstrom Intl Airport | Austin-Round Rock-San Marcos, TX | 2,283,391 | 0.1114 | 0.10 | 67,637 | 117 | 108 | 91 |
| ERCOT | MFE | 722506-12959 Mc Allen Miller Intl Arpt | McAllen-Edinburg-Mission, TX | 870,788 | 0.0425 | 0.05 | 67,573 | 109 | 180 | 91 |
| CAISO | LAX | 722950-23174 Los Angeles International Airport | Los Angeles-Long Beach-Anaheim, CA | 13,204,693 | 0.4740 | 0.50 | 67,695 | 60 | 107 | 90 |
| CAISO | SFO | 724940-23234 San Francisco International Airport | San Francisco-Oakland-Fremont, CA | 4,753,651 | 0.1706 | 0.15 | 67,670 | 60 | 132 | 90 |
| CAISO | ONT | 747040-03102 Ontario International Arpt | Riverside-San Bernardino-Ontario, CA | 4,601,615 | 0.1652 | 0.15 | 67,673 | 69 | 120 | 91 |
| CAISO | SAN | 722900-23188 San Diego International Airport | San Diego-Chula Vista-Carlsbad, CA | 3,298,648 | 0.1184 | 0.10 | 67,678 | 58 | 126 | 90 |
| CAISO | SJC | 724945-23293 N Y. Mineta Sn Jo Intl Apt | San Jose-Sunnyvale-Santa Clara, CA | 2,000,479 | 0.0718 | 0.10 | 67,610 | 87 | 165 | 90 |
| NYISO | LGA | 725030-14732 La Guardia Airport | New York-Newark-Jersey City, NY-NJ (the part in New York State) | 13,167,758 | 0.7763 | 0.80 | 67,700 | 61 | 101 | 90 |
| NYISO | BUF | 725280-14733 Buffalo Niagara International Airpor | Buffalo-Cheektowaga, NY | 1,166,897 | 0.0688 | 0.05 | 64,280 | 3,485 | 97 | 90 |
| NYISO | ROC | 725290-14768 Greater Rochester International Ap | Rochester, NY | 1,065,373 | 0.0628 | 0.05 | 64,319 | 3,425 | 118 | 90 |
| NYISO | ALB | 725180-14735 Albany International Airport | Albany-Schenectady-Troy, NY | 899,223 | 0.0530 | 0.05 | 67,690 | 71 | 101 | 90 |
| NYISO | SYR | 725190-14771 Syracuse Hancock International Ap | Syracuse, NY | 662,063 | 0.0390 | 0.05 | 67,680 | 61 | 121 | 90 |
| ISO-NE | BOS | 725090-14739 Gen E L Logan International Airport | Boston-Cambridge-Newton, MA-NH | 4,944,719 | 0.5160 | 0.50 | 67,611 | 154 | 97 | 90 |
| ISO-NE | PVD | 725070-14765 Theodore F Green State Airport | Providence-Warwick, RI-MA | 1,676,652 | 0.1750 | 0.15 | 67,579 | 128 | 155 | 90 |
| ISO-NE | BDL | 725080-14740 Bradley International Airport | Hartford-West Hartford-East Hartford, CT | 1,151,912 | 0.1202 | 0.15 | 67,697 | 64 | 101 | 90 |
| ISO-NE | ORH | 725100-94746 Worcester Regional Airport | Worcester, MA | 862,093 | 0.0900 | 0.10 | 67,571 | 102 | 189 | 90 |
| ISO-NE | BDR | 725040-94702 Igor I Sikorsky Memorial Airport | Bridgeport-Stamford-Danbury, CT | 946,700 | 0.0988 | 0.10 | 67,388 | 147 | 327 | 90 |
| PJM | ORD | 725300-94846 Chicago O'Hare International Airport | Chicago-Naperville-Elgin, IL-IN | 9,454,432 | 0.3465 | 0.35 | 67,687 | 62 | 113 | 90 |
| PJM | DCA | 724050-13743 Ronald Reagan Washington Natl Ap | Washington-Arlington-Alexandria, DC-VA-MD-WV | 6,278,627 | 0.2301 | 0.25 | 67,687 | 72 | 103 | 90 |
| PJM | PHL | 724080-13739 Philadelphia International Airport | Philadelphia-Camden-Wilmington, PA-NJ-DE-MD | 6,245,056 | 0.2289 | 0.20 | 67,684 | 58 | 120 | 90 |
| PJM | BWI | 724060-93721 Baltimore-Washington Intl Airport | Baltimore-Columbia-Towson, MD | 2,848,898 | 0.1044 | 0.10 | 67,718 | 47 | 97 | 90 |
| PJM | PIT | 725200-94823 Pittsburgh International Airport | Pittsburgh, PA | 2,456,916 | 0.0900 | 0.10 | 67,710 | 45 | 107 | 90 |
| MISO | DTW | 725370-94847 Detroit Metro Wayne County Airport | Detroit-Warren-Dearborn, MI | 4,392,378 | 0.3015 | 0.30 | 63,829 | 3,918 | 115 | 91 |
| MISO | MSP | 726580-14922 Minneapolis-St Paul International Ap | Minneapolis-St. Paul-Bloomington, MN-WI | 3,690,272 | 0.2533 | 0.25 | 67,600 | 129 | 133 | 90 |
| MISO | STL | 724340-13994 Lambert-St Louis International Ap | St. Louis, MO-IL | 2,820,862 | 0.1936 | 0.20 | 67,627 | 113 | 122 | 90 |
| MISO | IND | 724380-93819 Indianapolis International Airport | Indianapolis-Carmel-Greenwood, IN | 2,089,651 | 0.1434 | 0.15 | 67,715 | 50 | 97 | 90 |
| MISO | MKE | 726400-14839 General Mitchell International Ap | Milwaukee-Waukesha, WI | 1,574,759 | 0.1081 | 0.10 | 67,688 | 61 | 113 | 90 |
| SPP | MCI | 724460-03947 Kansas City International Airport | Kansas City, MO-KS | 2,192,063 | 0.3508 | 0.35 | 67,701 | 53 | 108 | 91 |
| SPP | OKC | 723530-13967 Will Rogers World Airport | Oklahoma City, OK | 1,425,730 | 0.2282 | 0.25 | 67,686 | 53 | 123 | 90 |
| SPP | TUL | 723560-13968 Tulsa International Airport | Tulsa, OK | 1,015,330 | 0.1625 | 0.15 | 67,670 | 70 | 122 | 90 |
| SPP | OMA | 725500-14942 Eppley Airfield Airport | Omaha, NE-IA | 967,604 | 0.1549 | 0.15 | 67,557 | 183 | 122 | 90 |
| SPP | ICT | 724500-03928 Wichita Eisenhower National | Wichita, KS | 647,632 | 0.1036 | 0.10 | 67,655 | 79 | 128 | 90 |

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

    demand = a + b1 HD + b2 HD^2 + b3 CD + b4 CD^2 + b5 HD24 + b6 CD24 + b7 HUM + b8 HUM24

HD and CD are the grid's heating and cooling degrees of the hour; HD24 and CD24 are their means over the 24 hours before (at least 18
of them held). HUM is how far the grid's dew point stands above 60 F in an hour that has cooling degrees, and zero in any other hour; HUM24 is its mean over the 24 hours before. Heating and cooling have their own terms, and every kind of hour its own numbers. There is no trend, no month and
no holiday in the fit: whatever repeats every year by the calendar is carried by the temperature it travels with.

**Dew point, tried and adopted (session 129).** The rule was set before the numbers were read: dew point goes into the fit for every grid when the mean of the
seven grids' error on an hour left out is lower with it and no grid's rises by more than 0.05 points; otherwise for none. Mean absolute error, percent:

| Grid | An hour left out, without | With dew point | A day left out, without | With dew point |
|---|---|---|---|---|
| ERCOT | 4.19 | 4.12 | 3.78 | 3.70 |
| CAISO | 6.99 | 6.97 | 6.18 | 6.13 |
| PJM | 3.77 | 3.61 | 3.29 | 3.14 |
| MISO | 3.84 | 3.83 | 3.44 | 3.42 |
| SPP | 3.74 | 3.72 | 3.22 | 3.21 |
| NYISO | 4.17 | 3.94 | 3.75 | 3.51 |
| ISO-NE | 5.54 | 5.10 | 4.62 | 4.17 |
| Mean of the seven | 4.61 | 4.47 | 4.04 | 3.90 |

It helps most where summers are humid (ISO-NE and NYISO) and not at all in MISO. It is a modest gain: the fit's error is still set mostly by what it
leaves out (sunshine, the calendar), not by humidity.

Texas's hours of 15 to 19 February 2021 are left out of the fit (120 hours): ERCOT was shedding load, so the meter did not record what
customers would have used. The dates are a stated choice of the method. Those hours stay in the year's own figures.


**The fit's error, by grid** (the fit as used). Mean absolute error, percent of the hour's (or the day's) demand. "Left out": each of 2019, 2020 and 2021 predicted by a fit
made on the other two. The last column is the same 48 lines with heating and cooling degrees only, to show what the squares and the day before buy.

| Grid | Hours in the fit | On an hour left out | On a day left out | On the hours it was fitted to | 2019 left out | 2020 | 2021 | With HD and CD only |
|---|---|---|---|---|---|---|---|---|
| ERCOT | 26,086 | 4.12 | 3.70 | 3.38 | 3.69 | 3.59 | 5.10 | 4.96 |
| CAISO | 26,232 | 6.97 | 6.13 | 6.46 | 7.42 | 7.02 | 6.47 | 7.63 |
| PJM | 26,285 | 3.61 | 3.14 | 3.30 | 3.13 | 4.36 | 3.34 | 4.82 |
| MISO | 26,286 | 3.83 | 3.42 | 3.46 | 3.72 | 4.55 | 3.21 | 4.64 |
| SPP | 26,287 | 3.72 | 3.21 | 3.52 | 3.78 | 4.20 | 3.18 | 4.63 |
| NYISO | 26,290 | 3.94 | 3.51 | 3.57 | 4.05 | 4.48 | 3.28 | 5.05 |
| ISO-NE | 26,122 | 5.10 | 4.17 | 4.81 | 4.70 | 5.90 | 4.70 | 6.62 |

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

### New England under two rules, for a ruling

The second rule: a grid's hour is held when at least 4 of its five stations hold it, each figure the weighted mean over the stations held, their
weights restated to add to one. New England then holds 67,739 of 67,862 hours, 328 of them on four stations, against 67,411 under the rule of five.
The tables use the rule of five. Growth not explained by temperature, percent, with its uncertainty:

**The year's energy**

| Year | All five | Give or take | Four of five | Give or take |
|---|---|---|---|---|
| 2022 | -0.1 | 1.7 | -0.0 | 1.7 |
| 2023 | -2.6 (a finding) | 1.7 | -2.6 (a finding) | 1.7 |
| 2024 | -1.7 (a finding) | 1.7 | -1.7 | 1.7 |
| 2025 | -1.1 | 1.7 | -1.0 | 1.7 |
| 2026 | -0.4 | 2.0 | -0.5 | 2.0 |

**The summer peak**

| Year | All five | Give or take | Four of five | Give or take |
|---|---|---|---|---|
| 2022 | -0.0 | 7.1 | -0.1 | 7.2 |
| 2023 | +3.5 | 7.1 | +3.5 | 7.2 |
| 2024 | +2.1 | 7.1 | +2.1 | 7.2 |
| 2025 | not held |  | +0.3 | 7.2 |
| 2026 | -1.6 | 7.1 | -1.4 | 7.2 |

**The winter peak**

| Year | All five | Give or take | Four of five | Give or take |
|---|---|---|---|---|
| 2022 | -3.0 | 5.1 | -3.0 | 5.1 |
| 2023 | -7.4 (a finding) | 5.1 | -7.4 (a finding) | 5.1 |
| 2024 | -0.9 | 5.1 | -0.8 | 5.1 |
| 2025 | +2.9 | 5.1 | +2.9 | 5.1 |
| 2026 | not held |  | +2.9 | 5.1 |

**The overnight minimum**

| Year | All five | Give or take | Four of five | Give or take |
|---|---|---|---|---|
| 2022 | +2.0 (a finding) | 1.5 | +2.0 (a finding) | 1.5 |
| 2023 | +0.4 | 1.5 | +0.3 | 1.5 |
| 2024 | +3.1 (a finding) | 1.5 | +3.0 (a finding) | 1.5 |
| 2025 | not held |  | +3.6 (a finding) | 1.5 |
| 2026 | not held |  | +6.4 (a finding) | 1.7 |

Where both rules hold a figure, the two differ by at most 0.21 points (the summer peak, 2026). The second rule holds 4 figures the first does not: the summer peak 2025; the overnight minimum 2025; the winter peak 2026; the overnight minimum 2026.
What the second rule costs: in an hour held on four stations the grid's weather is that of four cities, so the figure's meaning shifts a little with which station is missing.

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
| ERCOT | -2.5 | -1.4 | +4.0 | 4.0 |
| CAISO | -2.1 | -0.6 | +3.2 | 3.2 |
| PJM | +1.0 | -2.5 | +1.4 | 2.5 |
| MISO | +2.3 | -2.6 | +0.2 | 2.6 |
| SPP | +0.4 | -1.5 | +1.0 | 1.5 |
| NYISO | +3.0 | -2.6 | -0.5 | 3.0 |
| ISO-NE | +1.7 | -1.0 | -0.9 | 1.7 |

**The summer peak**

| Grid | 2019 left out | 2020 left out | 2021 left out | The uncertainty used |
|---|---|---|---|---|
| ERCOT | -0.9 | -4.8 | +6.2 | 6.2 |
| CAISO | -0.8 | -10.0 | +12.7 | 12.7 |
| PJM | -1.3 | -2.7 | +3.5 | 3.6 |
| MISO | -0.9 | -0.3 | -0.7 | 3.8 |
| SPP | -3.1 | +2.6 | -0.1 | 3.7 |
| NYISO | -3.6 | +2.6 | -2.4 | 3.9 |
| ISO-NE | -7.1 | +4.2 | -0.6 | 7.1 |

**The winter peak**

| Grid | 2019 left out | 2020 left out | 2021 left out | The uncertainty used |
|---|---|---|---|---|
| ERCOT | not held | +20.1 | -37.8 | 37.8 |
| CAISO | not held | -4.8 | +3.2 | 7.0 |
| PJM | not held | +6.3 | -7.5 | 7.5 |
| MISO | not held | -5.4 | +5.1 | 5.4 |
| SPP | not held | +3.3 | -8.4 | 8.4 |
| NYISO | not held | +3.5 | -3.5 | 3.9 |
| ISO-NE | not held | +4.3 | -4.7 | 5.1 |

**The overnight minimum**

| Grid | 2019 left out | 2020 left out | 2021 left out | The uncertainty used |
|---|---|---|---|---|
| ERCOT | -3.0 | -1.5 | +4.7 | 4.7 |
| CAISO | -3.4 | +0.3 | +4.5 | 4.5 |
| PJM | +0.1 | -2.2 | +2.0 | 2.2 |
| MISO | +1.2 | -2.4 | +1.0 | 2.4 |
| SPP | +0.7 | -2.3 | +1.6 | 2.3 |
| NYISO | +1.1 | -1.8 | +0.6 | 1.8 |
| ISO-NE | +0.8 | -1.5 | +0.4 | 1.5 |

Read for the year's energy: SPP comes back within 1.5 points in each of the three years and ISO-NE within 1.7;
2020 comes back below zero in all seven grids (-2.6 to -0.6), the year of the lockdowns; Texas's 2021 comes back at +4.0,
which reads as growth already under way inside the fit's own years. The base of 2019 to 2021 is not a still one, least of all for Texas, and a later figure is growth on top of it.

Texas's winter peak is the method's plain failure: the winter left out that holds February 2021 misses by 38 points, because the grid was shedding load at the
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
| the eight weeks before the hours were dated right | 2025-10-07 | 8.35 | 7.00 | 6.88 | +2.92 |
| the eight weeks from the change in EIA's generation series | 2025-12-16 | 9.41 | 8.67 | 8.79 | +6.36 |
| the eight weeks before the hours were dated right, a year earlier | 2024-10-07 | 7.81 | 6.97 | 7.13 | +4.76 |
| the eight weeks from the change in EIA's generation series, a year earlier | 2024-12-16 | 7.56 | 7.12 | 7.94 | +6.16 |

In 3 of the 4 windows the error is smallest as read; in the other the smallest is 0.12 points under it, with demand an hour late, against 1.35 points worse an hour early.
That is too little to read as a misdated hour, and too coarse to rule one out: demand follows temperature with a lag, so moving it later costs the fit
little. The last column rises from autumn to winter in both years. What this check can say is that nothing as large as an hour's shift shows at the change;
it cannot see a step of a point or two in the level.

## What moved from session 126's figures

Session 126 built these figures on stated weights and without dew point. With the Census Bureau's weights and dew point in the fit, of 136 figures both builds hold:

- the year's energy not explained moves by at most 1.03 points (CAISO, 2026: +6.0 to +5.0);
- any figure by at most 4.69 points (ISO-NE, 2026, the summer peak: -6.3 to -1.6);
- 4 figures change their reading:

| Grid | Year | Figure | Session 126 | Now | Give or take, now | Reading |
|---|---|---|---|---|---|---|
| CAISO | 2025 | the overnight minimum | +4.4 | +4.4 | 4.5 | no longer a finding |
| CAISO | 2026 | the overnight minimum | +4.9 | +4.6 | 4.9 | no longer a finding |
| PJM | 2023 | the summer peak | -4.3 | -4.4 | 3.6 | now a finding |
| ISO-NE | 2023 | the summer peak | +6.9 | +3.5 | 7.1 | no longer a finding |

## What is not in it

- A cause for the remainder (above).
- Wind, cloud and sunlight. Dew point is in the fit since session 129.
- Weather the fit never saw: a peak beyond every hour of 2019 to 2021 is marked and is not a finding.
- A still base: 2019 to 2021 holds the lockdowns of 2020 and, in Texas, growth already under way.
- The parts of a grid away from its five largest cities.
- Demand served behind the meter.

## The stations' hours as a table

`noaa_station_weather_hourly` (session 129) holds every station's measured temperature and dew point by the hour, in degrees Fahrenheit to two
decimals (NOAA's tenth of a degree Celsius turns back from it exactly). Measured values only: an hour NOAA holds no value for has no row, and
no interpolated value is written. With it the grid tables can be rebuilt with other weights, or another rule, on a machine that never held
NOAA's files: `python warehouse/connectors/noaa_grid_weather.py --from-table`.

