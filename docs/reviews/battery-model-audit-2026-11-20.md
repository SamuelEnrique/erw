# What a battery earns: the model audited as a hostile expert would

Session 9840, 20 November 2026, the desktop's fifth window. Read as a storage developer's quantitative analyst who wants to find it wrong.

- The page: `/cost-of-power/battery`. The model: `warehouse/derived/battery_stack.py`. The page's arithmetic: `site/lib/batterystack.ts`, `site/lib/battery/finance.ts`.
- The notes: `docs/methods/battery_earns_algorithm.md` ("the note"), `docs/methods/battery_stack.md`, `docs/methods/crosschecks/battery.md`. The replication: `replication/battery/`. The decisions block: `site/lib/decisions.ts`, `BATTERY_DECISIONS` (the note's section 12).
- Nothing changed on main but this file. No table written, no lock taken, no default moved.
- Each finding's test is on its own branch, `wip/audit-battery-<n>`, not requested for landing: a fix that moves a figure is the owner's ruling.

## How every number here was computed

- The default case: ERCOT, 4 hours, perfect foresight, 100 MW. The page's last twelve months: October 2025 to September 2026. Headline USD 81.40 per kW (81.4022 unrounded).
- Prices: the page's own public file, `site/public/battery/erw_2026_battery_dispatch.csv`, 1,096 local days.
- Re-solved with the model's own `solve_day` and `check_day`: every day equals the file to 0.000000 USD per MW. The last twelve months give 81.4022.
- To change one rule at a time: a sparse restatement of the same program. With the model's rules it equals `solve_day` on all 365 days of the last twelve months, to 0.000000.
- 15-minute prices: `ercot_all_hub_prices_history`, then `iso_rtm_hub_prices` (HB_HUBAVG, the model's own order), read from the main checkout, never written. Their hourly means equal the file's energy price in all 8,760 hours.
- Regulation called: measured in `ercot_sced_esr_hourly` (ERCOT's 60-day SCED storage data, 1 February to 27 August 2026).
- Finance: a mirror of `finance.ts`. It gives the page's NPV (USD -697.80 per kW), IRR (-8.8 percent), coverage (2.63) and toll (4.19).
- A change of USD 1 per kW a year in revenue moves the default NPV by USD 6.43 per kW (twenty years at 12 percent, 2.6 percent degradation).

## Findings, largest effect first

| # | Finding | Headline, USD per kW (81.40) | NPV, USD per kW (-697.80) | Branch |
|---|---|---|---|---|
| 1 | Regulation is never called; ERCOT's storage shows 17 percent of an award moving each hour | -6.44 (-7.9 percent) | -41.4 | `wip/audit-battery-1` |
| 2 | Each day starts empty: the reset costs USD 5.23 per kW, four times the note's bound of 1.29 | +5.23 (+6.4 percent) | +33.6 | `wip/audit-battery-2` |
| 3 | Energy is paid the hourly mean; ERCOT settles real-time energy every 15 minutes | +2.23 (+2.7 percent) | +14.4 | `wip/audit-battery-3` |
| 4 | Degradation cuts the whole revenue 2.6 percent a year; the model's own runs lose 1.1 percent a year at that fade | none (year 1) | +44.76 | `wip/audit-battery-4` |

## 1. Regulation is never called

- **Where.** `warehouse/derived/battery_stack.py` line 28 (the docstring), lines 211 to 217 (the state of charge moves only with charge and discharge), line 267 (the objective pays an award its price, nothing else). The note, section 3.4 ("Reserves are never deployed"), section 4.11 and section 6 ("Reserves called: never, assumed"). Decision 4 (`site/lib/decisions.ts` line 119).
- **Why it is wrong.** ERCOT deploys regulation all the time. In `ercot_sced_esr_hourly`, over the 56,845 resource-hours in which a storage resource held regulation and no other reserve, its output moved off its base point by 0.168 MWh per MW of Reg Up and 0.181 per MW of Reg Down, net within each hour (least squares). Hours with no reserve moved about a sixth as much (mean 0.54 MWh against 3.20).
- **The model leans on regulation.** In the mean hour of January to July 2026 it holds 44.6 percent of its power in Reg Up and 77.7 percent in Reg Down: 122 percent of its power in regulation.
- **The schedule it is paid for cannot be delivered.** Take `solve_day`'s own schedule and call regulation at 17 percent: on 342 of the 365 days the model's own `check_day` finds a limit broken (empty, full, or the energy behind a reserve).
- **How much.** Re-optimized with regulation called (the energy paid at the hour's price, the round-trip loss on it, Reg Up's energy counted in the one-cycle limit): USD 74.96 per kW, -6.44 (-7.9 percent). Of that, -3.93 is the energy and its losses and -2.51 the cycle limit. Called at 10 percent: 76.09; at 30 percent: 74.06. The battery then holds Reg Up 0.09 and Reg Down 0.35 MW per MW, not 0.47 and 0.76.
- **The test.** `tests/test_audit_battery_1.py` on `wip/audit-battery-1`: the paid schedule of every day of the last twelve months, with regulation called at 0.17, breaks `check_day` on at least 300 days (342 measured). On a machine with the SCED table it measures the share again (between 0.10 and 0.25).
- **Not fixed.** The fix is a model change (an energy flow per regulation award in the state of charge, the objective and the cycle row) and moves every figure: the owner's ruling. The measurement is real-time telemetry under ERCOT's real-time co-optimization (from 5 December 2025); the deployed energy is priced here at the hour's mean real-time price.

## 2. Each day starts empty, and the cost is four times what the note says

- **Where.** `warehouse/derived/battery_stack.py` lines 211 to 217 (`soc_row(-1)` is an empty battery at every day's first hour) and line 405 (each local day solved alone). The note, section 3.4 line 81 ("`s = 0` at the start of every local day"), section 5 lines 229 and 230, section 6 line 246. Decision 2 (`site/lib/decisions.ts` line 114).
- **What the note claims.** Section 5: the empty start "understates the result: at most USD 1.29 per kW over the last twelve months" (1 MW of the best-paid upward product in every first hour), and energy left at midnight is small (mean 0.023 MWh per MW). Both figures check: 1.2877 and 0.0227.
- **Why the bound is wrong.** It counts one channel, the first hour's reserves. The reset also stops the battery from charging before midnight for the next morning's peak, and from carrying stored energy behind overnight reserves. Winter, with two peaks a day, shows it most: December 2025 gains 11.6 percent, January 2026 9.3 percent.
- **How much.** The model's program with the state of charge carried across midnight within each calendar month, every other rule unchanged (one cycle per local day, 86 percent, hourly, the day's required durations): USD 86.63 per kW against 81.40, +5.23 (+6.4 percent). Carried over the month's end as well, it would be a little more.
- **The test.** `tests/test_audit_battery_2.py` on `wip/audit-battery-2`, with `tests/audit_battery_lp.py` (the restated program). It shows the restatement equals `solve_day` on all 365 days, gives the page's 81.4022, then finds the carried figure more than four times the note's bound above it.
- **Not fixed.** A carried state of charge is a model change that moves every figure: the owner's ruling. The note's section 5 sentence is wrong as written whatever the ruling, and can be corrected in words.

## 3. Energy is paid the hourly mean of a price ERCOT settles every 15 minutes

- **Where.** `warehouse/derived/cost_of_power.py` lines 72 to 80 (`hourly`: the four quarter prices of an hour become their mean), used by `warehouse/derived/battery_stack.py` lines 358 and 360. The note, section 3.1 line 48, section 4.11 line 213, section 6 line 247 ("Resolution: hourly, as ancillary prices are hourly"). Decision 3 ("paid the hourly mean of the real-time price").
- **Why it is wrong for an upper bound.** ERCOT settles real-time energy on 15-minute settlement point prices. A battery under perfect foresight can charge in a cheap quarter and discharge in a dear one inside the same hour; the mean hides that spread. Reserves are bought by the hour, so they can stay hourly; energy need not.
- **What the note says.** Section 4.11 admits it in words ("can earn more from energy than this shows"), yet decision 3 still calls each figure an upper bound.
- **How much.** The same program with the four quarter prices of each hour, reserves hourly, every other rule the model's (the midnight reset included): USD 83.64 per kW, +2.23 (+2.7 percent). Energy rises from 54.60 to 57.57 (+5.5 percent); reserves give a little back.
- **The test.** `tests/test_audit_battery_3.py` on `wip/audit-battery-3`. A day whose hours all have the same mean but whose quarters move: `solve_day` earns nothing from energy, the quarter-priced program earns from the spread. On a machine with ERCOT's 15-minute tables it also recomputes the last twelve months (the quarters' means checked equal to the public file in every hour).
- **Not fixed.** A 15-minute energy program moves every figure: the owner's ruling. The day-ahead schedule is hourly by ERCOT's own design and is not affected.

## 4. Degradation cuts the whole revenue by a capacity fade rate

- **Where.** `site/lib/battery/finance.ts` lines 213 to 221 (`revenueInYear`: `R x (1 - deg)^(t - 1)`, and under the fade method `R x (1 - fade)^k`). The note, section 11.1 line 385 (the default, 2.6) and line 417 ("Revenue in year t"), line 451 (the fade method: "revenue is taken proportional to the capacity"). Decision 15 (`site/lib/decisions.ts` line 140).
- **Why it is wrong.** Lazard's 2.6 percent is the battery's loss of energy capacity a year. Power does not fade, a third of the revenue is reserves paid on power, and energy arbitrage is not proportional to the hours held. The note itself says "revenue is not proportional to duration" (section 11), then applies the fade one for one, under both methods.
- **What the model says instead.** Re-solved by `solve_day` on every day of the last twelve months, keeping 1 MW and fading the energy by 2.6 percent a year: year 2 earns 98.91 percent of year 1, year 10 90.26, year 20 79.34. The page's cut gives 97.40, 78.89 and 60.62.
- **How much.** The headline (year 1) does not move. NPV at the defaults: USD -653.04 per kW on the model's own fade path against -697.80, +44.76 per kW (USD 4.48 million for 100 MW). Twenty years of revenue: 1,459 per kW against 1,282 (+14 percent).
- **The test.** `tests/test_audit_battery_4.py` on `wip/audit-battery-4`: the faded battery keeps more than 98.5 percent of its revenue after one year and more than 75 percent after nineteen, while `finance.ts` (run by Node) gives `R x 0.974^(t - 1)` under both methods.
- **Not fixed.** The fix is a fade path from the model (a table of revenue by faded duration, or a ratio the page reads) and moves NPV, IRR and payback: the owner's ruling. The same path would make the augmentation option's revenue right.
