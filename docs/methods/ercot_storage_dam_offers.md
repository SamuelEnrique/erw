# Method: what Texas's storage resources offered day-ahead

Energy Research Warehouse (ERW), session 116. Tables: `ercot_storage_dam_offers_daily` (series, derived, public; the
fleet by operating day) and `ercot_storage_dam_offers_monthly` (series, derived, public; the fleet by month). Code:
`warehouse/derived/ercot_storage_dam_offers.py`. Page: the section "Where the gap comes from: what was offered
day-ahead" of `/cost-of-power/battery/awards` (in review). Tests: `tests/test_session116.py` (the tables) and `tests/test_session116_page.py` (the page). It follows [`ercot_storage_dam_awards.md`](ercot_storage_dam_awards.md), which
describes the source, the pull and the awards.

## What this is not

**Day-ahead offers and awards only: no real-time offers, no state of charge, no contracts.** An offer is counted at
any price, so capacity offered at the market's cap is in the offered total; that is why the price bands are there.
Like the awards table, it is not what any battery earned.

## The source

ERCOT's "60-Day DAM Disclosure Reports" (EMIL NP3-966-ER, report type 13051): one zip a day, public, posted 60 days
after the operating day. Session 115 saved the zip of every operating day from 6 December 2025, the first day the
Energy Storage Resource files exist, under `warehouse/raw/ercot_60d_dam/zips/`. The offers were read from those zips:
no request was made for them. Two files of each zip are read, every value as ERCOT prints it:

| File | A row is | What is read |
|---|---|---|
| `60d_DAM_ESR_Data` | a resource and hour | its limits (HSL, LSL), its status, its Energy Bid/Offer Curve (`QSE submitted Curve-MW1` to `MW10` and `Price1` to `Price10`), its awards and their prices |
| `60d_DAM_ESR_ASOffers` | a resource, hour and offer | up to five blocks, each a quantity (`QUANTITY MW1` to `MW5`) and a price for each Ancillary Service the block is offered to |

**License: public.** ERCOT's terms (`https://www.ercot.com/help/terms`), quoted: "The publicly available contents of
this website may be used, reproduced, and redistributed, provided that the contents are not modified and that you
maintain all copyright and other notices contained in the contents, including this Agreement. Notwithstanding the
foregoing, raw data provided in public portions of this website may be used, reproduced, and redistributed in
compilations, charts, and analyses without maintaining such notices."

## How a curve is read

A resource's Energy Bid/Offer Curve is one curve of up to ten points, from charging (negative MW, a bid to buy) to
discharging (positive MW, an offer to sell), its prices never falling from one point to the next. It is read as
straight lines between its points: below the first point's price the first point's MW, above the last point's price
the last point's MW, and where two points share a price, the higher MW.

**The check that this is how ERCOT clears it:** on 98.5 percent of the 879,837 resource-hours with a curve (866,336),
the day-ahead energy award is the curve's MW at the hour's own day-ahead price at the resource's settlement point,
within 0.1 MW. The builder writes that count to its log on every run.

From the curve, each resource and hour:

- what it offers to sell at any price: its highest MW, when above zero (`energy_offer_mwh`);
- what it offers to sell at a price of P or less, for P of 0, 25, 50, 100, 250 and 1,000 USD per MWh
  (`energy_offer_mwh_le_<P>`);
- what it offers to sell at the hour's own day-ahead price (`energy_offer_mwh_at_clearing`);
- the same for the charging side: the most it bids to buy and what it bids to buy at the hour's own price
  (`energy_bid_mwh`, `energy_bid_mwh_at_clearing`).

A curve whose MW or prices fall from one point to the next, or a point with a MW and no price, stops the day.

## How the blocks are counted

- **Blocks add up within an offer.** Across the days held, a resource's award for a service never exceeds the sum of
  its blocks priced for that service and often exceeds the largest single block. So the offered quantity is the sum.
- **A resource has up to two offer rows an hour:** one for the upward services, where one block can carry a price
  for several of them (Regulation Up, the three kinds of Responsive Reserve, ECRS, Non-Spin), and one for Regulation
  Down. A block priced for several services is counted under each of them (`<service>_offer_mwh`) and once in
  `as_offer_mwh`.
- **Counted as printed, not capped.** A resource's blocks sometimes add up to more than its limit. Nothing is cut.
- **Responsive Reserve** is a block priced for any of its three kinds (PFR, FFR, UFR), at the lowest of those prices;
  ECRS and Non-Spin likewise take their online and offline columns together.
- **At or below the clearing price** (`<service>_offer_mwh_le_mcpc`) compares each block's price with the hour's
  Market Clearing Price for Capacity, which ERCOT prints on the rows of the ESR data file. An hour with a block and
  no clearing price printed stops the day; it is never valued at another price.
- **Offers by a resource with no row in the ESR data file that hour** have no limit, status or award to be set
  beside. They are in `as_offer_mwh_unlisted` and in no other sum: 68,899 MWh over January to July 2026, against
  82.9 million MWh of blocks counted.

## The tables

One entity, `ercot:esr_fleet`. The daily table's `ts_utc` is the operating day (local, Central) at 00:00:00Z; the
monthly table's is the first day of the local month. A "MWh" here is a MW for an hour: of limit, of offered or
awarded capacity, or of energy. Today the daily table holds 243 operating days (6 December 2025 to 5 August 2026) in
18,954 rows, and the monthly table 9 months in 819 rows.

| Variable | What it is |
|---|---|
| `resources` (daily only), `resource_hours` | resources with a row that day; rows |
| `resource_hours_energy_offer`, `_as_offer`, `_no_offer`, `_out` | rows with an energy curve; with an Ancillary Service offer; with neither; with status OUT |
| `limit_mwh` | the sum of HSL, hour by hour (a negative HSL counts as zero) |
| `limit_mwh_out` | of it, rows with status OUT |
| `limit_mwh_no_offer`, `limit_mwh_no_offer_out` | of it, rows with no energy curve and no Ancillary Service offer; those of them with status OUT |
| `limit_mwh_energy_offer`, `limit_mwh_as_offer` | of it, rows whose curve offers to sell; rows with an Ancillary Service offer |
| `limit_mwh_award` | of it, rows with any day-ahead award |
| `energy_offer_mwh`, `energy_offer_mwh_le_<P>`, `energy_offer_mwh_at_clearing` | the curve's offers to sell, as above |
| `energy_bid_mwh`, `energy_bid_mwh_at_clearing` | the curve's bids to buy, as above |
| `energy_sold_mwh`, `energy_bought_mwh` | the awards, as in `ercot_storage_dam_awards_monthly` |
| `<service>_offer_mwh` | the blocks priced for the service, added up; services `regup`, `regdn`, `rrs`, `ecrs`, `nspin` |
| `<service>_offer_mwh_le_mcpc` | of it, blocks priced at or below the hour's clearing price |
| `<service>_offer_mwh_le_<P>` | of it, blocks priced at P or less, for P of 1, 5, 20, 100 and 1,000 USD per MW |
| `<service>_award_mwh`, `<service>_award_usd` | the awards, and the awards at the clearing price |
| `<service>_unawarded_usd` | offered less awarded, each resource and hour, at the hour's clearing price |
| `as_offer_mwh`, `as_award_mwh`, `as_offer_mwh_unlisted` | every block once; the five services' awards; the blocks of resources with no row in the ESR data file |
| `mw` (monthly only) | the month's fleet, from `ercot_storage_dam_awards_monthly` |
| `<service>_award_usd_per_mw`, `<service>_unawarded_usd_per_mw` (monthly only) | over the month's `mw`, USD/MW; per kW is this over 1,000 |
| `days_held`, `days_missing`, `days_in_month` (monthly only) | as in the awards table |

Rules:

- **Nothing is filled, capped or smoothed.** A day whose zip is missing or fails a check has no row. A month is the
  sum of its days held and is never scaled to a whole one.
- **The monthly table is checked against the awards table before it is written:** each month's days held, its
  resource-hours, its energy sold and bought, and each service's awards at the clearing price have to agree with
  `ercot_storage_dam_awards_monthly`. If one does not, one of the two tables is stale and nothing is written.

## The gap in three parts

The page sets the awards beside the battery page's model (`battery_stack_monthly`, a 2-hour battery on the day-ahead
schedule at the hub average; [`battery_stack.md`](battery_stack.md)) over the months that the awards table, the
offers table and the model all hold whole. Over January to July 2026 the model's figure is USD 30.14 per kW and the
awards USD 6.53: a gap of USD 23.61. The page splits the gap by an identity, computed from the three tables each
time it is rendered (`site/lib/storageawards.ts`, `gapOf`):

1. **Never offered** = the model's total times the share of the fleet's limit-hours that carried no day-ahead offer
   of any kind, `sum(limit_mwh_no_offer) / sum(limit_mwh)`. Over January to July 2026: 32.2 percent, of which 6.5
   points were resources with status OUT; USD 9.70 per kW. **This part is an allocation, not a measurement.** It
   assumes the hours and resources that offered nothing would have made what the model makes on average.
2. **Price**, energy only = `Va x days x (Pm - Pa) / 1000`, where `Va` is the awards' MWh sold per MW per day (each
   month's `energy_sold_mwh` over its `mw`, the months added up, over the days), `Pm` the model's energy revenue per
   MWh it discharges, and `Pa` the awards' energy revenue net of charging per MWh sold. Over January to July 2026:
   USD -0.62 per kW. The fleet netted more on each MWh it sold (USD 45.16) than the model does on each MWh it
   discharges (USD 37.67), so price narrows the gap. In Ancillary Services there is no price part: every awarded MW
   is paid the hour's one clearing price, the same price the model takes.
3. **Offered and not awarded** = the gap, less the other two: USD 14.53 per kW. It is the remainder, which is why
   the three add up to the gap exactly.

Beneath the three, the page shows what the offers say, from the same months:

- **Energy.** The curves offered to sell on 48 percent of limit-hours, 10.7 MWh per MW per day at any price, against
  the 1.81 the model's battery discharges. 88 percent of it was priced above USD 1,000 per MWh and 92 percent above
  USD 100. At each hour's own price the curves offered 0.41 MWh per MW per day, and 0.39 was awarded.
- **Ancillary Services.** For each service: offered, offered at or below the clearing price and awarded, each as a
  share of limit-hours; the awards and the model's figure per kW; and the offered and unawarded capacity at the
  clearing price (`<service>_unawarded_usd_per_mw`). Where that value is at least the service's gap, the gap there is
  capacity offered and not awarded; where it is less, the rest of the gap is capacity the fleet did not offer to
  that service. Over January to July 2026 it is at least the gap in Responsive Reserve, ECRS and Non-Spin, 93 percent
  of the gap in Regulation Up (USD 3.73 of 4.02) and 33 percent in Regulation Down (USD 1.74 of 5.23).

Two cautions go with the last column:

- **The services overlap.** A block can be priced for several services and awarded to one, so the services'
  unawarded values count the same capacity more than once and must not be added to a total.
- **It is not a forecast.** The unawarded offers are valued at the price that was set. Had they been awarded, the
  price would have been lower.

## The standing daily pull

Approved in session 116: one zip a day of the same disclosure, in the daily run, under `warehouse/health.py`.
`python warehouse/connectors/ercot_dam_esr.py --daily`, started by `warehouse/scheduled.py ercot_storage_dam`, asks
ERCOT for the zip of the next operating day after the last one held and for no other, adds that day to the tables,
and rebuilds the monthly ones. So the tables stay 60 days behind ERCOT's calendar and no further. A zip is never
asked for twice.

## What the offers still cannot show

- **Why a resource offered nothing.** An outage is visible (status OUT). For the rest the file gives no reason:
  state of charge, a real-time strategy, a contract, or Ancillary Services its scheduling entity arranged itself,
  which ERCOT discloses by entity (`60d_DAM_QSE_Self_Arranged_AS`) and not by resource.
- **What the capacity not offered or not awarded day-ahead did in real time.** That is the 60-Day SCED Disclosure,
  which the warehouse does not hold.
- **How much energy stood behind the offered power.** The file has no state of charge and no duration, so MWh
  offered on paper cannot be read as MWh deliverable.
- **What the market would have paid had more cleared.**
- **Which service an unawarded block would have gone to.**
