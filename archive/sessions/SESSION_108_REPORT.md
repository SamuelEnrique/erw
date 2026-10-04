# Session 108 report: what real batteries earned, scoping

**Scoped. One sample month was pulled and nothing more.** ERCOT publishes, 60 days late, what each storage resource was awarded and at what price. A month of the day-ahead side is on the data machine (244,968 rows of the 300,000 ceiling, kept out of coverage). It is enough to say what a measured revenue per kW would take, and it is not yet that measure. The full note: `docs/methods/ercot_disclosure_scoping.md`. No page; no table; one push to carry the code and the note to main, with its snapshot.

## Read these first

1. **The data exist, by resource and hour, and they are public.** ERCOT's "60-Day DAM Disclosure Reports" (NP3-966-ER) has a file for Energy Storage Resources, `60d_DAM_ESR_Data`: for each resource and hour, its awarded energy, the price at its own settlement point, and its award and clearing price for each ancillary service. Each row names the resource and its scheduling entity.
2. **In July 2026, 332 storage resources' day-ahead awards, each at the price in its own row, come to USD 14.56 million: USD 0.68 per kW for the month** (0.53 energy net of charging, 0.15 ancillary services), over 21,365 MW (the sum of each resource's highest limit in the month).
3. **That is not what the batteries earned, and I do not set it beside the page's figure as if it were.** A battery holds a day-ahead energy award in 8.0 percent of its hours. Most of what a battery does in ERCOT is decided in real time, which is the other report. For scale only: the page's model for the same month gives USD 2.87 per kW for two hours on the day-ahead schedule (2.69 with foresight). The gap between 0.68 and 2.87 is mostly the real-time side that is not in the sample, not a finding about the model.
4. **The real-time side is three times the size and needs a table the warehouse does not hold.** The "60-Day SCED Disclosure Reports" list 23.0 GB for the same 932 days. And real-time prices at each resource's own node are not in the warehouse, which holds hubs.
5. **The public list goes back to operating day 24 January 2024 and no further.** The years session 101 asked about (2018 to 2023, Uri among them) are not on it. They would have to be asked of ERCOT.
6. **Two things I did not check, because checking them is another pull:** the first day the ESR file exists (one more zip would say), and how batteries were reported before it. The note says so where it gives the history's size.

## What ERCOT's documentation says

Read: the data product page for NP3-966-ER, ERCOT's "Disclosure Reports Column Definitions Guide" (v2.4, the sheet "60Day Disclosure Reports"), the user guides page, and the terms of use.

- The report "contains all 60-day disclosure data related to the Day-Ahead Market (DAM)"; audience public, security classification public; a zip a day; rule "NP3.2.5(12) PUCT Substantive Rule §25.506"; first run 29 January 2011.
- The ESR file, in the guide's words: "The ESR Resource name and the ESR Resource's Three-Part Supply Offer (prices and quantities), including Startup Offer and Minimum-Energy Offer, available for the DAM; The award of each Three-Part Supply Offer from the DAM and the name of the QSE receiving the" award. 48 columns; the ones that matter: Awarded Quantity, Settlement Point Name, Energy Settlement Point Price, and for each of Regulation Up, Regulation Down, Responsive Reserve (three kinds), ECRS and Non-Spin, the award and the MCPC; and the resource's limits, HSL and LSL.
- The real-time file for storage (`60d_ESR_Data_in_SCED`, in the SCED report), by the guide: a row per SCED run with Base Point, Telemetered Net Output, State of Charge, the limits, and real-time ancillary service awards.

**License, quoted** (`https://www.ercot.com/help/terms`, read today): "The publicly available contents of this website may be used, reproduced, and redistributed, provided that the contents are not modified and that you maintain all copyright and other notices contained in the contents, including this Agreement. Notwithstanding the foregoing, raw data provided in public portions of this website may be used, reproduced, and redistributed in compilations, charts, and analyses without maintaining such notices." Public. The files name each resource and its scheduling entity; that is ERCOT's own disclosure under the rule above.

## The sample pull

`warehouse/analysis/ercot_disclosure_sample.py --month 2026-07`. **32 requests** to `ercot.com` (the file list and the 31 daily zips of the operating days 1 to 31 July 2026, 339 MB, one a second), USD 0. Before it, to find and read the documentation: 6 requests (the product page, two file lists, the user guides page, the guide, and one zip of one day to see its shape, which is one of the 31). **Nothing else was pulled**: the second file list is an index, read to size the real-time history.

| | |
|---|---|
| Rows | 244,968, of a ceiling of 300,000 (the script keeps whole days while they fit and stops before the day that would pass it; all 31 fit) |
| Where | `warehouse/output/analysis_internal/ercot_60d_dam_esr_awards_2026-07.csv`, outside git. **Not in coverage**, the archive, Redivis or Supabase. The zips are under `warehouse/raw/ercot_60d_dam/` |
| Kept | the award columns, the limits, the resource, its scheduling entity and settlement point; the offer curve is left out |

**What it holds:** 332 resources (324 to 332 a day), 114 scheduling entities, 287 settlement points, every hour ending 1 to 24. Status ON in 204,841 resource-hours, OUT in 24,663, ONTEST in 15,464. The largest resource is 240 MW, the median 50 MW.

| | Resource-hours with an award | Awarded | At its own price |
|---|---|---|---|
| Energy sold | 11,527 | 280,537 MWh | USD 16,382,077 |
| Energy bought (charging) | 8,005 | 242,250 MWh | USD 5,020,285 |
| Regulation Up | 17,114 | 361,292 MW-hours | USD 289,277 |
| Regulation Down | 14,120 | 250,228 MW-hours | USD 251,826 |
| Responsive Reserve | 28,091 | 759,894 MW-hours | USD 333,545 |
| ECRS | 34,455 | 663,867 MW-hours | USD 471,439 |
| Non-Spin | 43,693 | 957,742 MW-hours | USD 1,853,114 |
| Together (energy net, plus ancillary services) | | | USD 14,560,994 |

No award lacks its price. By resource, per kW: the median USD 0.39, one in ten nothing, one in ten USD 1.58 or more; 68 of the 320 resources with a positive limit had no day-ahead award of any kind all month.

## How a measured revenue per kW could be built

1. **Day-ahead energy:** award times the settlement point price, each hour (the sample).
2. **Day-ahead ancillary services:** each award times its MCPC (the sample).
3. **Real-time energy:** what the resource delivered less what it sold day-ahead, at the real-time price at its own node. Delivered output is in the SCED report. Node prices are a pull the warehouse has not made.
4. **Real-time ancillary services:** the awards are in the SCED file. How they settle against the day-ahead awards is in ERCOT's protocols, **which I did not read this session**; that has to be read before this step is built.
5. **Per kW:** over the resource's highest limit (in the files), or EIA's nameplate, which needs ERCOT's resource names matched to EIA's plants; duration comes only through that match.

**What it would still not be:** cash received. Contracts and tolls, charges and make-whole payments on the private settlement statement, station power: none is disclosed. It would be market revenue at posted prices from disclosed awards and output, 60 days behind.

## The size of the full history

| Report | Files on the public list | Operating days | Bytes |
|---|---|---|---|
| 60-Day DAM Disclosure | 925 | 24 January 2024 to 5 August 2026 | 7,657,472,543 (7.7 GB), about 8 MB a day; the ESR file inside is 1.9 MB a day and 7,776 to 7,968 rows |
| 60-Day SCED Disclosure | 932 | the same span | 23,022,905,292 (23.0 GB), about 12 MB a day |

A file cannot be had without its zip. If the ESR file begins with the market change of 5 December 2025, there are about 244 days of it: about 2 GB to download and on the order of 1.9 million rows. That "if" is the thing not checked.

## Tests and checks

- `tests/test_session108.py`, 5 tests, on zips made for the test: an operating day is the day published less 60; the award columns are kept and the offer curve is not; a zip with no ESR file stops the run; whole days are kept under the ceiling and the run stops before the day that would pass it; the sample is outside coverage and the script writes no warehouse table; the note says what was and was not read.
- Every session's tests on this machine before the push: 771 ran; one fails and is not this session's (the interchange ceiling, as before).

## Errors and decisions

1. **A first draft of the note named an identifier for the real-time report that I had not read from its page,** and described how real-time ancillary services settle from memory. Both are out: the note now says the page was not read and the settlement rule has to be.
2. **The denominator is each resource's highest HSL in the month,** the only measure of power in the file. It counts a resource that was out or testing; a per kW over EIA's nameplate would differ.
3. **No model call. Model spend USD 0.00.** No table, no load, no page. MISO stays paused.

## For Samuel

1. **Whether to go ahead, and how far.** The cheap step: one more zip to find the ESR file's first day, then the day-ahead file for every day it exists (about 2 GB to download) as a warehouse table of awards. That alone gives "what batteries were awarded day-ahead", by resource, honestly labeled. The dear step is the real-time side (23 GB and node prices).
2. **The protocols on real-time settlement of ancillary services** want reading by someone who will own the measure.
3. **The years before 2024** are a request to ERCOT.

Energy Research Warehouse (ERW), session 108, on the old laptop (`samueloldlaptop`, data role), 2026-10-04 from about 21:32 to 21:50 UTC, unattended.
