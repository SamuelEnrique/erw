# Session 74 report: making the battery model believable before 2024

Energy Research Warehouse (ERW), session 74, third of the overnight chain, on the portable laptop, 2026-10-03 from about 10:20 to 10:55 UTC, unattended. **Model spend: USD 0.00** (the cap was USD 0). One approved pull, far under its ceiling, and it could not reach back to 2018 (below); two web searches to find documents' addresses, the documents then read locally; no model call, no force push. Branch `wip/074-fleet-limited` on GitHub (it holds sessions 72 and 73 too). **Nothing on `/cost-of-power/battery` and no live strategy's number changed.**

## To finish

```bash
# 1. After sessions 72 and 73 have merged, merge this one (it changes no live number: the cap is off unless asked for)
git checkout wip/074-fleet-limited
git fetch origin
git merge origin/main
git push origin wip/074-fleet-limited:task/074-fleet-limited

# 2. Only if you rule for it: CAISO's verified duration rules into the live model. This changes the live table (by at most
#    USD 0.2 per kW a year). In warehouse/derived/battery_stack.py, MARKETS["caiso"], the products spin and nonspin:
#      hours=[("2024-09-01", 0.5, "CAISO tariff Section 8 as of 2026-05-01, section 8.4.3")]
#    and regup and regdn's source from ONE_HOUR to "CAISO tariff Section 8 as of 2026-05-01, section 8.4.1.1(g)";
#    in site/lib/batterystack.ts, REQUIREMENTS.caiso, the same two rows (assumed: false). Then rebuild battery_stack,
#    validate, coverage, archive, the Redivis draft and the live set, as session 67 did.

# 3. To grow the quantities table day by day (it holds what ERCOT keeps, about a month), add to warehouse/run_daily.sh
#      run_other ercot_as_quantities "$PYTHON" warehouse/connectors/ercot_as_quantities.py
```

## In plain words

- **The fleet-limited estimate is built, but only for the days the quantities exist.** ERCOT keeps its DAM Ancillary Service Plan (the MW it buys of each reserve, hour by hour) on its public reports site for about a month. No keyless public source of 2018 to 2026 was found:
  - ERCOT's archive API needs a subscription key this machine does not have;
  - the yearly methodology documents give the rules and adjustment tables, not the quantities;
  - the projected-requirements spreadsheet holds only the coming months.

  So `ercot_as_quantities` holds 2026-09-03 to 2026-10-04 (3,840 rows of the 400,000 ceiling), and nothing earlier was filled or invented.
- **On those days the cap matters a great deal.** ERCOT's batteries (18,204.5 MW in August 2026) are now far larger than the reserves ERCOT buys. One battery's share averages 2.6 percent of its power for regulation and 13 percent for Responsive Reserve and Non-Spin. A 4-hour battery with perfect foresight earned USD 5.92 per kW over the 28 days as a price-taker, and **USD 4.52 fleet-limited (76.5 percent)**. Its ancillary income falls from 2.23 to 0.42, and part of the freed power goes to energy.
- **But the fleet-limited estimate cannot fix the years before 2024**, and the arithmetic says why. ERCOT's operating battery fleet was 87 MW at the end of 2018, 107 in 2019, 218 in 2020, 821 in 2021 and 2,130 in 2022. ERCOT's 2024 methodology states that at least 2,300 MW of Responsive Reserve is procured in every hour; that is the 2024 figure, and earlier years' quantities are not held. Against quantities of that order, the cap is 1 for Responsive Reserve, the stream that carried 2018 to 2021 (USD 2,463.5 of 2021's 3,430.6 per kW), until the fleet passed them in 2023. **The early years are implausible because the model pays a battery for reserves it is never asked to deliver, not because the fleet was too big for the market.** Capping by the fleet's share does not touch that.
- **California's rules are now verified** in CAISO's tariff (Section 8, as of 1 May 2026):
  - Regulation must be sustainable for 60 minutes in the day-ahead market (§8.4.1.1(g)), as the model assumed.
  - Spinning and Non-Spinning Reserve for 30 minutes (§8.4.3), not the hour assumed.

  Run both ways on the same days, CAISO's yearly totals move by at most USD 0.2 per kW. The live model still carries the assumed hour; changing it changes a live number, so it is in "To finish".
- **Recommendation, not applied: the page should not switch to the fleet-limited estimate as its default.** It would barely change the years that need fixing. It would change the recent months it already leads with, honestly, but only where quantities are held (a month today). Better:
  - keep the price-taker as the stated upper bound;
  - schedule the quantities connector, so a fleet-limited "last twelve months" exists within a year;
  - treat the pre-2024 years with a model of being called on reserves (energy delivered and lost when called), the assumption that actually inflates them, or show them only as an upper bound, as the page already says.

## Part A: the fleet-limited estimate

**The pull.** `warehouse/connectors/ercot_as_quantities.py`:

- Reads NP4-33-CD, ERCOT's DAM Ancillary Service Plan, one CSV a day, each holding seven delivery days. A delivery day takes the plan published the day before it, the one that day's day-ahead market used.
- Complete Central days only, using `ercot_as_prices`' own time conversion and completeness rule.
- **3,840 rows** (32 delivery days, 5 products, 24 hours), nothing left out, against a ceiling of 400,000. Validator pass with no warning; in coverage (public, power, source); archived; in the Redivis draft (`erw_headers` 1,773 lines); `--check-license` ok. Not in Supabase.

**The model.** `battery_stack.solve_day` takes optional `caps`: a per-hour upper bound on each product's award, per MW, between 0 and 1. With none it is the page's program exactly; a test checks that a cap of 1 reproduces it. `warehouse/analysis/battery_fleet_limited.py` solves each held day twice for both strategies and 2, 4 and 8 hours:

- price-taker: the page's program;
- fleet-limited: cap = min(1, ERCOT's planned MW of the product that hour / ERCOT's operating battery MW that month).

It checks every constraint and that no award passes its cap. **The fleet:** EIA-860M via `storage_buildout_monthly`; September and October 2026 are not published yet, so August's 18,204.5 MW is used, and the output names the month. The assumption is stated in the method: batteries share each product in proportion to their power and take all of it. ERCOT's published share of each product supplied by storage was not found in a form this session could read; if it exists, it should replace the proportional share.

**Results, USD per kW of rated power, ERCOT HB_HUBAVG, the held days** (`warehouse/output/analysis_internal/battery_fleet_limited_ercot_daily.csv`):

| Strategy | Hours | Days | Price-taker total | Its ancillary | Fleet-limited total | Its ancillary | Fleet-limited share of the price-taker |
|---|---|---|---|---|---|---|---|
| Perfect foresight | 2 | 28 | 4.18 | 2.16 | 2.88 | 0.34 | 68.9 percent |
| Perfect foresight | 4 | 28 | 5.92 | 2.23 | 4.52 | 0.42 | 76.5 percent |
| Perfect foresight | 8 | 28 | 7.12 | 2.15 | 5.64 | 0.41 | 79.2 percent |
| Day-ahead schedule | 2 | 30 | 3.85 | 2.25 | 2.72 | 0.31 | 70.6 percent |
| Day-ahead schedule | 4 | 30 | 5.86 | 2.18 | 4.66 | 0.34 | 79.7 percent |
| Day-ahead schedule | 8 | 30 | 7.37 | 2.11 | 6.03 | 0.35 | 81.8 percent |

Perfect foresight covers two days fewer: the real-time energy price is not held for the newest days.

| 4 hours, perfect foresight, by product | Mean cap (share of one battery's MW) | Hours the cap binds, of 672 | Price-taker | Fleet-limited |
|---|---|---|---|---|
| Regulation Up | 0.026 | 468 | 0.47 | 0.02 |
| Regulation Down | 0.025 | 541 | 0.92 | 0.03 |
| Responsive Reserve | 0.133 | 356 | 0.02 | 0.05 |
| ECRS | 0.091 | 358 | 0.49 | 0.07 |
| Non-Spin | 0.128 | 349 | 0.32 | 0.25 |

Responsive Reserve earns slightly more when capped: the battery, limited elsewhere, moves some power into it.

**CAISO:** procured quantities are not held, so the fleet-limited estimate is **not built for CAISO**.

## The three strategies side by side, ERCOT, by year

Total USD per kW (`warehouse/output/analysis_internal/battery_three_strategies_ercot_yearly.csv`). The two existing strategies are the page's table; the fleet-limited column is held only for September 2026:

| Year | Foresight 2h | 4h | 8h | Day-ahead 2h | 4h | 8h | Fleet-limited |
|---|---|---|---|---|---|---|---|
| 2018 | 233.1 | 243.7 | 246.8 | 208.8 | 209.4 | 209.5 | not held (fleet 87 MW at year end) |
| 2019 | 374.5 | 402.2 | 408.8 | 323.0 | 323.4 | 323.4 | not held (107 MW) |
| 2020 | 178.4 | 187.5 | 190.2 | 162.7 | 163.1 | 163.1 | not held (218 MW) |
| 2021 | 3,404.0 | 3,430.6 | 3,441.0 | 3,384.5 | 3,390.1 | 3,390.3 | not held (821 MW) |
| 2022 | 352.5 | 393.1 | 413.9 | 301.3 | 314.9 | 323.2 | not held (2,130 MW) |
| 2023 | 451.5 | 530.1 | 551.6 | 416.9 | 459.6 | 467.5 | not held (4,174 MW) |
| 2024 | 122.4 | 147.7 | 158.6 | 105.3 | 127.1 | 137.3 | not held (8,294 MW) |
| 2025 | 64.4 | 87.4 | 104.3 | 56.0 | 78.7 | 94.4 | not held (13,909 MW) |
| 2026 (to September) | 43.4 | 60.2 | 73.0 | 37.8 | 54.4 | 67.5 | September 3 to 30 only: 69 to 82 percent of the price-taker |

**How far the fleet-limited figures fall from the price-taker each year:** held for September 2026 only (above). For earlier years the quantities are not held, so I give no number. The fleet sizes in the table show why the cap would rarely bind on Responsive Reserve before 2023.

## Part B: California's rules, verified

Source: CAISO, Fifth Replacement Electronic Tariff, Section 8 (Ancillary Services), as of 1 May 2026, `https://www.caiso.com/documents/section-8-ancillary-services-as-of-may-1-2026.pdf`, read locally (39 pages).

| Product | Tariff text | Section | Model before | Verified |
|---|---|---|---|---|
| Regulation Up, Regulation Down | "Regulation capacity offered must be dispatchable on a continuous basis for at least sixty (60) minutes in the Day-Ahead Market and at least thirty (30) minutes in the Real-Time Market" | 8.4.1.1(g) | 1 hour, assumed | 1 hour day-ahead (the model's awards are day-ahead) |
| Spinning Reserve, Non-Spinning Reserve | "must be capable of maintaining that output or scheduled Interchange for at least thirty (30) minutes from the point at which the resources reaches its award capacity" | 8.4.3 | 1 hour, assumed | 30 minutes |
| Regulation, storage | "Regulation Energy Management ... a Regulation Bid for capacity (MW) of up to four (4) times the maximum Energy (MWh) the resource can generate or curtail for fifteen (15) minutes" | 8.4.1.2 | not modeled | an option a storage resource may request; still not modeled |

The tariff also says CAISO will dispatch a storage resource to keep enough state of charge for its ancillary schedule in real time (8.4.1.1(g)). The business practice manual was not read.

**Do the verified rules move CAISO's numbers?** Barely. Run both ways on the same days (`warehouse/analysis/battery_caiso_rules.py`; the assumed run reproduces the page's table exactly), total USD per kW:

| Year | Foresight 4h, assumed | verified | Day-ahead 4h, assumed | verified | Foresight 8h, assumed | verified |
|---|---|---|---|---|---|---|
| 2024 (from September) | 30.6 | 30.6 | 29.6 | 29.6 | 37.2 | 37.2 |
| 2025 | 91.6 | 91.7 | 85.2 | 85.3 | 115.3 | 115.5 |
| 2026 (to September) | 63.5 | 63.6 | 51.3 | 51.5 | 77.6 | 77.7 |

Spinning Reserve still earns almost nothing (at most USD 0.17 per kW a year), because Regulation Up pays more for the same power. Non-Spin moves both ways by a few tens of cents.

## Tests and checks

| Check | Result |
|---|---|
| `tests/test_session74.py` | 4 tests: a cap of 1 reproduces the program on 6 random days at 2, 4 and 8 hours; caps bind and no award passes one, and the capped revenue never exceeds the price-taker's; a cap of 0 is the energy-only optimum; the AS Plan parser. OK |
| `tests/test_session67.py` (the battery model's own) | 21 tests, OK, with the cap added |
| `python -m unittest discover -s tests` | 358 tests, OK (2 skipped), exit 0 |
| Validator, coverage, `--check-license` (`ercot_as_quantities`) | exit 0 each |

No site file changed in this session (the method doc is read by the site at build; session 75's build covers it).

## Errors and decisions

- **Decision: the quantities table holds only what ERCOT keeps.** The prompt asked for 2018 to today. I found no keyless public history and did not fill one; the header says so. Scheduling the connector (To finish, step 3) grows it.
- **Decision: the fleet for a month EIA has not published** is the newest month held (August 2026), named in the output. That is not filling a data row: it is a stated input to an analysis, and it makes the cap slightly more generous.
- **Decision: fleet-limited rows are a separate analysis file, not rows of `battery_stack_monthly`.** The live page and the daily run read that table, and the prompt keeps fleet-limited rows out of the live set. A separate file cannot reach either.
- **Decision: CAISO's verified rules are not written into the live model** (Part C forbids changing the live strategies' numbers); "To finish", step 2.
- **Two web searches** found the documents' addresses (ERCOT's projected requirements data product and the methodology documents; CAISO's tariff Section 8). The documents were downloaded and read locally, without the page-summarising fetch tool, which would be a model call.
- **The data lock** was held 10:22 to about 10:28 UTC, for the pull, coverage, archive and upload.

## For Samuel

1. **Do not switch the page's default to the fleet-limited estimate** (the recommendation above). If you want history for it, an ERCOT API key (free registration) would open ERCOT's archive; I could not check how far back it reaches.
2. **CAISO's Spinning and Non-Spinning Reserve need 30 minutes, not an hour.** It changes the numbers by cents; it changes the page's "assumed" label to a cited one. Yours to rule ("To finish", step 2).
3. **The years before 2024 stay an upper bound** under any fleet cap. If they matter to the CFO, the next model change is reserves that are called (energy delivered at the real-time price and the state of charge spent), not a cap.
