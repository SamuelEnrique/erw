# ERCOT storage in real time: what the fleet did after the day-ahead market closed

Energy Research Warehouse (ERW), session 120 (5 October 2026). Tables: `ercot_sced_esr_hourly`,
`ercot_rtm_node_prices`, `ercot_storage_rt_monthly`, `ercot_storage_node_basis`. Code:
`warehouse/connectors/ercot_sced_esr.py`, `warehouse/connectors/ercot_rt_spp.py`,
`warehouse/derived/ercot_storage_realtime.py`. Page: the last section of `/cost-of-power/battery/awards` (in review).

## What it still leaves out

Read this first. The tables add the real-time energy market to the day-ahead awards
([`ercot_storage_dam_awards.md`](ercot_storage_dam_awards.md)). They are still not what any battery earned. Not in
these files, and so in no figure:

1. **Contracts.** A toll, a hedge, a capacity sale outside ERCOT's markets. No public file holds them.
2. **The price at each battery's own node.** ERCOT settles real-time energy at the Resource Node and charging at the
   price at the resource's bus (below). The node price of a disclosed day is not public (below). Real-time energy is
   valued at the hub average's price (`HB_HUBAVG`), a stand-in, and every variable that rests on it carries `_hub` in
   its name.
3. **Real-time ancillary service money.** The disclosure holds each resource's real-time award of each service. ERCOT
   settles the difference from the day-ahead award at the service's real-time price, which neither approved file
   holds and the warehouse does not hold. The quantities are in the table; no dollar figure is put on them.
4. **Charges and credits of the settlement statement**: set point deviation charges, make-whole payments, uplift,
   fees.
5. **The meter.** Real-time energy here is telemetry integrated between dispatch runs. ERCOT settles on the
   settlement meter. The disclosure's metered file (`60d_SCED_SMNE_GEN_RES`) does not hold the storage resources: on
   5 August 2026 it holds none of the 339.
6. **The weeks from 6 December 2025 to 31 January 2026.** The pull's ceiling did not fit them (below).

## How ERCOT settles a storage resource since 5 December 2025

On 5 December 2025 ERCOT began co-optimizing energy and ancillary services in real time, and a battery became one
resource (an Energy Storage Resource, ESR) in place of a generator and a load. The sections below are from the ERCOT
Nodal Protocols as read on 5 October 2026: Section 4, Day-Ahead Operations, dated 1 August 2026, and Section 6,
Adjustment Period and Real-Time Operations, dated 28 August 2026 (`https://www.ercot.com/mktrules/nprotocols/current`).

| What | Section | The rule, in short |
|---|---|---|
| Energy sold day-ahead | 4.6.2.1, Day-Ahead Energy Payment | `DAESAMT = (-1) * DASPP * DAES`: the award times the day-ahead Settlement Point Price at the point of the offer, by hour |
| Energy bought day-ahead | 4.6.2.2, Day-Ahead Energy Charge | the same for a cleared bid: the charge is the day-ahead price times the MW bought |
| Ancillary services awarded day-ahead | 4.6.4.1, Payments for Ancillary Services Procured in the DAM (4.6.4.1.1 for Regulation Up) | `PCRUAMT = (-1) * MCPCRU_DAM * PCRU`: the award times the service's day-ahead clearing price for capacity |
| Real-time energy | 6.6.3.1, Real-Time Energy Imbalance Payment or Charge at a Resource Node | by 15-minute Settlement Interval: the resource's metered output at its node's real-time price, and at the node's Real-Time Settlement Point Price a quarter of the hour's day-ahead purchases less a quarter of its day-ahead sales (and trades). So what is settled in real time is the deviation from the day-ahead position |
| Charging in real time | 6.6.3.1 | `WSLAMTTOT = sum of RTRMPRESR_b * MEBL` and `ESRNWSLAMTTOT = sum of RTRMPRESR_b * MEBR`, with `RTRMPRESR_b = Max[-$251, (sum of RNWFL * RTLMP at the bus) + RTRDP]`: the energy an ESR draws is settled at the price at its own electrical bus, not at a Load Zone |
| Real-time ancillary services | 6.7.2.1, Real-Time Ancillary Service Imbalance Payment or Charge; 6.7.2.2 for Regulation Up, 6.7.2.3 to 6.7.2.6 for the others | the real-time award less the day-ahead award (less self-arranged quantities, with trades), times the service's real-time clearing price |
| Deviation from instructions | 6.6.5.5, Energy Storage Resource Set Point Deviation Charge for Over Performance; 6.6.5.5.1 for Under Performance | a charge when the resource strays from its set point beyond a tolerance |

What the tables compute follows the first four rows, with one substitution: the hub average's real-time price stands
where the protocols have the node's. The fifth row is why charging is valued at the same price as discharging here:
the protocols settle it at the resource's bus, and the bus price is not public either. The last two rows are left out.

## The sources

**60-Day SCED Disclosure Reports** (EMIL NP3-965-ER, report type 13052). ERCOT posts a zip each day for the operating
day 60 days before. In ERCOT's words: "This report contains all 60-day disclosure data related to Security Constrained
Economic Dispatch (SCED)." Since the market change a zip is about 56 MB. The file read is `60d_ESR_Data_in_SCED`: a
row for each ESR and each SCED run, about every five minutes (98,310 rows for 339 resources on 5 August 2026), with
its limits, Base Point, Telemetered Net Output, State of Charge and real-time ancillary awards. Its offer curves (160
of 198 columns) are not read.

**Settlement Point Prices at Resource Nodes, Hubs and Load Zones** (EMIL NP6-905-CD, report type 12301). A small zip
for each 15-minute Settlement Interval with the real-time price of every settlement point. A file's stamp is the end
of its interval; the interval is read from the file's own columns. ERCOT prints a Load Zone twice, as type `LZ` and as
type `LZEW`, and the two prices can differ: the table keeps the `LZ` row.

### Measured before pulling, and what the ceilings did

The approved ceilings were 12 GB of downloads and 9,000,000 stored rows in all.

- ERCOT's list of the SCED report on 5 October 2026: 932 zips, 23.0 GB. From the operating day 6 December 2025: 249
  zips, 15.2 GB, of which the regular daily zips are 13.4 GB for 243 days. That passes 12 GB. **So the pull takes the
  most recent months that fit: 1 February to 5 August 2026**, 186 operating days. The 57 days from 6 December 2025 to
  31 January 2026 were not pulled. Nothing stands in for them.
- One day measured first (5 August 2026): the storage file is about 100 MB of text; reduced, it is 8,136
  resource-hours. Each day is reduced as it is read and the zip is kept under `warehouse/raw/ercot_60d_sced/zips/`
  with a manifest (file, document id, bytes, SHA-256, when retrieved).
- **ERCOT's public list keeps seven days of node prices.** On 5 October 2026 it held 690 intervals, from the one
  ending at 00:00 on 28 September. The storage disclosure is 60 days old when it is posted. So the two never meet: the
  node prices of a disclosed day left the list 53 days before the disclosure appeared. The node prices for February to
  August 2026 cannot be had from the public list at any ceiling. The pull took what was listed, one week, and that
  week is used only to measure how far the nodes stand from the hub.

## From SCED runs to hours (`reduce_day`)

- A run's stamp is Central prevailing time. It is read to UTC before anything is measured, so the day the clocks go
  forward is 23 hours of runs and not a gap. A day with a repeated hour (the autumn change) is left out with its
  reason; no such day is in the months pulled.
- The day's SCED clock is every stamp in the file, whichever resources a run holds. A resource's MW at a run holds
  until the next run on that clock (the day's last run until local midnight). A resource a run does not hold has no
  energy for that run: its last value is never carried. (On 5 February 2026 one resource is in the file until 00:30
  and not after.)
- Each run's interval is cut at the 15-minute boundaries it crosses. `net_output_mwh` is the hour's sum,
  `x_net_q1_mwh` to `x_net_q4_mwh` the four Settlement Intervals', which add up to it. `x_discharge_mwh` and
  `x_charge_mwh` are the positive and the negative part. The ancillary awards are integrated the same way (a MW for
  an hour). A blank award in ERCOT's file is no award.
- A day stops, and is recorded in `days/missing.csv` with its reason, when: a stamp cannot be read, a row is of
  another day, a resource repeats a stamp, a Resource Type is not ESR, ERCOT flags a repeated hour, or two runs are
  more than an hour apart. Nothing is filled for it.
- An hour of a resource with no run in it has no row.

## The month (`ercot_storage_rt_monthly`)

One entity, `ercot:esr_fleet`, by local (Central) month, over the operating days both disclosures hold.

- `mw`: the sum of each resource's highest day-ahead High Sustained Limit in the month, the same denominator as the
  awards table, so that the figures per MW add up across the two.
- `rt_discharge_mwh`, `rt_charge_mwh`, `rt_net_mwh`; `da_sold_mwh`, `da_bought_mwh`, `da_net_mwh`;
  `rt_deviation_mwh` = real-time net less day-ahead net.
- `revenue_da_energy_usd`, `revenue_da_ancillary_usd`, `revenue_da_usd`: the day-ahead awards at their own prices
  (the node's day-ahead price for energy, the clearing price for each service). In a month whose days are the same,
  the builder checks these against `ercot_storage_dam_awards_monthly` and writes nothing if they differ.
- `revenue_rt_output_hub_usd`: for each resource and 15-minute interval, its energy times the real-time price of the
  interval at `HB_HUBAVG`.
- `revenue_da_position_hub_usd`: a quarter of its day-ahead award of the hour (sales less purchases) times the same
  price: the day-ahead position, settled back in real time.
- `revenue_rt_deviation_hub_usd` = the first less the second. `revenue_market_hub_usd` = `revenue_da_usd` plus it.
- Each revenue also `_per_mw`. A page's USD per kW is that over 1,000.
- `as_rt_<service>_mwh`, `as_da_<service>_mwh`, `as_imbalance_<service>_mwh` (regup, regdn, rrs, ecrs, nspin): a MW
  for an hour, real time, day-ahead, and the difference. Not valued.
- `intervals`, `intervals_priced`: an interval with no hub price is not valued and is counted.
- `da_node_minus_hub_sold`, `da_node_minus_hub_bought` (USD/MWh): the day-ahead price at the resources' own
  settlement points less the hub average's, weighted by the MWh sold and by the MWh bought. This is the first measure
  of what the hub price misses, taken day-ahead, where the warehouse holds both prices.

A resource-hour in one file and not the other is counted and valued on what it has: a day-ahead award with no
real-time row is a position with no output; real-time output with no day-ahead row has no position.

## One week at the nodes (`ercot_storage_node_basis`)

The second measure, in real time, over the week of node prices held. For each settlement point a storage resource is
settled at (the Settlement Point Names of `ercot_dam_esr_awards`): `intervals`, `mean_node`, `mean_hub`,
`mean_abs_difference`, and, over the whole days held, `spread_node` and `spread_hub`: a day's 16 dearest 15-minute
intervals less its 16 cheapest (four hours each), averaged over the days. The entity `ercot:esr_nodes` sums the
points up, each counted once: how many, the hub's spread, the points' median, mean, lowest and highest tenth, and how
many are wider than the hub.

It is one week, in early autumn. It is applied to no figure and nothing is adjusted by it.

## What would close the gaps (for a person to approve; none is scheduled)

1. **A standing pull of the node prices** (NP6-905-CD, about 96 small files a day, about 0.8 MB a day). ERCOT's list
   drops a day after seven. Kept from now, the node prices of a day meet its storage disclosure 60 days later, and
   real-time energy can be valued at the node as the protocols settle it. Days already dropped cannot be had from the
   public list.
2. **Real-time ancillary service prices** (the real-time clearing prices for capacity since 5 December 2025), to
   value the imbalance quantities. Not in the two approved files.
3. **The 57 days from 6 December 2025 to 31 January 2026** of the SCED disclosure, about 3 GB, above this session's
   ceiling.

## As built on 5 October 2026

What the pull and the tables held when they were first written. The page computes its figures from the tables each
time it is rendered; these are here so that a later build can be set against the first.

- Pulled: 186 zips of the SCED disclosure, 10.42 GB, and 690 interval files of node prices, 5.6 MB: 10.43 GB of the
  12 GB ceiling. Stored: 1,675,014 rows in the four tables, of the 9,000,000 ceiling.
- `ercot_sced_esr_hourly`: 1,458,735 resource-hours of 342 resources, 1 February to 5 August 2026, 186 operating
  days, none missing, none refused by a check.
- All 186 days are matched by the day-ahead disclosure. In each of the seven months the day-ahead revenue, the MWh
  sold and the MW equal `ercot_storage_dam_awards_monthly`'s. Every one of the 17,852 Settlement Intervals of the span
  has a hub price, so every resource-interval is valued.
- Over the six months held whole (February to July 2026), per kW of the fleet's MW: day-ahead awards USD 4.17;
  real-time deviations at the hub average's price USD 3.00; the two together USD 7.17. The battery page's model, one
  2-hour battery on its day-ahead schedule, makes USD 18.81 over the same months.
- Over all 186 days the fleet discharged 4,623,251 MWh in real time and had sold 1,483,064 MWh day-ahead, 32 percent
  of it. It discharged 1.26 MWh per MW per day.
- Day-ahead, the fleet sold at its own nodes for USD 0.02 to 2.49 per MWh above the hub average, by month (August's
  five days: 0.18 below), and bought for USD 1.89 to 4.90 below it.
- The week of node prices, 28 September to 4 October 2026, at 291 storage settlement points: the daily spread between
  the four dearest and the four cheapest hours averaged USD 28.27 per MWh at the hub average; at the points the
  median was USD 44.29 (a tenth of them below 25.66, a tenth above 178.62), and 227 of the 291 were wider than the
  hub. At the median point the real-time price stood USD 8.46 per MWh from the hub's in the average interval.
