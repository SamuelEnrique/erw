# What a battery earns: every number, step by step

Energy Research Warehouse (ERW), session 178, 10 October 2026. Written for sign-off. Page: `/cost-of-power/battery`. This note is written from the code, not from the older notes: `warehouse/derived/battery_stack.py` (the model), `site/lib/batterystack.ts` (the page's arithmetic), `site/app/cost-of-power/battery/page.tsx`, `BatteryForm.tsx` and `Contract.tsx` (the page). Where an older note and the code disagree, the code is what the page does; the disagreements are listed in "Where the notes and the code differ". The model's method, its sources and its limits are in [the method note](battery_stack.md); the early years are in [battery_early_years.md](battery_early_years.md).

Downloads, the default case hour by hour: [erw_2026_battery_dispatch.csv](/battery/erw_2026_battery_dispatch.csv) (4.3 MB, 26,304 hours), [the Stata do-file](/battery/erw_2026_battery_replication.do) and [its Python mirror](/battery/erw_2026_battery_replication.py).

**The default case**, used for every example below: ERCOT, a 4-hour battery, perfect foresight, 100 MW, fixed O&M USD 22 per kW a year, debt payments USD 6,783,357 a year. With the tables as retrieved on 5 October 2026 the page shows: USD 81.40 per kW over the last twelve months (October 2025 to September 2026), 33 percent of it from ancillary services, debt covered 0.88 times; USD 8,140,219 for 100 MW; a bad month of USD 475,477 (December 2024, of 36 months held).

## 1. The order of computation

1. **Prices in.** Connectors write ERCOT's hourly day-ahead ancillary clearing prices (`ercot_as_prices`) and hub energy prices (`iso_rtm_hub_prices`, `iso_dam_hub_prices`, and the yearly history `ercot_all_hub_prices_history`).
2. **The model, once a day** (`battery_stack.py`, in `warehouse/run_daily.sh`): for each market, strategy, duration and local day, one optimization. Its daily results are summed by local month into `battery_stack_monthly` (and, for the days of three ERCOT stress events, kept by day in `battery_stack_stress_daily`). Everything is per 1 MW of rated power.
3. **The live set.** The loader copies both tables to Supabase.
4. **The page, on each request**, reads the rows of one hub, one strategy and one duration, and computes every number it shows with `lib/batterystack.ts`, scaling by the reader's MW. The contract panel computes in the browser from the same months.
5. **The check.** `site/scripts/check-values.mjs` reads the tables itself, recomputes every number with the same library, and compares with what the page printed (key `bs|<inputs>|<stat>`).

## 2. The reader's inputs

All six are in the address, each bounded and defaulted by `inputsOf`:

| Input | Default | Bounds | What it changes |
|---|---|---|---|
| `grid` | `ercot` | `ercot`, `caiso`; `nyiso` and `spp` only in the internal view | which hub's rows are read |
| `dur` | 4 | 2, 4 or 8 hours | which rows; the defaults of `fom` and `ds` |
| `strat` | `foresight` | `foresight` or `dayahead` | which rows |
| `mw` | 100 | 1 to 5,000 | every US dollar figure is the per-MW figure times `mw`; per-kW figures do not move |
| `fom` | 11.2, 22 or 43.6 USD per kW a year (2, 4, 8 hours) | 0 to 500 | debt coverage only |
| `ds` | the default annual debt payment for the duration and size, rounded to a dollar | 0 to 1e11 | debt coverage only |

Anything outside its bounds is clipped; anything unreadable takes the default. A change of duration drops a typed `fom` or `ds` (their defaults scale with the duration).

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

`r(m, s)` below is the table's value for month `m` and stream `s` (per MW); `MW` the reader's size. "Scaled" means `round(value x MW)` to a whole US dollar.

**A month is "held"** when it has a total revenue row and `days_held / days_in_month >= 0.9`. Only held months enter any window, average or chart bar. A month that is not held is shown grey in "Every month" with its held days' revenue, and counted nowhere.

### 4.1 The input panel's note

- **Default annual debt payments**: `capex x 1000 x 0.6 x crf(0.08, 20) x MW`, rounded to a dollar, where `crf(i, n) = i / (1 - (1 + i)^-n) = 0.101852`. Capital cost per kW: 610 (2 hours), 1,110 (4 hours), 2,110 (8 hours). The 4-hour default: `1,110 x 1000 x 0.6 x 0.101852 x 100 = 6,783,357`.

### 4.2 The summary sentence

- **"earned USD X per kW"** (`l12_kw:total`): the sum of `r(m, total)` over the last twelve months, divided by 1,000. Default: 81.40.
- **"Y percent of it from ancillary services"** (`l12_share:ancillary`): `round(100 x sum of r(m, ancillary) / sum of r(m, total))` over the same twelve months. Default: 33.
- **"covered its debt Z times"** (`cover`): see 4.3.

**The last twelve months**: walk the months from newest to oldest; take the first held month whose eleven preceding calendar months are all held too. Those twelve are the window. If there is none, the page says so and shows no last-twelve-months figure. Default: October 2025 to September 2026.

### 4.3 The three headline numbers

1. **Last twelve months, all streams**: `l12_kw:total` again, and beneath it **USD for the reader's size** (`l12:total`): the twelve months' `r(m, total)` summed, scaled. Default: 8,140,219.
2. **A bad month** (`p10_36`): take the 36 calendar months ending with the last twelve months' last month (or with the newest held month when there is no twelve-month window); keep the held ones (`n36` of them); sort by total revenue, ties by month; take the one at rank `ceil(0.1 x n36)` (nearest rank, at least 1); its total, scaled. Default: 36 months, rank 4, December 2024, 475,477. A market held for less than 36 months has fewer and the page says how many.
3. **Debt coverage, last twelve months** (`cover`): `(sum of r(m, total) x MW - fom x 1000 x MW) / ds`. Revenue less a year of fixed O&M, over a year of debt payments. Shown with two decimals; not shown when `ds` is 0. Default: `(8,140,219 - 2,200,000) / 6,783,357 = 0.88`. The annual debt payment `ds` is printed beside it.

### 4.4 The chart: revenue by year, USD per kW

- One bar per calendar year with at least one held month: the sum of the held months' `r(m, energy)` and `r(m, ancillary)`, each divided by 1,000, stacked. The label above the bar is the two summed and rounded to a whole dollar.
- A year is **complete** when all twelve of its months are held; otherwise the bar is hatched and labeled with its count of months. A hatched bar is the held months' sum, not a year.
- When the tallest bar is more than 2.5 times the second tallest (and there are at least three), the scale is set by the second tallest and the tallest is drawn broken with its value written (`year:<Y>:total`). ERCOT's 2021.
- Default, full years inside the exported window: 2024 energy 62.70 and ancillary 84.98; 2025 energy 57.39 and ancillary 30.05.

### 4.5 Income by stream

Rows: energy; ancillary services; each product; capacity (words only, never a number); the total; the total per kW. Columns:

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

### 4.7 With your contract (computed in the browser, never sent)

The reader types a share (percent), a price (USD per kW-month) and an end month. With `s = share / 100`, `M12` the last twelve months' total per MW and `AVG` the every-year average per MW:

- **Contracted income a year**: `s x MW x 1000 x price x 12`.
- **Market income on the uncontracted share**: `(1 - s) x M12 x MW`; beside it `(1 - s) x AVG x MW`.
- **Debt coverage with the contract**: `(contracted + (1 - s) x M12 x MW - fom x 1000 x MW) / ds`.
- **Debt coverage without it**: the headline coverage.
- **From the market after the contract ends**: `M12 x MW`; beside it `AVG x MW`.

The contracted share earns nothing from the market. **The end month changes no number**: it only words the last row's label.

### 4.8 Other grids

Words only. No number.

### 4.9 Every month (folded)

For each month the table holds, newest first: energy, ancillary and total (`month:<m>:<s>`: `r(m, s)`, scaled); **coverage**: `(r(m, total) x 12 x MW - fom x 1000 x MW) / ds`, the month's revenue less a month of fixed O&M over a month of debt payments, shown only for a held month; days held of days in the month; days left out. Beneath: the days left out in all (`out`), and how many for a missing ancillary price.

### 4.10 Stress days (folded, ERCOT only)

From `battery_stack_stress_daily`: for Winter Storm Uri (7 to 24 February 2021), Winter Storm Elliott (19 to 29 December 2022) and the 2023 heat (1 August to 10 September 2023), over the solved days inside the window: the count of days, energy, ancillary and total summed and scaled (`stress:<event>:<s>`), and the best single day's total with its date (`stress:<event>:best`).

### 4.11 What this model cannot see (folded)

One number: the round-trip efficiency, 86 percent. The list of required durations is section 3.3's, printed from `REQUIREMENTS`.

## 5. Edge cases, as the code handles them

- **A missing interval or hour.** An hour missing one interval has no price; a day missing one hour of the energy price or of any product bought that day is left out whole and counted in `days_left_out`. ERCOT: no day left out under either strategy in the table of 5 October 2026.
- **A day with fewer or more than 24 hours.** Only the clock-change days: 23 hours in March, 25 in November. The same program with 23 or 25 hours; the one-cycle limit is per local day whatever its length. In the export: 10 March 2024, 9 March 2025, 8 March 2026 (23) and 5 November 2023, 3 November 2024, 2 November 2025 (25). CAISO's two 25-hour days are left out because the hub history does not hold their energy price.
- **Negative prices.** Section 3.4.
- **The first hour of every day holds no upward reserve.** The battery starts each local day empty, and an upward award needs its energy at the hour's start. In all 1,096 exported days the upward awards of the first hour are zero. This understates the result: at most USD 1.29 per kW over the last twelve months of the default case (1 MW of the best-paid upward product in every first hour), 1.6 percent of 81.40. Regulation Down is not affected (it needs room, and an empty battery has it).
- **Energy left at midnight is lost.** The next day starts empty. In the last twelve months 11 days end with more than 0.01 MWh stored; the mean at day's end is 0.023 MWh per MW.
- **The cap of a product by duration.** Section 3.3.
- **A month so far.** The current month is not held until 90 percent of its days are solved, so it is grey and outside every window. **But a month becomes held before it ends**: on the 28th solved day of a 31-day month (28/31 = 0.903), the 27th of 30, the 26th of 28. From that day it is the last of the last twelve months, with the revenue of its solved days only, not scaled; the window moves forward one month and the headline changes, then rises a little each remaining day. This is the 90 percent rule working as written. Whether the headline should wait for whole months is a ruling for Samuel (see the session report).
- **A held month with days left out** (up to 10 percent) counts with its solved days' revenue only. Nothing is scaled up.
- **A grid with no ancillary data.** The model is not built for it: PJM, ISO-NE and MISO are rows of words on the page. A grid in review (NYISO, SPP) is read from `site/data/battery_stack_review.json`, in the internal view only.
- **A table that cannot be read.** The page says so and shows no number.
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
| Capital cost | 610, 1,110, 2,110 USD per kW (2, 4, 8 hours) | Lazard LCOE+ June 2025, LCOS v10.0, midpoints; 8 hours is a straight line through the other two, an extrapolation | through `ds` |
| Debt | 60 percent of capital cost, 8 percent, 20 years, level payments | Lazard's capital structure | through `ds` |
| Fixed O&M | 11.2, 22, 43.6 USD per kW a year | the same Lazard cases | yes |
| A month counts | 90 percent of its days solved | the seller tab's rule | no |
| The outlier month | more than 25 percent of everything held | session 71 | no |

## 7. The replication

- **The CSV** (`warehouse/derived/battery_dispatch_export.py`): one row per local hour of the default case, 36 local months (October 2023 to September 2026, the window of the bad month), `in_last_twelve` marking the twelve. Columns: the hour in UTC and local time; the energy price and each product's price; charge, discharge, state of charge, the megawatts in each product; revenue by component. Per 1 MW. Fourteen comment lines of provenance (source tables, their retrieval times, the model's file hash and commit). The exporter solves each day with the model's own `solve_day` and refuses to write unless every month's sums equal `battery_stack_monthly` to within half a cent per MW; on 10 October 2026 all 36 months agreed.
- **The do-file** reads the CSV and prints: the last twelve months by stream for 100 MW, per kW, the ancillary share, the debt payment, the coverage, the full calendar years of the chart inside the window (2024, 2025), and the bad month. It follows the house rules: no continuation operator, one empty line between commands outside loops and none inside, every numeric column destrung with `replace force`, the sentinel -999 recoded per variable before any loop.
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
4. **No note says that a month becomes held, and enters the last twelve months, before it ends** (section 5). The older note states the 90 percent rule for "the averages"; the code applies it to the last twelve months, the bad month's window and the chart as well.
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

## Checks

`tests/test_session178.py`: the do-file's rules, parsed; the mirror against the CSV and against `battery_stack_monthly` through the page's own library (skipped without the tables or without node); the optimizer check on five days of the committed CSV; the awards snapshot against the two tables; the page's new line and links. `site/scripts/check-values.mjs` checks the new line's three numbers (`bsa|...`).
