# What a battery earns: every number, step by step

Energy Research Warehouse (ERW), session 178, 10 October 2026. Written for sign-off. Page: `/cost-of-power/battery`. This note is written from the code, not from the older notes: `warehouse/derived/battery_stack.py` (the model), `site/lib/batterystack.ts` (the page's arithmetic), `site/app/cost-of-power/battery/page.tsx`, `BatteryForm.tsx` and `Contract.tsx` (the page). Where an older note and the code disagree, the code is what the page does; the disagreements are listed in "Where the notes and the code differ". The model's method, its sources and its limits are in [the method note](battery_stack.md); the early years are in [battery_early_years.md](battery_early_years.md).

Downloads, the default case hour by hour: [erw_2026_battery_dispatch.csv](/battery/erw_2026_battery_dispatch.csv) (4.3 MB, 26,304 hours), [the Stata do-file](/battery/erw_2026_battery_replication.do) and [its Python mirror](/battery/erw_2026_battery_replication.py).

**The default case**, used for every example below: ERCOT, a 4-hour battery, perfect foresight, 100 MW, fixed O&M USD 22 per kW a year, debt payments USD 6,783,357 a year. With the tables as retrieved on 5 October 2026 the page shows: USD 81.40 per kW over the last twelve months (October 2025 to September 2026), 33 percent of it from ancillary services, debt covered 0.88 times; USD 8,140,219 for 100 MW; a bad month of USD 475,477 (December 2024, of 36 months held).

**Session 208 (the owner's rulings of 12 October 2026).** The default debt share is 20 percent (Lazard's storage cases, "20% debt at an 8% interest rate and 80% equity at a 12% cost") and the default hurdle rate is 12 percent (Lazard's cost of equity: the NPV is to equity, after the debt payments). So the default case's debt payments are USD 2,261,119 a year (`1,110 x 1000 x 0.2 x 0.101852 x 100`), debt covered 2.63 times, its NPV USD -69.78 million (USD -697.80 per kW) and its IRR -8.8 percent; the breakeven toll is USD 4.19 per kW-month. Every other figure of the default case is unchanged: the revenue, the bad month, the chart and the income table read no cost. The generator page takes the same hurdle rate (its debt share stays 60, Lazard's generation structure); the datacenter page keeps 9.6. Where this note gives 6,783,357, 0.88, 8.90 or -62.59 it describes the defaults of sessions 67 to 207 and stands as the record of those sessions. The replication files of section 7 carried 60 percent until session 263, which moved them to the page's defaults (20 percent debt, a hurdle rate of 12) and made them rebuild scenario A's column as well; `tests/test_session178.py` reads the page's library at the page's own debt payment. The page itself asks three questions since session 208 (section 4).

## 1. The order of computation

1. **Prices in.** Connectors write ERCOT's hourly day-ahead ancillary clearing prices (`ercot_as_prices`) and hub energy prices (`iso_rtm_hub_prices`, `iso_dam_hub_prices`, and the yearly history `ercot_all_hub_prices_history`).
2. **The model, once a day** (`battery_stack.py`, in `warehouse/run_daily.sh`): for each market, strategy, duration and local day, one optimization. Its daily results are summed by local month into `battery_stack_monthly` (and, for the days of three ERCOT stress events, kept by day in `battery_stack_stress_daily`). Everything is per 1 MW of rated power.
3. **The live set.** The loader copies both tables to Supabase.
4. **The page, on each request**, reads the rows of one hub, one strategy and one duration, and computes every number it shows with `lib/batterystack.ts`, scaling by the reader's MW. The contract panel computes in the browser from the same months.
5. **The check.** `site/scripts/check-values.mjs` reads the tables itself, recomputes every number with the same library, and compares with what the page printed (key `bs|<inputs>|<stat>`).

## 2. The reader's inputs

Until session 195 all six were in the address, each bounded and defaulted by `inputsOf`. Since then the first four are the page's own, and the last two are scenario A's (the paragraph under the table):

| Input | Default | Bounds | What it changes |
|---|---|---|---|
| `grid` | `ercot` | `ercot`, `caiso`; `nyiso` and `spp` only in the internal view | which hub's rows are read |
| `dur` | 4 | 2, 4 or 8 hours | which rows; the defaults of `fom` and `ds` |
| `strat` | `foresight` | `foresight` or `dayahead` | which rows |
| `mw` | 100 | 1 to 5,000 | every US dollar figure is the per-MW figure times `mw`; per-kW figures do not move |
| `fom` | 11.2, 22 or 43.6 USD per kW a year (2, 4, 8 hours) | 0 to 500 | debt coverage only |
| `ds` | the default annual debt payment for the duration and size, rounded to a dollar | 0 to 1e11 | debt coverage only |

Anything outside its bounds is clipped; anything unreadable takes the default. A change of duration drops a typed `fom` or `ds` (their defaults scale with the duration).

**Session 195: `fom` and `ds` are scenario A's.** "Your battery" no longer holds a fixed O&M and annual debt payments. Scenario A of "Scenarios A and B" (section 11.1) holds the fixed O&M, and its annual debt payment is computed from its capital cost, debt share, interest rate and term; every coverage figure of the page reads the two from scenario A. In an address written before the session the two names are still read, once, as old names of scenario A's own assumptions (section 11.1, "The block the three pages share"), so an older link opens the same headline. Everything this note says of `fom` and `ds` below holds with "scenario A's fixed O&M" and "scenario A's annual debt payment for the size, rounded to a dollar" in their place.

## 3. What the model does, one local day at a time

### 3.1 The prices it reads

| Price | Table | Rows | Used by |
|---|---|---|---|
| Energy, real time | `ercot_all_hub_prices_history`, then `iso_rtm_hub_prices` after the history's last interval | `market = ercot_rtm`, `node = HB_HUBAVG`; 15-minute intervals | `foresight` |
| Energy, day-ahead | the same two tables | `market = ercot_dam`, `node = HB_HUBAVG`; hourly | `dayahead` |
| Regulation Up, Regulation Down, Responsive Reserve, ECRS, Non-Spin | `ercot_as_prices` | `entity = ercot:REGUP`, `ercot:REGDN`, `ercot:RRS`, `ercot:ECRS`, `ercot:NSPIN`; `variable = mcpc_dam`; hourly, USD per MW held for the hour | both strategies |

CAISO: `TH_SP15_GEN-APND` from `iso_hub_prices_history` then the rolling tables, and `caiso_as_prices`, entity `caiso:AS_CAISO_EXP`, variables `as_price_dam_ru`, `_rd`, `_sr`, `_nr`.

**The hourly energy price** is the mean of the hour's intervals, and only of an hour whose intervals are all present (four of four for ERCOT's real-time price). An hour with a missing interval has no price.

**Both strategies use day-ahead ancillary prices.** They differ only in the energy price: `foresight` is paid the hourly mean of the real-time price, `dayahead` the day-ahead price.

### 3.2 The day

A day is the market's local day (Central for ERCOT, Pacific for CAISO): 24 hours, 23 on the spring clock-change day, 25 on the autumn one. The model solves a day only when every one of those hours has an energy price and a price for every product bought that day. Otherwise the day is left out and counted, never estimated: no hour is filled, no day is scaled.

The days run from the market's start (ERCOT 1 January 2018, CAISO 1 September 2024) to the last local day reached by both the energy price and the ancillary prices.

### 3.3 The products and how long each must be backed

| Product (ERCOT) | Direction | Stored energy behind 1 MW | Source |
|---|---|---|---|
| Regulation Up, Responsive Reserve | up | 1 hour to 4 December 2025; 30 minutes from 5 December 2025 | before: assumed, not verified; from: NPRR 1282 |
| Regulation Down | down | the same, as room to absorb | the same |
| ECRS, bought from 10 June 2023 | up | 2 hours; 1 hour from 5 December 2025 | NPRR 1096; NPRR 1282 |
| Non-Spin | up | 1 hour to 8 December 2022; 4 hours from 9 December 2022 | before: assumed; from: NPRR 1096 |

CAISO: Regulation Up and Down 1 hour (tariff 8.4.1.1(g)); Spinning and Non-Spinning Reserve 30 minutes (tariff 8.4.3). The rule in force on the local day applies. Before 10 June 2023 ECRS is not a product of the day at all.

**The cap this puts on a product.** An upward award of 1 MW with a requirement of `h` hours needs `h / eta` MWh stored, where `eta = sqrt(0.86) = 0.9274`. A full battery of duration `D` therefore holds at most `min(1, D x eta / h)` MW of that product. Non-Spin (4 hours): 0.464 MW per MW for a 2-hour battery, 0.927 for a 4-hour one, 1 for an 8-hour one. In the exported hours the largest Non-Spin award is 0.927362 MW.

### 3.4 The optimization

For each hour `t` of the day, per 1 MW of rated power: charge `c_t` and discharge `d_t`, both measured at the grid, and one award `r_k,t` per product `k`, each between 0 and 1 MW.

Maximize

    sum over t of  p_t x (d_t - c_t)   +   sum over k and t of  a_k,t x r_k,t

`p_t` the energy price, `a_k,t` the product's price. Subject to:

- **State of charge.** `s_t = s_(t-1) + eta x c_t - d_t / eta`, with `s = 0` at the start of every local day, and `0 <= s_t <= D`.
- **Power, upward.** `d_t + (upward awards in t) <= 1`.
- **Power, downward.** `c_t + (Regulation Down in t) <= 1`.
- **Energy behind upward awards.** `sum over upward k of r_k,t x h_k / eta <= s_(t-1)` and `<= s_t`: at the hour's start and at its end.
- **Room behind Regulation Down.** `r_regdn,t x h x eta <= D - s_(t-1)` and `<= D - s_t`.
- **One cycle.** `sum over t of d_t / eta <= D`: the energy taken out of the battery in a day is at most one full charge.

Reserves are never deployed: an award is paid its price and moves no energy.

The solver is scipy's `linprog` with HiGHS. **This split is why nothing is counted twice:** in an hour, a megawatt is discharged or held as an upward reserve, never both (the upward power limit), and the same optimization chooses both. The page's "energy" and "ancillary" rows are the two parts of that one objective.

**Negative prices.** At a negative price the linear program can charge and discharge in the same hour, to be paid for burning energy. When its solution does that in any negative-price hour, the day is solved again as a mixed-integer program with one switch per negative-price hour (charge or discharge, not both). In the 36 months exported, 586 hours on 141 days have a negative energy price; one day needed the switch (4 January 2025). At a price of zero or more, charging and discharging together never pays; a tie that leaves both is netted out, which leaves the state of charge unchanged and the revenue the same or higher. No ancillary price in the 36 months is negative; an award is never negative, so a negative reserve price would simply not be taken.

**After solving**, the model checks every limit on the solution hour by hour and stops the whole build on a violation (`check_day`).

### 3.5 From days to the monthly table

A day's result: energy revenue `sum of p_t x (d_t - c_t)`, each product's revenue `sum of a_k,t x r_k,t`, the total, and the MWh discharged. For each market, strategy, duration and local month, `battery_stack_monthly` holds:

| Variable `<strategy>_<N>h_...` | Unit | What it is |
|---|---|---|
| `revenue_energy_usd_per_mw` | USD/MW | the sum over the month's solved days |
| `revenue_<product>_usd_per_mw` | USD/MW | the same per product (only products bought on some day of the month) |
| `revenue_ancillary_usd_per_mw` | USD/MW | the products' sum |
| `revenue_total_usd_per_mw` | USD/MW | energy plus ancillary |
| `discharged_mwh_per_mw` | MWh/MW | energy delivered to the grid |
| `days_held`, `days_left_out`, `days_left_out_ancillary`, `days_left_out_energy`, `days_in_month` | count | the days behind the month |

Each value is rounded to four decimals, half up. Entity `ercot:HB_HUBAVG` or `caiso:TH_SP15_GEN-APND`; `ts_utc` is the first day of the local month written as `YYYY-MM-01T00:00:00Z`. A month with no solved day has its day counts and no revenue row, never a zero.

## 4. Every number on the page, in the order the page shows it

**Session 208: one page, three questions, nothing folded** (the owner's ruling of 12 October 2026). The order is now: (1) **What did it earn?**: the summary sentence, the three headline numbers (4.2, 4.3), the chart (4.4) and the income table (4.5) with the awards line (4.6), unchanged in every number; under the table one sentence of what the model cannot see (energy is priced at the hub, not the battery's node; reserves are paid for being held and are assumed never called) and the download "Every month, CSV" (4.9). (2) **Is it worth building?**: scenarios A and B (11.1), with the contract's share and price as two more assumptions (0 by default, so the default is fully merchant), and the results table. (3) **What matters most**: the NPV sensitivity chart (11.1) with one line on how to read it. Gone from the page: the panel "Your contract (optional)" and the section "With your contract" (4.7: the contract is a scenario's), the table "Other grids" (4.8: one line under the grid picker), and the folds "Every month" (4.9: the CSV), "Stress days" (4.10: the table is public) and "What this model cannot see" (4.11: this note). The headline reads scenario A, its contract included; at a contract share of 0 every number that stays on the page is what it was (session 208's report: 51 checked numbers identical in key, value and text at the defaults of sessions 196 to 207; the 330 keys that left the page are the monthly and stress-day rows).

`r(m, s)` below is the table's value for month `m` and stream `s` (per MW); `MW` the reader's size. "Scaled" means `round(value x MW)` to a whole US dollar.

**A month is "held"** when it has a total revenue row and `days_held / days_in_month >= 0.9`. Only held months enter any window, average or chart bar. A month that is not held is shown grey in "Every month" with its held days' revenue, and counted nowhere.

### 4.1 The input panel's note

- **Default annual debt payments**: `capex x 1000 x 0.6 x crf(0.08, 20) x MW`, rounded to a dollar, where `crf(i, n) = i / (1 - (1 + i)^-n) = 0.101852`. Capital cost per kW: 610 (2 hours), 1,110 (4 hours), 2,110 (8 hours). The 4-hour default: `1,110 x 1000 x 0.6 x 0.101852 x 100 = 6,783,357`.

### 4.2 The summary sentence

- **"earned USD X per kW"** (`l12_kw:total`): the sum of `r(m, total)` over the last twelve months, divided by 1,000. Default: 81.40.
- **"Y percent of it from ancillary services"** (`l12_share:ancillary`): `round(100 x sum of r(m, ancillary) / sum of r(m, total))` over the same twelve months. Default: 33.
- **"covered its debt Z times"** (`cover`): see 4.3.

**The last twelve months**: walk the months from newest to oldest; take the first held month that is whole (every one of its days is in the table, solved or left out: `days_held + days_left_out = days_in_month`) and whose eleven preceding calendar months are all held too. Until session 195 the first held month was taken, whole or not (section 5, "A month so far"). Those twelve are the window. If there is none, the page says so and shows no last-twelve-months figure. Default: October 2025 to September 2026.

### 4.3 The three headline numbers

1. **Last twelve months, all streams**: `l12_kw:total` again, and beneath it **USD for the reader's size** (`l12:total`): the twelve months' `r(m, total)` summed, scaled. Default: 8,140,219.
2. **A bad month** (`p10_36`): take the 36 calendar months ending with the last twelve months' last month (or with the newest held month when there is no twelve-month window); keep the held ones (`n36` of them); sort by total revenue, ties by month; take the one at rank `ceil(0.1 x n36)` (nearest rank, at least 1); its total, scaled. Default: 36 months, rank 4, December 2024, 475,477. A market held for less than 36 months has fewer and the page says how many.
3. **Debt coverage, last twelve months** (`cover`): `(sum of r(m, total) x MW - fom x 1000 x MW) / ds`. Revenue less a year of fixed O&M, over a year of debt payments. Shown with two decimals; not shown when `ds` is 0. Default: `(8,140,219 - 2,200,000) / 6,783,357 = 0.88`. The annual debt payment `ds` is printed beside it.

**Session 195: the summary sentence and these three numbers are scenario A's**, computed in the browser as A is changed (`BatteryHeadline` in `site/app/cost-of-power/battery/Scenarios.tsx`). `fom` is A's fixed O&M and `ds` is `round(capex x 1000 x share x crf(rate, n) x MW)` with A's capital cost, debt share, interest rate and years of debt: the multiplication of 4.1, so at the defaults `ds` is 6,783,357 to the dollar and the three numbers are what they were (81.40, 475,477, 0.88). At the model's own round-trip efficiency and cycle limit each figure carries its check key, written with A's `fom` and `ds`, and `check-values` recomputes it from the table. At another step of efficiency or of the cycle limit the first two read the months of the file of steps (section 11.1), as scenario A's rows do; the summary sentence then names the step and leaves out the ancillary share, which the file does not hold; those figures carry no check key, and the first number's note says that the sections below are the model's own run at 86 percent and one cycle a day. Each month's coverage in "Every month" (4.9) and the two coverage lines of "With your contract" (4.7) read A's fixed O&M and debt payment as well.

### 4.4 The chart: revenue by year, USD per kW

- One bar per calendar year with at least one held month: the sum of the held months' `r(m, energy)` and `r(m, ancillary)`, each divided by 1,000, stacked. The label above the bar is the two summed and rounded to a whole dollar.
- A year is **complete** when all twelve of its months are held; otherwise the bar is hatched and labeled with its count of months. A hatched bar is the held months' sum, not a year.
- When the tallest bar is more than 2.5 times the second tallest (and there are at least three), the scale is set by the second tallest and the tallest is drawn broken with its value written (`year:<Y>:total`). ERCOT's 2021.
- Default, full years inside the exported window: 2024 energy 62.70 and ancillary 84.98; 2025 energy 57.39 and ancillary 30.05.

### 4.5 Income by stream

Rows: energy; ancillary services; each product; capacity (words only, never a number); the total; the total per kW. Columns:

**Session 296 (the owner's ruling of 15 October 2026, item 6: no window is the ERW's).** The columns are now the last twelve months (`l12:s`, as below), each calendar year the chart draws (`yr:<year>:s`: the year's held months summed, scaled; an incomplete year says how many months it holds), and one window the reader sets with two year pickers, leaving out the grid's stress events by a checkbox each (`win:<from>:<to>:<left out>:s`, the left-out events' ids joined by `+`, or `none`: the twelve-calendar-month mean of the window's held months, as "every year held" was computed, with each left-out event's days taken out of the month's energy, ancillary and total first, from `battery_stack_stress_daily`; a product's cell is not held once an event is left out, the daily table holding three streams). The window opens on every year held with nothing left out, which is the old "every year held" average and keeps its key (`avg:s`), so every figure at the default is what it was. The columns "last three full years" (`y3`) and "without the one month" (`avg_without`) are gone: the one month's share is still said under the table, and a reader who leaves Winter Storm Uri out of the window sees the average without its days. The table's units follow the box's toggle (per kW: the `_kw` keys, any stream), and a Chart | Table toggle draws the same columns as stacked bars. `site/app/cost-of-power/battery/Income.tsx`; `lib/batterystack.ts` (`eventMonths`, `windowMonths`, `windowAverage`, `yearStream`, the `yr`, `yr_kw`, `win` and `win_kw` cases of `stat`).

| Column | Formula per stream `s` | Shown when |
|---|---|---|
| Last twelve months (`l12:s`) | sum of `r(m, s)` over the last twelve months, scaled | a twelve-month window exists |
| Last three full years, a year (`y3:s`) | the newest complete calendar year and the two before it, each complete: their months' `r(m, s)` summed, divided by 3, scaled | three such years are held (ERCOT: 2023 to 2025) |
| Every year held, a year (`avg:s`) | for each calendar month January to December, the mean of `r(m, s)` over the held months of that calendar month; the twelve means summed; scaled | every calendar month has a held month |
| Without the one month (`avg_without:s`) | the same average with that month removed | one month carries the window (below) |

- A product not bought in a month counts as 0 in that month's sums (ECRS before June 2023).
- **The one month that carries the window** (`top_share`): among the held months, the one with the highest total; if it alone is more than 25 percent of the sum of all held months' totals (and at least twelve are held), the fourth column appears and the note gives its share, rounded to a whole percent. ERCOT: February 2021, 57 percent. It is removed from that one column only.
- The last row, per kW: the column's total per MW divided by 1,000 (`l12_kw:total`, `y3_kw:total`, `avg_kw:total`, `avg_without_kw:total`). Default: 81.40, 255.08, 614.58 and 269.68.

### 4.6 The line beside ERCOT's real awards (new in session 178, ERCOT only)

"Day-ahead ancillary services, January 2026 to July 2026: this model takes USD 2.25 per kW a month; ERCOT's storage resources were awarded USD 0.40 per kW of their power a month; the model is 5.66 times the awards." See section 9. Keys `bsa|<strategy>_<N>h|model`, `fleet`, `ratio`. It follows the reader's strategy and duration, not the size or the costs.

**For CAISO, since session 257: the line beside its market monitor.** CAISO's storage awards are not held, so the line sets the model beside a published report: "In 2025, for a 4-hour battery on the day-ahead schedule, this model takes USD 42.31 per kW from energy and USD 42.25 from regulation; CAISO's market monitor reports that real batteries in its area with a full year of operation earned about USD 35 per kW from energy and USD 9 from regulation" (figures as the table stood on 13 October 2026), with the report cited: CAISO Department of Market Monitoring, 2025 Annual Report on Market Issues and Performance, June 2026, section 1.3.3, Tables 1.7 and 1.8. The model's two figures are computed, not typed: the sum of `r(m, energy)`, and of `r(m, regup)` plus `r(m, regdn)`, over the twelve held months of 2025 for the 4-hour day-ahead battery at SP15, divided by 1,000 (`year_kw:2025:energy` and `year_kw:2025:regup+regdn`, under the key of that case, `bs|grid=caiso&dur=4&strat=dayahead&...`; no figure unless all twelve months are held). The line does not follow the reader's strategy or duration: it is the one case the market monitor's own model and the fleet's figures are set beside in [the method note](battery_stack.md), "CAISO beside its market monitor". When the reader's battery is another, the page reads that case's months from the same table. The published 35 and 9 are a constant of `site/lib/batterystack.ts` (`FLEET_BESIDE`), held to the method note by `tests/test_session257.py`.

### 4.7 With your contract (computed in the browser, never sent)

**Not on the page since session 208.** The contract is scenario A's and B's two assumptions, share and price (11.1, "The contract"), in the address like the others; the formulas below are those of sessions 67 to 207, kept as the record. The headline's coverage with a contract in A is 11.1's `(C + (1 - share_c) x R - fom) / debt`, the same arithmetic as the second line below, and carries no check key.

The reader types a share (percent), a price (USD per kW-month) and an end month. With `s = share / 100`, `M12` the last twelve months' total per MW and `AVG` the every-year average per MW:

- **Contracted income a year**: `s x MW x 1000 x price x 12`.
- **Market income on the uncontracted share**: `(1 - s) x M12 x MW`; beside it `(1 - s) x AVG x MW`.
- **Debt coverage with the contract**: `(contracted + (1 - s) x M12 x MW - fom x 1000 x MW) / ds`.
- **Debt coverage without it**: the headline coverage.
- **From the market after the contract ends**: `M12 x MW`; beside it `AVG x MW`.

The contracted share earns nothing from the market. **The end month changes no number**: it only words the last row's label.

### 4.8 Other grids

Words only. No number. **Since session 208 the table is one line under the grid picker** (`BatteryForm.tsx`, `data-other-grids`): PJM's prices are licensed and not held; NYISO and SPP are built and in review; ISO-NE's and MISO's reserve prices are held, not shown (license needed); their energy prices are on the seller tab.

### 4.9 Every month (folded)

**Since session 208 the fold is gone and the rows are a download**: `/cost-of-power/battery/months.csv` with the page's own parameters (`grid`, `dur`, `strat`, `mw`) and scenario A's, served by `site/app/cost-of-power/battery/months.csv/route.ts` from the same read as the page (`read.ts`) and the same library, with the provenance in `#` lines (the source table, when it was read, the fixed O&M and debt payments the coverage column uses, the 90 percent rule). Columns: month, held, energy, ancillary and total in USD for the size, total per kW, coverage (the formula below, blank for a month not held), days held, days in the month, days left out, days left out for a missing ancillary price, and each product's USD. The address takes the page's status: in review it answers the internal view alone (the proxy never sees a path with an extension, so the route applies `statusOf` itself).

For each month the table holds, newest first: energy, ancillary and total (`month:<m>:<s>`: `r(m, s)`, scaled); **coverage**: `(r(m, total) x 12 x MW - fom x 1000 x MW) / ds`, the month's revenue less a month of fixed O&M over a month of debt payments, shown only for a held month; days held of days in the month; days left out. Beneath: the days left out in all (`out`), and how many for a missing ancillary price.

### 4.10 Stress days (folded, ERCOT only)

**Not on the page since session 208.** The page no longer reads `battery_stack_stress_daily`; the table is public and the page links its download (`/api/download?table=battery_stack_stress_daily`) under the CSV line. The figures below are those the fold drew until then.

**Session 257: the table is read again, for the events' names alone.** The sentence with the download names the events the table holds for the grid shown, at the reader's strategy and duration: ERCOT's three by name ("Uri, Elliott, the 2023 heat", as before) and CAISO's by their days ("4 to 9 September 2024, 20 and 21 January 2025, ...": a rule makes them from CAISO's notices, [the method note](battery_stack.md), "CAISO's stress days"). No stress figure is drawn; `stress:<event>:<s>` still answers for any event the rows hold, CAISO's among them.

From `battery_stack_stress_daily`: for Winter Storm Uri (7 to 24 February 2021), Winter Storm Elliott (19 to 29 December 2022) and the 2023 heat (1 August to 10 September 2023), over the solved days inside the window: the count of days, energy, ancillary and total summed and scaled (`stress:<event>:<s>`), and the best single day's total with its date (`stress:<event>:best`).

### 4.11 What this model cannot see (folded)

<a id="cannot-see"></a>

**Not on the page since session 208.** The page keeps one sentence under the income table (energy is priced at the hub, not the battery's own node; reserves are paid for being held and are assumed never called) and links here. The fold's list, as it stood, for the default case's grid (ERCOT; the other grids' hub and products are section 3):

- **One battery does not move prices.** The battery is a price taker. Ancillary markets are small next to the energy market. A large battery, or a fleet of them, pushes those prices down, so large sizes are overstated, ancillary income most of all.
- **The hub, not your node.** Energy is priced at the grid's hub (ERCOT's `HB_HUBAVG`, CAISO's SP15, NYISO's N.Y.C. zone, SPP's `SPPNORTH_HUB`). A battery is paid its own node's price, which can differ in either direction.
- **Reserves are never called.** An award pays its capacity price and moves no energy. A real battery that is called sells energy at the real-time price, and must recharge.
- **No degradation beyond the round trip.** Round-trip efficiency is 86 percent, at most one full cycle a day, each day from empty. Capacity fade, augmentation, outages and station power are not modeled (the scenarios' degradation rate is a yearly cut to revenue, 11.1).
- **The strategy.** Perfect foresight: energy at the hourly real-time price and ancillary services at day-ahead prices, all known in advance, an upper bound, not a forecast. Day-ahead schedule: the battery is scheduled against day-ahead energy and ancillary prices and paid those prices, with no real-time trading, and its offers are assumed to clear.
- **Hourly.** Ancillary prices are hourly, so the whole model is. A battery trading the 5- and 15-minute real-time prices can earn more from energy than this shows.
- **No capacity payment.** ERCOT has none (an energy-only market); California's resource adequacy prices are contract statistics, not yet in the warehouse; New York's are held and their license is under review; SPP has no capacity market.
- **How long a reserve must be backed.** The battery must hold stored energy to deliver each upward reserve for the product's required duration: section 3.3's list, printed from `REQUIREMENTS` (ERCOT NPRR 1096 and 1282; CAISO tariff 8.4.1.1(g) and 8.4.3; one hour assumed for ERCOT before those dates).

## 5. Edge cases, as the code handles them

- **A missing interval or hour.** An hour missing one interval has no price; a day missing one hour of the energy price or of any product bought that day is left out whole and counted in `days_left_out`. ERCOT: no day left out under either strategy in the table of 5 October 2026.
- **A day with fewer or more than 24 hours.** Only the clock-change days: 23 hours in March, 25 in November. The same program with 23 or 25 hours; the one-cycle limit is per local day whatever its length. In the export: 10 March 2024, 9 March 2025, 8 March 2026 (23) and 5 November 2023, 3 November 2024, 2 November 2025 (25). CAISO's two 25-hour days are left out because the hub history does not hold their energy price.
- **Negative prices.** Section 3.4.
- **The first hour of every day holds no upward reserve.** The battery starts each local day empty, and an upward award needs its energy at the hour's start. In all 1,096 exported days the upward awards of the first hour are zero. This understates the result: at most USD 1.29 per kW over the last twelve months of the default case (1 MW of the best-paid upward product in every first hour), 1.6 percent of 81.40. Regulation Down is not affected (it needs room, and an empty battery has it).
- **Energy left at midnight is lost.** The next day starts empty. In the last twelve months 11 days end with more than 0.01 MWh stored; the mean at day's end is 0.023 MWh per MW.
- **The cap of a product by duration.** Section 3.3.
- **A month so far.** The current month is not held until 90 percent of its days are solved, so it is grey and outside every window. A month becomes held before it ends: on the 28th solved day of a 31-day month (28/31 = 0.903), the 27th of 30, the 26th of 28. **Until session 195 it was from that day the last of the last twelve months**, with the revenue of its solved days only, not scaled: the window moved forward one month about three days early and the headline changed, then rose a little each remaining day. **Since session 195 (the owner's ruling of 11 October 2026 on session 178's finding) the last twelve months end with the last complete month in the table**: a month is the window's last only when every one of its days is in the table, solved or left out (`whole` in `lib/batterystack.ts`). The window, the bad month's 36 months (which end with the window's last month), the first column of "Income by stream", the contract's market lines and the scenarios' revenue all move together, on the day the month is complete. The months inside a window are still the held ones (the 90 percent rule), and the averages of every year held and the chart still take a month from 90 percent of its days, as the older note states. On 11 October 2026 the newest held month is September 2026, which is whole, so no number moved: the headline before and after is 81.40, 475,477 and 0.88. The rule first acts when October 2026 reaches 28 solved days, about 28 October: the window then stays October 2025 to September 2026 until October is complete.
- **A held month with days left out** (up to 10 percent) counts with its solved days' revenue only. Nothing is scaled up.
- **A grid with no ancillary data.** The model is not built for it: PJM, ISO-NE and MISO are rows of words on the page. A grid in review (NYISO, SPP) is read from `site/data/battery_stack_review.json`, in the internal view only.
- **A table that cannot be read.** The page says so and shows no number.
- **What the address asks for and the page does not show (session 263).** A grid the tool does not hold or open, a duration or strategy the model was not run at, a size outside 1 to 5,000 MW, a scenario value outside its field's bounds or not a step of the model: the page shows the nearest thing it can (ERCOT; 4 hours; perfect foresight; the nearer bound; the default) and says so in one status line (`typedNotes()` in `site/lib/batterystack.ts`, `scenarioNotes()` in `site/lib/battery/finance.ts`). A value typed in a scenario's field outside its bounds is brought inside them and the field's note says so (`clampWords()`). Until session 263 each was replaced in silence. With no debt (a capital cost or a debt share of 0) the headline reads "has no debt to cover" and "No debt" (it read "not held times"); a term above the project life is cut to the life and the tail's note says so. The edge cases tested, with what the page does in each: `docs/reviews/packs/battery.md`, part 5.
- **On a machine without the ERCOT history** (the GitHub runner), the builder solves only the months the rolling tables reach and keeps every earlier month from its previous table; a month is never replaced by one resting on fewer days (`keep_fuller`).
- **Ties.** Where two schedules earn the same total, the split between energy and ancillary is not unique; the total is.

## 6. Assumptions, their defaults and sources

| Assumption | Value | Source | Reader can change it |
|---|---|---|---|
| Round-trip efficiency | 86 percent, split evenly between charging and discharging | Lazard LCOS v10.0, utility-scale, low end; the seller tab's | no: it is inside the model |
| Cycles | at most one full cycle a day; each day from empty | the seller tab's rule | no |
| Resolution | hourly | ancillary prices are hourly | no |
| Foresight | perfect, within the day | the strategy's definition | the strategy |
| Price taker | awards up to full power at the posted price | assumed | no |
| Reserves called | never | assumed | no |
| Where energy is priced | the hub (`HB_HUBAVG`, SP15) | assumed | the grid |
| Required durations | section 3.3 | ERCOT NPRR 1096 and 1282; CAISO tariff 8.4.1.1(g) and 8.4.3; one hour assumed for ERCOT before those dates | no |
| Capital cost | 610, 1,110, 2,300 USD per kW (2, 4, 8 hours) | Lazard LCOE+ June 2025, LCOS v10.0, midpoints; 8 hours NREL's Annual Technology Baseline 2025 since session 296: USD 241 per kWh times 8 hours plus USD 372 per kW, 2024 dollars (2,110, a straight line through the other two, until then) | through `ds` |
| Debt | 20 percent of capital cost, 8 percent, 20 years, level payments (session 208; 60 percent from session 67 to 207) | Lazard's storage capital structure | through scenario A's debt share, interest rate and term |
| Fixed O&M | 11.2, 22, 92 USD per kW a year | the same Lazard cases; 8 hours the ATB's 4 percent of its capital cost a year, which pays for augmentation (43.6 until session 296) | yes |
| A month counts | 90 percent of its days solved | the seller tab's rule | no |
| The outlier month | more than 25 percent of everything held | session 71 | no |

## 7. The replication

- **The CSV** (`warehouse/derived/battery_dispatch_export.py`): one row per local hour of the default case, 36 local months (October 2023 to September 2026, the window of the bad month), `in_last_twelve` marking the twelve. Columns: the hour in UTC and local time; the energy price and each product's price; charge, discharge, state of charge, the megawatts in each product; revenue by component. Per 1 MW. Fourteen comment lines of provenance (source tables, their retrieval times, the model's file hash and commit). The exporter solves each day with the model's own `solve_day` and refuses to write unless every month's sums equal `battery_stack_monthly` to within half a cent per MW; on 10 October 2026 all 36 months agreed.
- **The do-file** reads the CSV and prints: the last twelve months by stream for 100 MW, per kW, the ancillary share, the debt payment, the coverage, the full calendar years of the chart inside the window (2024, 2025), and the bad month. **Since session 263** it takes the page's defaults (20 percent debt at 8 percent over 20 years, a hurdle rate of 12 percent, degradation 2.6 percent a year, a life of 20 years; 60 percent debt until then) and prints scenario A's column too: coverage, NPV at the hurdle rate (per kW and for 100 MW), IRR (the same bisection as `irr()` in `site/lib/battery/finance.ts`: -99 to 1,000 percent, at most 200 halvings), the breakeven toll and the merchant tail. On the CSV of 13 October 2026 its Python mirror prints USD 81.40 per kW, 8,140,219, 33 percent, debt payments 2,261,119, coverage 2.63, NPV USD -697.80 per kW (-69,779,883 for 100 MW), IRR -8.8 percent, toll 4.19, tail 0 years, and a bad month of 475,477 (December 2024), each equal to what the page's library computes from the same months (`docs/reviews/packs/battery.md`, part 8). It follows the house rules: no continuation operator, one empty line between commands outside loops and none inside, every numeric column destrung with `replace force`, the sentinel -999 recoded per variable before any loop.
- **Stata is not installed on the machine that wrote it, so the do-file has not been run.** `tests/test_session178.py` parses it and enforces each rule; the Python mirror follows it step for step and its output equals the page's library on the same months.
- **Not in the CSV**: the columns that need years before October 2023 (the last three full years, every year held, the column without February 2021) and the stress days. They are sums of `battery_stack_monthly` rows by the formulas of section 4, and `check-values.mjs` recomputes them.

## 8. The independent check of the optimizer

`warehouse/derived/battery_optimizer_check.py` reads only the CSV and does not import the model.

1. **Is the model's dispatch allowed?** Every limit of section 3.4 is recomputed from the hourly columns.
2. **Could another dispatch earn more?** The day is written again from scratch in another form (the state of charge as its own variable, tied by an equation; the model uses running sums and inequalities only) and solved with the interior-point method of HiGHS, named explicitly; the model leaves the choice of method to HiGHS. Both use the HiGHS library: scipy is the only solver in the environment.
3. **A ceiling that needs no solver.** By weak duality, any non-negative prices on the limits give, in plain arithmetic, an upper bound on what any allowed dispatch can earn. The script computes that bound from the second solve's dual prices. When the model's revenue reaches it, the model's day is proven optimal whatever the solvers did.

**The sample**: three days of each of the last twelve months drawn with `random.Random(178)`, plus the highest-revenue day (26 January 2026, USD 3,923.87 per MW), the day with the most negative energy price (24 February 2026), and both clock-change days (2 November 2025, 8 March 2026): 40 days. No day of the last twelve months used the switch.

**Result, the sample**: largest absolute gap USD 0.00000003 per MW and day, largest relative gap 2.9e-10; the model is never above the optimum and never below it; the ceiling is reached on 40 of 40 days; no limit is broken.

**Result, every one of the 1,096 days**: the same, largest relative gap 3.2e-10; the ceiling reached on 1,095. The other day is 4 January 2025, the one switch day: the model's USD 129.841672 equals this script's own mixed-integer optimum and the best of all 4,096 switch patterns tried one by one, and stands USD 0.038 below the linear ceiling, as it should (the ceiling allows charging and discharging together).

## 9. Beside ERCOT's real awards

**What is compared.** The model's ancillary revenue (`battery_stack_monthly`, `ercot:HB_HUBAVG`, `<strategy>_<N>h_revenue_ancillary_usd_per_mw`) beside the day-ahead ancillary awards of every Energy Storage Resource in ERCOT (`ercot_storage_dam_awards_monthly`, `ercot:esr_fleet`, `revenue_ancillary_usd_per_mw`), from ERCOT's 60-Day DAM Disclosure Reports (see [its note](ercot_storage_dam_awards.md) and the page `/cost-of-power/battery/awards`). Both value awards at the same day-ahead clearing prices.

**Window.** The local months both tables hold whole (`days_held = days_in_month` in each): January to July 2026, seven months. December 2025 (26 days) and August 2026 (5 days) are partial in the awards and are left out, not scaled.

**Unit.** USD per kW of power and month: the sum over the seven months, divided by 1,000 and by 7. The model's kW is the battery's rated power. **The fleet's kW** is the month's `mw`: the sum over every storage resource in the file of its highest HSL (high sustained limit) in the month, a resource with no award included: 17,180 MW in January 2026 to 21,365 MW in July.

| Strategy, duration | Model | Fleet | Ratio |
|---|---|---|---|
| Perfect foresight, 2 hours | 2.26 | 0.40 | 5.71 |
| Perfect foresight, 4 hours (the default) | 2.25 | 0.40 | 5.66 |
| Perfect foresight, 8 hours | 2.06 | 0.40 | 5.20 |
| Day-ahead schedule, 2 hours | 2.24 | 0.40 | 5.64 |
| Day-ahead schedule, 4 hours | 2.17 | 0.40 | 5.48 |
| Day-ahead schedule, 8 hours | 1.86 | 0.40 | 4.69 |

**Why the model is higher: it sells more megawatts, not at better prices.** In the mean hour of those months the default model holds 142 percent of its rated power in awards (Regulation Up 45, Regulation Down 78, Responsive Reserve 3, ECRS 2, Non-Spin 15; upward and downward power count separately). The fleet held 21.6 percent of its `mw` (Regulation Up 2.4, Regulation Down 1.9, Responsive Reserve 6.6, ECRS 4.6, Non-Spin 6.1; from `ercot_dam_esr_awards`, megawatt-hours awarded over `mw` times the month's hours). Regulation is the gap: the model takes 122 percent of its power in the two regulation products, the fleet 4.4 percent.

**Caveats.**
- The model is a price taker with perfect foresight of the day's prices: it takes as many megawatts of each product as its power and energy allow, at the posted price. ERCOT buys a fixed quantity of each product; a fleet of about 20,000 MW cannot all hold regulation at once.
- The fleet's awards are real quantities at real clearing prices, but day-ahead only: no real-time awards, no deployment energy, no contracts. They are a floor on what the fleet earned from ancillary services, not the whole.
- Of the fleet, 216 to 252 of 306 to 332 resources held any day-ahead award in a month; the others are in the denominator.
- The fleet's durations are not known (ERCOT's file states power, not energy), so the fleet is one mixed class beside each of the model's durations.
- Seven months, none of them a summer peak in full. The ratio is a statement about those months.

**Where the number on the page comes from.** `warehouse/derived/battery_awards_compare.py --snapshot` writes `site/data/battery_awards_beside.json` from the two tables; the page imports it. It is refreshed by running that command again, and a test compares it with the tables when they are on the machine.

## 10. Where the notes and the code differ

1. **`battery_stack.md`, "The grids in review", "Required durations: assumed, not cited"** says both NYISO products and all four SPP products are assumed at one hour because the operators' documents were not read. The code (since session 102) cites SPP's Integrated Marketplace Protocols, Revision 119, section 4.2.2, and NYISO's tariff section 4.4.2.1 for spinning reserve; only NYISO's Regulation Capacity is still assumed. The hours are the same (one), so no number differs. The note's table is out of date.
2. **`battery_stack.md`, "Never filled"** gives session 67's day counts (ERCOT 3,195 and 3,197 days). The table of 5 October 2026 holds 3,198 and 3,199. A dated count, not a method difference.
3. **No note says that the first hour of each day can hold no upward reserve** (section 5). The older note says each day starts empty and that energy bought late is lost at midnight; the first-hour consequence follows from the code's limit at the hour's start and is not written anywhere.
4. **No note says that a month becomes held, and enters the last twelve months, before it ends** (section 5). The older note states the 90 percent rule for "the averages"; the code applies it to the last twelve months, the bad month's window and the chart as well. Session 195: the last twelve months now wait for the whole month (section 5, "A month so far"), by the owner's ruling.
5. **No note says the contract's end month changes no number** (section 4.7). The page collects it and uses it in one label.
6. **`lib/batterystack.ts` still computes four statistics the page no longer shows** (`share`, `p10`, `n`, `avg_without_top`: session 67's lead, replaced in session 71). They are reachable only through a check key; nothing prints them.
7. **The page's own text and the code agree** on everything checked: the round trip, one cycle, each day from empty, the debt default, the 90 percent rule, the required durations.

## 11. What the browser has, for session 179

**What reaches the browser today.** The server reads one hub, one strategy and one duration and passes to the client component `ContractResult` the array `ms: Month[]` and the inputs `x`. Each `Month`, per 1 MW of rated power:

| Field | Unit | Note |
|---|---|---|
| `m` | `YYYY-MM` | the local month |
| `held` | true or false | 90 percent of its days solved |
| `daysHeld`, `daysOut`, `daysOutAncillary`, `daysOutEnergy`, `daysInMonth` | count | |
| `energy`, `ancillary`, `total` | USD per MW for the month | null when no day is solved |
| `products` | USD per MW, by key | ERCOT: `regup`, `regdn`, `rrs`, `ecrs`, `nspin` |

`x`: `grid`, `dur`, `strat`, `mw`, `fom` (USD per kW a year), `ds` (USD a year). The constants `COSTS` (capital cost and fixed O&M by duration), `DEBT` (0.6, 0.08, 20), `RTE` (0.86) and `crf` are exported by `lib/batterystack.ts` and can be imported by a client component.

**Not passed today, though the table carries it:** `discharged_mwh_per_mw` (MWh per MW, by month). `monthsOf` keeps only the revenue and day variables. It is in the rows the server already reads, so adding it to `Month` costs no new read. With it the browser can state the cycles the model actually ran: `discharged / (sqrt(0.86) x duration) / days`: 0.983 a day over the default case's last twelve months.

**Only one strategy and one duration are on the page at a time.** Two scenarios that differ in duration or strategy need a second set of months: a second read on the server, or both passed down.

**What the browser can compute from the monthly output**, because it sits after the model: capital cost, debt share, interest rate, term (the debt payment is `capex x 1000 x share x crf(rate, term) x MW`), fixed O&M, project life and hurdle rate (a present value of a yearly revenue it assumes), and a degradation rate applied as a yearly haircut to revenue, which is an assumption of its own (the model has no degradation: fade shortens duration, and revenue is not proportional to duration; the three durations give 2, 4 and 8 hours and nothing between).

**What it cannot compute, and must state as fixed:**
- **Round-trip efficiency.** It is inside every day's optimization three times: the state of charge, the energy behind each reserve, and the cycle limit. Revenue is not a simple function of it: the dispatch changes. The monthly table holds 86 percent only. To offer it the model must be run for each value offered and the table given an efficiency dimension (each value adds a full copy of the table: 2 grids x 2 strategies x 3 durations).
- **Cycles a day.** The limit of one full cycle is a constraint of the optimization, and it binds on most days (0.983 realized). A different limit is a different model run, with the same cost as above. The browser can show the realized cycles once `discharged_mwh_per_mw` is passed, and cannot change the limit.
- The same holds for the required durations, the hourly resolution, the price-taker assumption and reserves never called.

### 11.1 Scenarios A and B: what session 179 built on this

The section "Scenarios A and B" of the page: ten assumptions, two scenarios on the same seven rows, and a sensitivity chart. It is computed in the browser by `site/lib/battery/finance.ts` (pure arithmetic, no request) from the months the page already holds. Nothing above this section changed: an address with none of the parameters below shows the page as it was, with this block at its defaults.

#### The block the three pages share (session 195)

Since session 195 the assumptions panel, the two columns, the row "What differs", the row "B against A" (the datacenter page's) and the sensitivity chart are one component, `site/components/decisions/ScenarioBlock.tsx`, on the three decision pages: this page, "What a generator earns" (`generator_earns_algorithm.md`, section 11) and "What a datacenter pays" (`datacenter_pays_algorithm.md`, section 4.14). It is described here once; the other two notes point to this section.

- **What each page hands it.** Its own assumptions (label, unit, bounds, default, the default's source, and for a listed assumption its steps), its own rows (each a function of a scenario), its own chart figures and the words a row of the chart gives. The arithmetic stays in the page's own library (`site/lib/battery/finance.ts`, `site/lib/seller/finance.ts`, `site/lib/datacenter/finance.ts`); the component computes nothing.
- **What is the same on the three.** The two buttons that put A or B in view; "Copy A to B"; "Reset all of" the scenario in view; one field an assumption, with its Reset (grey at the default) and the line "Default ..." with its source; the table with a column for A and one for B, whose headings list only the assumptions that differ; the row "What differs" in words; the chart for the scenario in view, one row an assumption, two thin bars (lowered and raised by the stated step) from the scenario's own figure, largest move first, with the sentence a row gives when pointed at and "The chart as a table".
- **Where the two scenarios are held.** Above the page's sections (`ScenarioState`), not inside the block, so that the page's headline reads scenario A.
- **Scenario A sets the headline.** The headline numbers of each page are scenario A's rows, computed in the browser as A is changed. The fields that held one idea twice are gone: the fixed O&M and the annual debt payments of "Your battery" and of "Your plant", the power per GPU and the overhead ratio of "Your load". A change of B moves no headline number. At the defaults every headline number is what it was before the session.
- **The sentence under the table states scenario A**, whichever scenario is in view. Until session 195 it stated the scenario in view. The chart is still the scenario in view's.
- **The old names.** An address written before session 195 can hold the names of the fields that are gone. They are read once, as old names of the scenarios' assumptions, and then leave the address:
  - `fom` (battery, generator): scenario A's fixed O&M.
  - `ds` (battery, generator), the annual debt payments in USD for the reader's size: scenario A's capital cost becomes the one at which A's debt share, interest rate and term give that payment, `capex = ds / (1000 x MW x share x crf(rate, n))`. A's debt payment for the size, rounded to a dollar, is then `ds` again, so the headline coverage is the one the link showed. When `ds` is what A already pays, nothing moves. A payment that would need a capital cost above the field's bound (10,000 USD per kW) is clipped to it.
  - `gpu` and `pue` (datacenter): the power per GPU and the overhead ratio of both scenarios, because "Your load" was the default of both.
  - A scenario's own parameter wins over an old name: `af` over `fom`, `ac` over `ds`, `ag` and `bg` over `gpu`, `ap` and `bp` over `pue`.
- **The address.** As before: two-letter parameters, the scenario's letter then the assumption's, written only where a value differs from its default; `v=b` puts B in view. It is rewritten in place (`history.replaceState`).
- **Nothing is sent.** A change sends no request, and no usage count is sent from the block: the owner's ruling of 11 October 2026 closes the question sessions 179, 186 and 194 left open.
- **Checks.** `site/scripts/check-decisions-face.mjs` (the three pages in four states, at 1,280 and 390 px: the headline is scenario A's rows, the sentence states A, no sentence tells the reader what to do); each page's own scenario check; `tests/test_session195.py` and `site/scripts/test-decisions-195.mjs` (the old names, the debt payment to the dollar, the whole-month rule).

#### The ten assumptions and their defaults

| Assumption | Default | Source of the default | Bounds | Address (A, B) |
|---|---|---|---|---|
| Capital cost, USD per kW | 610, 1,110, 2,300 (2, 4, 8 hours) | Lazard, Levelized Cost of Energy+, June 2025, LCOS v10.0, midpoints; 8 hours NREL's Annual Technology Baseline 2025 since session 296 (2,110, a straight line through the other two, until then; section 6) | 0 to 10,000 | `ac`, `bc` |
| Debt share, percent | 20 | Lazard, the storage cases: "20% debt at an 8% interest rate and 80% equity at a 12% cost" (session 208; 60 from session 179 to 207, Lazard's generation structure) | 0 to 100 | `as`, `bs` |
| Interest rate, percent a year | 8 | the same | 0 to 30 | `ar`, `br` |
| Term of the debt, years | 20 | Lazard: "Economic life sets debt amortization schedule"; 20 years for storage | 1 to 40, whole | `at`, `bt` |
| Fixed O&M, USD per kW a year | 11.2, 22, 92 | the same Lazard cases as the capital cost; 8 hours the ATB's 4 percent of its capital cost a year since session 296 (43.6 until then) | 0 to 500 | `af`, `bf` |
| Round-trip efficiency, percent | 86 | Lazard LCOS v10.0: 86 to 92 percent for utility-scale storage; the model runs at the low end | the steps 86, 89 and 92 | `ae`, `be` |
| Cycles a day, at most | 1 | the model's rule (section 3.4) | the steps 0.5, 1, 1.5 and 2 | `ay`, `by` |
| Degradation, percent a year | 2.6 | Lazard, Levelized Cost of Energy+, June 2025, LCOS v10.0, "Energy Storage Use Cases, Illustrative Operational Parameters": battery degradation of 2.6% per annum for the utility-scale standalone battery, at 2 and at 4 hours (session 196; until then 0, none held) | 0 to 20 | `ad`, `bd` |
| Project life, years | 20 | Lazard: 20 years for storage | 1 to 40, whole | `al`, `bl` |
| Hurdle rate, percent a year | 12 | Lazard, the same report: "80% equity at a 12% cost" in its storage cases; the default is that cost of equity, since the NPV is to equity (session 208; 9.6, the weighted cost 0.6 x 8 + 0.4 x 12, from session 196 to 207; 8 before, none held) | 0 to 40 | `ah`, `bh` |
| Contract share, percent of the battery's power | 0 | none: the default is fully merchant (session 208). A contracted share is paid the contract price every month of the debt's years and earns nothing from the market | 0 to 100 | `an`, `bn` |
| Contract price, USD per kW-month | 0 | none: the reader's own term; no published price is held (session 208) | 0 to 100 | `ap`, `bp` |

- **The two defaults that had no cited source have one since session 196** (the owner's ruling of 11 October 2026). Until then the degradation defaulted to none and the hurdle rate to the interest rate, both to be confirmed by Samuel (session 179's report). Lazard's June 2025 report states its financing in full, "60% debt at an 8% interest rate and 40% equity at a 12% cost", so the hurdle rate's default is that weighted cost, 9.6 percent; the same report's storage cases give a battery degradation of 2.6 percent a year, which is the degradation default at every duration (Lazard prints it for 2 and 4 hours; 8 hours takes the same, as its costs are already an extrapolation). What moved at the defaults: NPV, from USD -52.68 million to USD -62.59 million for the default case; the 2-hour battery's IRR, from -1.7 percent to none. No headline number moved. "Cross-checks", at the end of this note, sets the two beside the other published conventions.
- **Session 208 (the owner's rulings of 12 October 2026): the debt share is 20 and the hurdle rate 12, and a contract is two assumptions.** Lazard's storage cases carry "20% debt at an 8% interest rate and 80% equity at a 12% cost", a different structure than its generation cases (the cross-check row "Debt share" below asked the question; this is the ruling). The NPV is to equity, after the debt payments, so the rate that discounts it is equity's, 12 percent, on the battery and on the generator page; the datacenter page keeps the weighted cost. What moved at the defaults of the default case: debt payments USD 6,783,357 to 2,261,119 a year; coverage 0.88 to 2.63 times; NPV USD -62.59 million to -69.78 million (less debt means more equity paid in at year 0, and a higher rate on it); IRR from none to -8.8 percent; the breakeven toll USD 8.90 to 4.19 per kW-month. No headline number other than the coverage moved. The contract's share and price are the eleventh and twelfth assumptions, 0 by default, so the default scenario is fully merchant and every figure at a share of 0 is what it was.
- The steps of efficiency are the two ends and the midpoint of Lazard's range. The steps of the cycle limit other than 1 are the reader's, not a source's.
- **The address.** Each scenario's assumptions are two-letter parameters, the scenario's letter then the assumption's (`c` capital cost, `s` debt share, `r` interest rate, `t` term, `f` fixed O&M, `e` efficiency, `y` cycles, `d` degradation, `l` life, `h` hurdle rate, and since session 208 `n` contract share, `p` contract price); `v=b` puts B in view. A parameter is written only when its value differs from the default, so no parameter means the defaults. The page's own four (`grid`, `dur`, `strat`, `mw`) work as before; since session 195 `fom` and `ds` are old names of scenario A's (above). A value outside its bounds is clipped; one that cannot be read, or a step that is not held, takes the default. The address is rewritten in place (`history.replaceState`): a change sends no request. The panel's Show and its duration links carry the scenarios; a change of duration drops a typed capital cost and fixed O&M, whose defaults scale with the duration.
- **Scenario A sets the headline (session 195).** Until session 195 the scenarios did not read the "Your battery" panel's fixed O&M and annual debt payments, which set the headline coverage: one idea in two places. Those two fields are gone. A scenario's fixed O&M is its own, and its debt payment is computed from its capital cost, debt share, interest rate and term; the headline coverage is scenario A's (0.88 times in the default case, before and after).

#### The revenue a scenario reads

`R` is the last twelve months' total revenue per kW (section 4.2's window and sum, divided by 1,000), and the 10th-percentile month is section 4.3's. Both are read:

- at the model's own values (86 percent, one cycle): from the page's months, so the scenario shows the page's own figures (USD 81.40 per kW and USD 475,477 in the default case);
- at another step: from `site/data/battery_scenario_steps.json`, the model's own run at that step.

**The file of steps** is written by `warehouse/derived/battery_scenario_steps.py`. For ERCOT and CAISO, both strategies and the three durations, it solves every day of the page's 36-month window with the model's own `solve_day`, once for each of the twelve pairs of an efficiency (0.86, 0.89, 0.92) and a cycle limit (0.5, 1, 1.5, 2), and keeps each month's total. The efficiency is `solve_day`'s own argument. The cycle limit is the right-hand side of the model's one-cycle constraint (section 3.4: `sum of d_t / eta <= D`), multiplied by the step: `<= cycles x D`. Nothing else differs, and the model's file is not changed. Each solution passes the model's `check_day`. The script refuses to write unless its (0.86, 1) run equals `battery_stack_monthly` month by month to half a cent per MW with the same count of days.

**Nothing is interpolated.** The two controls offer exactly the steps in the file. At a step, a month's total replaces the page's total for that month; the windows, the 90 percent rule and the nearest-rank percentile are unchanged.

**The file is static and dated; it cannot go stale silently.** It is rebuilt by running the script, not by the daily run. The page uses a step only while the file still describes the live table: every held month of the page's 36-month window must be in the file, with the same count of solved days and, in the file's (0.86, 1) cell, the same total to within half a cent per MW (`stepState`). When the window has moved on (a new month is held, about the 28th of each month) or a month was revised, the two controls offer the default step alone and the panel says which happened and to which month the file reaches. `tests/test_session179.py` fails on a machine with the tables, with the command to rebuild. A grid in review (NYISO, SPP) has no case in the file and offers the default step alone.

#### The formulas

Per kW of rated power; the page multiplies by `1,000 x MW` for the reader's size. `share`, `rate`, `deg` and `hurdle` are fractions here (the reader types percent).

- **Capital recovery factor.** `crf(i, n) = i / (1 - (1 + i)^-n)`; at `i = 0`, `1 / n`.
- **The debt's years.** `n = min(term, life)`: a term longer than the project life is cut to the life.
- **Annual debt payment.** `debt = capex x share x crf(rate, n)`. Default case: `1,110 x 0.6 x 0.101852 = 67.83` per kW, USD 6,783,357 for 100 MW.
- **Revenue in year t.** `R_t = R x (1 - deg)^(t - 1)`: the last twelve months repeated every year of the life, falling by the degradation rate each year after the first. This is an assumption, not a forecast: the future is taken to repeat the last twelve months. Degradation is a haircut on revenue; the model itself has no fade (fade shortens duration, and revenue is not proportional to duration).
- **Cash flows to equity.** `F_0 = -capex x (1 - share)`. For `t = 1 to life`: `F_t = R_t - fom - debt` while `t <= n`, and `F_t = R_t - fom` after. No tax, no tax credit, no augmentation, no residual value, no inflation: revenue and costs are flat in today's dollars apart from degradation.
- **NPV at the hurdle rate.** `NPV = sum over t = 0 to life of F_t / (1 + hurdle)^t`. It is the value to equity, after debt payments, which is why the debt share, the interest rate and the term move it.
- **The contract (session 208).** With `share_c` the contracted share of the battery's power (a fraction) and `price` the contract price in USD per kW-month: the contract's income a year is `C = share_c x price x 12` per kW of the whole battery. For the debt's years, `t = 1 to n`, the income is `I_t = C + (1 - share_c) x R_t`: the contracted share is paid the contract price every month and earns nothing from the market, and the rest earns what the market paid, falling with degradation as before. After them, `I_t = R_t`: the whole battery in the market. The cash flow becomes `F_t = I_t - fom - debt` while the debt lasts and `I_t - fom` after. Debt coverage with a contract is `(C + (1 - share_c) x R - fom) / debt`. The breakeven toll and the merchant tail do not read the contract (the toll is a price on the whole battery; the tail is the years after the debt, when the contract has ended). At `share_c = 0` every formula is the one above it, so the default is the merchant case of sessions 179 to 207. An older address or an older set of assumptions without the two keys is read as no contract.
- **IRR.** The rate at which that sum is zero, found by bisection between -99 percent and 1,000 percent a year, to 1e-10 of a percentage point. When the sum has the same sign at both ends of the bracket (for example no year's cash flow is positive, as in the default case), there is no such rate and the page says "none". Where the flows change sign more than once, several rates can exist; the page shows the one the bisection reaches.
- **Debt coverage.** `(R - fom) / debt`: the last twelve months' revenue less fixed O&M, over the annual debt payment. With no debt (`share = 0` or `capex = 0`) the page says "no debt".
- **Breakeven toll.** The price, in USD per kW-month, of a toll on the whole battery at which coverage is 1.25: solving `(12 x toll - fom) / debt = 1.25` gives `toll = (1.25 x debt + fom) / 12`. A battery under a toll on all of its power earns nothing from the market, so this row does not depend on revenue, efficiency, cycles or degradation. Default case: `(1.25 x 67.83 + 22) / 12 = 8.90`.
- **Merchant tail after the contract.** The toll is taken to run as long as the debt (`n` years). The tail is the years after it, `t = n + 1 to life`, and its value is `sum of (R_t - fom) / (1 + hurdle)^t` over those years: what the market pays the battery after the contract, with no debt left, valued at year 0 at the hurdle rate. With the default term equal to the life there are no such years and the value is zero; a term of 10 years gives years 11 to 20. The contract panel's own end month is not read (it stays on the reader's device and is never in the address, so a shared link could not carry it).

#### The rows, and what differs

Seven rows, the same for A and B: revenue last twelve months (USD per kW); the 10th-percentile month (USD for the reader's size, with its month); debt coverage (with the annual debt payment); NPV at the hurdle rate (USD for the size, and per kW); IRR; the breakeven toll; the merchant tail. Each column's header lists only the assumptions whose values differ between A and B, and nothing when none does. The last row says it in words: "B: capex USD 1,100 per kW against 1,300; hurdle rate 8 percent against 10." "Copy A to B" sets B to A. The sentence under the table states the NPV of the scenario in view at its hurdle rate.

#### The sensitivity chart

For the scenario in view: each assumption is moved down and up by one stated step, the other eleven held (session 208; nine until then), and the NPV recomputed. The steps: capital cost USD 100 per kW; debt share 10 points; interest rate 1 point; term 5 years; fixed O&M USD 5 per kW a year; efficiency one step (3 points); cycles one step (0.5); degradation 1 point; life 5 years; hurdle rate 1 point; contract share 10 points; contract price USD 1 per kW-month (session 208). A move that leaves the assumption's bounds, or a step the file does not hold, is not drawn (degradation at 0 has no lower step). The rows are sorted by the larger of the two moves. The two bars start at the scenario's own NPV (the vertical line). The colours are the site's first two categorical colours and carry no verdict; the same figures are in the table under the chart.

Since session 208 the chart is the page's third section, "What matters most", with one line on how to read it: each row moves one assumption of the scenario in view down and up by its step, holds the others, and draws where NPV lands from the scenario's own NPV; the longest bars are the assumptions that matter most. At the defaults of the default case the order is: capital cost (USD 9.52 million either way), cycles a day (the model's own step, USD 11.14 million up), contract share (USD 5.23 million: ten points of the battery contracted at a price of 0 earn nothing), fixed O&M, degradation, project life, debt share, interest rate, round-trip efficiency, hurdle rate, term, contract price (USD 0: a price with no share moves nothing). **Session 263: that order is not what the library draws.** At the defaults the contract's two rows are not drawn (session 211), and `sensitivity()` sorts cycles a day first: its larger move is the step down to 0.5 cycles (USD 11.14 million), the step up to 1.5 is USD 1.40 million; capital cost is second (USD 9.52 million). Section 11.2 holds the figures as the library computes them.

#### Session 296: the box, the figures, the charts and the two sensitivity modes (the owner's rulings of 15 October 2026)

- **The box "Assumptions"** (`site/app/cost-of-power/battery/Settings.tsx`): the page's left box holds five sections that open and close, each with one line of its settings while it is closed: Assumptions (the battery: grid, duration, strategy, size; and the units, per kW or this battery), Headline figures, Charts, Financing and Sensitivity. Assumptions and Headline figures open by default. Financing holds the twelve assumptions of the scenario in view, the panel this section described in the second question until this session, unchanged, with the contract's share and price as a sub-group (`components/decisions/ScenarioBlock.tsx`, `ScenarioPanel`); the second question draws the table alone. Every choice lives in the address with the scenarios (`lib/battery/view.ts`: `u`, `hf`, `ch`, `sc`, `wf`, `wt`, `lo`, `it`, `sm`, `sp`, `sx`, written only where it differs from the default) and nothing is requested.
- **Headline figures:** the reader picks up to six of eight, in the page's order: the three of before (the last twelve months, the bad month, debt coverage), NPV at the hurdle rate, IRR, the breakeven toll, the payback year and NPV per dollar of equity, each scenario A's. The payback year is the first year `t` in which `F_0 + ... + F_t` is no longer negative, undiscounted (0 when no equity is paid in; "none" when it stays negative through the life); NPV per dollar of equity is `NPV / (capex x (1 - share))`, "no equity" at a debt share of 100 or a capital cost of 0 (`paybackYear`, `npvPerEquity`, `equityIn`). The three of before keep their check keys; the five new figures carry none, as the results table's cells carry none. Per kW, the bad month is written from `p10_36_kw` (the month's total per MW over 1,000, no key: the table's own figure is the USD one).
- **Charts:** up to three of four, side by side on a wide screen: revenue by stream (the year chart of 4.4, unchanged in its numbers) and three from scenario A's years (`projection`: for `t = 1 to life`, the income `I_t`, `I_t - fom`, the debt payment while the debt lasts, `I_t - fom - debt`, and the debt still owed at the end of the year, `B_t = B_(t-1) x (1 + rate) - debt`, from `B_0 = capex x share`): "cash after costs", "cash after debt" and "the debt" (the payment and what is owed). Each has a Chart | Table toggle, as the income table does. The scale is the reader's: linear; log (base 10, drawn only when every value is above zero, else the chart says so and draws linear); adjusted, the page's own rule, where a period above 2.5 times the next is drawn to the top of the scale with a break and its value written, the default. `components/tool/SeriesChart.tsx`.
- **The two sensitivity modes** (`sensitivityIn`, `movedValue`, `rangesOf`): the chart of "What matters most" moves each assumption of the scenario in view either to its published low and high case (the sourced range, the default) or down and up by a percent of its value the reader sets (10 by default, 1 to 100), and measures the move in NPV or in IRR (a move that leaves no rate of return draws no bar on that side). In the sourced range the cases are Lazard's (LCOE+ June 2025, LCOS v10.0: the low and high of its 2- and 4-hour cases for the capital cost and fixed O&M, 20 and 60 percent debt from its storage and generation structures, 86 to 92 percent efficiency, 2.6 percent degradation, 20 years) and the ATB's (NREL, Annual Technology Baseline 2025: its own capital cost by duration, 4 percent of it as fixed O&M, 85 percent efficiency, no degradation, 15 years), the lower and the higher of the two where both state a figure; an assumption both state once (the interest rate, the term, the hurdle rate, cycles a day, the contract's two) has no row, and a line under the chart says so. At 8 hours Lazard prints no case: the capital cost's and fixed O&M's low and high are the straight lines through its 2- and 4-hour low cases and high cases, an extrapolation, with the ATB's 8-hour figures inside them. Efficiency and cycles a day take the steps the model was run at: the lowest and highest step inside the range, or, by a percent step, the nearest step held in that direction. The figures are typed in `rangesOf` with their sources; `site/data/sourced_ranges.json` (the data machine's session 306) takes the same shape and replaces them when it is in the live set. The sensitivity of session 208 (`sensitivity`, one stated step each way) is kept in the library for its tests; the page no longer draws it at the default, which is the one figure of the page that reads differently after this session.
- **The 8-hour defaults are the ATB's** (item 8): a capital cost of USD 2,300 per kW (241 per kWh times 8 hours plus 372 per kW, in 2024 dollars, NREL/TP-6A40-93281, section 2.2) and fixed O&M of USD 92 per kW a year (4 percent of it, which pays for augmentation), where a straight line through Lazard's 2- and 4-hour midpoints gave 2,110 and 43.6 until this session. The 8-hour page's revenue does not move; its debt payment, coverage, NPV, IRR and toll do.
- **Hover tips** (items 9 and 10): the grey notes that explained (the year chart's, the income table's, the units', the scale's, the sensitivity's) are tips beside their titles; a grey line that carries a checked number, a link or a download stays in view. The duration and each strategy carry a one-line hover; "perfect foresight" keeps its name.
- **Checks:** `site/scripts/test-battery-finance.mjs` (the ATB's figures, the payback year, NPV per dollar of equity, the projection, the two modes, the ranges); `site/scripts/check-battery-scenarios.mjs` (the box's five sections and their lines, the six rows of the sourced range and the line naming the four without one, the percent step with a contract); `tests/test_session296.py`.

#### Session 297: the tax credit, the fade method with augmentation, and the stress repeats (the chain prompt of 19 October 2026)

Six more assumptions, each at a default that moves nothing, so every figure at the defaults is what it was. Per kW; `itc`, `fade` are fractions here (the reader types percent); the address letters are `i`, `o`, `g`, `m`, `k`, `x`.

- **Investment tax credit** (`itc`, default 0, 0 to 70 percent of the capital cost): taken at year 0 against the equity paid in, `F_0 = -capex x (1 - share) + capex x itc`. Nothing else moves: no depreciation, no tax, no basis adjustment. The hover names the federal credit for energy storage (the IRS's, Internal Revenue Code section 48E) and says to confirm the credit, its rate and the project's eligibility before use. At the default case, 30 percent raises NPV by the credit itself, USD 333 per kW (USD -697.80 to -364.80), and the IRR from -8.8 to -4.2 percent.
- **The degradation method** (`method`: 0 the revenue cut, the page's own since session 196; 1 capacity fade with augmentation). Under the fade method the degradation rate above is not applied; instead the battery's capacity fades by `fade` each year since its last restoration, and revenue follows the capacity (an assumption: the model is not run again at a shorter duration, so revenue is taken proportional to the capacity): `R_t = R x (1 - fade)^k`, where `k = (t - 1) mod aug` when augmentation restores the battery every `aug` years (3, 5, 7 or 10) and `k = t - 1` with none. Augmentation is paid at the end of each year `t` that is a multiple of `aug`, except the last year of the life: `(1 - (1 - fade)^aug) x hours x augcost`, the capacity lost over the period, times the battery's hours (kWh per kW), times the cost per kWh added; it is a cost of that year in the flows, the tail and the projection. Defaults: `fade` 2.6 percent (Lazard's rate; NREL's ATB 2025 states none of its own), `aug` none, `augcost` USD 241 per kWh (the ATB's energy component, 2024 dollars). With no augmentation and the same rate the fade method's revenue equals the revenue cut's, so switching the method alone moves nothing; augmentation every 5 years at the default case costs USD 118.97 per kW in years 5, 10 and 15 and takes NPV from USD -697.80 to -768.12 per kW; fade 0 (the ATB's convention, its fixed O&M paying for augmentation) gives -613.19.
- **The stress repeats** (`stress`, default 0, whole, 0 to 40; the roadmap's "what if Uri happened again"): each repeat adds the grid's peak stress event's window revenue (the event in `battery_stack_stress_daily` whose window paid the most for this battery, USD per kW) once, spread evenly over the life's years: `R_t` gains `stress x peak / life` in every year, before the contract's share, after the degradation. Coverage and the breakeven toll read the last twelve months and do not move; NPV, IRR, the payback year, the tail and the projection do. At the default case one repeat of Winter Storm Uri (USD 3,430.60 per kW in its window) adds USD 171.53 per kW a year and takes NPV from -697.80 to +583.43: the page states it; it does not judge it. The control sits in "Is it worth building?", beside the results it moves, for the scenario in view; the field is in the address like the others.
- **The sensitivity** draws the credit's row only with a credit, the stress row only with a repeat, the fade's three rows only under the fade method, and the method itself never (`sensitivityKeys`), so the ten rows of session 208 are what the default draws (the sourced range, session 296: six). A choice (the method, the period) has no published range; by a percent step the period goes to the next choice that way.
- **The stress-day rule** for every grid is `battery_stress_days.md` (the price test, the 98th percentile of the trailing year's daily means, or the operator's notice); the table is the data machine's to rebuild.
- **Checks:** `site/scripts/test-battery-finance.mjs` (the credit at year 0, the fade with and without augmentation, the augmentation cost and its years, the repeats, the rows drawn); `tests/test_session297.py`; `scripts/check-values.mjs` reads the page at one non-default setting of each (`?ai=30`, `?ao=1`, `?ao=1&am=5`, `?ax=2`).

#### Session 314: the income chart's fault, and session 296's three open items at their defaults (the owner's ruling of 19 October 2026)

- **The fault.** The "Income by stream" chart drew its first column, the last twelve months, as thin bars over the dollar axis, and its column sub-labels ran into each other ("calendar yearcalendar year"). The cause was in the shared chart (`site/components/tool/SeriesChart.tsx`, session 296), not in the page: its axis step came from a fixed list that ended at 20,000, so an axis in tens of millions of dollars (the income table in USD for a 100 MW battery) drew thousands of ticks, each with a grid line and a label, over the first column; and every column wrote its sub-label whatever its width. The chart now chooses its step by magnitude (1, 2, 2.5 or 5 times a power of ten, five steps at most), is drawn for the width it measures (its text keeps its size on a phone; the phone's sideways scroll of `app/tokens.css` is left to the charts that are not measured), wraps a label by words to its column, thins the labels to every k-th column when a line is wider than a column, writes a sub-label and the figure above a bar only where they fit (the hover and the table hold them whatever the width), and spaces the series' names by their own length. Every chart drawn through it (the income chart, the year chart and the three cash charts) benefits; no page changed its data, and every checked number is what it was.
- **The default charts** stay the year chart alone (`DEFAULT_VIEW.charts`); the reader adds up to two more.
- **The contract takes no sourced range** (`cshare`, `cprice`): no published case exists for the reader's own term, so the sourced range draws no row for them and the line under the chart says the percent step moves them; the fields' hovers say the same.
- **8 hours takes the ATB's figure alone, with no range**: `rangesOf(8)` holds no capital cost and no fixed O&M row (session 296 drew the straight lines through Lazard's 2- and 4-hour low cases and high cases, 1,180 to 3,040 per kW, an extrapolation; they are gone), and `noRangeOf(8)` names both under the chart with the ATB's figures (USD 2,300 per kW; 4 percent a year, USD 92) and why: Lazard prints no 8-hour case. At 4 hours (and 2) nothing moved.
- **Checks:** `site/scripts/test-battery-finance.mjs` (the 8-hour range, `noRangeOf`, the contract's words); `tests/test_session314.py` (the chart's step and label rules, the ranges, the screenshots); `tests/test_session296.py` follows (its 8-hour pin, marked).

#### What this block is not

It is not a forecast and not a valuation. It repeats one year of an upper-bound revenue (perfect foresight, a price taker, reserves never called: sections 5 and 6) over the project's life. It has no tax, no tax credit, no augmentation and no residual value. It states numbers for two sets of assumptions; it does not say which to choose.

#### Checks

`site/scripts/test-battery-finance.mjs` (hand cases); `tests/test_session179.py` (a Python mirror of every formula above against the library on 308 cases to 1e-6; the file of steps; the builder; the page's source); `site/scripts/check-battery-scenarios.mjs` (the page in a browser: the ten inputs and their Resets, the seven rows, the address round trip, no request on a change, the chart's bars and hover, 390 px). Session 195: `site/scripts/check-decisions-face.mjs` and `tests/test_session195.py` (the block the three pages share, above).

### 11.2 The figures no check key carries (session 263)

The review pack (`docs/reviews/packs/battery.md`) quotes figures the page does not print at its bare address: other cases' headlines, scenario A moved, the sensitivity chart's rows. Until session 263 they were marked [c] in the old how-it-works note and computed once on the data machine (`docs/howitworks/computed/battery_headline.mjs`). Each is now recomputed with the page's own libraries from a read of `battery_stack_monthly` in Supabase (the anon key, as `check-values.mjs` reads it) and from `site/data/battery_scenario_steps.json`, by `site/scripts/check-battery-figures.mjs`, which exits 1 when any figure differs from the value printed here at the precision printed. The figures are those of the table on 14 October 2026 (last twelve months October 2025 to September 2026); when October 2026 is complete every one moves, and the script, this table and the pack change together.

| Figure | Value | How it is computed |
|---|---|---|
| ERCOT, 4 hours, day-ahead: share from ancillary services | 35 percent | `stat(rows, [], x, "l12_share:ancillary")` in `site/lib/batterystack.ts`: the last twelve months' ancillary revenue over their total, rounded |
| the same: debt coverage | 2.26 times | `stat(..., "cover")`: `(total x MW - 22 x 1000 x MW) / 2,261,119` |
| ERCOT, 4 hours, day-ahead: last twelve months | USD 73.00 per kW | `stat(..., "l12_kw:total")` |
| CAISO, 4 hours, perfect foresight: last twelve months | USD 79.05 per kW | the same, entity `caiso:TH_SP15_GEN-APND` |
| CAISO, 4 hours, day-ahead: last twelve months; ancillary share; coverage | USD 64.96 per kW; 51 percent; 1.90 times | the same three stats |
| Scenario A with 50 percent contracted at USD 10 per kW-month: coverage; NPV | 3.48 times; USD -51.13 million for 100 MW | `resultOf()` in `site/lib/battery/finance.ts` with `cshare: 50, cprice: 10`, the default case's revenue (USD 81.40 per kW): coverage `(0.5 x 10 x 12 + 0.5 x 81.40 - 22) / 22.61`; NPV at 12 percent times 1000 x 100 |
| Scenario A at a capital cost of USD 620 per kW: NPV; IRR | USD -23.12 million; 2.1 percent | `resultOf()` with `capex: 620` |
| The sensitivity chart's first two rows at the defaults | "Cycles a day, at most", then "Capital cost" | `sensitivity()` in `finance.ts`, sorted by the larger of the two moves; the revenue of each step as `Scenarios.tsx` builds it (the page's months with the step's totals) |
| Cycles a day: the move down to 0.5; the move up to 1.5 | USD 11.14 million; USD 1.40 million | the bar's `down` and `up` NPV less its base, times 1000 x 100 |
| Capital cost; degradation: the larger move | USD 9.52 million; USD 3.02 million | the bar's `size` |
| Scenario B at 92 percent and 2 cycles: last twelve months | USD 88.24 per kW | the file of steps, efficiency 92 and 2 cycles, over the last twelve months |
| 1.5 cycles: last twelve months | USD 83.57 per kW | the file of steps, efficiency 86 and 1.5 cycles |

The same script also holds the default case's headline (81.40, 8,140,219, 33, 475,477, 2,261,119, 2.63, 255.08, 614.58, 269.68, 57, -69.78 million, -8.8, 4.19), which `check-values.mjs` checks on the page. On 14 October 2026 it printed "all 32 figures are the pack's" and exited 0.

### 11.3 The node band (session 355, 20 October 2026)

For ERCOT at `HB_HUBAVG`, under "Income by stream": over the battery's own last twelve months, the day-ahead four-hour spread of ERCOT's storage nodes at the 10th percentile, the median and the 90th, the hub's own spread over the same days and the share of storage nodes wider than the hub, from `node_basis_summary` (`dam_storage_*`, `docs/methods/node_basis.md`), each month's figures with their keys in a fold and the twelve months' means weighted by the days held (`days`). The median node's spread over the hub's is the one ratio written: the energy this page counts at the hub would scale about with it, the reserves not at all. Added to no figure. Read in `site/lib/nodebasisread.ts`, so the page's own reads stay `read.ts`'s.

## Checks

`tests/test_session178.py`: the do-file's rules, parsed; the mirror against the CSV and against `battery_stack_monthly` through the page's own library (skipped without the tables or without node); the optimizer check on five days of the committed CSV; the awards snapshot against the two tables; the page's new line and links. `site/scripts/check-values.mjs` checks the new line's three numbers (`bsa|...`).
<a id="cross-checks"></a>

## Cross-checks

Session 196, 11 October 2026. The page's numbers are reproducible from its tables; here they stand beside what others publish, so that a reader sees each gap and its reason. Every published figure was read on 11 October 2026 from the address given, after the host's robots file and terms; no file of theirs is copied, the figure is quoted and the source linked. "Gap" is ours less theirs. A gap is not an error to be closed: most rows compare one modeled plant with a fleet, or a cost with a market's revenue, and the reason says which.

| Our figure | Published figure | Source and date | Gap | Reason |
|---|---|---|---|---|
| CAISO, 100 MW, 4-hour, at SP15, the year 2025: USD 92 per kW with perfect foresight, USD 85 on the day-ahead schedule (last twelve months to September 2026: 79.05 and 64.96) | The CAISO fleet's net market revenue: USD 53 per kW-year in 2024, 78 in 2023, 103 in 2022 | [CAISO, Department of Market Monitoring, *2024 Special Report on Battery Storage*, 29 May 2025](https://www.caiso.com/documents/2024-special-report-on-battery-storage-may-29-2025.pdf), section 2.9.1 | +39 and +32 against 2024 | No year is held by both: our table holds CAISO from September 2024, their report ends with 2024. Ours is an upper bound for one price-taking battery that sells reserves at the posted price and is never called; theirs is what the fleet was settled, weighted by capacity, over batteries of every duration at their own nodes. In their 2024, 82 percent of revenue was energy; in our 2025, 52 percent |
| ERCOT, day-ahead ancillary services, January to July 2026: the model takes USD 2.25 per kW a month (27.00 a year) | ERCOT's storage resources were awarded USD 0.40 per kW of their power a month (4.80 a year) | ERCOT's own day-ahead awards to energy storage resources, held in the warehouse (`ercot_storage_dam_awards_monthly`); section 9 of this note | +1.85 a month; the model is 5.66 times the awards | Section 9: the model sells as much of its power as reserves as the price pays for, as if the market had no limit; the fleet shares a market of fixed size. The page prints this line under "Income by stream" |
| Breakeven toll, default case: USD 8.90 per kW-month, USD 106.79 per kW-year; revenue of the last twelve months, USD 81.40 per kW | Lazard's levelized cost of storage, 100 MW, 4-hour, unsubsidized: USD 115 to 254 per MWh; on Lazard's own 126,000 MWh a year for 100 MW that is USD 144.90 to 320.04 per kW-year | [Lazard, *Levelized Cost of Energy+*, June 2025](https://www.lazard.com/media/uounhon4/lazards-lcoeplus-june-2025.pdf), LCOS v10.0, pages 19 and 43 | toll -38.11 to -213.25; revenue -63.50 to -238.64 | The toll here covers the debt payments 1.25 times and the fixed O&M, on 60 percent debt, and nothing else. Lazard's cost also pays the charging energy (USD 27 per MWh), warranty and augmentation, taxes, and a 12 percent return on equity that is 80 percent of its storage capital. That the market's revenue is below both is what the page's NPV row says: USD -62.59 million |
| Round-trip efficiency: 86 percent | 92 to 86 percent (Lazard, the 4-hour case); 85 percent (ATB) | [Lazard, *Levelized Cost of Energy+*, June 2025](https://www.lazard.com/media/uounhon4/lazards-lcoeplus-june-2025.pdf), page 43; [Annual Technology Baseline 2025, utility-scale battery storage](https://atb.nlr.gov/electricity/2025/utility-scale_battery_storage) | 0 to -6; +1 | The model runs at the low end of Lazard's range; the page offers 89 and 92 as steps |
| Fixed O&M, 4 hours: USD 22 per kW a year, 2.0 percent of the capital cost | 4 percent of the capital cost a year, which pays for augmentation: USD 44.40 at our capital cost of 1,110 | [Annual Technology Baseline 2025, utility-scale battery storage](https://atb.nlr.gov/electricity/2025/utility-scale_battery_storage) | -22.40 | Two conventions. Lazard's O&M (USD 3.0 to 8.0 per kWh a year) leaves augmentation out and lets the battery fade; the ATB pays for augmentation inside fixed O&M and holds the battery at its rating. The page follows Lazard on both, so its degradation default is Lazard's (next row but one) |
| The fade method at the ATB's convention (session 297): NPV of the default case USD -697.80 per kW with the revenue cut, 2.6 percent | the fade method with the ATB's convention, no fade (its fixed O&M pays for augmentation): USD -613.19 per kW; with Lazard's 2.6 percent fade and augmentation every 5 years at the ATB's USD 241 per kWh: -768.12 (USD 118.97 per kW paid in years 5, 10 and 15) | [Annual Technology Baseline 2025, utility-scale battery storage](https://atb.nlr.gov/electricity/2025/utility-scale_battery_storage); Lazard, LCOS v10.0 | +84.61 with no fade; -70.32 with augmentation | The two conventions set beside each other on the page's own finance (`site/lib/battery/finance.ts`, `projection`, `augmentationCost`): the ATB's 4 percent fixed O&M (USD 53.44 at its own cost) is not applied here, only its "no fade"; the page's default stays the revenue cut at Lazard's rate |
| Project life: 20 years | 15 years | [Annual Technology Baseline 2025, utility-scale battery storage](https://atb.nlr.gov/electricity/2025/utility-scale_battery_storage) | +5 | Lazard's storage cases run 20 years; the ATB's battery has a 15-year lifetime |
| Degradation: 2.6 percent a year, as a cut to revenue | none: "FOM costs include battery augmentation costs, which enables the system to operate at its rated capacity throughout its 15-year lifetime" | [Lazard, *Levelized Cost of Energy+*, June 2025](https://www.lazard.com/media/uounhon4/lazards-lcoeplus-june-2025.pdf), page 47; [Annual Technology Baseline 2025, utility-scale battery storage](https://atb.nlr.gov/electricity/2025/utility-scale_battery_storage) | +2.6 against the ATB; 0 against Lazard | The ruling of 11 October 2026 named the ATB as the place to look for a degradation rate. It holds none: its battery does not fade, at twice our fixed O&M. Lazard's rate goes with Lazard's costs, which are the page's, so Lazard's is the default. For Samuel's ruling |
| Debt share: 20 percent, at 8 percent (session 208; 60 percent until then) | Lazard's storage cases: "20% debt at an 8% interest rate and 80% equity at a 12% cost, which is a different capital structure than Lazard's LCOE analysis" | [Lazard, *Levelized Cost of Energy+*, June 2025](https://www.lazard.com/media/uounhon4/lazards-lcoeplus-june-2025.pdf), page 19 | 0 (session 208); +40 points until then | Ruled on 12 October 2026 (session 208): the battery takes Lazard's storage structure, 20 percent debt, and the hurdle rate is Lazard's cost of equity, 12 percent. The default case's coverage is 2.63 times on a third of the debt payments, as this row computed when it asked the question; its NPV at 12 percent is USD -69.78 million |
| SP15, day-ahead, the peak block, January to September 2026: USD 24.04 per MWh over 166 delivery periods (a day, or two or three days sold as one) | USD 23.97, ICE's "SP15 EZ Gen DA LMP Peak" | [EIA, Wholesale Electricity and Natural Gas Market Data, the 2026 file of ICE hub prices](https://www.eia.gov/electricity/wholesale/) | +0.07; by month -0.77 to +0.83 | ICE's index is the volume-weighted price of trades made the day before for the peak block; ours is the mean of the cleared hourly day-ahead price over the same block (hours ending 7 to 22 Pacific, Monday to Saturday, NERC holidays out) on the same delivery days. A traded expectation against the cleared price: SP15's months agree within USD 1, single days differ by about USD 3. Three periods are left out: an hour of ours is not held |
| ERCOT, 100 MW, 4-hour, at `HB_HUBAVG`, perfect foresight: USD 148 per kW in 2024, 87 in 2025, 81.40 over the last twelve months (October 2025 to September 2026); day-ahead schedule: 127, 78 and 73.00 | ERCOT's fleet average: USD 55 per kW in 2024 ("the average battery energy storage system in ERCOT earned revenues of $55 per kW of installed capacity", USD 4.63 a month), down 71 percent from USD 192 in 2023 | [Modo Energy, *ERCOT: Annual battery energy storage revenue report 2024*, 19 March 2025](https://modoenergy.com/research/en/ercot-battery-energy-storage-revenues-energy-markets-ancillary-services-capacity-location-owners-operators-annual-report-2024), read 12 October 2026 | 2024: +93 (foresight), +72 (day-ahead) | Ours is an upper bound for one price-taking battery that sells its reserves at the posted price and is never called, at the hub; theirs is what the fleet was paid, weighted by capacity, at its own nodes, over batteries of every duration (most of Texas's fleet in 2024 was 1 and 2 hours) and every operator. The ancillary line under the income table measures the largest part of the gap: the model takes 5.66 times what the fleet was awarded day-ahead in 2026 |
| the same, 2025: USD 87 per kW (foresight), 78 (day-ahead) | ERCOT's fleet, 2025: USD 26.0 per kW through November and "the Modo Energy Nowcast anticipates total-year revenues to land at $29.4/kW", "roughly half of 2024's $56/kW and one-sixth of 2023's $193/kW" | [Modo Energy, *Why were ERCOT battery revenues so low in 2025?*, 3 February 2026](https://modoenergy.com/research/en/why-were-ercot-battery-revenues-so-low-in-2025-weather-energy-arbitrage-builodout), read 12 October 2026 | 2025: +58 (foresight), +49 (day-ahead) | The same reasons; 2025 had no scarcity event, and the fleet grew to 13.9 GW, which compressed both the reserve prices and the energy spreads the fleet captured. The ratio of ours to theirs is about the same in both years (2.7 and 3.0 with foresight), which is what an upper bound on the same prices should give |
| the same, 2024 and 2023: USD 148 and 530 per kW (foresight), 127 and 459 (day-ahead), for 4 hours | A modeled 2-hour battery in ERCOT North: "could have earned up to ~$475/kW-Year across all AS products and Energy" in 2023; 2024 "may settle at ~$127/kW-year" (data to 15 December 2024) | [E3, *2024 ERCOT Market Update*, December 2024](https://www.ethree.com/wp-content/uploads/2024/12/E3-2024-ERCOT-Market-Update.pdf), pages 2 and 17, read 12 October 2026 | 2024: +21 (foresight), 0 (day-ahead); 2023: +55 and -16 | The closest published figure in method: an optimization over the real prices for one battery, as ours is. Theirs is a 2-hour battery at the North hub; ours is 4 hours at the hub average. The two agree within what the duration and the hub explain: a 4-hour battery earns more energy arbitrage and backs longer reserves, and 2023's August scarcity was priced by the hour |
| the same, the first half of 2025, a month: USD 7.3 per kW (foresight; 87 for the year over twelve months) | ERCOT's fleet, the first half of 2025: "Median asset came in at $2.13/kW-month", the top 20 assets USD 4.63 a month and the best USD 6.19; "Revenue ($/kW-month): $2.46 in H1 2024 vs. $2.33 in 2025" | [Tyba, *ERCOT Storage Performance, H1 2025*](https://www.tyba.ai/resources/ercot-storage-performance/ercot-storage-performance-h1-2025/), read 12 October 2026 | +5.2 a month against the median; +1.1 against the best asset | The spread inside the fleet is the measure of what operation is worth: the best asset earned three times the median. Ours sits above the best, as an upper bound should, by the margin that perfect foresight and uncalled reserves give |
| the same | ERCOT's market monitor's 2024 report gives no net revenue for an energy storage resource: its net revenue analysis (section VI.B, Figure 55) covers gas, wind and solar, and says "IRRs and ESRs have been treated at length in other chapters" | [Potomac Economics, *2024 State of the Market Report for the ERCOT Electricity Markets*, May 2025](https://potomaceconomics.com/wp-content/uploads/2025/06/2024-State-of-the-Market-Report.pdf), pages 78 to 80, read 12 October 2026 | none to compute | Read because the prompt named it. Its storage chapter describes the fleet's awards and the fall in ancillary prices, which the awards table in the warehouse holds directly (section 9) |

- **CAISO, 2025, a year both hold (session 246).** CAISO's market monitor's *2025 Annual Report on Market Issues and Performance* (June 2026) models a 100 MW, 4-hour battery over 2025 and gives the real fleet's revenue beside it. Run its way, this model gives USD 84.72 per kW against its 77.3; the real fleet was paid about 35 for energy and 9 for regulation, against the model's 42.31 and 42.25. The table, by quarter, with each gap and its reason: `docs/methods/battery_stack.md`, "CAISO beside its market monitor". The first row of the table above (no year held by both) was written before that report.
- Read and not used: Modo Energy's research sitemap. Its terms could not be found in two tries, so none of its posts on ERCOT battery revenue was read. Not reached: GridStatus's public posts, ERCOT's own reports beyond the awards already in the warehouse.
- The coverage at 20 percent debt is this note's arithmetic: `(81.40 - 22) / (1,110 x 0.2 x 0.101852) = 2.63`.
- **Is the negative NPV at the defaults credible? Yes, plainly.** At the defaults the default case's NPV is USD -69.78 million (session 208: 20 percent debt, 12 percent). The arithmetic: the last twelve months paid USD 81.40 per kW, an upper bound; less fixed O&M of 22 that is 59.40 a year, and twenty years of it at 12 percent are worth USD 444 per kW today, against USD 888 of equity (80 percent of a capital cost of 1,110) and the debt's payments on the rest. Revenue would have to be about USD 190 per kW a year, every year, for the NPV to reach zero at these defaults; ERCOT paid that to this battery only in 2021, 2022 and 2023, the scarcity years, and not since. Every published figure above sits below ours (the fleet earned 55 in 2024 and about 29 in 2025; the closest modeled figure, E3's 2-hour battery, 127 in 2024), so a real battery's NPV at these prices is lower still, not higher. Lazard's own levelized cost of storage says the same from the cost side: USD 145 to 320 per kW-year is what its 4-hour battery needs. What would change the sign: a capital cost at Lazard's low end (USD 620 per kW gives USD -23 million and an IRR of 2 percent, still short of 12), a contract (50 percent of the battery at USD 10 per kW-month lifts the NPV to USD -51 million), or a return of scarcity pricing. The headline's coverage of 2.63 times is not in tension with this: coverage asks whether the year's revenue pays the year's debt, and at 20 percent debt it does; the NPV asks whether it also pays equity its 12 percent over twenty years, and it does not.
- Session 208 read three more hosts, each after its robots file (none disallows reading): Modo Energy (its website terms of service forbid redistributing its analysis; one figure is quoted here with its source, as a citation, and the question of keeping the two rows is for Samuel's ruling), E3 and Tyba. Enverus's newsroom answered 403 and is not used; Gridmatic publishes no 4-hour ERCOT figure.


## The figures on the page and their keys

Each number `/cost-of-power/battery` shows carries its key (`site/components/Num.tsx`), which `site/scripts/check-values.mjs` checks against the live set and `site/scripts/check-methods.mjs` against this note (session 409). The keys the sections above do not name:

- `node_basis_summary`, `dam_storage_days`, `dam_storage_spread_4h_p10`, `dam_storage_spread_4h_p50`, `dam_storage_spread_4h_p90`, `dam_storage_hub_spread_4h`, `dam_storage_share_wider_pct`: for ERCOT at `HB_HUBAVG`, in the fold under "Income by stream", each month of the battery's last twelve: the days held, the storage nodes' day-ahead four-hour spread at the 10th percentile, the median and the 90th, the hub's own spread, and the percent of storage nodes wider than the hub (the series key `series|node_basis_summary|ercot:HB_HUBAVG|dam_storage_<figure>|<month>`).
- `price_years_by_window`, `battery_dayahead_<d>h_year_<year>` and `battery_foresight_<d>h_year_<year>`: what the same battery earned, in USD per kW, in a window of price years at the model's own step (one cycle a day, the model's efficiency), for the strategy and duration shown. The page shows it in the line on the highest and the lowest whole year held, each with scenario A's NPV on it, and, when the "Price years" choice prices the page on a window, in the summary and the first headline figure.
