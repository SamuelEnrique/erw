# What a datacenter pays

The method of the page `/cost-of-power` ("What a datacenter pays", in review), the first tab of the cost of power
beside "What a generator earns" and "What a battery earns". It answers four questions for a load the reader describes:
what the power will cost, whether it will be there, how clean it is, and how soon it can be had.

The page's face carries no method. Everything about how a figure is made, and what it leaves out, is here.

## The reader's load

| Input | Choices | Default |
|---|---|---|
| Grid | ERCOT, CAISO, NYISO, ISO-NE, SPP. MISO is shown and blank ("paused while terms are reviewed"); PJM is shown and blank ("licensed source needed") | ERCOT |
| Region | every hub and zone of that grid whose public price the warehouse holds; in ERCOT the load zones first, then the trading hubs | the grid's main hub; in ERCOT the North load zone |
| Size | megawatts of load at the meter | 100 |
| How it runs | flat; off in a number of the most expensive hours of each year; off in a share of hours; or a share of each day's energy moved to the day's cheapest hours. A load that is not flat is judged on a rule it could follow (below), with the same load "if perfectly foreseen" beside it | flat |
| How it buys | real time, or day-ahead; and, in the browser only, a contract for a share of the energy at a typed price | real time |
| Power per GPU | kW | 1.3 |
| Facility overhead ratio | facility power over IT power (PUE) | 1.56 |

The inputs live in the page's address, except the contract.

**The two stated defaults.** Power per GPU, 1.3 kW: NVIDIA's DGX H100 system holds 8 H100 GPUs and draws at most
10.2 kW, so about 1.3 kW per GPU with its share of the server; a GPU alone is rated up to 700 W. Overhead ratio, 1.56:
the industry average power usage effectiveness in the Uptime Institute's Global Data Center Survey 2024; large
operators report lower (Google reports 1.09 for its fleet over twelve months). Both are assumptions a reader should
replace with their own.

## Where the prices come from

`warehouse/derived/datacenter_page.py` reads the public hub and zone price tables the warehouse holds and writes the
page's own files under `site/data/datacenter/`. No request is made and no warehouse table is written.

| Table | What it gives |
|---|---|
| `ercot_all_hub_prices_history` | ERCOT's six trading hubs, day-ahead and real time, from 2015 |
| `ercot_zone_prices_history` (session 140) | ERCOT's eight load zones, day-ahead from 2015; real time from 2015 for the four competitive zones (Houston, North, South, West) |
| `iso_zone_prices_history` (session 140) | NYISO's eleven zones, day-ahead and real time by the hour, from 2019; CAISO's ZP26, day-ahead from 26 June 2023 and real time from September 2024; SPP South, day-ahead, the days pulled so far |
| `isone_zone_prices_history` (session 140) | ISO-NE's eight load zones, day-ahead and real time by the hour, 2019 to August 2026. **Internal: not read by this page** |
| `iso_hub_prices_history` | from September 2024: CAISO SP15 and NP15, ISO-NE Internal Hub, NYISO N.Y.C., SPP North |
| `iso_dam_hub_prices`, `iso_rtm_hub_prices` | the daily run's hubs since late August 2026 (CAISO ZP26, SPP South, and the newest days of the others) |
| `isone_dam_zone_prices`, `isone_rtm_zone_prices`, `isone_rtm_zone_prices_hourly` | ISO-NE's eight load zones, since late August 2026 |
| `nyiso_dam_zone_prices`, `nyiso_rtm_zone_prices` | NYISO's eleven zones, since late August 2026 |

The reader is the one `hub_price_comparison` uses (`warehouse/derived/price_compare.py`): a row held in two tables is
read once; a table marked internal in `coverage.csv` is not read; a publisher in
`warehouse/metadata/paused_sources.csv` is not read (MISO, since 4 October 2026: [`miso_pause.md`](miso_pause.md)).
PJM's hub and zone prices are licensed and not held.

**An hour.** A day-ahead price is hourly. A real-time price is the mean of the hour's four 15-minute prices, and the
hour is held only when all four are. ISO-NE's real-time price is also held as ISO-NE's own hourly report: the one of
the two that holds more hours is used whole, never mixed. Prices are kept to the cent.

**Standard time.** Hours are counted in each grid's standard time with no daylight saving shift (ERCOT and SPP: UTC
less 6 hours; CAISO: less 8; NYISO and ISO-NE: less 5), so every day has 24 hours, a year 8,760 or 8,784, and a month
its calendar hours. In summer an hour on this page is one hour behind the clock on the wall.

**Nothing is filled.** An hour that is not held is left out of every sum. A month counts only when at least 95
percent of its hours are held. A year's figure is the sum of its counted months, and the year is marked incomplete
(drawn pale) unless all twelve count. "The last twelve months" are the newest twelve consecutive counted months; when
there are none, the figure is the placeholder "not held yet" with the date the region is held from. Depth is uneven:
ERCOT's hubs and load zones reach back to 2015, NYISO's zones to 2019, the other grids' main hubs to September 2024,
CAISO's ZP26 to June 2023, and ISO-NE's zones (on this page) and SPP South only to recent months. When the address names no market and real time has no twelve counted months but
day-ahead has, day-ahead is shown.

**A Texas load prices at its load zone** (session 140, the owner's ruling). A load in ERCOT settles at its load
zone's price, not at a trading hub's. `ercot_zone_prices_history` (`warehouse/connectors/ercot_zone_prices.py`) holds
the eight load zones from the same two yearly reports as the hubs (ERCOT NP4-180-ER, day-ahead, and NP6-785-ER, real
time), from 2015. The pull's ceiling was 3,000,000 rows, and eight zones at full resolution are about 4.1 million, so
day-ahead is held for all eight and real time (15-minute) for the four competitive zones: Houston, North, South and
West (2,473,320 rows). The four zones of municipal and cooperative systems (Austin Energy, CPS Energy, the Lower
Colorado River Authority, Rayburn) hold day-ahead only: their real-time figures read "not held yet", and with no
market named the page shows day-ahead there. Every hub row in the same workbooks equals the hub table's row for the
same interval (3,063,570 rows, no difference). ERCOT prints each load zone twice in a real-time interval, as type LZ
and as type LZEW, and the two can differ by a cent: the LZ row is kept. The default region is the North load zone.

**The hub beside it.** For a load zone the page shows its trading hub's price over the same twelve months, a flat
load, as a row of its own: North, Houston, South and West each have a hub of the same area; the four zones of
municipal and cooperative systems have none of their own and stand beside the hub average. The hub is for reference:
no figure of the load is computed from it.

**The zones' history** (session 140, `warehouse/connectors/zone_price_history.py`; an approved pull with a ceiling
of 3,000,000 rows, 2,820,388 read). Until this pull the zones of NYISO and ISO-NE, CAISO's ZP26 and SPP South held six
weeks of prices and had no year.

- **NYISO, eleven zones, from 2019.** Day-ahead is NYISO's hourly zonal price. Real time is NYISO's own hourly
  "Time-Weighted/Integrated Real-Time LBMP", not a mean of 15-minute prices made here. For a zone the hourly report
  holds more hours than the six weeks of 15-minute prices, so by the rule above it is used whole. NYISO's own archive
  of that report lacks 19 days of July 2026 (1 to 18 and 20 July); those hours are not held and not made from the
  5-minute files, so July 2026 does not count as a month for real time and the last twelve months of real time stop
  short of it.
- **CAISO's ZP26.** CAISO's system answered "no data" for every month before late June 2023, so day-ahead starts on
  26 June 2023, not 2019. Real time is the same 15-minute product the hub history holds for SP15, from September 2024.
- **SPP South.** Day-ahead only. SPP serves a finished year as one archive and the current year day by day; the days
  held grow as the pull, which is slow, goes back (126 days of 2026 at this page's first build). Real time was not
  asked for.
- **ISO-NE's eight load zones are pulled and held internal, and this page shows none of that history.** They come from
  ISO-NE's yearly workbook of hourly zonal information, the same file as the hourly demand the owner ruled internal,
  under the same notice ("Any duplication of the Content or non-personal use may violate copyright, trademark, and
  other laws.", `https://www.iso-ne.com/legal-privacy`). So ISO-NE's zones still read "not held yet" for the last
  twelve months, from the six weeks of the public tables; its Internal Hub has its year from the hub history.
  **Ruled on 7 October 2026 (the owner): ISO-NE's zone prices stay internal. Nothing of them is shown.** Session 140
  had held them internal by its own decision and asked; the question is closed.
- **The hour.** Each market was set against the six-week table over the days both hold: day-ahead prices equal to the
  cent at the same hour in every market (NYISO 10,824 hours, ISO-NE 1,152, CAISO 960, SPP 960), and not one hour
  either side. That settles ISO-NE's workbook: its hour is the hour ending in Eastern prevailing time, so the demand
  table read from the same workbook is placed correctly.
- **One kind, whole, across builds.** Where a kept file's hours and a new build's are of two kinds for one region and
  market (the operator's hourly report in one, means of 15-minute prices in the other), the kind that holds more hours
  stands whole and the other adds nothing.
- **Terms.** NYISO: its legal notice (below, under New York's load in line). CAISO: its materials "may be used by you
  provided that you keep intact all copyright, trademark and other proprietary notices and that you credit the
  California ISO when using such materials and/or information." SPP: "Permission is implicitly granted to copy and
  distribute (via computer network or printed form) in whole or in part (with appropriate citation) EXCEPT when such
  materials will be used, in whole or in part, within a commercial publication".

**A hub is not a site.** A hub or zone price is an average over many points. The price at one substation differs by
congestion and losses.

## What will it cost

Every figure is per megawatt of load and multiplied by the reader's size.

- **A flat load** draws its size in every hour. Its cost per MWh is the mean of the hourly prices held; its cost in
  dollars is their sum times the size.
A load that is not flat is computed twice (session 140): by a rule an operator could follow, which is the page's
figure, and with its hours chosen knowing the year's prices, which stands beside it labelled "if perfectly foreseen".

**The rule (the page's figure).** Every decision for an hour rests on prices published before that hour begins, and
never on the price the hour settles at (`site/lib/datacenter.ts`, `ruleWeights`).

- **Off in n hours a year, or in a share of hours.** The load is off in an hour when that hour's day-ahead price,
  published the day before, is at or above a threshold fixed before the day begins: the k-th dearest hourly day-ahead
  price of the prior 30 days (the 720 hours that end where the day begins), with k the share of hours the load means
  to shed (n over 8,760, or the share) times the hours held of those days, rounded, and at least 1. For 100 hours a
  year k is 8. The load has a budget: the n hours (or the share of the year's hours) in each calendar year. Once a
  year's budget is used, the load runs for the rest of that year; on a day with more hours at or above the threshold
  than are left, the dearest day-ahead hours are taken first. A day whose prior 30 days are not held (under 95 percent
  of their hours), which includes the first 30 days a region is held, is not decided: the load runs.
- **Shifting.** In each whole day a share of the day's energy leaves the day's dearest day-ahead hours and is added to
  its cheapest day-ahead hours: 24 times the share hours of each, the last one in part. Day-ahead prices are published
  the day before, so the load knows them when it decides. A day with a day-ahead hour or a paid hour missing is not
  shifted. A load that buys day-ahead and shifts by day-ahead prices pays exactly what foresight pays.
- **What it pays.** The price of the market it buys in (real time or day-ahead) in the hours it runs. A region with no
  day-ahead price gives no figure under the rule for a flexible load: the placeholder says so.

**"If perfectly foreseen" (beside it).** The same load with its hours chosen knowing every price of the year: off in
the n hours of each calendar year with the highest price (a year held in part takes the same share of its hours), or
in the dearest share of its hours; or, shifting, each day's energy moved from that day's dearest hours of the market
bought in to its cheapest. It is the most the load could have saved. No operator knows these hours in advance.

**Why the budget.** The threshold alone sheds more hours than the reader names when prices rise through a season (at
ERCOT's North load zone, real time, a load set for 100 hours would have been off in 256 hours of 2021 and 100 to 183
in the other years since 2015). With the budget the load is never off in more hours than the reader asked for, so the
figure "if perfectly foreseen" is never worse than the rule's, and the two compare like for like. The cost of the
budget is real: the rule spends its hours on the first dear days of a year and has none left for a later, dearer
event. `site/scripts/rule-gap.mjs` prints the rule, the foreseen figure and the threshold alone, by grid and year.
**Ruled on 7 October 2026 (the owner): the page keeps the budget of hours.** Session 140 added it without being
asked and put both versions before the owner; the rule stands as built.

**What the rule kept.** At ERCOT's North load zone, real time, off in 100 hours a year, the rule kept between 14 and
41 percent of the foreseen saving in each year from 2015 to 2025 (2021: a flat load USD 150.61 per MWh, the rule
136.09, foreseen 49.86). Shifting 20 percent of each day by day-ahead prices kept 85 to 90 percent of the foreseen
saving in 2023 to 2025. A load that turns off is assumed to turn off whole; a partial turn-down saves in proportion. A
real load also has a minimum it cannot go below and takes time to stop and start: neither is modelled.

- **Cost per MWh** of a load that turns off is its cost over the energy it did consume. **What the flexibility
  saves** is the flat load's cost per MWh less the load's, and in dollars the flat load's bill less the load's (a load
  that turns off buys less energy, and the row says how much).
- **A bad month.** Of the counted months among the 36 that end with the last twelve months, the month at the top
  tenth by cost per MWh, by nearest rank: one month in ten cost that or more. It mirrors the battery page's
  10th-percentile month of revenue. With fewer than 36 months held it is taken over those held, and the page says
  how many.
- **Power per GPU-hour.** The last twelve months' cost per MWh, times the power per GPU, times the overhead ratio,
  over 1,000. It is the energy bought at the market price and nothing else: no delivery, no demand or capacity
  charges, no hardware.
- **By year.** The chart and the folded table give each calendar year since the region's prices begin.

**Wholesale energy only.** The market cost is the price of energy at the hub or zone. It does not include delivery
(below, for Texas), ancillary service and uplift charges allocated to load, capacity charges where a grid has a
capacity market, a retailer's margin, or taxes.

### The contract

A share of the load's energy at a typed price per MWh, computed in the browser from the twelve months already on the
page; the two terms are never in the address, never sent and never stored. The contracted share of the energy is
bought at the contract price and pays nothing to the market; the rest pays what the market cost over the last twelve
months. This is the battery page's contract arithmetic (`site/lib/batterystack.ts`, `contractResult`) with the sign of
a buyer: a share at the typed price, the rest at the market's figure for the same twelve months. A real contract has a
shape, a settlement point, collateral and a term that are not here.

### Delivery and transmission charges, Texas

Shown as rows of their own, never added to the market cost. The table is `texas_delivery_charges`
(`warehouse/connectors/texas_delivery_charges.py`): the current retail delivery tariffs of the four large Texas wires
utilities (Oncor, CenterPoint Energy Houston Electric, AEP Texas, Texas-New Mexico Power), the schedule a customer at
transmission voltage takes and its riders. Each page that holds a rate schedule was read by a Claude model; every
figure is stored with the line it was read from, its page and the document's address, and was kept only when code
found that line in the page's text with the figure in it. 73 figures were read and 73 kept. The table is internal.

**What the page shows: all four utilities** (session 140, the owner's ruling). Session 138 showed Oncor's rows
alone, by its own reading of each utility's website terms, and asked for a ruling. The owner ruled that all four
utilities' delivery charges are shown, each row citing its tariff document, address and date, as public regulatory
filings: the tariffs are on file with the Public Utility Commission of Texas. The sentences of the four sites' terms
that session 138 read are kept here for the record:

| Utility | The sentence of its terms |
|---|---|
| Oncor | "You may copy, display and distribute Content, without modification, enhancement, customization, or reformatting of any kind, for personal, noncommercial, and/or educational purposes only" (`https://www.oncor.com/content/oncorwww/us/en/home/legal.html`) |
| CenterPoint | "you agree not to copy, reproduce, modify, create derivative works from, or store any Content ... or to display, perform, publish, distribute, transmit, broadcast or circulate any Content to anyone, or for any commercial purpose, without the express prior written consent of CenterPoint." (`https://www.centerpointenergy.com/en-us/about-us/legal/terms-of-use`) |
| AEP Texas | "AEP hereby authorizes you to copy and display the content herein, but for your personal use only." and "You may not copy or display for redistribution to third parties for commercial purposes any portion of the content without the prior written permission of AEP." (`https://www.aep.com/terms/`) |
| Texas-New Mexico Power | not read: its site refused the request on 7 October 2026 |

**Which rows.** A review of session 140 (`warehouse/derived/texas_delivery_review.json`, from the saved tariff pages)
names, for each utility, the rate class a load at transmission voltage takes (Oncor, CenterPoint and Texas-New Mexico
Power: "Transmission Service"; AEP Texas: "Transmission Voltage Service") and, for each of its 45 charges, whether it
is transmission, distribution or another rider, in the tariff's own words. A row is shown when the review names it,
its unit is printed on its page, its column was checked where its line holds more than one figure, and it is not
another customer's rate: 41 rows. Left out: two factors on base revenue that print no unit (AEP Texas), and two
energy efficiency factors read from a non-profit column (Oncor 0.000446, CenterPoint 0.000621; the columns for a
for-profit transmission customer print zero). Each row carries its tariff document, page, the date its sheet prints
and the line it was read from, on hover.

**Transmission and distribution apart.** Each utility's row lists its transmission charges, its distribution charges
and its other riders separately. For all four, the base Transmission System Charge prints zero (Oncor's schedule has
none): what a transmission-voltage customer pays for transmission is the transmission cost recovery factor rider
alone. Texas-New Mexico Power's factor is on a sheet effective 1 September 2025 in a tariff file dated 29 December
2025; the factor is updated each March and September, so the figure shown is probably superseded.

**A figure from a many-column table.** Some riders print one row of figures across the rate classes. Code proves the
figure is in the line, not which column it is. Such a figure is shown only when its column was checked against the
table's header by reading the page: Oncor's transmission cost recovery factor, its distribution cost recovery factor
and its mobile generation rider were. Oncor's energy efficiency factor is not shown: the figure the model read stands
in the column for non-profit transmission customers, and the for-profit column prints zero.

**The figures computed.** The transmission cost recovery factor is billed each month on the customer's demand in
the grid's four summer peak intervals (4CP). For a flat load that demand is its size, so the factor times twelve
months over the 8,760 hours of a year is its cost per MWh. It is computed only where the factor is printed per kW of
that demand (Oncor, AEP Texas); CenterPoint's and Texas-New Mexico Power's are printed per kVA, and no power factor is
assumed. A load that is off in those four intervals pays less; that is not computed. No other charge is converted,
and no total delivery cost is given: the riders held may not be all that apply to a given customer.

**The Commission's transmission charge matrices** (session 140). `texas_transmission_matrix`
(`warehouse/connectors/texas_transmission_matrix.py`), internal: Commission Staff's final matrices for 2025 (Docket
57491, item 51, filed 20 March 2025, approved by the Commission's Order of 5 June 2025, item 58) and for 2026 (Docket
59080, item 50, filed 16 March 2026: matrices A and B). **The 2026 matrices are not approved**: the docket was
remanded on 4 June 2026 and has no signed order (a proposed order on remand of 25 September 2026 is unsigned), so
every 2026 figure is marked "filed, not approved". The filed documents are scans with no text; the same attachments
were read from each item's file of native documents, and each row keeps the scan's address and page beside it. Each
page that holds the matrix was read by a Claude model (12 calls, USD 0.67); 855 figures were returned and 855 kept,
each with its line found in the page's text. The 47 providers' costs sum to the printed total in both years.

- **On the page:** the statewide rate (the "postage stamp" rate) as a row of its own: USD 68.547301 per kW of
  four-peak demand a year in 2025, USD 75.527270 in the 2026 matrices; and, computed, what it comes to per MWh for a
  flat load (the rate times 1,000 over 8,760 hours). A fold gives, for all of ERCOT and for the four utilities as
  transmission providers, each one's transmission cost of service, its rate per kW and its four-peak demand, as
  printed.
- **A utility's own rate is its share, not what its customers pay.** Every distribution provider pays the statewide
  rate on its load's four-peak demand; each transmission provider collects its own part of it. A retail customer pays
  it through its utility's transmission cost recovery factor, which is why that factor and the statewide rate are
  shown as separate rows and neither is added to the market cost.
- **Terms.** The Commission: "Documents that are filed in Central Records, such as docketed cases and ongoing agency
  projects, are available for downloading through the PUCT Interchange."
  (`https://www.puc.texas.gov/agency/about/contact/pia/`); and its link policy: "all PUCT content is protected by
  federal copyright laws" and "Site owners should contact the PUCT to request permission to use or copy content from
  the PUCT's website." (`https://www.puc.texas.gov/agency/about/policies/LinkPolicy/`). The table is internal; the
  figures above are shown as filings of a public docket, by the owner's approval of the pull.

Other grids show "delivery charges: not held yet": their utilities' tariffs are not in the warehouse.

## Will the power be there

Headline figures from the demand and mix tools, read from those tools' own files and linked; nothing of theirs is
recomputed here.

- **Demand growth**: `eia930_demand_growth` (method: [`demand_growth.md`](demand_growth.md)), the change in average
  and in peak hourly demand from 2019 to the last whole year. Weather is not removed.
- **The highest hour of demand, and installed capacity by fuel**: `grid_stress_yearly` (method:
  [`grid_stress.md`](grid_stress.md)), the newest whole year. Hovering a fuel gives its capacity as a share of that
  hour. Installed capacity is nameplate: it is not what is available in a tight hour.

- **Hours the grid was tight.** From the operator's own hourly demand, pulled in session 138 (four connectors under
  `warehouse/connectors/`, in the weekly refresh): `ercot_zone_load_hourly` (ERCOT's own system total, from 2015),
  `caiso_area_load_hourly` (CAISO's system total, from September 2021) and `nyiso_zone_load_hourly` (the sum of its
  eleven zones in the hours all eleven are held, from 2019). **An hour is counted tight when the grid's demand was at
  or above 95 percent of that year's highest hour.** A year is counted when at least 95 percent of its hours are held;
  the newest year is counted up to its last hour held and is not whole. The row shows the newest whole year, with the
  months and the hours of the day (standard time) the tight hours fall in. This is a count of hours of high demand. It
  does not know what generation was available, so it is not a count of scarcity or of emergencies.
- **Of those hours, this load was off in.** The tight hours in which the reader's load, as described, draws nothing:
  the overlap of the grid's highest demand and the region's highest prices of that year. A flat load is off in none. A
  shifting load is never off for a whole hour by rule, so the row is not counted for it.
- **Demand by region.** Each zone's average hourly demand in its newest whole year against its first whole year held.
  ERCOT's eight are weather zones, which are not its trading hubs or load zones and do not join the prices; NYISO's
  eleven are the zones of the page's region list (the reader's own in bold); CAISO's five are transmission access
  charge areas. Hovering a zone gives the megawatts.
- **ISO-NE: "licensed source needed".** ISO-NE publishes its hourly demand by zone and its legal notice says "Any
  duplication of the Content or non-personal use may violate copyright, trademark, and other laws."
  (`https://www.iso-ne.com/legal-privacy`). The table, `isone_zone_load_hourly`, is held internally and nothing of it
  is written to the page's files.
- **SPP: "not held yet".** No hourly demand by zone was pulled for SPP.
- **The hour.** Each new table's hours were set against EIA-930's hourly demand for the same grid over the days both
  hold: ERCOT, CAISO and NYISO agree at the same hour (correlation above 0.9999) and not one hour either side. ISO-NE's
  does not settle it (0.935 at the same hour, 0.951 one hour later, on 148 hours: the two series define demand
  differently), which is one more reason nothing of it is shown.

## How clean

From `clean_energy_summary`, the table behind `/mix?view=clean` (method: [`clean_energy.md`](clean_energy.md)), for
the newest whole year: the carbon-free share of the grid's generation over the year (the annual figure); the share a
flat load meets hour by hour; for a purchase of carbon-free energy equal to the load's whole year and shaped like the
grid's own carbon-free generation, the share of the energy matched hour by hour and the share of hours fully covered;
and the carbon per MWh of a flat load. These are the grid's figures.

**This load's own hours** (session 140). The grid's carbon-free share in each hour (`clean_energy_hourly`, the table
behind the same tool, written into the page's files by hour) weighted by the reader's load in that hour, under the
rule above, over the hours of the year in which the price and the share are both held: the sum of share times load
over the sum of load. A flat load's figure over the same hours stands beside a flexible load's. It is the share of
the grid's generation that was carbon-free while the load ran, not a claim about the energy the load bought, and it
is the average of the hour, not the marginal plant.

## How soon

- **The interconnection queue**: `interconnection_queue_summary` (method:
  [`interconnection_queue_summary.md`](interconnection_queue_summary.md)), from Lawrence Berkeley National Laboratory's
  queue data: the capacity and number of active requests, the median years from request to operation, and of the
  requests entered in the summary's past window the shares now operating and withdrawn. This is the queue of
  generators and storage, not of loads.
- **ERCOT's large load**: `ercot_large_load_status` (method: [`ercot_large_load_status.md`](ercot_large_load_status.md)):
  the megawatts with approval to energize and the megawatts ERCOT has observed running, from ERCOT's newest status
  report held.
- **Large load in line by region: "not published anywhere yet"; New York's is held and not shown.** A search on 7 October 2026
  (`docs/paper/related_projects_notes.md`, section 3) found no public list of the large load waiting for power by
  place for ERCOT (which publishes system totals in slide decks), CAISO, ISO-NE or SPP. "Not published anywhere yet"
  means that a search found none, not that none can exist.
- **New York's load in line: "NYISO's terms do not allow it"** (session 140; ruled on 7 October 2026 and applied in
  session 149). NYISO is the one grid that publishes load in line by place: `nyiso_load_queue`
  (`warehouse/connectors/nyiso_load_queue.py`) reads the sheet "Load Projects" of its interconnection queue workbook,
  one row a request. **In line** means: on that sheet, with a status in the sheet's own key whose words say neither
  "Withdrawn" nor "In Service"; withdrawn requests and requests in service are counted apart and never added.
  Megawatts are the sheet's "Peak MW load" as printed, summed within NYISO's one list. The sheet prints no in-service
  date for any request, so a wait cannot be measured from it.
  - **The ruling.** The owner, 7 October 2026: NYISO's terms for the queue rows are to be quoted, and the rows shown
    if they allow it. Session 140 had shown megawatts and requests by zone and every request in a fold, on the
    owner's approval of the pull.
  - **The notice, every sentence that bears on copying, redistribution and display, word for word**
    (`https://www.nyiso.com/legal-notice`, read 7 October 2026; the page is saved beside the workbook with its hash,
    sha256 `8b693099a6e75854479d3aecaa4d35989f238bb7682e403f21bb4dc91d7fa580`, and the connector checks each
    sentence in it before it writes):
    1. "The NYISO maintains this Web site for the benefit of its Market Participants and other authorized users."
    2. "Access to this Web site does not confer any license or ownership interest in either the form or content of the
       Web site, including any confidential or proprietary information or intellectual property of any kind or nature,
       and the NYISO hereby expressly reserves such rights and property in its entirety."
    3. "Downloading, republishing, retransmitting, reproducing, or other use of any image or video on this website as
       a stand-alone file is strictly prohibited"
    4. "The NYISO’s trademarks (including its logo) are owned by the NYISO and may only be used with the
       NYISO’s prior written permission."
    5. "Even if prior written permission is obtained, the NYISO may revoke permission to use the NYISO’s
       trademarks at any time."
    6. "Copyright © 2026 New York Independent System Operator. All Rights Reserved."
  - **The reading, by the words alone.** They do not allow it. The notice confers no license in the form or content
    of the site, reserves NYISO's rights and property in their entirety, and closes with all rights reserved. No
    sentence grants a reader leave to copy, redistribute or display anything. The one thing it forbids by name is
    republishing an image or a video as a stand-alone file; that says nothing in favour of anything else. A notice
    that reserves every right and grants none does not allow a public page to show its rows.
  - **What follows.** The megawatts in line by zone, each zone's requests by status and the fold of requests have
    left the page: the row reads "NYISO's terms do not allow it", with the reason on hover. The table is internal
    (its header, the source registry, the internal Redivis dataset), and the page's file
    (`site/data/nyiso_load_queue.json`) holds the source, these sentences and the reading, and no request, zone or
    megawatt. One switch puts them back (`SHOWN` in the connector) if a person rules that the notice allows it, or
    NYISO gives leave in writing. The same notice covers every NYISO table the ERW publishes (its prices by zone, its
    interconnection queue): this ruling was asked and applied for the load queue only.
- **How long a new large load waits: "not published anywhere yet".** The same search found no public dataset of the
  time from a large load's request to its energization, for any grid.

### Rules in motion (session 154)

The block "Rules in motion" in "How soon" lists, for the grid chosen, the regulatory actions that are moving and
that bear on a large load seeking power: the date, the status, the regulator and docket number (a link to the
regulator's own document), and one line on what it would change. The page reads one file,
`site/data/datacenter/rules.json`, written whole by `warehouse/derived/rules_in_motion.py`. No table is read from
Supabase for it and nothing is loaded.

**What it is not.** Not legal advice. Not complete: a docket system cannot be proved complete from outside, and each
commission's list was found through its own search page, its large-load page or a known docket's document list, not
through a register of everything it has open. Federal regulators, state utility commissions and grid operators only:
nothing municipal (permitting, zoning, local hearings) is recorded, tagged or shown, even where a document mentions
it. A row is what a document said on its date; a later order may have changed it.

**Where the rows come from.** Two places.

1. `large_load_rules` and `large_load_rules_internal` (`warehouse/connectors/large_load_rules.py`; two tables, one
   for each license, see "Each regulator's terms" below): proceedings and orders on large-load
   interconnection, large-load tariffs, transmission cost allocation and interconnection reform at the Federal
   Energy Regulatory Commission and the utility commissions of Texas, Virginia, Ohio, Georgia, Indiana, Arizona,
   Pennsylvania, Illinois, Oregon and California. One row a proceeding (the docket itself: its opening order, notice
   or petition is the document) and one row for each order in it. Three research passes, each an AI research agent,
   read the regulators' public dockets on 8 October 2026 under the owner's approved pull (USD 0, a ceiling of
   20,000 rows) and saved every document they opened. The connector makes no request. It proves each row again by
   its own code: the sentence, white space normalized, is a literal substring of the saved document's text, and for
   a PDF the page is found by the connector, not taken from the pass. A row that does not prove, or that lacks a
   real document date, a docket number, a topic of the four, or an address on a regulator's or grid operator's own
   host, is left out and listed with its reason. Nothing is filled: a field the document does not state is empty.
   `status_as_worded` is the regulator's wording where its page or the document states one; `status_class` (open,
   decided, closed, not stated) is the collecting pass's reading and always stands beside those words. Never taken:
   an address on MISO's site or PJM's Data Miner or API; an address that holds a filer's e-mail address; a news
   article, a law firm's note or a search summary. On 8 October 2026 the passes collected 118 rows; 116 were taken
   (49 proceedings and 67 orders, of 11 regulators) and 2 left out: an Oregon docket page that prints no date, and
   an Illinois order whose docket number the pass could tie to the minutes only by matching company, subject and
   date across two of the commission's lists, not by the commission's own words.
   - **What a sentence is cut from** (`sentence_from`, and on the page the docket's hover). 87 of the 116 sentences
     are the document's own text (an order, decision, notice, proposed rule, application, letter; `sentence_kind`
     `document`). 29 are the regulator's own record of the document, not its text (`sentence_kind` `record`),
     because the document sits behind a check or is a scan: Ohio's 10 rows are the docket card's one-line summary
     of each filing (the document viewer answers with a reCAPTCHA and was not requested); 9 Illinois rows are from
     the commission's open meeting minutes (5), agendas (3) and its list of suspended cases (1), since a docket's
     own page answers with a robot check; 4 Arizona rows are the commission's own news releases, since its
     decisions are scans whose text layer misreads letters; 4 are docket pages (California 2, Oregon 1, Arizona
     1); 1 is Indiana's weekly hearings list; 1 is FERC's regulatory agenda in the Federal Register. A sentence of
     the minutes is what the Chair said the order does, not the order's words.
   - **Flags** (`row_flag`). 4 rows carry a docket number that is not in their own document and is tied to it by
     another document of the same commission (an agenda item of the same meeting, later minutes, the docket's own
     page): 3 from Illinois, 1 from Pennsylvania. 12 rows are a contract or agreement with one customer, placed
     under the nearest topic by the pass (Indiana 6, California 4, Arizona 2): kept, flagged, never among the ten
     rules of the month. 4 California rows are draft resolutions as posted for the agenda: their status reads
     "DRAFT" as the document words it and their status class is "not stated", since no adopted text was read.
2. The federal policy actions held in `policy_actions` that the tags' rule marks (`policy_action_tags`; method and
   the rule's measurement: [`policy_action_tags.md`](policy_action_tags.md)): large loads, interconnection,
   transmission cost, tax credits. The rule is a list of terms that code applies to the title and the abstract, with
   stated exclusions (the interconnection of a gas pipeline is not the grid's; a bill credit is not a tax credit;
   nothing municipal) and a list of dockets by number. A state commission's news release that the rule tags stays
   in the tags table: the block shows a state's dockets, not its releases.

**What "in motion" means.** A proceeding whose status class is open, whatever its date; an order or rule dated in
the 12 months before the file was built; a tagged federal action held of those 12 months. A proceeding that is
decided or closed, or whose status no document states, is in the table and not in the block.

**Which grid sees which action.** By rule:

- An action whose own words name a grid operator (ERCOT, PJM, MISO, CAISO, NYISO, ISO-NE, SPP, by name or by the
  operator's full name) is under that operator and no other. For a proceeding or order this is the operator the
  collecting pass recorded from the document (`grids`), or the operator another document of the same docket names;
  a pass leaves out an operator named only in passing. So a Texas case of a utility in SPP is under SPP, not ERCOT,
  and an Indiana order that names MISO is under MISO, where no row is shown. A federal notice tagged by its docket
  number is under the operator that docket is about.
- A state commission's action that names no operator is under the operators that serve that state's utilities. The mapping is stated here
  plainly as common knowledge of the US power system, the states listed; no federal table of it is cited in this
  repository:

  | State | Grid on the page | Why |
  |---|---|---|
  | Texas | ERCOT | The Texas commission regulates the ERCOT region. The parts of Texas in SPP and MISO see a Texas action only when its own words name them |
  | Virginia | PJM | Dominion Energy Virginia and Appalachian Power are in PJM |
  | Ohio | PJM | AEP Ohio, FirstEnergy's Ohio companies, AES Ohio and Duke Energy Ohio are in PJM |
  | Pennsylvania | PJM | PECO, PPL Electric, FirstEnergy's Pennsylvania company and Duquesne Light are in PJM |
  | Illinois | PJM and MISO | Commonwealth Edison is in PJM; Ameren Illinois is in MISO. MISO shows no row, so an Illinois action is seen under PJM |
  | Indiana | PJM and MISO | Indiana Michigan Power is in PJM; the state's other utilities are in MISO. Seen under PJM |
  | California | CAISO | PG&E, Southern California Edison and SDG&E are in CAISO |
  | Georgia | none | Georgia's utilities are in no organized market: in the table, not in the block |
  | Arizona | none | Arizona's utilities are in no organized market operator's footprint: in the table, not in the block |
  | Oregon | none | Oregon's utilities are in no organized market operator's footprint: in the table, not in the block |

  The mapping is coarse: a state's action that names no operator is shown under every grid the state is mapped
  to (an Illinois action under PJM, since MISO shows no row; a Texas case of El Paso Electric, which is in neither
  ERCOT nor SPP, under ERCOT). Each row's hover says why it is under the grid.
- A federal action that names no operator is under every grid, in a group of its own: "Federal, all grids".
- **MISO: "paused while terms are reviewed", and no row.** MISO's own site is never requested
  ([`miso_pause.md`](miso_pause.md)); the block shows nothing under MISO, including federal orders that name it.
- **PJM: rows are shown**, although the rest of the page reads "licensed source needed" for PJM's prices: a
  regulator's filing about PJM is the regulator's public document. They are read from FERC, the state commissions
  and PJM's public committee documents, never from PJM's Data Miner or API.

**The one-line read is a model's, and is marked so.** `warehouse/policy/rule_reads.py` gives a model the row's own
sentence and the saved text of the same document around it (2,500 characters before the sentence and 3,500 after,
white space normalized), under one heading line made of the row's own fields, and nothing else; for a federal action
held, its title and abstract as the Federal Register prints them. The model writes one line: what the action would
change for a large load seeking power. Code keeps the line only if every number in it stands in the text the model
was given, numbers written as words included; it is one line of at most 320 characters with no em dash; it holds
none of the words the block never shows; and, where the row's regulator restricts copying or its terms were not
read, it holds no run of more than five consecutive words of the document, so that the line states facts and quotes
nothing. A line that fails is not shown: the row reads "no read yet". A row was asked at most three times (the last
time with the copied run named back to the model); every answer paid for is kept beside the table. On 8 October
2026: 92 rows in motion with a saved text, 87 with a line, 5 without. A federal action that already has a read in `policy_reads` uses that read's plain line, which is a
model's too. The line is never the regulator's words: the regulator's sentence is on the docket's hover, and the
link opens the document. Every call goes through the cost ledger, with the stop before each call.

**Kept out of the file, and counted in it** (`not_on_page`): a state with no grid on the page; a row under MISO
alone; a state commission's news release held in `policy_actions`; a row whose shown title, sentence, read or status
holds one of the words "zoning", "permit", "city council" or "county board" (the block never shows them, so an order
that uses "permit" as a verb would be kept out too; it stays in the table; none was on 8 October 2026); a row whose
shown words hold an em dash (none).

**Each regulator's terms, and what the page shows of its rows.** A decision made for the owner to confirm. A table
has one license, so the rows are in two tables, as session 140 held ISO-NE's zone prices beside the public ones.
`warehouse/config/large_load_rule_terms.json` holds, for each regulator, the sentence that decided it, word for
word as the pass that read the page saved it, with the saved page's hash.

- **Allowed or a public-records statement: `large_load_rules`, public.** The row is shown with the regulator's
  sentence and its worded status.
- **Restricted, or not quoted: `large_load_rules_internal`.** The page shows the row's facts (the date, the
  regulator, the docket number, the status class, the topic, the link to the regulator's own document) and the
  model's read, which quotes nothing. It shows neither the regulator's sentence nor its worded status nor the
  document's title: the hover says why and says to open the document.
- Two lines in `warehouse/derived/rules_in_motion.py` let the owner rule either way: a regulator named in
  `OFF_PAGE_REGULATORS` has no row on the page at all; one named in `SHOW_SENTENCE_REGULATORS` has its sentences
  shown.

| Regulator | Class | The sentence that decided it (the regulator's own words) | Page read |
|---|---|---|---|
| California Public Utilities Commission | allowed | "In general, information presented on this web site, unless otherwise indicated, is considered in the public domain. It may be distributed or copied as permitted by law." | `www.cpuc.ca.gov/about-cpuc/conditions-of-use`, 2026-10-08, sha256 `8c49fa90dd82` |
| Oregon Public Utility Commission | public record | "Most information collected by state government is assumed to be open to the public unless specifically exempted." and "The PUC will make public records available unless the records are exempt from disclosure by law." | `www.oregon.gov/pages/terms-and-conditions.aspx`, 2026-10-08, sha256 `a85cd8ed6af6` |
| Arizona Corporation Commission | public record | "In other words, much of the information you disclose to us becomes a matter of public record as required by law." | `www.azcc.gov/privacy-policy`, 2026-10-08, sha256 `9afd6435558e` |
| Pennsylvania Public Utility Commission | public record | "Persons requesting copies of public records maintained by the Commission must submit a written request to the Commission’s Open Records Officer." | `www.puc.pa.gov/filing-resources/issues-laws-regulations/right-to-know-policies-and-procedures/`, 2026-10-08, sha256 `6c8c682ab8c1` |
| Illinois Commerce Commission | public record | "Information collected and received through the Illinois Commerce Commission web site may become public record and therefore subject to disclosure under the Illinois Freedom of Information Act." | `icc.illinois.gov/privacy.htm`, 2026-10-08, sha256 `1308fa4664da` |
| Public Utility Commission of Texas | restricted | "Although the content of PUCT web sites is available to the public, certain information on the PUCT web sites may be trademarked, service marked, or otherwise protected as the PUCT's intellectual property, and all PUCT content is protected by federal copyright laws." and "Site owners should contact the PUCT to request permission to use or copy content from the PUCT's website." | `www.puc.texas.gov/agency/about/policies/linkpolicy/`, 2026-10-08, sha256 `ce2831de052a` |
| Indiana Utility Regulatory Commission | restricted | "Except as may otherwise be allowed by law (including but not limited to the Indiana Access to Public Records Law), the viewing, printing, or downloading of any content, graphic, form, or document from the Portal grants you only a limited, nonexclusive license for use solely by you for your own personal use, and not for republication, distribution, assignment, sublicense, sale, preparation of derivative works or other use." | `www.in.gov/core/terms_of_use.html`, 2026-10-08, sha256 `2c92c4dd2142` |
| Georgia Public Service Commission | restricted | "Request in writing by any person pursuant to the Georgia Open Records Act, O.C.G.A. Section 50-18-70, et seq." and "2026 Georgia Public Service Commission. All rights reserved." (the footer of every page of the site, after a copyright sign, as pass C records it) | `psc.ga.gov/open-records-requests/`, 2026-10-08, sha256 `2fe67dc328ef` |
| Public Utilities Commission of Ohio | not quoted | None: puco.ohio.gov answered 404 to six plain requests, its privacy notice among them (pass B); no terms page could be read | none |
| Virginia State Corporation Commission | not quoted | None: one guessed web policy address answered 404, so no terms page was met (pass A) | none |
| Federal Energy Regulatory Commission | not quoted | None: every ferc.gov page answered HTTP 403 with a browser check, recorded once and left; only order files at known addresses answered (pass A). No terms page of the Commission, of the Federal Register or of govinfo.gov was read | none |

Only California's terms speak of reuse ("may be distributed or copied"). **Oregon's, Arizona's, Pennsylvania's and
Illinois's statements are about access to public records, not about reuse**: they say that records are open or how
to ask for them, and no sentence of theirs permits or forbids copying. They are shown with their sentences on that
footing (Oregon and Arizona by the session coordinator's ruling, Pennsylvania and Illinois by the same rule applied
by the build agent), and the owner may rule otherwise in one line. Illinois's docket pages also answer "Please, no
robots or crawlers beyond this point.": one request was made and none after, and every Illinois row is cut from the
commission's minutes, agendas or list. Indiana's terms carve out what "the Indiana Access to Public Records Law"
allows; whether one quoted sentence of an order is inside that exception is the owner's to rule. FERC's orders are
works of the United States government, but every page of ferc.gov answered a browser check and no terms page of
the Commission, the Federal Register or govinfo.gov was read, so by the rule FERC stands as not quoted.

## Tests

`site/scripts/test-datacenter.mjs`, on saved real samples (`tests/fixtures/session138`: ERCOT HB_HUBAVG, every hour of
2021 and of 2025, both markets): a flat load pays the mean of the hourly prices; no flexible load pays more than a
flat one, in a calm year or in the year of Winter Storm Uri; the contract arithmetic equals the battery page's; a
load that turns off n hours is off in exactly n and never keeps an hour dearer than one it cut; a shifted day keeps
its energy; an hour not held is left out. `tests/test_session138.py` runs it and checks the builder and the page.

`site/scripts/test-datacenter-rule.mjs` (session 140), on the same samples: the forecast rule never uses a price from
the hour it decides (every real-time price can be replaced and no decision changes; a day's threshold does not move
when any price of that day or of a later day changes; the decisions up to a day are the same whatever the later
prices are); each day's threshold and each hour shed are worked by hand; the first 30 days are not decided; the load
is never off in more hours of a year than named; the rule never pays less than the same hours perfectly foreseen; the
30 days are read across the boundary between two years' files; and the clean share of a load's own hours.
`tests/test_session140.py` runs it and checks the builder's new parts and the page.

`tests/test_session154.py` (session 154, rules in motion): the tags' rule on made-up rows and on the table held (a
company's name is not a topic, a gas pipeline's interconnection is not the grid's, a bill credit is not a tax
credit, nothing municipal, a docket listed by number); the connector (a sentence proves and its page is found, a
sentence over a page break, a row that does not prove, never MISO's site or an address with an e-mail address, what
a sentence is cut from, the flags, a regulator's rows public only by its own quoted terms, each quoted sentence
found in the page its pass saved); the reads (no number the text lacks, no quotation of a restricted regulator, the
stop before the call); the site's file (which grid sees which action, MISO paused, a row of the internal table
with its facts and never its sentence, the owner's two switches, the built file against its contract); the ten.

## Refresh

`python warehouse/derived/datacenter_page.py` rebuilds the files; the weekly refresh (`warehouse/refresh_supply.sh`,
Saturdays) runs it after the load connectors and, on a machine that holds the table, after the newest files of the
zones' history. ERCOT's load zones are not refreshed on a schedule: each new copy of the current year's two workbooks
counts against that pull's ceiling, which leaves room for two, so their hours stop at 3 October 2026 until a person
rules on it. New York's load queue is refreshed with the interconnection queues on Mondays. A build is merged into the kept files: an hour the new build holds is
the new build's, an hour only the kept file holds is kept, so a machine with a shorter history (the scheduled runner
holds no ERCOT price history) adds hours and never thins a file. A file is rewritten only when its content changes.
