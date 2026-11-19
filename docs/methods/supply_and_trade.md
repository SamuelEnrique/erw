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

Held since session 136 for the five operators that publish it openly, each from the operator's own report, by its own connector (`warehouse/connectors/<iso>_dam_cleared.py`), in the tables `ercot_dam_cleared_energy`, `caiso_dam_cleared_energy`, `nyiso_dam_cleared_energy`, `isone_dam_cleared_energy` and `spp_dam_cleared_energy`. MISO's row reads "paused while terms are reviewed" and PJM's "licensed source needed": neither operator is asked.

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

### The table whose five-year columns are all "not held" (session 247)

On the page's file of 10 October 2026 this is the one table of the nine in which a whole column is empty: "The five-year average" and "Change against the five-year average change" read "not held yet" in all eight rows, and "A year ago" in five. Every other table holds every column for most of its rows (`runs/session247/supply_cells.out` on the data machine). Each row, and what would fill it:

| Row | A year ago | The five years | What the publisher offers | Filled tonight? |
|---|---|---|---|---|
| ERCOT | not held (from 23 September 2026) | not held | ERCOT lists 31 days of this report and no more; it publishes no yearly history of it | No: there is nothing older to ask for. The row fills by itself: a year in September 2027, five years in 2031 |
| CAISO | held (from September 2025) | not held | CAISO's system serves about 39 months back | No: a pull would reach mid 2023, three years, and the five-year columns need all five. About 26 requests would lengthen the chart and fill neither column |
| NYISO | held | not held | not looked at tonight: this chain may not ask NYISO | No. Whether its archive reaches five years back is for the session that may ask |
| ISO-NE | not held (from September 2026) | not held | its page puts a CAPTCHA on past dates (above); the table is internal | No: this chain may not ask ISO-NE, and its connector never walks back |
| SPP, SPP West | SPP held; SPP West not held (the area exists in the file from 1 April 2026) | not held | not looked at tonight: this chain may not ask SPP | No. SPP West cannot have a year before April 2027 |
| MISO | not held | not held | paused: its terms forbid automated access | No |
| PJM | not held | not held | licensed | No |

- **So nothing was pulled for this table.** For the two operators the chain may ask, the publisher's own window is shorter than the column needs.
- **The other rows that read "not held" somewhere,** as the page's file states them: five LNG points of exit without all five years in EIA's table (Plaquemines, Freeport, Calcasieu Pass, Golden Pass, Altamira; Golden Pass also has no year before); four fuel-burn rows whose fuel EIA's hourly file leaves blank in the latest weeks (coal in ISO-NE; oil in CAISO, ISO-NE and MISO); PJM's three fuel-burn rows and the seven grids' gas total, which hold a year and not all five; weekly gas production (EIA publishes none of its own) and ICE's Brent positioning (licensed). None was pulled for: the first three kinds are what the publisher's file holds, and the last two are another publisher's, under a license.

### The operators' terms, as read on 6 October 2026

- **ERCOT**, terms of use, item 5: "Notwithstanding the foregoing, raw data provided in public portions of this website may be used, reproduced, and redistributed in compilations, charts, and analyses without maintaining such notices." Item 6: "Use of this website in a manner that negatively affects the performance of this website or other ERCOT systems is prohibited." (https://www.ercot.com/help/terms). Public.
- **CAISO**, terms of use: its materials "may be used by you provided that you keep intact all copyright, trademark and other proprietary notices and that you credit the California ISO when using such materials and/or information." Of its API: "Users are prohibited from using the CAISO API in a manner that adversely impacts the performance of CAISO's systems". (https://www.caiso.com/privacy-terms-of-use). Public, with credit.
- **NYISO**, legal notice: "Access to this Web site does not confer any license or ownership interest in either the form or content of the Web site ... Downloading, republishing, retransmitting, reproducing, or other use of any image or video on this website as a stand-alone file is strictly prohibited". (https://www.nyiso.com/legal-notice). It grants no license and its prohibition names images and video, not data: public with a caution, the ERW's standing reading since session 65. A person can rule otherwise.
- **ISO-NE**, legal notice: "You are also hereby put on notice that the Content is protected by copyright under United States laws. Any duplication of the Content or non-personal use may violate copyright, trademark, and other laws." (https://www.iso-ne.com/legal-privacy). **Internal**, the ERW's standing reading since session 65: the table is in no public dataset and no download. Its report answers a plain request with HTTP 403 and answers a session that has opened one of ISO Express's pages (an anonymous cookie, no account); ISO Express's own page puts a CAPTCHA on its search of past dates. The connector therefore asks for the last days only and never walks back through the years.
- **SPP**, terms and conditions: "Permission is implicitly granted to copy and distribute (via computer network or printed form) in whole or in part (with appropriate citation) EXCEPT when such materials will be used, in whole or in part, within a commercial publication ... Any commercial use of these materials requires prior, express written authorization". (https://www.spp.org/terms-conditions/). Public, with citation.

## The replication (session 7013, chain 301)

`replication/supply/replicate.py` rebuilds each row's series from its table by this note alone (the series ids, the
million barrels, the gas trade in Bcf a day with the other points of exit as the total less the terminals named, the
Outlook's months to three before the build, managed money's net, the cleared weeks of seven whole local days ending
Friday) and recomputes the three comparisons, the change and its surprise, and the spark: 5,125 of 5,125 equal on the
file rebuilt on 16 November 2026 (76 rows). The fuel burn's 16 rows are counted apart: they are derived from EIA-930's
hourly generation workbooks held in the data machine's raw store, not from a table. A series whose five years of changes
are not all held still carries its change, never "outside". `replicate.do` rebuilds five figures of the week of 6
November 2026 in Stata, its expected values at its top.

The file was three weeks behind on 16 November (built 24 October): the page is built on Saturdays, and the Saturdays of
31 October, 7 and 14 November fell in the days the daily run's commits were refused. Session 7013 ran the refresh by
hand (`PYTHON=<the repository's interpreter> bash warehouse/refresh_supply.sh` under the data lock).

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

## The page as it stands (session 333, 20 October 2026)

- **The bands** (storage and stocks through the year against the five years before) are drawn in SVG through the
  site's shared chart set since session 317 (`BandChart`); no value moved.
- **Every number** is the file's (`site/data/supply.json`), and `check-supply` reads them against it.
- **Downloads** (session 333): at the foot of the page, the five tables the file's sources name (`cftc_cot_positions`,
  `eia_basin_production_monthly`, `eia_gas_storage_weekly`, `eia_gas_trade_monthly`, `eia_petroleum_supply_weekly`),
  each as the live set's CSV with a Python and a Stata reader of that CSV, or named with its place on Redivis where the
  live set does not hold it (session 328's shared line). The list is read from the file's sources, so it follows the
  file. The grid operators' day-ahead load rows the file also reads are not an ERW table of their own. **On 20 October
  2026 none of the five is in the site's live catalogue** (all five are public in `warehouse/metadata/coverage.csv`), so
  the line says the tables are not in the site's live set and names Redivis; once they are loaded, it offers them.

## The whole country (session 8430, 19 November 2026)

The page has a section "The whole country", under the last of its tables and above the decisions block. Nothing else
on the page changed: outside what was added, the page is byte for byte what it was at every address it answered
before (`site/scripts/test-supply-pin.mjs`: 103 addresses, drawn on a copy of the page's two input files kept beside
the pin, with the clock standing still, so a weekly rebuild of `site/data/supply.json` does not move the pin).

- **What it reads.** The data machine's files of the whole country under `site/data/regions/`, written from EIA's Form
  EIA-930 in the form of the contract [`docs/state/page_files_regions.md`](../state/page_files_regions.md):
  `trade/<region>.json` (its section 5), `trade_matrix.json` (section 7), `mix/<region>.json` (section 4) and, for the
  names of the balancing authorities only, `index.json` (section 2). The regions are EIA's thirteen of the lower 48
  (California, Carolinas, Central, Florida, Mid-Atlantic, Midwest, New England, Northwest, New York, Southeast,
  Southwest, Tennessee, Texas), with Canada and Mexico as neighbours. Six of the regions were on no page before: the
  Southeast, Florida, the Carolinas, Tennessee, the Northwest and the Southwest (none of the seven grids is in them).
- **Until a file is on the site** its view reads "not built yet" and draws no figure; with none of the files there the
  whole section reads so. A file that cannot be read as JSON is treated the same way. No value is filled in.
- **Net imports by month and by neighbour** (one region, or two side by side). A chart of the region's net imports by
  month since July 2018, from all its neighbours and from each (GWh; above zero the region imported). For the chosen
  year, a table with a row a neighbour: the region's own report, the neighbour's report of the same flow, the gap (the
  own report less the neighbour's, over the hours both reported, as the file gives it), the gap in percent and the
  months held; and a table of the year month by month, by the own report, whose hover gives the neighbour's report,
  the gap and the hours each side held. A year's figure is the sum of the months the file holds; a month that is not
  held is left out and counted beside the sum ("9 of 12"), never filled or scaled. The total from all neighbours is the
  file's own monthly total, which the file leaves null when any neighbour holds fewer than half the month's hours.
- **Who trades with whom.** For the chosen year, each pair of regions from the matrix file: which sent and which
  received (the file's `direction`; the sign of its mean where it names none), each side's report turned to that
  direction (a report below zero says that side counted the year's net flow the other way), the file's mean (over the
  hours both sides reported, the mean of the two; the one side's report where the other reported no hour), the
  file's gap (the sender's report less the receiver's, over the hours both reported) and the gap in percent. A side
  whose report the file does not hold reads "not held yet", and so do the gap and its percent. The pairs stand in EIA's order of codes; none is ranked against another. In two folds: the same for
  each pair of balancing authorities, and each authority's partners by gross and by net exchange, in the file's order
  (`ba_trade_partners`).
- **The gap that is called large.** The gap in percent is the gap over the mean size of the two reports (the mean of
  their absolute values); for a year with a neighbour it runs over the months that hold both reports and the gap. A
  gap of 10 percent or more is marked (a dotted line under the figure) and said in words on hover: who reported what,
  the gap, its percent, the rule, its default and its source. **Default: 10 percent, the page's own choice (session
  8430); no publisher's threshold stands behind it.** It waits for the owner's ruling.
- **The generation mix by month.** The tables above the section draw no generation mix of their own: they link each of
  the seven grids' Mix view on the Grid page, which this session did not touch. So a region's mix stands here in the
  plainest form: a chart of each source's share of net generation by month over every month the file holds, and a
  table of the chosen year's months with each source's share as the file writes it, the net generation and the days
  held. The year's row is each source's energy over the year's held months as a percent of the net generation of
  those same months. The file's hourly profiles and its newest 35 days by hour are not drawn here.
- **The choices of the address:** `region` (Region A), `b` (Region B, or `none`) and `year`; the page's own choices
  (`g`, `s`) are carried beside them. **Defaults:** Region A California and Region B the Carolinas, the first two of
  EIA's thirteen in EIA's own order of codes; the year the last calendar year that had ended when the files were built
  (the newest they can hold whole), or the newest year held when they hold no such year. The charts run over every
  month whatever the year. The page's own choices, session 8430; said on hover.
- **What it does not do.** No region is summed against another; no ledger of regions that gave and took is formed and
  no region is ranked; no share of anything covered by imports is estimated. The matrix file also holds each
  balancing authority's net imports as a share of its demand; that figure is not drawn until the owner rules (a switch
  in `site/components/supply/Country.tsx`, `SHOWN.importShare`).
- **Licenses.** Each file's own `license` line and the status of each table it names
  (`site/data/license_status.json`) are read. EIA's Form EIA-930 is public domain and the contract gives every file as
  public, so every region is drawn. A file that is not public, or a region put on hold (`REGIONS_HELD` in the same
  component), is drawn with blank cells and "license needed" on hover, and no chart.
- **Where the code is:** `site/lib/countrytrade.ts` (the types, the readers and the sums),
  `site/components/supply/Country.tsx` (the views), `site/scripts/test-supply-regions.mjs` and
  `site/scripts/regions-fixture-trade.mjs` (the test and its fixtures, whose values are made by a rule and are not
  data), `tests/test_session8430_supply_regions.py`.
- **The rules above, made exact (session 8460).** The replication below was written from this section and the
  contract; where the lines above did not settle a figure, the rule is written here, as the page applies it.
  - **Units and digits.** Energy is the file's MWh shown as GWh to one decimal; a percent is shown to one decimal. A
    region's own report, a neighbour's report, a gap and a total carry a plus sign above zero; a pair's two reports
    and its mean carry none.
  - **A year with a neighbour.** The own report, the neighbour's report and the gap are each the sum of that array
    over the months of the year in which that array holds a value. "Months held" is the count of the year's months
    that hold the own report, of the year's months in the file. The percent is taken on three sums over the months
    that hold all three arrays: the size of the summed gap over the mean of the sizes of the two summed reports. It
    is not drawn when no month holds all three or when both summed reports are zero.
  - **A month with a neighbour.** The month's own report is on the face. Its hover gives the neighbour's report and
    the gap as the file holds them and the percent on the month's own three values; the hours on the hover are the
    file's own counts.
  - **Large.** A gap is large when its percent before rounding is 10 or more, so a percent shown as 10.0 can stand
    without the mark (9.95 to 9.99). In the year's table and in the pairs the mark stands on the percent; in the
    month table it stands on the month's own report.
  - **A pair.** The direction is the file's `direction` when it reads `a_to_b` or `b_to_a`; else the sign of the
    file's mean; with a mean of zero or none there is no direction. With a direction, the sender's report, the
    receiver's report and the mean are the file's values turned to it (times minus one when power ran from the second
    to the first), so a mean is not below zero unless the file's direction and its mean disagree. The gap is the
    file's value unturned: the first side's report less the second's is also the sender's less the receiver's when
    power ran the other way. With no direction the pair stands in the file's order, the first side's report first,
    and the second column reads "no net flow" at a mean of zero. The percent is the size of the file's gap over the
    mean of the sizes of the two reports, and needs all three and two reports that are not both zero.
  - **The counts in the two folds.** The pairs of balancing authorities the file holds for the year, and the
    authorities for which it lists partners in the year; zero in a year the matrix does not hold.
  - **The mix.** A month's share is the file's `<source>_share_pct`, its net generation the file's
    `net_generation_mwh`, its days the file's `days_held` of `days_in_month`. The year's row counts the year's months
    in the file; a source's share of the year is its energy over the months that hold both it and the net generation,
    over the net generation of those same months; the year's net generation is the sum over the months that hold it.
    A mix month is the region's own local month (the file's `tz`); a trade month is EIA's Eastern month.
  - **The year drawn first.** Of the files read for the two regions drawn first and the matrix: the last calendar
    year that had ended when the newest of them was built, when they hold it; else the newest year they hold before
    it; else the newest year they hold.
- **Five hovers completed (session 8460).** No word on the section's face and no figure moved
  (`site/scripts/test-supply-regions-8460.mjs`, 20 of 20; session 8430's two tests hold). A flow with Canada or
  Mexico: the cells that read "not held yet" for the other side's report, the gap and the percent now say why on
  hover (no balancing authority of Canada or Mexico files Form EIA-930). A balancing authority the index of the
  regions does not list says so, where its hover said its name would come with the index. The mix table's net
  generation says whose local month a month is and that the net imports run by EIA's Eastern months. The hover beside
  the mix's heading says why a month's shares need not add up to 100 (the file holds an hour when its sources add up
  to its net generation within 5 percent). The head of the balancing authorities' pairs says what a balancing
  authority is.
- **The replication (session 8460).** `replication/supply/replicate_regions.py`, written from this section and the
  contract alone and not from the page's code, recomputes every figure the section prints from the trade, matrix and
  mix files and sets it beside the figure the site's own code draws (`site/scripts/supply-regions-figures.mjs`
  draws the section once for each region and each year and writes what it prints): every checked figure on the
  face, the month hover's neighbour's report, gap and percent, the counts of months and days, which figures carry
  the mark of a large gap, which side each pair's row says sent and which received, and the regions and the year
  drawn first. A figure passes within half the last digit shown; a figure the rule gives that the page does not show
  fails, and so does one the page shows that the rule does not give. Not compared: the hours on the hovers (the
  file's own counts) and the charts' boxes and tables, which a browser draws from the same arrays as the month
  tables. Run from `site/`: `node --import ./scripts/tsx-register.mjs scripts/supply-regions-figures.mjs
  <figures.json>`, then `python replication/supply/replicate_regions.py --figures <figures.json>`; with
  `--same-flow` it also sets a pair's year in the matrix beside the same year's months in each region's trade file
  (the same flow in two files; a difference there is a matter of the files). While no file is on the site it says so
  and compares nothing. On the test's fixtures: 33,132 of 33,132 over 27 files
  (`tests/test_session8460_supply_regions_replication.py`). The count on the real files, the Stata do-file's five
  headline figures and the cross-check against published figures are written when the files land
  (`docs/reviews/supply-regions-read-2026-11-19.md` says what waits).

## The cross-checks (session 7018, chain 301)

EIA's weekly estimate of US crude oil production (the page's weekly production row, `WCRFPUS2`), averaged over the report weeks ending in each month, beside EIA's Petroleum Supply Monthly for the same month (its monthly survey, `eia_crude_production_state_monthly`, `MCRFPUS`), thousand barrels a day:

| Month | Weekly estimate, mean (weeks) | Petroleum Supply Monthly | Difference |
|---|---|---|---|
| February 2026 | 13,711.5 (4) | 13,711 | 0.5 (0.00 percent) |
| March 2026 | 13,665.0 (4) | 13,726 | -61.0 (-0.44 percent) |
| April 2026 | 13,590.8 (4) | 13,981 | -390.2 (-2.79 percent) |
| May 2026 | 13,681.4 (5) | 13,811 | -129.6 (-0.94 percent) |
| June 2026 | 13,808.5 (4) | 13,844 | -35.5 (-0.26 percent) |
| July 2026 | 13,823.8 (5) | 13,948 | -124.2 (-0.89 percent) |

EIA rounds its weekly estimate and revises it in its monthly data (the note's "Notes on the series"); the weekly row ran below the survey in every month from March, by 0.3 to 2.8 percent. A reader who wants the survey's figure takes the monthly. The weekly stocks, storage and trade rows are EIA's own figures and the replication recomputes every figure of the page from them (5,125 of 5,125); EIA's headline pages for a week were read on 16 November 2026 and carried another week's text than the tables', so they are not set beside them here.

## The decisions on the page (session 7018, chain 301)

The page draws these at its foot (`site/lib/decisions.ts`, `SUPPLY_DECISIONS`), each choice's default and source on hover:

1. Every series is set against three values, each actually held: the period before, the same time last year and the five-year average; nothing is filled or estimated, and a comparison not held reads "not held". **Default:** The week or month before, last year, and the five-year average. **Source:** docs/methods/supply_and_trade.md, "The three comparisons". (session 134)
2. A weekly year is 52 weeks, so a comparison is always the same weekday: last year is the value 364 days back or the nearest within 3 days, and over five years the date drifts five or six days from the calendar's. **Default:** 52 weeks back, or the nearest value within 3 days. **Source:** docs/methods/supply_and_trade.md, "The three comparisons"; EIA's own report weeks follow the same idea. (session 134)
3. The five-year average is the mean of the values 52, 104, 156, 208 and 260 weeks back (the same month of the five years before), given only when all five are held, with their lowest and highest beside it. **Default:** All five years held, or no average. **Source:** docs/methods/supply_and_trade.md, "The three comparisons". (session 134)
4. The surprise is the period's change less the mean of the same change in the five years before, marked outside when beyond their lowest or highest; the page never says "against expectations", since no analysts' consensus is held. **Default:** Against the five-year average change, never a consensus. **Source:** docs/methods/supply_and_trade.md, "The surprise": the analysts' polls are licensed. (session 134)
5. Tighter or looser is written only where the direction has a reading: more in storage, more production or more imports is looser, more exports or more fuel burned is tighter; refinery runs, the reserve and positioning carry none. **Default:** A reading only for the series whose direction has one. **Source:** docs/methods/supply_and_trade.md, "The three comparisons". (session 134)
6. Stocks are shown in million barrels and natural gas trade in Bcf a day (the month's volume over its days), so months of different length compare; commercial crude excludes the Strategic Petroleum Reserve. **Default:** Million barrels; Bcf a day; commercial crude without the reserve. **Source:** EIA's Weekly Petroleum Status Report and Natural Gas Monthly, converted as docs/methods/supply_and_trade.md, "Notes on the series", says. (session 134)
7. An LNG terminal is listed by name when it shipped at least 5,000 MMcf in a month of the last twelve; every other point of exit is one row, the total less the terminals named. **Default:** 5,000 MMcf in a month of the last twelve. **Source:** EIA's natural gas exports by point of exit; docs/methods/supply_and_trade.md, "Notes on the series". (session 134)
8. Fuel burned for power is derived, not reported: each grid's hourly gas, coal and oil generation, summed over whole local days, times a stated fleet heat rate (natural gas 7.6 MMBtu per MWh), so a grid's real fleet differs. **Default:** Stated fleet heat rates; whole local days only. **Source:** EIA-930's hourly generation by fuel; EIA's Electric Power Annual, Table 8.1, for the heat rates. (session 134)
9. Positioning is the CFTC's managed money, futures only, and its net; Brent is the NYMEX contract the CFTC reports, not ICE's, whose terms forbid copying its own report. **Default:** Managed money's net, futures only; NYMEX Brent. **Source:** CFTC, Disaggregated Commitments of Traders; ICE Futures Europe's terms of use. (session 134)
10. Day-ahead energy cleared is each operator's own figure, as a week's mean of seven whole local days ending Friday, a day counting only when every hour of it is held; the operators define it differently and are not summed. **Default:** Seven whole local days ending Friday; never summed across operators. **Source:** ERCOT, CAISO, NYISO, ISO-NE and SPP day-ahead market reports, as docs/methods/supply_and_trade.md, "Day-ahead energy cleared", lists them. (session 136)
11. Weekly natural gas production is not shown: EIA publishes none of its own, and the weekly supply figures in its Natural Gas Weekly Update are S&P Global's, so the row reads "licensed source needed". **Default:** The row greyed, licensed source needed. **Source:** EIA's Natural Gas Weekly Update credits S&P Global for its weekly supply figures. (session 134)

## What waits for the owner (session 7018)

- Weekly natural gas production (S&P Global's, a license) and an analysts' consensus for the surprise (licensed polls).
- ICE's Brent positioning (ICE's terms).

## Sign-off

- Signed off by:
- Date:
- Items of the section above ruled, and how:
