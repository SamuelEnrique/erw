# The curtailment tracker: its figures audited as a hostile expert would

Session 10210, chain 710 part D, 26 November 2026, the old laptop. Read as a renewables developer's analyst and an ISO market monitor who want to find it wrong. Platform tool 22 (`docs/platform-tools.md`): `/curtailment` and its view `/curtailment/where-when`.

- Nothing changed on main but this file and its evidence folder (`docs/reviews/curtailment-model-audit-2026-11-26/`). No table written, no lock taken, no default moved, no model called, no live service asked.
- Each finding has its own branch, `wip/audit-curtailment-<n>`. Words-only fixes (2, 4, 5, 6) are for landing; 1 and 3 would move figures and wait for the owner; 7 is a data request.

## In short

- **The arithmetic is right.** Every figure the default view prints (CAISO, January to October 2026, a 4-hour battery) follows from its files as the note says: 141 of 141 marked figures, the thirteen months of the monthly table and the 78 days' totals came out to the digit in an independent restatement. "What it is worth", never replicated before, was rebuilt from CAISO's intervals and the hubs' prices: 86 of 88 hub, market and month cells of 2025 and 2026 agree (the two others lack hours in this machine's price table).
- **A held grid's figure reaches the page (finding 1).** On `?grid=isone` and `?grid=nyiso` the summary and a headline print hours under USD 5 (ISO-NE 1, NYISO 17) read from `iso_hub_prices_history`, "license needed" for both since 21 October, while the same page says "license needed" in that section's place. For the owner.
- **"What it is worth" never says what its value is (finding 2).** One hub's price for CAISO's whole system: SP15 gives USD -29.0 million for January to October 2026, NP15 +27.7 million, and 81 percent of the energy was turned down for local congestion, behind lines the hub does not price. Words, for landing.
- **"An hour with any curtailment" changes meaning in 2026 (finding 3).** CAISO's hourly report puts a figure in 80.5 percent of priced hours (55.6 in 2025; 1,365 hours under 1 MWh), so "a flat load in those hours" moved to within 1.36 USD of the all-hours mean. In hours with at least 100 MWh it is 10.82, not 26.96. For the owner.
- **The default year is ten months, and the batteries were "already charging" (finding 4).** "In 2026" (6.52 percent) sits beside 2025's twelve months (4.53); the twelve months to October give 5.98. The batteries' sentence implied they could not have taken the energy; the code counts net-charging hours of two system totals. Words, for landing.
- **Smaller.** Decision 11 and the where-when hover say ISO-NE's figure is not pulled or not held; it is held, internal (finding 5, words). "Pacific time" is clock time beside prices on standard time: 2026's peak hour is 14:00 on the prices' clock, not 15:00 (finding 6, words). SPP's share may divide SPP-only curtailment by an output that includes its western area from April 2026 (finding 7, a data request).
- **What an analyst would add:** nodal prices for local curtailment, the lost tax credits and certificates, five-minute prices; none is held. The where-when trend legend still reads "CAISO, the whole system: curtailment" over solar alone: the fix of 20 November (`4f3247287`) is not on main.
- **Held grids otherwise reach nothing:** ISO-NE's own undelivered energy, NYISO's and MISO's appear as words only; the downloads offer no held table.

## The ground: each file and what it does

| File | What it does |
|---|---|
| `site/app/curtailment/page.tsx` | The page. Chooser of seven grids (CAISO, SPP, ERCOT, ISO-NE, NYISO open; MISO and PJM named only), California's period (a year or a month of the five-minute record) and a battery of 2, 4 or 8 hours. With no address it opens on CAISO, the newest year the profile holds (2026, ten months), a 4-hour battery. The summary sentence, the headline rows, "By day" and "By month" (the two live reads), California by hour, by reason and against the batteries, "Where free energy is", "What it is worth", "What each grid's number is", every month's share, the decisions block |
| `site/app/curtailment/Sections.tsx` | "Where free energy is" (`free_energy.json`), "What it is worth" (`worth.json`), Texas by the hour (`ercot.json`) |
| `site/app/curtailment/Charts.tsx` | The charts' wrappers (the site's SVG chart set) |
| `site/app/curtailment/where-when/page.tsx`, `Decisions.tsx` | "Where and when power is spare": a place's hour of the day against month (CAISO's curtailment, SPP's months, the hubs' hours below zero), the trend by whole year, the places ranked, eight decisions |
| `site/lib/curtailment.ts` | The chooser, addresses, a year's share from its months (`yearShare`), the newest and highest month, the number formats |
| `site/lib/curtailmentv2.ts` | California's profile read: hour-of-day arrays, the peak hour, whether a reason is published, the battery months |
| `site/lib/freeenergy.ts` | `FACE` (one line a grid: whose number it is), the share rule, the free-energy ranking and heat map, the flat load, the battery ceiling |
| `site/lib/wherewhen.ts` | The where-when view's cells, a cell's share of hours below zero, the newest whole year |
| `site/lib/decisions.ts` `CURTAILMENT_DECISIONS` | The page's eleven decisions, word for word the note's |
| `site/data/curtailment_profile.json` | California by month and year from CAISO's record (five-minute to 2025, the Daily Renewable Report by the hour from 2026): MWh by fuel, reason, category and Pacific clock hour, and the battery overlay. Built 2026-11-16, months 2019-01 to 2026-10 |
| `site/data/curtailment/shares.json` | Every month's share of available output (CAISO 150 months, SPP 98), with the output source of each month. Built 2026-11-17 |
| `site/data/curtailment/worth.json` | The value of curtailed energy at the hubs' prices, the flat load, the battery rule and the fleet (CAISO; ERCOT's estimate over its hours). Built 2026-11-17 |
| `site/data/curtailment/free_energy.json` | Hours under USD 5 and below zero by hub and zone, the twelve months to October 2026 and October alone, ERCOT, CAISO, NYISO, ISO-NE, SPP. Built 2026-11-16 |
| `site/data/curtailment/ercot.json`, `zone_shapes.json`, `where_when.json` | Texas's hours and days (the ERW's estimate); the boundaries found (none); the where-when view's file (built 2026-11-20) |
| Live reads | `iso_curtailment_monthly` (one entity, every row) and the grid's daily table (`caiso_curtailment_daily`, `spp_curtailment_daily`, `ercot_wind_solar_hsl_daily`) since 100 days back |
| Builders | `warehouse/connectors/curtailment.py`, `caiso_curtailment_intervals.py`, `ercot_wind_solar_history.py`; `warehouse/derived/iso_curtailment_monthly.py`, `curtailment_profile.py`, `curtailment_shares.py`, `curtailment_worth.py`, `free_energy.py`, `ercot_estimate_page.py`, `where_when.py` |
| Notes | `docs/methods/curtailment.md` (the method, its decisions and cross-checks), `caiso_curtailment_intervals.md`, `caiso_curtailment_daily.md`, `spp_curtailment_daily.md`, `where_when.md`; `replication/curtailment/` (profile and Texas 11,515 of 11,515 on 16 November; free energy; not worth, not SPP's shares) |
| Earlier reads | `docs/reviews/curtailment-faults-2026-11-16.md`, `curtailment-read-2026-11-16.md`, the ruling files of 17 November; not repeated here |

## The default view re-done, to the digit

The live set holds newer days than this machine. Every figure below is the page's figure on the page's committed files and, for the two live reads, on the main copy's tables as this machine holds them (read only; the daily table to 4 November 2026, the monthly table to September 2026), with "now" set to 26 November 2026 12:00 UTC.

- **The page's own code.** `draw.mjs` draws `/curtailment` (and seven other addresses) to HTML with the site's own components, the two live reads answered from `fixture.json` (rows of the main copy's tables), every other request refused. Every figure the page marks (`data-n`) is collected (`main_default_n.json`).
- **The restatement.** `restate.py` (standard library, none of the site's code), written from the method note and the page's words, computes every figure from the same files.
- **Result: 141 of 141 figures of the default view agree to the digit** (`compare.out`), and so do the thirteen months of the monthly table and the totals over the 78 days the daily table gives (solar 374,254.63 MWh, wind 51,376.40).

| Figure (CAISO, 2026, 4-hour battery) | Page | Restated |
|---|---|---|
| Solar curtailed, wind curtailed | 4,944,663 MWh; 353,207 | the same |
| Days | "304 of 304 days, 10 months" | 304 days held of the 304 in the ten months; the calendar year has 365 |
| For local congestion, system-wide oversupply | 4,301,964; 995,905 MWh | the same |
| The hour with the most | 15:00 (602,149 solar, 39,639 wind) | the same; 14:00 holds 635,266 against 641,788, 1.0 percent less |
| Share of available output, 2026 | 6.52 percent | 6.52 (ten months' curtailed over curtailed plus output) |
| The highest month; the newest | 15.81 (April 2026); 2.73 (October 2026); 150 months | the same |
| Curtailed while the batteries charged, October 2026 | 91.54 percent (182,465 MWh, 31 days, 1,668,564 MWh charged) | the same |
| Hours under USD 5, SP15, twelve months | 1,375 (1,109 below zero) | the same; the heat map's cells add to it |
| Cheapest against dearest place | 4.18 (ZP26 28.98, NP15 33.16); October 5.02 | the same |
| Curtailed energy at SP15 real-time prices, 2026 | USD -29.0 million, -5.48 per MWh, 5,297,870 MWh | the same |
| In hours below zero; under USD 5 | 79.97; 84.23 percent | the same |
| A flat load in those hours; in all hours | 26.96; 28.32 USD per MWh, 5,876 hours | the same |
| A 4-hour battery could have taken in | 1,210 MWh per MW, 99.48 percent of one full charge a day over 304 days | the same |
| A 4-hour fleet against what the fleet charged in the curtailed hours | 4,245,847 of 15,638,274 MWh, 27.15 percent | the same |

### What it is worth, restated from the tables (never replicated before)

`worth_check.py` (standard library, written from the note's "What it is worth") rebuilds the value, the flat load and the battery rule from `caiso_curtailment_intervals` and the hubs' prices, one year at a time. **86 of 88 hub, market and month cells of 2025 and 2026 agree with `worth.json`** (value to USD 1, per MWh and shares to 0.01, MWh to 0.1, hours exactly); the two that differ are October 2026 at the two hubs in real time, where this machine's price table holds 720 of the month's 744 hours (`worth_compare.out`). The battery rule per MW agrees in every month.

### One rule changed at a time

`measures.py` (`measures.json`, `measures.out`), from the page's files, the worth restatement and the main copy's tables.

| Rule | The page | Changed to | Measured worth |
|---|---|---|---|
| The hub | SP15 | NP15 | January to October 2026, real time: USD -29.0 million (-5.48 per MWh) becomes +27.7 million (+5.23). 2025: -41.2 million (-10.93) becomes +24.9 million (+6.62). The sign turns in both years |
| The market | real time | day-ahead (SP15) | 2026: -29.0 million becomes -13.6 million (-2.56 per MWh); 2025: -41.2 becomes -22.3 (-5.91) |
| "An hour with any curtailment" | above zero | at least 1, 10 or 100 MWh (SP15 real time) | 2026 (this machine's prices, 5,857 hours): the flat load 26.99 becomes 22.26 (4,492 hours), 16.38 (3,505), 10.82 (2,689); all hours 28.32. 2025: 21.57 (4,868 hours) becomes 20.64, 18.09, 13.19 (3,188); all hours 31.19. Hours counted: 80.6 percent of priced hours in 2026 against 55.6 in 2025; under 1 MWh, 1,365 hours against 208 |
| The battery rule's interval | five-minute to 2025, hourly from 2026 (the source's) | 2025's energy summed to the hour first | per MW over 2025: 2 hours 724.17 becomes 728.00 MWh (+0.53 percent), 4 hours 1,426.84 becomes 1,450.90 (+1.69), 8 hours 2,753.89 becomes 2,848.07 (+3.42). 2026's figures carry that lift by construction |
| The share's output, 2026 | CAISO's Today's Outlook | CAISO's Daily Renewable Report, on the days it holds | April 15.81 becomes 18.97 percent, May 13.58 becomes 17.06, March 9.86 becomes 10.94, June 5.62 becomes 6.92; July 2.48 becomes 2.19 (9 days), October 2.73 becomes 2.53. The note already holds this open for a person |
| The default period | 2026, January to October | the twelve months to October 2026 | the share 6.52 becomes 5.98 percent; curtailed 5,288,355 MWh becomes 5,344,831 (shares' days); 2025 was 4.53 |
| The clock of the hour of the day | Pacific clock time | Pacific standard time (the prices' clock) | 2026's hour with the most moves from 15:00 to 14:00; the day's MWh-weighted centre from 12.95 to 12.05. 15:00 led 14:00 by 1.0 percent on the clock |
| ERCOT's share | below the limit over the limit | below over below plus output (CAISO's form) | the 57 whole days: 6.27 becomes 6.23 percent (wind 6.67 either way, solar 5.68 becomes 5.60) |
| The fleet's "curtailed hours" | any curtailment | (measured, not changed) | the share of all the fleet charged that falls in those hours: 2025 September to December 94.9, 96.2, 75.2, 83.0 percent; 2026 every month 96.3 to 100.0 |

## Each claim against the code

- **What each operator counts.** CAISO: its market's dispatch of economic bids below a plant's forecast, cuts of self-schedules, and operator instructions, each local or system. In 2026 economic bids were 98.5 percent of the curtailed MWh (5,218,521 of 5,297,869), operator instructions 1.1, self-schedule cuts 0.4. The face line ("the wind and solar energy its market or its operators turned down") is right; the categories table says it from 2026. SPP: redispatch for congestion, manual curtailment and "curtailed for energy", per balancing authority area; the face says "SPP's own figure" and that the share is the ERW's on EIA's output. Right. ERCOT: output below the High Sustained Limit, the ERW's estimate, never called curtailment on the face. Right.
- **Economic against manual, local against system.** CAISO's two axes are both shown (reason table, category table); the headline "For local congestion" is the reason axis. SPP's three parts are in the table but the page shows only their sum. Not wrong.
- **Five-minute against hourly, MW against MWh.** A five-minute MW is MW x 5/60 MWh (restated in `worth_check.py`, 86 of 88 cells; the replication's 11,515 of 11,515 for the profile). From 2026 the source is hourly: the battery rule then lifts by up to 3.4 percent (measured on 2025) and "an hour with any curtailment" changes meaning (**finding 3**). The page does not say the source changed resolution at the turn of the year.
- **A share of what.** CAISO and SPP: curtailed over curtailed plus output, "of available output", said on the page and in the hover. ERCOT: below the limit over the limit, said as "of the limit". Right. CAISO's output source changes from the workbook to Today's Outlook in 2026; each month's hover names it. SPP's output is EIA-930's SWPP; whether it includes SPP's western area from April 2026 is not known here (**finding 7**).
- **CAISO's, ERCOT's and SPP's figures side by side.** Decision 1 says they are never summed, and the page sums none. The where-when table "The operators that publish curtailment, by whole year" sets CAISO's and SPP's GWh in one table under their own names; its decision says each is the operator's own figure. Acceptable.
- **Months not whole.** Shares need 95 percent of a month's hours, the profile 90 percent of its days, worth 90 percent of days and 95 percent of priced hours; nothing is scaled up; August and September 2026's shares rest on 30 of 31 and 29 of 30 days and say so on hover. The default year is ten months and the summary did not say so (**finding 4**).
- **Daylight saving days.** CAISO's fall-back day counts all 300 intervals; its hour 01:00 holds two hours that day. The hour of the day is clock time beside prices on standard time (**finding 6**). Texas, 1 November 2026: the day row (muted, not whole) still carries 21,817 MWh of wind below the limit, 6,392.8 of it from the second 01:00's doubled limit; this is row 3 of `curtailment-faults-2026-11-16.md`, which waits for the owner; the hour is out of the hourly chart and of every whole-day figure.
- **Trends from few years.** The where-when trend draws CAISO's seven whole years (2019 to 2025) and SPP's eleven (2015 to 2025), whole years only, and its words claim no trend. Its legend still reads "CAISO, the whole system: curtailment" over the solar line when the fuel is solar: the fix of 20 November (`4f3247287`, session 9203) never reached main, so it is still wrong; not redone here.
- **The price link.** No sentence words a correlation as a cause. "Curtailed in hours priced below zero: 79.97 percent" is a share of MWh, said as such. "Where free energy is" counts hub hours under USD 5, energy only. Its ranking sets places on different markets against each other (SPP's south hub day-ahead, 1,449 hours, above its north hub in real time, 1,336); each place's market is said. The value of curtailed energy is one hub's price for an unnamed place (**finding 2**).
- **Held grids.** ISO-NE and NYISO price counts reach the summary and a headline of their own views (**finding 1**). ISO-NE's own undelivered energy (internal) reaches no figure; NYISO's and MISO's curtailment are words only; the downloads list offers no held table (drawn: "Download the tables: every public table is on Data and methods"). Decision 11 and the where-when hover misdescribe ISO-NE's figure (**finding 5**).
- **The window.** Each section names its window: California's period, the twelve months to October 2026 for prices, the period of worth, Texas's 57 whole days (28 September to 24 November) and worth's 1,175 priced hours to 16 November for ERCOT: two windows for Texas on one page, each named. The source line gives each file's build date. Right.
- **"More in the hour from 15:00 than in any other."** True to the digit, by 1.0 percent over 14:00, and 14:00 on the prices' clock (finding 6). A fragile statistic for a headline; left.
- **The batteries.** "Taken in by the batteries ... each five-minute value below zero, added up" and the storage page's netted count: right. "Already charging": **finding 4**.

## What an expert's own number would hold that this does not

- **Local prices for local curtailment.** 81 percent of 2026's curtailed MWh was for local congestion, where the node's price is below the hub's; CAISO publishes no location, so no nodal value can be built. The sign already turns between the two hubs (finding 2). Not measurable here.
- **What the plant forgoes.** A developer's analyst values curtailment at the production tax credit and the renewable certificate lost, not the hub's energy price; the warehouse holds no credit or certificate price. Not sized.
- **Five-minute prices.** Curtailment runs in CAISO's five-minute dispatch; the page prices it at the hour's mean of four fifteen-minute prices. Not held.
- **A threshold for "an hour with curtailment"**, or the curtailment-weighted price alone (USD -5.48 in 2026): finding 3.
- **SPP's parts.** A market monitor would split SPP's redispatch (congestion) from "curtailed for energy" (price); the table holds both, the page shows the sum.
- **ERCOT before September 2026.** The estimate has 57 whole days; history needs ERCOT's registered service. Said on the page.

## Findings

| # | Severity | Finding | Measured | Branch | Kind |
|---|---|---|---|---|---|
| 1 | Major | A held grid's price count reaches `/curtailment?grid=isone` and `?grid=nyiso` (summary and a headline) | ISO-NE 1 hour (INTERNAL, October 2026), NYISO 17 (N.Y.C., twelve months), both from `iso_hub_prices_history`, "license needed" since 21 October 2026 | `wip/audit-curtailment-1` (`d64aabbbf`) | figure, the owner's ruling |
| 2 | Major | "What it is worth" says nothing of what its value is | SP15 -29.0 million against NP15 +27.7 million (2026), -41.2 against +24.9 (2025); 81 percent of 2026 local | `wip/audit-curtailment-2` (`c85a439e5`) | words, for landing |
| 3 | Moderate | "An hour with any curtailment" changes meaning at the turn of 2026 | 55.6 to 80.5 percent of hours; the flat load 9.62 then 1.36 under the mean; at 100 MWh 13.19 and 10.82 | `wip/audit-curtailment-3` (`9b3cc05a2`) | figure, the owner's ruling |
| 4 | Moderate | "In 2026" is ten months; the batteries "already charging" | 6.52 against 5.98 for the twelve months to October; 2025 4.53 | `wip/audit-curtailment-4` (`74a068cc2`) | words, for landing |
| 5 | Minor | Decision 11 and the where-when hover say ISO-NE's figure is not pulled or not held | held internal since the ruling of 7 October 2026 | `wip/audit-curtailment-5` (`ad090240b`) | words, for landing |
| 6 | Minor | "Pacific time" is clock time beside prices on standard time | 2026's peak 15:00 becomes 14:00; the centre 12.95 becomes 12.05 | `wip/audit-curtailment-6` (`c59d76994`) | words, for landing |
| 7 | Minor | SPP's share may divide SPP-only curtailment by an output that includes its western area from April 2026 | not measurable here | none | a data request |

### 1. A held grid's figure on its own view

- **Where.** `site/app/curtailment/page.tsx`: `top` and `cheap` are computed for any grid with a price file, outside `licenseHeldGrid`; the summary for a grid with no curtailment figure prints `{cheap}`, and its third headline prints `top.win.under5`. The free-energy and worth sections of the same view are replaced by the licence words.
- **Drawn.** `?grid=isone`: "ISO-NE: no curtailment figure is in the ERW. Its place with the most hours under USD 5 in October 2026 is INTERNAL, with 1." and the headline "Most hours under USD 5: 1 hours, INTERNAL, October 2026". `?grid=nyiso`: N.Y.C., 17 (`main_isone.txt`, `main_nyiso.txt`). The source line names `iso_hub_prices_history`; `site/data/license_status.json` marks it "license needed" from 2026-10-21 for ISO-NE, MISO and NYISO.
- **The test.** `tests/test_audit_curtailment_1.py` (passes on main: it shows the fault).
- **For the owner.** Removing the two counts moves figures a reader sees. Default: left as it is (the page is in review; no visitor sees it).

### 2. What the value of curtailed energy is

- **Where.** `site/app/curtailment/Sections.tsx`, `Worth`, California: "Curtailed energy at SP15 prices, 2026: USD -29.0 million ... each hour at its real-time price". The note says "The data does not locate a curtailment, so the hub's price stands for a place the data does not name" and "it is what the energy would have fetched at the hub, not a loss anyone booked"; the page said neither.
- **How much.** The same energy at NP15 is worth the opposite sign in both years (table above). 81 percent of 2026's curtailment was for local congestion (4,301,964 of 5,297,869 MWh).
- **The fix on the branch.** Words only, one sentence under the headline row (`WORTH_WORDS`): "The hub's price stands for a place the data does not name: CAISO publishes one curtailment figure for its whole system, and energy turned down for local congestion sits behind a congested line, where the price is below the hub's. The two hubs can value the same energy with opposite signs (the table below). A value below zero is what the energy would have fetched at the hub, not a loss anyone booked, and it leaves out the tax credits and renewable certificates a plant forgoes when it is turned down." Drawn and read: pass (`b2_default.txt`); the 141 figures unchanged. Test `tests/test_audit_curtailment_2.py`; the six test files that read `Sections.tsx` pass.

### 3. "An hour with any curtailment"

- **Where.** `warehouse/derived/curtailment_worth.py` `value_of`: `hours_curtailed_priced` and `price_curtailed_hours_mean` take every hour with curtailment above zero; the fleet's "curtailed hours" take every hour holding an interval. The page: "A flat load in those hours paid 26.96 ... the mean price of the 5,876 hours with any curtailment" and "The fleet charged in the curtailed hours: 15,638,274 MWh".
- **Why it matters.** To 2025 the hours come from CAISO's five-minute record; from 2026 from its hourly report, whose small category values (a self-schedule cut of 0.8 MWh) put a figure in most hours. The figure then reads as if curtailed hours had become ordinary hours.
- **How much.** Table above: 80.5 percent of 2026's priced hours count (55.6 in 2025); the flat load sits 1.36 USD under the all-hours mean in 2026 against 9.62 in 2025; in hours with at least 100 MWh it is 10.82 (2026) and 13.19 (2025). January 2026 counts 586 hours, of which 369 hold 1 MWh or more.
- **The test.** `tests/test_audit_curtailment_3.py` (passes on main).
- **For the owner.** A threshold (100 MWh) would move 2026's flat load from 26.96 to about 10.82 and 2025's from 21.57 to 13.19. Default: left as it is.

### 4. The default year, and the batteries' sentence

- **Where.** `page.tsx`, the summary and the first headline note; the batteries' clause of the summary.
- **Why.** "In 2026, California curtailed ... 6.52 percent" and "Over 304 of 304 days, 10 months" read as a whole year beside 2025's twelve months; November and December, months of little curtailment, are missing. "The batteries were already charging" reads as if they could not have taken the energy; the code counts the curtailed MWh in hours of net charging, both system totals, and the note says the data does not show what the batteries could have taken.
- **The fix on the branch.** Words only: "In 2026, January to October, California curtailed ..." and "Over 304 of 304 days, 10 months, January to October." (a year held in full reads as before); "... fell in hours in which the batteries took in more than they gave back; both are totals for the whole system, not a count of what the batteries could have taken." The site's own read script (`site/scripts/test-curtailment-read.mjs`) pinned "already charging"; its check now holds the new words, 23 of 23. Drawn and read: pass. Test `tests/test_audit_curtailment_4.py`; the fourteen test files that read the page pass (the face rule of session 144 refused "does not say", so the clause says "not a count of").

### 5. ISO-NE's figure: held, not "not pulled"

- **Where.** Decision 11 (`site/lib/decisions.ts`, word for word `docs/methods/curtailment.md`): "ISO-NE's monthly undelivered energy is not pulled under its legal notice". `warehouse/derived/where_when.py`: "no curtailment figure of ISO-NE is held". The note records the owner's ruling of 7 October 2026 (pulled, held internal, not shown) and the page's face line says "Held, not shown".
- **The fix on the branch.** Words only: "ISO-NE's monthly undelivered energy is held internal and not shown under its legal notice (pulled on the owner's ruling of 7 October 2026), ..." in the list and the note; the builder's hover "ISO-NE's monthly undelivered energy is held internal under its legal notice and not shown", which reaches `where_when.json` at its next build on the data machine. Drawn and read: pass (every view's decisions). Test `tests/test_audit_curtailment_5.py`; the nineteen test files that read the decisions list or the where-when builder pass.

### 6. Two clocks on one page

- **Where.** `page.tsx`: "Pacific time; each bar is the period's total in that hour of the day" and the batteries' "Pacific time." The free-energy heat map on the same page is in "US Pacific standard time".
- **How much.** On standard time 2026's hour with the most is 14:00, not 15:00, and the day's centre moves from 12.95 to 12.05.
- **The fix on the branch.** Words only (`CLOCK_WORDS`): "Pacific clock time, with daylight saving time from March to November, so an hour later than the standard time of the prices below in those months; each bar is the period's total in that hour of the day." and "Pacific clock time, with daylight saving time." Drawn and read: pass. Test `tests/test_audit_curtailment_6.py`. Branches 2, 4, 5 and 6 merge with origin/main together without a conflict (tried; their tests and the read script pass on the merge).

### 7. SPP's denominator after April 2026

- **Where.** `warehouse/derived/curtailment_shares.py`: SPP's curtailment of `spp:SPP` (its western area `spp:SWPW` is apart in SPP's own file) over EIA-930's wind and solar for SWPP.
- **Why.** If EIA's SWPP takes in the western area from SPP's expansion of April 2026, the share from then divides SPP-only curtailment by both areas' output. The share's own output (`shares.json`) steps at April: January to March 2026 is 2.9 percent above the same months of 2025 (30.91 against 30.05 TWh), April to October 16.8 percent above (72.54 against 62.09 TWh). The western area joining would make such a step; so could new plants. Not told apart here. If it is the west, SPP's shares from April 2026 (2.76 to 13.62 percent a month) are understated. No branch: a data request.

## What was checked and found right

- `yearShare`: the months' curtailed over their curtailed plus output, never a mean of shares (6.52 restated).
- `shareMarks`, `peakHour`, `reasonCover`, `batteryFill` (99.48 = 1,209.66 over 4 x 304), `ranked` (most hours, then most below zero, then the id), `worthPeriod`, `curtailedOf`, the number formats (`whole` as `Math.round`, `usd` to one decimal of a million).
- The worth builder's value, shares of cheap hours, hour coverage rules and the battery rule (restated by month, 2025 and 2026).
- The face lines of each grid; MISO and PJM named with words and no number; the ERCOT estimate never called curtailment on the face.
- The two live reads: the page's months and days equal the tables' rows.

## Not covered, or left open

- SPP's and ERCOT's views were drawn (their drawn text is under runs, not kept) but their figures were not restated beyond the ERCOT share.
- The where-when price cells (hours below zero by hourly mean) against counts of fifteen-minute intervals below zero: not measured (a year of fifteen-minute prices for each place was over this run's read budget).
- October 2026's worth at the two hubs in real time: this machine's price table lacks 24 hours (data request).
- The Ask panel was not run (it calls a model).

## Rows for the desk

- **Landing (words, requested):** `wip/audit-curtailment-2` `c85a439e5`; `wip/audit-curtailment-4` `74a068cc2`; `wip/audit-curtailment-5` `ad090240b`; `wip/audit-curtailment-6` `c59d76994`.
- **For the owner (not for landing):** `wip/audit-curtailment-1` `d64aabbbf`; `wip/audit-curtailment-3` `9b3cc05a2`.
- **Data requests:** (a) whether EIA-930's SWPP wind and solar net generation includes SPP's western area (SWPW) from 1 April 2026, month by month to October 2026; if it does, SPP's share from April 2026 is understated. (b) `worth_check.py 2026` (this folder) run on the data machine's tables, to close October 2026 at SP15 and NP15 in real time against `worth.json`.
