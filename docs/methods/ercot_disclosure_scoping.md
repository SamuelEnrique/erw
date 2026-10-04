# What real batteries earned: scoping ERCOT's 60-day disclosure data

Session 108. A scoping note, not a table's method: one sample month was pulled and nothing else. Session 101 found that
the warehouse holds no measure of what real batteries earned; this note says what ERCOT publishes that could give one,
what a month of it holds, and what a measured revenue per kW would take.

## What ERCOT publishes

ERCOT's Market Information List (`https://www.ercot.com/mp/data-products`) has two daily reports of 60-day-old data
that name each resource:

| Report | EMIL ID | Report type | What it is, in ERCOT's words |
|---|---|---|---|
| 60-Day DAM Disclosure Reports | NP3-966-ER | 13051 | "This report contains all 60-day disclosure data related to the Day-Ahead Market (DAM)." File types: "Energy Bid Awards, Energy Bids, Energy Only Offer Awards, Energy Only Offers, Generation Resource AS Offers, Generation Resource Data, Load Resource AS Offers, Load Resource Data, Point-to-Point Obligation Bid Awards, Point-to-Point Obligation Bids, Point-to-Point Obligation Option, Point-to-Point Obligation Option Awards, QSE-SpecificSelf-Arranged AS, AS Only Offers, ESR Data, ESR AS Offers, and AS Only Awards." |
| 60-Day SCED Disclosure Reports | not read from its page | 13052 | The real-time side: among its files `60d_ESR_Data_in_SCED` ("the ESR Resource name and the ESR Resource's Energy Offer Curve") and `60d_SCED_SMNE_GEN_RES` ("actual metered Generation Resource net output") |

The data product page for the DAM report gives: audience public, security classification public, generation frequency
daily, first run 29 January 2011, rule "NP3.2.5(12) PUCT Substantive Rule §25.506", file type zip and csv. The columns
are defined in ERCOT's "Disclosure Reports Column Definitions Guide" (v2.4, an Excel file linked from its user guides
page), sheet "60Day Disclosure Reports". The SCED report's own page was not read: its type number is the one its public file
list answers to, and its files are as the guide describes them.

For storage the DAM file is `60d_DAM_ESR_Data-DD-MMM-YY.csv`. The guide: "The ESR Resource name and the ESR Resource's
Three-Part Supply Offer (prices and quantities), including Startup Offer and Minimum-Energy Offer, available for the
DAM; The award of each Three-Part Supply Offer from the DAM and the name of the QSE receiving the" award. Its 48
columns: Delivery Date, Hour Ending, QSE, DME, Resource Name, Resource Type, ten pairs of offer MW and price, three
start-up costs, Min Gen Cost, HSL, LSL, Resource Status, **Awarded Quantity, Settlement Point Name, Energy Settlement
Point Price, RegUp Awarded, RegUp MCPC, RegDown Awarded, RegDown MCPC, RRSPFR Awarded, RRSFFR Awarded, RRSUFR Awarded,
RRS MCPC, ECRSSD Awarded, ECRS MCPC, NonSpin Awarded, NonSpin MCPC**.

## License

Public. ERCOT's terms (`https://www.ercot.com/help/terms`, read 4 October 2026): "The publicly available contents of
this website may be used, reproduced, and redistributed, provided that the contents are not modified and that you
maintain all copyright and other notices contained in the contents, including this Agreement. Notwithstanding the
foregoing, raw data provided in public portions of this website may be used, reproduced, and redistributed in
compilations, charts, and analyses without maintaining such notices."

The files name each resource and its scheduling entity (QSE). That is ERCOT's own disclosure, required by the rule
above after 60 days; the terms put no further limit on it.

## The sample: July 2026

`warehouse/analysis/ercot_disclosure_sample.py --month 2026-07`. 32 requests to `ercot.com` (the file list and 31
daily zips, 339 MB, one a second), USD 0. A zip published on a day holds the operating day 60 days before. The sample
keeps the award columns and the limits of the ESR file and leaves the offer curve out. It is written under
`warehouse/output/analysis_internal/` and is **not in coverage**, the archive, Redivis or Supabase; the zips stay on the
data machine.

| | |
|---|---|
| Rows | 244,968, of a ceiling of 300,000 |
| Operating days | 31, 1 to 31 July 2026, every hour ending 1 to 24 |
| Resources | 332 (324 to 332 a day), all of type ESR |
| Scheduling entities (QSE) | 114 |
| Settlement points | 287 |
| Resource status | ON in 204,841 resource-hours, OUT in 24,663, ONTEST in 15,464 |
| Size of the fleet | the sum of each resource's highest HSL in the month is 21,365.1 MW; of its lowest LSL (charging), -20,723.0 MW. 320 resources have an HSL above zero; the largest is 240.0 MW, the median 50.0 MW |

**What the awards add up to** (each award at the price in the same row; nothing is estimated):

| | Resource-hours with an award | Awarded | Valued at its own price |
|---|---|---|---|
| Energy sold | 11,527 | 280,537 MWh | USD 16,382,077 |
| Energy bought (charging) | 8,005 | 242,250 MWh | USD 5,020,285 |
| Energy, net | 19,532 of 244,968, 8.0 percent | | USD 11,361,793 |
| Regulation Up | 17,114 | 361,292 MW-hours | USD 289,277 |
| Regulation Down | 14,120 | 250,228 MW-hours | USD 251,826 |
| Responsive Reserve (three kinds) | 28,091 | 759,894 MW-hours | USD 333,545 |
| ECRS | 34,455 | 663,867 MW-hours | USD 471,439 |
| Non-Spin | 43,693 | 957,742 MW-hours | USD 1,853,114 |
| Ancillary services, all | | | USD 3,199,201 |
| Together | | | USD 14,560,994 |

No award in the month lacks its price. Per kW of each resource's highest HSL: **USD 0.68 for the month** (0.53 energy,
0.15 ancillary services). By resource: the median is USD 0.39 per kW, one in ten earned nothing, one in ten earned
USD 1.58 or more; 68 of the 320 resources had no day-ahead award of any kind all month.

**This is not what the batteries earned.** It is their day-ahead awards valued at day-ahead prices. A battery holds an
energy award in 8 percent of its hours; most of what a battery does in ERCOT is decided in real time, and that is in
the other report. For scale only: the battery page's model, for the same month, gives USD 2.87 per kW for a two-hour
battery on the day-ahead schedule and USD 2.69 with perfect foresight (4.45 and 3.94 for four hours). The two cannot
be compared until the real-time side is added.

## How a measured revenue per kW could be built

For each resource and month:

1. **Day-ahead energy.** Awarded Quantity times the Energy Settlement Point Price, each hour (this sample). A negative
   award is a purchase.
2. **Day-ahead ancillary services.** Each product's award times its MCPC (this sample).
3. **Real-time energy.** What the resource delivered less what it sold day-ahead, at the real-time price of its
   settlement point, each 15-minute interval. Delivered output: the SCED report. The guide lists, for
   `60d_ESR_Data_in_SCED`, a row per SCED run with "Base Point", "Telemetered Net Output", "State of Charge" and the
   resource's limits; `60d_SCED_SMNE_GEN_RES` is metered output by interval. Real-time prices at resource nodes: **not in the warehouse**, which holds hubs only; ERCOT publishes
   them for every settlement point.
4. **Real-time ancillary services.** The guide lists real-time awards in the same SCED file ("AS Awards REGUP",
   "REGDN", "RRSPFR", "RRSFFR", "RRSUFR", "ECRS", "NSPIN"). How a resource is settled on them against its day-ahead
   awards, and at which price, is in ERCOT's protocols and was not read this session: it has to be read before this
   step is built, not assumed.
5. **Per kW.** Over the resource's power: its highest HSL in the month (in the files), or EIA-860M's nameplate, which
   needs ERCOT's resource names matched to EIA's plants. Duration (MWh) is in neither ERCOT file: it comes from
   EIA-860M through the same match.

**What it would still leave out, and should say:** contracts and tolls outside the market; charges and make-whole
payments on the settlement statement, which is private; station power and losses. It would be market revenue at posted
prices from disclosed awards and output, not cash received. And it runs 60 days behind.

## The size of the full history

From ERCOT's public file lists, read 4 October 2026 (the lists are an index; nothing but the sample month was pulled):

| Report | Files listed | Published | Bytes | A day |
|---|---|---|---|---|
| 60-Day DAM Disclosure (13051) | 925 | 2024-03-24 to 2026-10-04, so operating days 24 January 2024 to 5 August 2026 | 7,657,472,543 (7.7 GB) | about 8 MB; the ESR file inside is 1.9 MB and 7,776 to 7,968 rows |
| 60-Day SCED Disclosure (13052) | 932 | 2024-03-24 to 2026-10-04 | 23,022,905,292 (23.0 GB) | about 12 MB |

- **The ESR file alone:** at July 2026's rate, 31 days are 244,968 rows and 58 MB unzipped. How far back the ESR file
  goes was not checked: that takes one more zip, and this session pulls nothing more. If it begins with the change of
  5 December 2025, there are about 244 operating days of it to 5 August 2026, on the order of 1.9 million rows (the
  fleet was smaller earlier, so fewer). Before it, a battery was reported as a generation resource and a load
  resource in the older files; that also was not checked.
- **A file cannot be had without its zip:** each day is one zip of every file type, so the day-ahead history is 7.7 GB
  to download to keep about 1.8 GB of it, and the real-time history 23.0 GB.
- **Before 24 January 2024** nothing is on the public list (it keeps about 925 days). Uri and 2022 to 2023, the years
  session 101 asked about, are not there: they would have to be asked of ERCOT.
- **Real-time prices at resource nodes** are a further pull, not sized here.

## A first step, if this goes ahead

The day-ahead ESR file for every day it exists (one zip to find its first day, then about 250 zips, about 2 GB), as a
warehouse table of awards; then one month of the SCED report to learn its size and shape before the real-time side is
committed to.

## Tests

`tests/test_session108.py`: an operating day is the day published less 60; whole days are kept while they fit under
the ceiling and the run stops before the day that would pass it; the sample is written outside coverage; the columns
kept are the award columns.
