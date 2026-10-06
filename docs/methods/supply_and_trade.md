# Supply and trade: method

Built in session 134 for the page `/supply` ("Supply and trade", under the Prices menu, in review). The reader is a trader in oil, gas and power. The page answers one question: **is the market tighter or looser than last week, last year and normal for the season.**

The page face carries no method, by the owner's rule: a figure that is missing is a short placeholder with its reason on hover, and everything about method, gaps and sources is here.

## Where the page's numbers come from

The page reads the site's own file, `site/data/supply.json`, written by `warehouse/derived/supply_page.py` from tables in `warehouse/output`. The builder makes no request.

| Group on the page | Table | Publisher, report | Step | From |
|---|---|---|---|---|
| Natural gas in storage | `eia_gas_storage_weekly` | EIA, Weekly Natural Gas Storage Report | weekly | 2010 |
| Crude and product stocks; weekly crude production; refining; weekly trade | `eia_petroleum_supply_weekly` | EIA, Weekly Petroleum Status Report | weekly | 2010 |
| Production by region | `eia_basin_production_monthly` | EIA, Short-Term Energy Outlook, history only | monthly | 2015 |
| Natural gas trade | `eia_gas_trade_monthly` | EIA, natural gas imports and exports by point of entry and exit | monthly | 2015 |
| Managed money positioning | `cftc_cot_positions` | CFTC, Commitments of Traders, Disaggregated report, futures only | weekly | 2015 |
| Fuel burned for power | derived (below) | EIA-930 hourly generation by source | weekly | 2019 |

## The three comparisons

Every series is set against three values, each one actually held. Nothing is filled or estimated.

| Comparison | Weekly series | Monthly series |
|---|---|---|
| The period before | the value 7 days before the latest | the month before |
| Last year | the value 364 days before the latest (the same weekday, 52 weeks back), or the nearest within 3 days | the same month a year before |
| The five-year average | the mean of the values 52, 104, 156, 208 and 260 weeks before the latest, given only when all five are held; with their lowest and highest | the same month of the five years before |

- **A year is 52 weeks**, so a weekly comparison is always the same weekday. Over five years this drifts five or six days from the calendar date. EIA's own five-year average in its storage report is by report week, which is the same idea; figures can differ from EIA's by a few units where EIA has revised or reclassified a week.
- **Tighter or looser** is written only where the direction has a reading: more in storage, more production or more imports is looser; more exports or more fuel burned is tighter. Refinery runs, utilization, the Strategic Petroleum Reserve and positioning carry no reading.

## The surprise

A desk reads a weekly report for its surprise, not its level. With no analysts' consensus held (those polls are licensed), the page uses the open stand-in:

> the period's change (latest less the period before), less the mean of the same change in the five years before.

It is marked "outside the five years" when the change is below the lowest or above the highest of those five changes. The page says "against the five-year average change" and never "against expectations". The list at the top of the page holds the series whose newest change is outside, ordered by how far the change stands from the five-year average change, measured in the width of the five years' changes.

## The seasonal band

For each date of the current year and on to its end: the value this year where held, the value 52 weeks before, and the mean, lowest and highest of the five years before (drawn only where all five are held). The band charts shown by default are gas storage (the Lower 48 and its five regions) and commercial crude, Cushing, gasoline and distillate stocks. Any row opens its own chart.

## Notes on the series

- **Stocks** are shown in million barrels (EIA's thousand barrels over 1,000). Commercial crude excludes the Strategic Petroleum Reserve; Cushing excludes it too.
- **Weekly crude production** is EIA's weekly estimate, which EIA rounds and later revises in its monthly data.
- **Weekly natural gas production is not held.** EIA publishes no weekly production of its own: the weekly supply figures in its Natural Gas Weekly Update are S&P Global's. The row is greyed, "licensed source needed".
- **Production by region** is the Short-Term Energy Outlook's crude oil production and marketed natural gas production for Appalachia, Bakken, Eagle Ford, Haynesville, Permian and the rest of the Lower 48 (the series that replaced the Drilling Productivity Report). **The Outlook's series run on into EIA's forecast.** Only months up to three months before the month of the run are written: the newest months are EIA's estimates and later ones its forecast, and the lag keeps the forecast out. Built on 6 October 2026, the table ends with July 2026.
- **Natural gas trade** is EIA's monthly volume (MMcf) divided by 1,000 and by the days of the month, shown in Bcf a day so months of different length compare. LNG terminals are listed by name when they shipped at least 5,000 MMcf in a month of the last twelve; every other point of exit (trucked and small-scale) is one row, the total less the terminals named.
- **Refinery utilization and crude runs** are by PADD, as EIA publishes them.

## Fuel burned for power

Derived, not reported. For each of the seven ISO grids: hourly generation from natural gas, coal and oil (EIA-930, the energy mix's held hours: `warehouse/derived/mix_profile.py`, `generation_mix_hourly.md`) is added up by local day when every hour of the day is held, then multiplied by a stated heat rate and divided by a stated heat content.

| Fuel | Heat rate, MMBtu per MWh | Heat content | Unit shown |
|---|---|---|---|
| Natural gas | 7.6 | 1.037 million MMBtu per Bcf | Bcf a day |
| Coal | 10.6 | 19.0 MMBtu per short ton | thousand short tons a day |
| Oil | 11.0 | 5.8 MMBtu per barrel | thousand barrels a day |

- The heat rates are assumptions, about the fleet averages EIA publishes (Electric Power Annual, Table 8.1). A grid's real fleet differs, and a peaking plant burns more per MWh than a combined-cycle plant.
- **A blank hour is never read as zero.** A day counts for a fuel only when every one of its hours names that fuel. Where the hourly file leaves a fuel blank for a grid (oil in California since 16 December 2025 and in MISO since November 2021, coal in New England since late March 2026, oil in New England in about half of its hours), the row is "not held yet" and its hover gives the last whole week held. A zero the file does report (oil in SPP and New York in most hours) is shown as zero. An hour reported below zero (a plant's own use) counts as zero.
- A week is the mean of its seven days, ending Friday as the gas storage week does, and is given only when all seven days are held. "The seven grids together" is the sum when all seven hold the week.
- It is burn in the seven ISO grids, not the whole country's: the utilities outside them are not in it. California from 16 December 2025 is read from CAISO's own supply by fuel, which names no oil.
- MISO's and PJM's generation here is EIA's, which is public; only their own sites' data are paused or licensed.

## Positioning

The CFTC's Disaggregated Commitments of Traders report, futures only: managed money long and short, and the net (long less short, the one figure computed). The date is the report's "as of" Tuesday; the CFTC publishes it on the Friday after. The last column places the latest net position between the lowest and highest of the last 156 weeks.

- **Brent:** the contract the market trades is ICE Futures Europe's, and ICE publishes its own report. ICE's terms forbid copying it (below), so it is not pulled. The Brent row is the NYMEX Brent Last Day contract the CFTC reports, a far smaller market (open interest about an eighth of WTI's). The ICE row is greyed.
- The five-year average is shown for positioning as for every row, but positioning has no season: read the three-year range instead.

## Day-ahead energy cleared

Held since session 136 for the five operators that publish it openly, each from the operator's own report, by its own connector (`warehouse/connectors/<iso>_dam_cleared.py`). MISO's row reads "paused while terms are reviewed" and PJM's "licensed source needed": neither operator is asked.

| Row | The operator's figure | Report | Unit as published | History held |
|---|---|---|---|---|
| ERCOT | energy bought in the day-ahead market, summed over every settlement point of the file | NP4-192-CD, DAM Total Energy Purchased | not named in the file; an amount of energy for the hour, read as MWh | from 23 September 2026 (ERCOT lists 31 days only; the table grows by merging) |
| CAISO | the ISO's total load cleared in the day-ahead market (`ISO_TOT_LOAD_MW`) | OASIS, Market Schedules (ENE_SLRS) | MW over the hour | from September 2025 |
| NYISO | Total Load Scheduled | P-30, Day-Ahead Market Daily Energy Report | MW over the hour | from September 2025 |
| ISO-NE | Day-Ahead Cleared Demand | ISO Express, Day-Ahead Hourly Cleared Demand | MWh | from September 2026 (internal, below) |
| SPP | Total Demand, balancing authority area SPP | Marketplace portal, Market Clearing (DA-MC) | MW over the hour | from September 2025 |
| SPP West | Total Demand, balancing authority area SWPW | the same file | MW over the hour | from 1 April 2026, when SPP's file first names the area |

- **What the row shows:** MWh a day, as the mean of the seven whole days of a week ending on Friday, in the operator's own time. An hour's MW over the hour is its MWh. A day counts only when every hour of the operator's day is held (23, 24 or 25 at a clock change); a week counts only when all seven days do. Nothing is filled. The week, the day sum and ERCOT's sum over settlement points are the only arithmetic.
- **The rows are not the same measure and should not be added or ranked.** Each is the operator's own total. NYISO's Total Load Scheduled and SPP's Total Demand include cleared virtual bids (in SPP's file Total Demand is the sum of its three cleared bid columns, the virtual one among them); ISO-NE's and CAISO's are their cleared demand; ERCOT's is every purchase at every settlement point.
- **SPP has two rows** because its file names two balancing authority areas from 1 April 2026. The first is the area the file held before, so its comparison with a year earlier is like for like.
- **A comparison that cannot be made is a placeholder.** ERCOT has one whole week so far, so its change on the week and on the year are blank until the table has grown; no row has five years.
- **What each run asks for.** ERCOT: the files of the last 8 days, about 23,000 rows each (one row a settlement point and hour) to make 24 hours; a file already kept is not asked for again. CAISO: this month and the last, by half month. NYISO: this month's and last month's files. ISO-NE: the last 14 days, fifteen days a request. SPP: one small file a day, read from the files the reserve-quantity connector already keeps where it has them.

### The operators' terms, as read on 6 October 2026

- **ERCOT**, terms of use, item 5: "Notwithstanding the foregoing, raw data provided in public portions of this website may be used, reproduced, and redistributed in compilations, charts, and analyses without maintaining such notices." Item 6: "Use of this website in a manner that negatively affects the performance of this website or other ERCOT systems is prohibited." (https://www.ercot.com/help/terms). Public.
- **CAISO**, terms of use: its materials "may be used by you provided that you keep intact all copyright, trademark and other proprietary notices and that you credit the California ISO when using such materials and/or information." Of its API: "Users are prohibited from using the CAISO API in a manner that adversely impacts the performance of CAISO's systems". (https://www.caiso.com/privacy-terms-of-use). Public, with credit.
- **NYISO**, legal notice: "Access to this Web site does not confer any license or ownership interest in either the form or content of the Web site ... Downloading, republishing, retransmitting, reproducing, or other use of any image or video on this website as a stand-alone file is strictly prohibited". (https://www.nyiso.com/legal-notice). It grants no license and its prohibition names images and video, not data: public with a caution, the ERW's standing reading since session 65. A person can rule otherwise.
- **ISO-NE**, legal notice: "You are also hereby put on notice that the Content is protected by copyright under United States laws. Any duplication of the Content or non-personal use may violate copyright, trademark, and other laws." (https://www.iso-ne.com/legal-privacy). **Internal**, the ERW's standing reading since session 65: the table is in no public dataset and no download. Its report answers a plain request with HTTP 403 and answers a session that has opened one of ISO Express's pages (an anonymous cookie, no account); ISO Express's own page puts a CAPTCHA on its search of past dates. The connector therefore asks for the last days only and never walks back through the years.
- **SPP**, terms and conditions: "Permission is implicitly granted to copy and distribute (via computer network or printed form) in whole or in part (with appropriate citation) EXCEPT when such materials will be used, in whole or in part, within a commercial publication ... Any commercial use of these materials requires prior, express written authorization". (https://www.spp.org/terms-conditions/). Public, with citation.

## The release calendar

`warehouse/connectors/release_schedule.py` reads EIA's two schedule pages and writes `warehouse/metadata/release_schedule.json`; the builder works out each report's next date.

| Report | Standing release | Exceptions |
|---|---|---|
| EIA Weekly Petroleum Status Report | Wednesday 10:30 a.m. Eastern | EIA's holiday table (eia.gov/petroleum/supply/weekly/schedule.php) |
| EIA Weekly Natural Gas Storage Report | Thursday 10:30 a.m. Eastern | EIA's holiday table (ir.eia.gov/ngs/schedule.html) |
| CFTC Commitments of Traders | Friday 3:30 p.m. Eastern | none read: the CFTC's schedule page lists no dates in its text. A federal holiday in the week can move the release |

The next date is the standing weekday of the week, or the alternate date the publisher lists for that week; once that has passed, the same for the week after. The page works it out on Eastern time each time it is read, from the rule and the alternate dates in its file, so the calendar does not go stale between refreshes. The alternate dates themselves are as EIA listed them when the schedule was last read (6 October 2026): a date EIA changes later is picked up at the next refresh.

## What trader desks and public dashboards show each morning

Read by web search on 6 October 2026, before the page was built:

- **The weekly petroleum report is the most watched weekly dataset in oil**, and prices react to the surprise against expectations, not the level. Cushing stocks and implied demand (product supplied) matter as much as the headline crude number. Refinery utilization is tracked beside them.
- **Gas storage is read three ways:** the weekly change against the five-year average change for the week, the level against a year earlier, and the level against the five-year average, as a surplus or deficit in Bcf.
- **A gas desk's daily balance** sets production against power burn, LNG feedgas, exports to Mexico and other demand, in Bcf a day.
- **Positioning** is read as managed money's net position (long less short) in WTI, Brent, Henry Hub and RBOB, its weekly change and where it sits in its recent range.

What the page took from this: the three comparisons, the surprise as the change against the five-year average change, the seasonal bands, Cushing beside the headline, the gas rows in Bcf a day, and positioning with its range. What it could not take: analysts' consensus, daily pipeline flows (LNG feedgas, Mexico, production by day) and ICE's Brent positioning, which are licensed; and implied demand, which was not among the approved pulls.

Sources read: [EIA, This Week in Petroleum](https://www.eia.gov/petroleum/weekly/crude.php); [EIA, Weekly Petroleum Status Report summary](https://ir.eia.gov/wpsr/wpsrsummary.pdf); [World Oil Monitor, EIA Petroleum Status Report explained](https://worldoilmonitor.com/eia-report); [NRG, daily energy market updates](https://www.nrg.com/en/resources/energy-tools/daily-market-updates); [Natural Gas Intelligence, storage and LNG demand](https://naturalgasintel.com/news/heat-lng-demand-support-natural-gas-futures-despite-ample-supplies/); [RBN Energy, daily posts](https://rbnenergy.com/daily-posts); [CFTC, Commitments of Traders](https://www.cftc.gov/MarketReports/CommitmentsofTraders/index.htm); [Barchart, disaggregated COT net positions](https://www.barchart.com/futures/disaggregated-cot-reports); [Saxo, COT on forex and commodities, week to 29 September 2026](https://home.saxo/en-mena/content/articles/commodities/cot-on-forex-and-commodities---week-to-29-sept-2026-05102026).

## Terms of the sources, quoted

**EIA** (four tables), Copyrights and Reuse:

> U.S. government publications are in the public domain and are not subject to copyright protection. You may use and/or distribute any of our data, files, databases, reports, graphs, charts, and other information products that are on our website or that you receive through our email distribution service.

License: public.

**CFTC** (positioning), Web Policy (cftc.gov/WebPolicy/index.htm, read 6 October 2026):

> Government information at the CFTC website is in the public domain. Public domain information may be freely distributed and copied, but it is requested that in any subsequent use the CFTC be given appropriate acknowledgement.

License: public, with the CFTC acknowledged.

**ICE** (ICE Brent positioning: not pulled), Terms of Use (ice.com/terms-of-use, read 6 October 2026): the site's content may be downloaded "only for your own personal, non-commercial use", and without written permission a user will not

> sell, license, rent, modify, print, collect, copy, reproduce, download, upload, transmit, disclose, distribute, disseminate, publicly display, publicly perform, publish, edit, adapt, electronically extract or scrub, compile or create derivative works from any content or materials

These terms forbid republishing. The session read the header line of one ICE file to see what it held and kept nothing.

## The refresh

`warehouse/refresh_supply.sh`: the two connectors, the schedule, the validator and the builder, each under `warehouse/health.py`. Weekly, written and not scheduled. The fuel burned for power is rebuilt only on a data machine that holds EIA-930's workbooks; elsewhere the builder is run with `--no-burn` and those rows read "working on it".
