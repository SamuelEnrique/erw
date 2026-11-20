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

## 1. Regulation is never called

- **Where.** `warehouse/derived/battery_stack.py` line 28 (the docstring), lines 211 to 217 (the state of charge moves only with charge and discharge), line 267 (the objective pays an award its price, nothing else). The note, section 3.4 ("Reserves are never deployed"), section 4.11 and section 6 ("Reserves called: never, assumed"). Decision 4 (`site/lib/decisions.ts` line 119).
- **Why it is wrong.** ERCOT deploys regulation all the time. In `ercot_sced_esr_hourly`, over the 56,845 resource-hours in which a storage resource held regulation and no other reserve, its output moved off its base point by 0.168 MWh per MW of Reg Up and 0.181 per MW of Reg Down, net within each hour (least squares). Hours with no reserve moved about a sixth as much (mean 0.54 MWh against 3.20).
- **The model leans on regulation.** In the mean hour of January to July 2026 it holds 44.6 percent of its power in Reg Up and 77.7 percent in Reg Down: 122 percent of its power in regulation.
- **The schedule it is paid for cannot be delivered.** Take `solve_day`'s own schedule and call regulation at 17 percent: on 342 of the 365 days the model's own `check_day` finds a limit broken (empty, full, or the energy behind a reserve).
- **How much.** Re-optimized with regulation called (the energy paid at the hour's price, the round-trip loss on it, Reg Up's energy counted in the one-cycle limit): USD 74.96 per kW, -6.44 (-7.9 percent). Of that, -3.93 is the energy and its losses and -2.51 the cycle limit. Called at 10 percent: 76.09; at 30 percent: 74.06. The battery then holds Reg Up 0.09 and Reg Down 0.35 MW per MW, not 0.47 and 0.76.
- **The test.** `tests/test_audit_battery_1.py` on `wip/audit-battery-1`: the paid schedule of every day of the last twelve months, with regulation called at 0.17, breaks `check_day` on at least 300 days (342 measured). On a machine with the SCED table it measures the share again (between 0.10 and 0.25).
- **Not fixed.** The fix is a model change (an energy flow per regulation award in the state of charge, the objective and the cycle row) and moves every figure: the owner's ruling. The measurement is real-time telemetry under ERCOT's real-time co-optimization (from 5 December 2025); the deployed energy is priced here at the hour's mean real-time price.
