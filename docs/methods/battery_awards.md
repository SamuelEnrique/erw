# Method: what Texas's batteries were awarded day-ahead, the tool as a reader meets it

Energy Research Warehouse (ERW), session 7505 (chain 304), 16 November 2026. Page: `/cost-of-power/battery/awards` (in
review). Code: `site/app/cost-of-power/battery/awards/` (`page.tsx`, `Offers.tsx`, `RealTime.tsx`, `Decisions.tsx`),
`site/lib/storageawards.ts`, `site/lib/storagerealtime.ts`. Replication: `replication/battery_awards/`. Faults found:
[`docs/reviews/battery-awards-faults-2026-11-16.md`](../reviews/battery-awards-faults-2026-11-16.md).

This note is the tool's: every view, every figure's table and rule, every choice with its default and source, and what
the tool does not hold. It does not repeat the tables' notes, which say how each table is built from ERCOT's files:

| Table (all public) | Its note | What it holds |
|---|---|---|
| `ercot_storage_dam_awards_monthly` | [`ercot_storage_dam_awards.md`](ercot_storage_dam_awards.md) | the fleet's day-ahead awards by month |
| `ercot_dam_esr_awards` | [`ercot_dam_esr_awards.md`](ercot_dam_esr_awards.md) | the same, a row a resource and hour (not in the site's database) |
| `ercot_storage_dam_offers_monthly` | [`ercot_storage_dam_offers.md`](ercot_storage_dam_offers.md) | what the fleet offered day-ahead, by month |
| `ercot_storage_rt_monthly`, `ercot_storage_node_basis` | [`ercot_storage_realtime.md`](ercot_storage_realtime.md) | the real-time side by month; the storage nodes' prices against the hub |
| `ercot_sced_esr_hourly` | [`ercot_sced_esr_hourly.md`](ercot_sced_esr_hourly.md) | real-time output, a row a resource and hour |
| `battery_stack_monthly` | [`battery_stack.md`](battery_stack.md), [`battery_earns_algorithm.md`](battery_earns_algorithm.md) | the battery page's model, set beside the awards |

This note carries no tables line of its own: each table's note above stays the one the coverage page links.

## 1. What the tool is, and what it is not

It sets what ERCOT's storage fleet was really awarded (day-ahead energy and ancillary services, then real-time
dispatch) beside what the ERW's battery model takes from the same markets. It is one page with no input: a reader
chooses nothing, and every figure is computed from the five tables each time the page is drawn.

It is not what any battery earned. The first part is day-ahead awards only, a floor on market revenue. The last part
adds real-time energy at the hub average's price, a stand-in for each battery's own node. Contracts, real-time
ancillary money, the settlement statement's charges and the meter are in no figure (section 7).

## 2. The head of the page: the awards by month and by year

All from `ercot_storage_dam_awards_monthly`, entity `ercot:esr_fleet`, and from `battery_stack_monthly`, entity
`ercot:HB_HUBAVG`, the variables that begin `dayahead_2h_` (one 2-hour battery on the day-ahead schedule).

- **A month** is the first seven characters of `ts_utc` (the Central month). It is shown when the table holds its
  `days_held`, `days_in_month`, `revenue_energy_usd_per_mw`, `revenue_ancillary_usd_per_mw` and
  `revenue_total_usd_per_mw`. It is **whole** when `days_held = days_in_month`, else partial (hatched in the chart,
  marked in the table, the held days' sum, never scaled).
- **USD per kW** is the table's USD per MW over 1,000, written with two decimals.
- **The sentence** at the top is the newest whole month: `resources`, `mw`, and the month's total, energy and
  ancillary per kW.
- **The chart** stacks each month's energy and ancillary per kW; the label over a bar is the month's total.
- **By month:** days held of the month's days, `resources`, `mw` (whole numbers), energy, ancillary and total per kW,
  and the model's `dayahead_2h_revenue_total_usd_per_mw` over 1,000 for the same month. The model's month is whole when
  `dayahead_2h_days_held = dayahead_2h_days_in_month`. Beside a partial month the model's figure is its whole month
  and is labeled so.
- **By year:** the sum of the year's months per kW (every month held, partial ones with the days they hold); the
  months held whole; the awards over those months; the model over the same months, shown only when the model holds
  every one of them whole; and the awards as a share of the model, a whole percent.
- **"Why the two differ":** the share of resource-hours that hold a day-ahead energy award is
  `sum(resource_hours_energy_award) / sum(resource_hours)` over every month held, with one decimal; and for the
  newest whole month, `resources_with_award` of `resources`.

Completed in session 7505, since the table's note did not say it: **an award printed as zero is not an award.**
`resource_hours_energy_award` counts the resource-hours whose Awarded Quantity is not blank and not zero, and
`resources_with_award` the resources with one award of any kind that is not zero in the month. Recomputed from the
disclosure's rows under that rule, both counts equal the table's in all nine months (section 5).

## 3. "Where the gap comes from": what was offered day-ahead

The rules are in [`ercot_storage_dam_offers.md`](ercot_storage_dam_offers.md), "The gap in three parts". As the page
applies them:

- **The months** are those the awards table, the offers table and the model all hold whole, with every figure the
  arithmetic reads, the offers table's `mw` and `limit_mwh` above zero. Today: January to July 2026.
- **The gap** is the model's total less the awards' total, per kW, the months added up.
- **Never offered** = the model's total times `sum(limit_mwh_no_offer) / sum(limit_mwh)`. An allocation.
- **Price** (energy only) = `S x (Pm - Pa) / 1000`, with `S` the sum over the months of `energy_sold_mwh / mw`,
  `Pm = sum(model energy revenue per MW) / sum(dayahead_2h_discharged_mwh_per_mw)` and
  `Pa = sum(awards energy revenue per MW) / S`.
- **Offered and not awarded** = the gap less the other two. Each part's share of the gap is a whole percent.
- **Energy:** the share of limit-hours whose curve offers to sell (`limit_mwh_energy_offer / limit_mwh`); MWh per MW
  per day offered at any price, at each price band, at the hour's own price, and sold: each the sum over the months
  of the month's MWh over the month's `mw`, over the sum of `days_held`; a band's share is its MWh over
  `energy_offer_mwh`; "above USD 100" and "above USD 1,000" are one less the bands at or below.
- **Ancillary services,** each of five: offered, offered at or below the clearing price and awarded as shares of
  `limit_mwh`; awarded over offered; the awards and the model per kW and their difference; and
  `<service>_unawarded_usd_per_mw` over 1,000. A service is "covered" when that last value is at least its gap.

## 4. "The real-time side"

The rules are in [`ercot_storage_realtime.md`](ercot_storage_realtime.md), "The month" and "One week at the nodes".
As the page applies them, from `ercot_storage_rt_monthly` (`ercot:esr_fleet`):

- A month is shown when it holds `days_held`, `days_in_month`, `revenue_da_usd_per_mw`,
  `revenue_rt_deviation_hub_usd_per_mw` and `revenue_market_hub_usd_per_mw`; whole as above. Its days are the
  operating days both disclosures hold.
- **The summary and the table:** over the whole months, the day-ahead awards, the real-time deviations at the hub
  average's price and the two together, per kW; the model's figure over the same months when it holds each whole; by
  month, the two together as a whole percent of the model's.
- **Energy:** over every month held, `rt_discharge_mwh`, `da_sold_mwh`, `rt_charge_mwh`, `da_bought_mwh`; sold over
  discharged; MWh discharged per MW per day = `sum(rt_discharge_mwh / mw) / sum(days_held)`; and the day-ahead price at
  the resources' nodes less the hub's (`da_node_minus_hub_sold`, `da_node_minus_hub_bought`).
- **Ancillary quantities:** each service's `as_rt_`, `as_da_` and `as_imbalance_` MW-hours, added over every month
  held. Not valued.
- **The nodes** (`ercot_storage_node_basis`, `ercot:esr_nodes`): `nodes`, `whole_days`, `spread_hub`,
  `spread_node_median`, `spread_node_p10`, `spread_node_p90`, `nodes_spread_above_hub` of `nodes_with_spread`, and
  `mean_abs_difference_median`. Since session 7505 the words follow `whole_days`: seven or fewer is "one real week",
  more is said as its days (the table held 21 whole days from 28 September 2026 while the page still said one week).

## 5. Replication and cross-check

### The replication

`replication/battery_awards/replicate.py` (Python, standard library), written from this note and the tables' notes:

- **The page:** every figure the page shows, recomputed from the five tables (and, since session 7514, the EIA's
  count in `storage_buildout_monthly`) and set beside what the page's own functions give on the same rows
  (`page_figures.json`, written by `site/scripts/battery-awards-figures.mjs`, which also draws the offers and
  real-time sections to HTML and finds each of their 224 figures in it). On 16 November 2026, on the tables as
  retrieved on 5 October (awards, offers, real time), 19 October (nodes), 21 October (the model) and 3 October 2026
  (the EIA's count): **373 of 373 figures within half the page's last shown digit, 0 named, 0 failed.** Session 7505
  counted 307 of 307 (217 in the two drawn sections); the other 66 are the figures section 8 added.
- **The file `site/data/battery_awards_beside.json`** (the battery page's line beside the real awards,
  [`battery_earns_algorithm.md`](battery_earns_algorithm.md), section 9): 24 of 24 figures.
- **The monthly tables from ERCOT's disclosure:** with `--awards`, `--sced` and `--hub`, every month of the two
  monthly tables recomputed from the rows by resource and hour (`ercot_dam_esr_awards`, 2,026,149 rows;
  `ercot_sced_esr_hourly`, 1,637,727 rows) and the hub average's real-time prices by 15-minute interval
  (`ercot_all_hub_prices_history`), over the operating days each monthly table was built on: **297 of 297 rows agree,
  9 months (December 2025 to August 2026).** For the awards table, 19 variables a month: the days, the resources and
  those with an award, the resource-hours and those with an energy award, the MW, the MWh sold and bought, each
  revenue in dollars and the three per MW. For the real-time table, 18 variables in each of 7 months: the days, the MWh
  discharged and charged, the MWh sold and bought day-ahead, the ten ancillary quantities, and the three figures per
  MW the page reads (day-ahead awards, real-time deviations at the hub price, the two together). A dollar sum agrees
  inside three cents (the table adds rounded sums; the largest difference was 1.3 cents on USD 14.6 million); every
  figure per MW agrees to the fourth decimal. `source_rows.csv` holds each row.
- **Without the warehouse:** `python replication/battery_awards/replicate.py` runs the first two parts on
  `monthly_rows.csv`, the 1,699 public rows the page reads, copied beside the script.
- **Stata:** `replicate.do`, five headline figures from `monthly_rows.csv`, the expected values at its top. Stata is
  not on the machine that wrote it, so it has not been run.

### The cross-check against published figures

Read on 16 November 2026. Each host's robots file was read before any other request to it. No figure is adjusted.

| Our figure | Ours | Published figure | Publisher, document, date | Difference | Why |
|---|---|---|---|---|---|
| The fleet's MW, December 2025 (`mw`) | 16,392 MW (6 to 31 December); 17,180 MW in January 2026 | "The installed capacity of ESRs increased to more than 17,000 MW and 31,500 MWh by the end of 2025" | Potomac Economics, *2025 State of the Market Report for the ERCOT Electricity Markets*, June 2026, page ii | at least -608 MW in December; +180 or less in January | Ours is each resource's highest day-ahead limit in the days held, theirs the capacity installed at the year's end; a resource that entered late in December, or never showed its full limit day-ahead that month, is short in ours |
| The fleet's MW, July 2026 (`mw`) | 21,365 MW, 332 resources | 18,070 MW of batteries operating in ERCOT | U.S. Energy Information Administration, Form EIA-860M, as the warehouse's `storage_buildout_monthly` holds it (`iso:ercot`, `battery_operating_mw`, July 2026) | +3,296 MW (18 percent) | ERCOT's file lists a resource from the day it can be dispatched, in testing included, at the highest limit it showed; the EIA counts a generator once its owner reports it operating, by nameplate. Over the EIA's MW every per kW figure of the page would be 18 percent higher |
| Energy offered to sell at USD 100 per MWh or less, share of all offered (the offers table) | 8.0 percent of what the day-ahead curves offered, January to July 2026 | "In 2025, 55% of energy offers were priced between $0-100 per MWh"; at the offer cap "18% in 2025" | The same report, page 24 | -47 points | Not the same market or year: theirs is the offers submitted to real-time dispatch in 2025, ours the day-ahead curves of 2026. The page's own real-time section says the fleet sold day-ahead a third of what it discharged; a battery prices most of its power out of the day-ahead market and trades it in real time |
| Day-ahead ancillary awards as a share of the two markets together | 20 percent, February to July 2026 (1.42 of 7.17 USD per kW; real-time ancillary money is not valued) | "ERCOT BESS earned 76% of revenue from energy arbitrage in June 2025": 24 percent from services | Modo Energy, *How does a battery energy storage system make money?*, 19 May 2026 (as held in `docs/methods/crosschecks/battery.md`) | -4 points | Another period, and ours leaves out real-time ancillary money. The market monitor says the same direction in words: "a shift toward ESRs earning more of their revenue from energy arbitrage than from providing ancillary services" (the report above, page ii) |
| The same | 20 percent by dollars | "ERCOT reported 8.1 GW of battery capacity, half of which was primarily used for arbitrage" (the end of 2024) | U.S. Energy Information Administration, *Utility-scale batteries are more commonly used for price arbitrage*, Today in Energy, 22 September 2025 (Form EIA-860, 2024) | none computed | Theirs is capacity by the owner's stated primary use, ours dollars awarded; the two measure different things and agree only in direction |
| Revenue per kW of the fleet | 7.17 USD per kW over February to July 2026: day-ahead awards plus real-time deviations at the hub average's price | No published figure for these months. The market monitor: "Annual revenue per unit of ESR capacity declined significantly in 2025, falling by almost 37% from 2024"; its figure per kW is the axis of a chart (Figure 17) and is not typed here. Modo Energy: "the average battery energy storage system in ERCOT earned revenues of $55 per kW" in 2024 | The report above, page 22; Modo Energy, *ERCOT: Annual battery energy storage revenue report 2024*, 19 March 2025 (as held in `docs/methods/crosschecks/battery.md`) | none computed | Six months without a summer against calendar years; ours is at the hub and not the node, without real-time ancillary money, and over every MW in ERCOT's file |
| Each ancillary service awarded, share of the fleet's limit-hours | Regulation Up 2.6 percent, Regulation Down 2.1, Responsive Reserve 6.9 (January to July 2026) | "On average, ESRs provided 94%, 86%, and 51% of Reg-Up, Reg-Down, and RRS" in 2025 | The report above, page 42 | none computed | Theirs is the fleet's share of what ERCOT bought, ours the share of the fleet's own capacity that was awarded: a fleet of about 20,000 MW fills a market of a few hundred MW with a few percent of itself. The warehouse holds ERCOT's ancillary service plan only from September 2026 (`ercot_as_quantities`), so the fleet's share of the quantity bought cannot be computed for these months |
| The gap's three parts; the node spread; the share of resource-hours with an award | 9.70, 14.53 and -0.62 USD per kW; USD 68.22 against 57.60 per MWh; 7.0 percent | Nothing published stands against them | | none | They are the ERW's own arithmetic on ERCOT's disclosure; the replication traces each to ERCOT's rows |

**Hosts.** `potomaceconomics.com`: its robots file allows every path but `/wp-admin/`; the report was read (one
request). `eia.gov`: its robots file allows `/todayinenergy/`; one article read. `ercot.com`: its robots file disallows
`/misapp` and `/misdownload`, the paths its report lists and files are served from, so no ERCOT document was asked for
in this session (the owner's ruling 2 of 6 November 2026); ERCOT's own figures stand here through its disclosure, which
the warehouse already holds, and through its market monitor's report. Modo Energy's two figures are quoted from the
battery tool's cross-check and were not read again.

## 6. The decisions on the page

The page has no input, so no choice is editable. Each choice below is fixed, moves a figure, and is drawn at the foot
of the page with its default and its source on hover (`site/app/cost-of-power/battery/awards/Decisions.tsx`;
`site/scripts/test-battery-awards-render.mjs` holds this table and that list to the same keys in the same order).

| # | Key | The choice | Default | Source |
|---|---|---|---|---|
| 1 | `fleet` | Every Energy Storage Resource with a row in the month, awarded or not, out or testing included | every resource in the file | ERCOT, 60-Day DAM Disclosure Reports (NP3-966-ER), `60d_DAM_ESR_Data` |
| 2 | `per-kw` | Per kW of the sum of each resource's highest High Sustained Limit in the month | the highest limit, every resource | ERCOT's file, HSL; the EIA's 18,070 MW (section 5) |
| 3 | `energy-price` | An energy award at the day-ahead price of the resource's own settlement point, net of charging | the row's own price | ERCOT Nodal Protocols 4.6.2.1 and 4.6.2.2 |
| 4 | `ancillary-price` | An ancillary award at the service's day-ahead clearing price; Responsive Reserve's three kinds at one price | the day-ahead clearing price | ERCOT Nodal Protocols 4.6.4.1 |
| 5 | `month` | The Central month; nothing filled; a partial month never scaled | no filling, no scaling | ERCOT's Delivery Date |
| 6 | `year` | A year is the sum of its months per kW, each over its own MW | the months added up | `ercot_storage_dam_awards.md`, "Rules" |
| 7 | `model` | The model beside the awards: one 2-hour battery, the day-ahead schedule, the hub average; whole months of both only | 2 hours, day-ahead, `HB_HUBAVG` | `battery_stack.md`; the market monitor's 17,000 MW and 31,500 MWh (about 1.9 hours) |
| 8 | `never-offered` | "Never offered" is the model's figure times the share of limit-hours with no day-ahead offer: an allocation | the model's average | `ercot_storage_dam_offers.md` |
| 9 | `price-part` | "Price" is energy only; "offered and not awarded" is the remainder | energy only | `ercot_storage_dam_offers.md` |
| 10 | `offers-counted` | An offer counts at any price, as power; a block priced for several services counts under each | as printed, not capped | ERCOT's two offer files |
| 11 | `hub-price` | Real-time energy, and charging, at the hub average's real-time price | `HB_HUBAVG`, each 15 minutes | ERCOT Nodal Protocols 6.6.3.1; NP6-905-CD |
| 12 | `deviation` | Real time values the deviation from the day-ahead position: output less a quarter of the hour's award | output less position | ERCOT Nodal Protocols 6.6.3.1; `60d_ESR_Data_in_SCED` |
| 13 | `telemetry` | Real-time energy is telemetry between dispatch runs, not the meter | telemetry | `ercot_storage_realtime.md` |
| 14 | `rt-ancillary` | Real-time ancillary awards are quantities, not valued; the statement's charges are left out | no dollar figure | ERCOT Nodal Protocols 6.7.2.1 to 6.7.2.6, 6.6.5.5 |
| 15 | `node-days` | The nodes' distance from the hub is measured on the days of node prices held and applied to nothing | 16 intervals each side, whole days | NP6-905-CD, `ercot_storage_node_basis` |

## 7. What the tool does not hold

- **Contracts, tolls and hedges; real-time ancillary money; set point deviation charges, make-whole payments and
  fees; the settlement meter; the price at each battery's own node on a disclosed day.** Each is said on the page.
- **A duration class.** ERCOT's file states power and never energy ([`ercot_storage_dam_awards.md`](ercot_storage_dam_awards.md), "No duration class").
- **Days after late August 2026.** The disclosure is listed and served under ERCOT's `/misapp` and `/misdownload`
  paths, which its robots file disallows; under the owner's ruling 2 of 6 November 2026 no new request goes there. So
  the rows by resource and hour stop where the last pull left them (day-ahead to 29 August 2026, real time to 27
  August), and the sentence in the offers note that the tables "stay 60 days behind ERCOT's calendar and no further"
  no longer holds. The page shows the days each month holds and does not say why the newest month is partial (faults
  file, row 4).
- **The weeks from 6 December 2025 to 31 January 2026 in real time** (the pull's ceiling).
- **The fleet's share of what ERCOT bought of each service** for these months (section 5).

## 8. Added by the read of 16 November 2026 (session 7514)

The page was read as a lender's analyst reads it
([`docs/reviews/battery-awards-read-2026-11-16.md`](../reviews/battery-awards-read-2026-11-16.md)). Six things were
added to the page; none changes a figure it had.

- **A month's ancillary award by service** (the hover of each month's ancillary cell in "By month"): the table's
  `revenue_regup_usd_per_mw`, `revenue_regdn_usd_per_mw`, `revenue_rrs_usd_per_mw`, `revenue_ecrs_usd_per_mw` and
  `revenue_nspin_usd_per_mw` over 1,000, two decimals each, and the ancillary figure as a whole percent of the month's
  total. A month that lacks one of the five has no hover.
- **The five services together** (the last row of the ancillary table, and the sentence under it): the sum of the five
  rows' awards and of the model's, over the months of the offers section; the same two over the number of months, per
  kW a month; and the model's over the awards. With the tables of this machine: 2.78 and 15.66 over January to July
  2026, 0.40 and 2.24 per kW a month, 5.64 times. They are the figures `site/data/battery_awards_beside.json` holds for
  `dayahead_2h` (0.3965, 2.2369, 5.6411), which the battery page draws; the test holds the two to the fourth decimal.
- **ECRS** carries its name, ERCOT Contingency Reserve Service, on hover in both service tables.
- **The fleet's MW beside the EIA's count** (the hover of the MW line of "What is counted"): a sixth read,
  `storage_buildout_monthly`, entity `iso:ercot`, the variables `battery_operating_mw`, `battery_operating_units` and
  `battery_operating_mwh_per_mw`, for the newest month the awards table holds whole. July 2026: 18,070 MW in 257
  generators holding 1.65 MWh per MW, against 21,365 MW in 332 resources here; 3,296 MW, 18 percent. When the table
  cannot be read the hover says so and no other line of the page changes.
- **The MWh beside the storage page's** (a sentence under the MWh table): words only. This page adds each resource's
  own discharge and charge; the storage page's daily cycle (`storage_daily_cycle`, from EIA-930) is the fleet's net
  output by hour. July 2026: 847,905 MWh discharged here, 705,980 there.
- **Where the node part stops** (its last paragraph): words and two links, to the ERCOT node list of the All grids tab
  (`/cost-of-power?view=allgrids&rows=nodes`) and to the battery page.

**The rules a second implementation needs,** for the 66 figures the six add (the replication's keys in brackets):

- **By service, by month** (`month|<month>|service|<service>_kw`, 45 figures; `month|<month>|ancillary_share_pct`, 9):
  for every month "By month" shows (section 2), from `ercot_storage_dam_awards_monthly`, entity `ercot:esr_fleet`. A
  service's figure is its `revenue_<service>_usd_per_mw` over 1,000, two decimals; the five are `regup`, `regdn`,
  `rrs`, `ecrs`, `nspin`. They are drawn only when the month holds all five. The share is
  `revenue_ancillary_usd_per_mw / revenue_total_usd_per_mw` times 100, a whole percent, drawn when the total is not
  zero. A partial month has its hover too, on the days it holds.
- **The five together** (`offers|five|...`, 7 figures): over the months of the offers section (section 3: January to
  July 2026 today). Awards: the sum over those months and the five services of `revenue_<service>_usd_per_mw`, over
  1,000. The model's: the same sum of `battery_stack_monthly`'s `dayahead_2h_revenue_<service>_usd_per_mw`, entity
  `ercot:HB_HUBAVG`. Gap: the model's less the awards. Each with two decimals. Per kW a month: each sum over the
  number of months (`months`, drawn as a number when there is more than one). The ratio: the model's sum over the
  awards' sum, two decimals. The sentence is drawn only when the awards' sum is above zero.
- **The EIA's count** (`inventory|...`, 5 figures): the month is the newest month the awards table holds whole (the
  month of the page's sentence). From `storage_buildout_monthly`, entity `iso:ercot`, that month's row of
  `battery_operating_mw` (whole MW), `battery_operating_units` (whole) and `battery_operating_mwh_per_mw` (two
  decimals). The difference is the awards table's `mw` of the month less the EIA's MW, as an absolute whole number of
  MW with "more" or "less". The percent is `mw` over the EIA's MW, less one, times 100, absolute, whole. No figure is
  drawn when the EIA's row for the month is missing or its MW is not above zero.
- **The MWh sentence and the node paragraph** draw no figure of their own (the node paragraph repeats `nodes` and
  `whole_days`, section 4).

The whole page is drawn without a build by `site/scripts/battery-awards-page.mjs` (the page's own function, its reads
answered from CSV rows), and `site/scripts/test-battery-awards-read.mjs` holds the six on the public rows beside the
replication (`monthly_rows.csv` and, for the EIA's count, `inventory_rows.csv`), and finds each of the 66 figures of
`page_figures.json` in its own place on the drawn page. `replicate.py` recomputes the 66 by the rules above, from the
tables or from the two files of public rows beside it: 373 of 373 with the 307 the page had (section 5).
