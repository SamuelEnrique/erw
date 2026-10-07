# What a datacenter pays

The method of the page `/cost-of-power` ("What a datacenter pays", in review), the first tab of the cost of power
beside "What a generator earns" and "What a battery earns". It answers four questions for a load the reader describes:
what the power will cost, whether it will be there, how clean it is, and how soon it can be had.

The page's face carries no method. Everything about how a figure is made, and what it leaves out, is here.

## The reader's load

| Input | Choices | Default |
|---|---|---|
| Grid | ERCOT, CAISO, NYISO, ISO-NE, SPP. MISO is shown and blank ("paused while terms are reviewed"); PJM is shown and blank ("licensed source needed") | ERCOT |
| Region | every hub and zone of that grid whose public price the warehouse holds | the grid's main hub |
| Size | megawatts of load at the meter | 100 |
| How it runs | flat; off in a number of the most expensive hours of each year; off in a share of hours; or a share of each day's energy moved to the day's cheapest hours | flat |
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
ERCOT's hubs reach back to 2015, the other grids' main hubs to September 2024, and the zones only to late August
2026, so a zone has no year yet. When the address names no market and real time has no twelve counted months but
day-ahead has, day-ahead is shown.

**ERCOT's regions are its six trading hubs.** A load in ERCOT settles at its load zone's price; the warehouse holds
hub prices, not load zone prices, so the hub nearest the load is the nearest thing held.

**A hub is not a site.** A hub or zone price is an average over many points. The price at one substation differs by
congestion and losses.

## What will it cost

Every figure is per megawatt of load and multiplied by the reader's size.

- **A flat load** draws its size in every hour. Its cost per MWh is the mean of the hourly prices held; its cost in
  dollars is their sum times the size.
- **Off in the n most expensive hours of each year.** In each calendar year the n hours with the highest price are
  found, and the load draws nothing in them. A year held in part takes the same share of its hours (n times the hours
  held over the hours of the year, rounded). Months, the last twelve months and years are all sums over these same
  hours, so they add up; the last twelve months therefore hold the off hours of two calendar years that fall in them,
  which need not be exactly n.
- **Off in a share of hours.** The same, with the most expensive share of each year's hours held.
- **Shifting.** In each whole day a share of the day's energy leaves the day's most expensive hours and is added to
  its cheapest: 24 times the share hours of each, the last one in part. The load is off in the dearest hours and draws
  twice its size in the cheapest, so the day's energy is unchanged. The share is at most 50 percent. A day with an hour
  missing is not shifted.

**These are the most a load could have saved.** The hours are chosen knowing the year's prices. A real load schedules
on a forecast, has a minimum it cannot go below, and takes time to stop and start. The page's flexible figures are an
upper bound on the saving, never a forecast. A load that turns off is assumed to turn off whole; a partial turn-down
saves in proportion.

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

DELIVERY_SECTION

Other grids show "delivery charges: not held yet": their utilities' tariffs are not in the warehouse.

## Will the power be there

Headline figures from the demand and mix tools, read from those tools' own files and linked; nothing of theirs is
recomputed here.

- **Demand growth**: `eia930_demand_growth` (method: [`demand_growth.md`](demand_growth.md)), the change in average
  and in peak hourly demand from 2019 to the last whole year. Weather is not removed.
- **The highest hour of demand, and installed capacity by fuel**: `grid_stress_yearly` (method:
  [`grid_stress.md`](grid_stress.md)), the newest whole year. Hovering a fuel gives its capacity as a share of that
  hour. Installed capacity is nameplate: it is not what is available in a tight hour.

DEMAND_SECTION

## How clean

From `clean_energy_summary`, the table behind `/mix?view=clean` (method: [`clean_energy.md`](clean_energy.md)), for
the newest whole year: the carbon-free share of the grid's generation over the year (the annual figure); the share a
flat load meets hour by hour; for a purchase of carbon-free energy equal to the load's whole year and shaped like the
grid's own carbon-free generation, the share of the energy matched hour by hour and the share of hours fully covered;
and the carbon per MWh of a flat load. These are the grid's figures. The reader's own flexible load is not matched
against them: the row says "not held yet".

## How soon

- **The interconnection queue**: `interconnection_queue_summary` (method:
  [`interconnection_queue_summary.md`](interconnection_queue_summary.md)), from Lawrence Berkeley National Laboratory's
  queue data: the capacity and number of active requests, the median years from request to operation, and of the
  requests entered in the summary's past window the shares now operating and withdrawn. This is the queue of
  generators and storage, not of loads.
- **ERCOT's large load**: `ercot_large_load_status` (method: [`ercot_large_load_status.md`](ercot_large_load_status.md)):
  the megawatts with approval to energize and the megawatts ERCOT has observed running, from ERCOT's newest status
  report held.
- **Large load in line by region, and how long a new large load waits: "not published anywhere yet".** No operator
  or agency publishes either as a dataset. The pieces sit in utility planning filings, rate cases and operator
  reports. This is true of every grid on the page.

## Tests

`site/scripts/test-datacenter.mjs`, on saved real samples (`tests/fixtures/session138`: ERCOT HB_HUBAVG, every hour of
2021 and of 2025, both markets): a flat load pays the mean of the hourly prices; no flexible load pays more than a
flat one, in a calm year or in the year of Winter Storm Uri; the contract arithmetic equals the battery page's; a
load that turns off n hours is off in exactly n and never keeps an hour dearer than one it cut; a shifted day keeps
its energy; an hour not held is left out. `tests/test_session138.py` runs it and checks the builder and the page.

## Refresh

`python warehouse/derived/datacenter_page.py` rebuilds every file; `--since <year>` rewrites only that year's files on.
A past year's file is rewritten only when its content changes.
