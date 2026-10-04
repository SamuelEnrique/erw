# New York and SPP: the reserve quantities, the duration rules, and the fleet-limited estimate

Session 100. For the two grids the battery model holds in review (`battery_stack_review_monthly`, session 86): what
each operator procures day-ahead, how long each product must be sustained by the operator's own document, and what the
model earns when one battery cannot sell more than its share of what the market buys. Nothing here changes the page or
its tables.

## The quantities

### SPP: `spp_as_quantities`, an approved pull

`warehouse/connectors/spp_as_quantities.py`. SPP's public portal, "Day-Ahead Market Clearing"
(`https://portal.spp.org/pages/market-clearing`), one file per operating day: by hour, the MW cleared in the Day-Ahead
Market of each operating reserve product. From 2024-09-01, ceiling 300,000 rows, USD 0 (Samuel, 4 October 2026). It
holds 159,768 rows.

| | |
|---|---|
| Entity | `spp:SPP`, and `spp:SWPW` from 2026-04-01 (the file's BAA column, as it names them; the file does not say what SWPW stands for) |
| Variables | `quantity_mw_dam_regup`, `_regdn`, `_spin`, `_supp`, `_rampup`, `_rampdn`, `_uncup` |
| Unit, freq | MW; `PT1H`, `ts_utc` the hour's start (the file's GMTIntervalEnd less one hour) |
| Whole days only | a (BAA, product, day) is written only with every hour of the day; none was left out |

The files before April 2026 have no BAA column and one row an hour: the system's, written as `spp:SPP`. The file's
other columns (generation, demand, virtuals, prices) are not kept.

Means, MW, system row: Regulation-Up 459 (2024), 489 (2025), 485 (2026); Regulation-Down 408, 436, 470; Spinning
Reserve 686, 665, 680; Supplemental Reserve 720, 702, 698.

**License: public, with citation.** SPP's terms (`https://www.spp.org/terms-conditions/`, as session 85 read and
recorded them on 2026-10-04): "Permission is implicitly granted to copy and distribute (via computer network or
printed form) in whole or in part (with appropriate citation) EXCEPT when such materials will be used, in whole or in
part, within a commercial publication". A commercial use needs SPP's written authorization. Whether the ERW's site is
a commercial publication is a person's ruling; the same question stands for `spp_as_prices`.

### New York: no hourly quantity is published

NYISO's public market data (`http://mis.nyiso.com/public/`, every report in its menu read on 2026-10-04) has prices
for the day-ahead ancillary services (P-5) and no report of the MW scheduled or procured. Its Day-Ahead Market Daily
Energy Report (P-30) holds load, generation, imports and virtuals, not reserves. Its bid data (P-27, released after
three months, generators masked) holds what was offered, not what was taken. So nothing was pulled for New York, and
no table was written.

What NYISO does publish is what it sets out to procure:

- **Operating reserves:** "NYISO Locational Reserve Requirements"
  (`https://www.nyiso.com/documents/20142/3694424/Locational-Reserves-Requirements.pdf`, read 2026-10-04). For the
  New York Control Area: 10-minute spinning reserve 655 MW (half of the most severe operating capability loss,
  1,310 MW), 10-minute total reserve 1,310 MW, 30-minute reserve 2,620 MW. East of Central-East: 330, 1,200 and
  1,200 MW. Southeastern New York: 30-minute 1,300 to 1,800 MW by hour. New York City: 10-minute total 625 MW,
  30-minute 1,250 MW. Long Island: 10-minute total 120 MW,
  30-minute 270 to 540 MW.
- **Regulation:** the tariff says "The ISO shall establish and post a target level of Regulation Service for each
  hour, which will be the number of MW of Regulation Capacity that the ISO would seek to maintain as its Regulation
  Service requirement in that hour" (Market Administration and Control Area Services Tariff, Rate Schedule 3,
  section 15.3.7, Regulation Service Demand Curve, effective 9/16/2026). The posted targets were not found at an
  address the data machine could read: four addresses under `nyiso.com/documents` answered "not found", and the
  ancillary services page lists its documents by script. **No regulation quantity is held.**

## The duration rules, as each operator's document states them

### NYISO: Market Administration and Control Area Services Tariff (MST)

Read from the full tariff as NYISO's tariff viewer serves it
(`https://nyisoviewer.etariff.biz/ViewerDocLibrary/MasterTariffs/9FullTariffNYISOMST.pdf`, 3.3 MB, read 2026-10-04).

| Product | Rule | Where |
|---|---|---|
| Operating reserves (10-minute spinning, and the others) from storage | **One hour.** "The Beginning Energy Level of an Energy Storage Resource or of an Aggregation comprised only of Energy Storage Resources will be used to ensure that Operating Reserves scheduled from the Resource can be sustained for one hour if the Operating Reserves are converted to Energy." | MST section 4.4.2.1 (Real-Time Dispatch, Overview), effective 9/16/2026, docket ER26-2567-002 |
| Regulation from storage | **No time is stated.** "The ISO may reduce the real-time Regulation Capacity (in MW) from an Energy Storage Resource or an Aggregation of Limited Energy Storage Resources to account for the Energy Level of such Resource." | MST Rate Schedule 3, section 15.3.2.1 (Bidding Process), item (e), effective 9/16/2026, docket ER25-2382-002 |

So session 86's assumption of one hour for New York's spinning reserve is the tariff's own rule. For regulation the
tariff gives the operator a discretion and no number; the model's one hour stays an assumption, and the model's note
should say so in those words.

The one-hour sentence is in the section on real-time dispatch. The day-ahead section (4.2.1.3.4, Additional Parameters
for Energy Storage Resources) says the day-ahead schedule of a resource whose energy level NYISO manages "will reflect
the Resource's Energy Level constraints" and states no time. The model applies the hour day-ahead as well.

### SPP: Integrated Marketplace Protocols, Revision 119

Read from SPP's document library ("Integrated Marketplace Protocols 119 - Active Version",
`https://www.spp.org/spp-documents-filings/?id=18162`, latest revision 7/17/2026, read 2026-10-04). Session 86 had
found only the 2016 and 2017 copies.

| Product | Rule | Where |
|---|---|---|
| Regulation-Up, Regulation-Down | **60 minutes.** "The Resource is capable of deploying 100% of cleared Regulation-Up or cleared Regulation-Down within the Regulation Response Time for a continuous duration of 60 minutes." | Section 4.2.2 (Offer Submittal), resource qualifications, item (a)(ii) |
| Spinning Reserve, and Supplemental Reserve on line | **60 minutes.** A Spin Qualified Resource must self-certify "that the Resource is capable of deploying 100% of cleared Spinning Reserve and/or cleared online Supplemental Reserve within the Contingency Reserve Deployment Period for a continuous duration of 60 minutes" | Section 4.2.2, item (b)(i) |
| Supplemental Reserve from off line | **60 minutes**, in the same words | Section 4.2.2, item (c)(i) |

So session 86's assumption of one hour for all four of SPP's modeled products is the protocols' own rule.

One more rule, for a storage resource's state of charge in the market's clearing: "For enforcement of the Maximum
State of Charge constraint, cleared Regulation-Up, Regulation-Down and cleared Contingency Reserve will impact the
Resource's State of Charge by 50% of the cleared product" (section 4.2.2.1, Resource Offer Parameters, items (58)(a)
and (59)(a), for a resource registered as a Market Storage Resource). The model holds a full hour of energy behind
each MW awarded, which is the qualification rule and is stricter than the clearing's.

## The fleet-limited estimate

`warehouse/analysis/battery_fleet_limited_review.py`, session 74's method for ERCOT applied to the two grids: in each
hour, one battery's award of a product per MW of its power is at most the MW the operator procures divided by the
grid's operating battery MW of the month (EIA-860M via `storage_buildout_monthly`), and never above 1. Prices and the
program are the page's. Analysis only: it writes daily files under `warehouse/output/analysis_internal/` and no table.

### SPP

From `spp_as_quantities`, all four modeled products. SPP's battery fleet was 29.5 MW until April 2025, 199.5 MW from
May 2025, 451.5 MW from December 2025 and 490.5 MW by July 2026.

| | 2024, from September | 2025 | 2026, to 3 October |
|---|---|---|---|
| Days with a cap under 1 in some hour | 0 of 122 | 31 of 365 | 267 of 275 |
| Fleet-limited over price-taker, day-ahead strategy, 2, 4 and 8 hours | 100.00 percent each | 99.85, 99.86, 99.88 | 97.33, 97.78, 97.98 |
| The same, perfect foresight | 100.00 each | 99.88, 99.89, 99.90 | 97.88, 98.20, 98.39 |
| At 4 hours, day-ahead, USD per kW: price-taker, fleet-limited | 47.77, 47.77 | 162.59, 162.37 | 123.69, 120.94 |

The cap that binds is regulation's: the fleet reached the size of the regulation market (about 480 MW each way) in
2026. Spinning and Supplemental Reserve are bought in larger quantities than the fleet; their caps are 1 in almost
every hour. Two days are left out (a price not held).

### New York

Spinning reserve: the cap uses the control area's requirement, 655 MW, in every hour, against a fleet of 213.5 MW
(September 2024) to 268.7 MW (August 2026). **The cap never binds:** the fleet is smaller than the requirement.

Regulation: no quantity is held, so no cap can be computed. Two cases are solved, and neither is the estimate:

| USD per kW, 4 hours | 2024, from September | 2025 | 2026, to 4 October |
|---|---|---|---|
| Day-ahead strategy: regulation not capped (the page's price-taker) | 26.15 | 138.43 | 159.14 |
| Day-ahead strategy: no regulation sold | 21.82 | 112.50 | 105.34 |
| The second over the first | 83.44 percent | 81.27 | 66.19 |
| Perfect foresight: not capped, none sold | 30.73, 26.82 | 172.82, 150.22 | 177.17, 127.92 |

The fleet-limited figure lies between the two. With NYISO's regulation targets it could be computed.

## Fit to open?

- **SPP: yes, on the model's side.** Every modeled product's duration rule is now the operator's own (60 minutes),
  the quantities are held hour by hour, and the fleet limit takes nothing off 2024, a tenth of a percent off 2025 and
  two to three percent off 2026. What stands between SPP and the page is not the model: SPP's terms except "a
  commercial publication" from the permission to copy, and that is a person's ruling. Two things to say on the page
  if it opens: the model earns almost all of its reserve income from Regulation-Up (session 86), and the ramp and
  uncertainty products are not modeled.
- **New York: not yet.** The reserve rule is verified and the spinning reserve cap never binds. But regulation is 28
  to 73 percent of the model's New York figure by year, strategy and duration (with none sold the battery keeps 63 to
  89 percent of the figure, the freed power going to spinning reserve and energy), its duration is an assumption the
  tariff does not settle, and its quantity is not held. With the posted regulation targets (a document to find, or to ask NYISO for)
  the last two could be closed; until then the page would be showing a number whose largest uncertainty is not stated
  in a form a reader could use.

## To carry the verified rules onto the page (not done: the live battery page reads these notes in its internal view)

In `warehouse/derived/battery_stack.py`: replace `SPP_ASSUMED` with the citation above for the four products; replace
`NYISO_ASSUMED` for spinning reserve with MST section 4.4.2.1, and for regulation with "assumed: one hour; MST Rate
Schedule 3 section 15.3.2.1(e) states no time"; then rebuild the review table. After the freeze.

## Checks

`tests/test_session100.py`: the connector on files made for the test (with and without the BAA column, an empty cell,
a changed layout), with no request; the shared framework's new options and that the other reserve connectors keep
their unit and their ceiling; the caps; that every quotation above is in the document as saved on the data machine
(`runs/session100/`, not in git); and the table as built.
