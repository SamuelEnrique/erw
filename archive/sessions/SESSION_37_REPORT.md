# Session 37 report: cost-of-power model v0 (tool 16), market-based

Energy Research Warehouse (ERW), session 37, run 2026-09-30 from 09:09 to about 09:45 UTC. **Wall time about 36 minutes.**

**API spend: USD 0.00, confirmed.** No model call. The cost ledger's last row is 05:12 UTC, before this session.

- **No pull.** Everything comes from tables held and the saved EIA extracts.
- **Nothing released or deleted:** nothing released on Redivis, nothing deleted from it, no force push.
- **The daily job did not land** during the session, so there was nothing to merge.
- **Deployed and checked live:** routes 44 of 44, values 1,594 of 1,594 (83 on `/cost-of-power`).

## Part A: the tables

All three are tier derived, public, written by `warehouse/derived/cost_of_power.py`; method `docs/methods/cost_of_power.md`.

| Table | Rows | What |
|---|---|---|
| `cost_of_power_monthly` | 977 | Per ISO main hub and local month, real-time and day-ahead: `*_load_weighted`, `*_simple_mean`, `*_shape_premium`, `*_hours`, and `hours_in_month` |
| `cost_of_power_hourly_profile` | 1,008 | `rt_mean_h00` to `rt_mean_h23` and `rt_days_hNN`, the last 12 months each hub holds |
| `cost_of_power_carbon` | 309 | `rt_load_weighted` beside `intensity_demand` and `intensity_generation`, over the same hours |

**How the figures are built:**

- **Hubs:** the price board's main hubs.
- **Weights:** each hub's hourly price is weighted by the whole balancing authority's hourly demand, from EIA's per-BA workbooks (the session 34 extracts).
- **Hours:** an hour is used only when every interval of it is present.
- **Months:** the ISO's local month.
- **PJM is excluded,** because its prices are internal.

### Months per ISO

| ISO (hub) | Months | Complete |
|---|---|---|
| ERCOT (HB_HUBAVG) | 99, 2018-07 to 2026-09 | All but four: 2018-07 (720 of 744 hours; EIA's ERCO demand starts 2018-07-02), 2018-11 (673 of 721), 2025-12 (696 of 744), 2026-09 (648 of 720, to the 27th) |
| CAISO (TH_SP15_GEN-APND) | 2, 2026-08 and 2026-09 | none (144 and 648 hours) |
| ISO-NE (.H.INTERNAL_HUB) | 2 | none (144 and 647 hours) |
| MISO (INDIANA.HUB) | 2 | none (real-time 120 and 648 hours) |
| NYISO (N.Y.C.) | 2 | none (144 and 648 hours) |
| SPP (SPPNORTH_HUB) | 2 day-ahead, 1 real-time | none (real-time 96 hours, 2026-09-24 to 27) |

**Why only ERCOT has history.** The other five ISOs' hub prices exist in the warehouse only from about 2026-08-26: in the output CSVs, the archive, and so in Redivis. Their price tables are rolling windows, and no longer history was ever pulled.

**Months are carried over.** The builder keeps any month the rolling tables no longer reach, and never recomputes a month from fewer hours. The months already built will survive, but September 2026 needs a rerun by hand to complete (below).

**Cross-check.** ERCOT's August 2026 real-time month, recomputed from the raw 15-minute rows and the ERCO extract with separate code: 744 hours, load-weighted **36.6951**, simple **35.4505**. Both equal the rows.

**Left out, with each named in the header and log:** 15 carbon months with missing CO2 hours. In 2026-09, `intensity_demand` is missing in ERCOT, CAISO, MISO and SPP (1 to 3 hours each).

## Part B: `/cost-of-power`

The page is in the Prices menu, next to Markets (the nav has no Markets group; `/markets` sits in Prices). `/datacenters` and every `/grid/<iso>` page link to it; PJM's grid page says the model has no PJM row.

### The headline figures and their rows

**Ranked bar: load-weighted real-time price, 2026-09,** the latest month every ISO holds. The month is partial and labelled as such, with each bar's hours in the table. Rows are `cost_of_power_monthly`, `rt_load_weighted` at `2026-09-01`:

| ISO | Load-weighted | Simple mean | Shape premium | Hours |
|---|---|---|---|---|
| MISO | 96.8275 | 86.0534 | 10.7741 | 648 of 720 |
| NYISO | 44.9269 | 43.0291 | 1.8978 | 648 |
| ISO-NE | 41.0058 | 39.5225 | 1.4833 | 647 |
| ERCOT | 40.1646 | 38.9797 | 1.1849 | 648 |
| CAISO | 38.7305 | 38.4033 | 0.3272 | 648 |
| SPP | 32.0202 | 30.5765 | 1.4437 | 96 |

MISO's figure is driven by real spikes in `iso_rtm_hub_prices` at Indiana Hub: 7,627.01 USD/MWh at 2026-09-17 23:00 UTC, and 4,118.32 at 2026-09-03 00:00 UTC. Its 18:00 hour averages 509.85 in the profile.

**ERCOT since 2018:**

- Latest complete month, 2026-08: **36.6951** USD/MWh load-weighted, a shape premium of **1.2446** (rows `ercot:HB_HUBAVG` `rt_load_weighted` and `rt_shape_premium` at `2026-08-01`).
- The dearest month since July 2018: **1,768.62** in 2021-02, Winter Storm Uri.

**Hour of day, 2026-09, from `rt_mean_hNN` rows (local time):**

| ISO | Cheapest hour | Dearest hour |
|---|---|---|
| ERCOT | 09:00, 22.49 | 20:00, 76.03 |
| CAISO | 09:00, 20.08 | 18:00, 52.46 |
| ISO-NE | 10:00, 31.62 | 20:00, 49.64 |
| MISO | 02:00, 31.37 | 18:00, 509.85 |
| NYISO | 03:00, 33.37 | 17:00, 70.72 |
| SPP | 03:00, 9.79 | 14:00, 59.62 |

**Cost against carbon, 2026-09** (`cost_of_power_carbon`), in USD/MWh and kg CO2 per MWh generated:

| ISO | Load-weighted, USD/MWh | kg CO2 per MWh generated |
|---|---|---|
| ERCOT | 40.16 | 342.07 |
| CAISO | 38.73 | 135.27 |
| ISO-NE | 41.01 | 208.03 |
| MISO | 96.83 | 454.47 |
| NYISO | 44.93 | 258.45 |
| SPP | 32.02 | 449.58 |

The point plots intensity of generation, because intensity of demand is missing in four ISOs this month.

### The calculator's default outputs

The defaults are 100 MW, load factor 0.9 and 90 days, each labelled on the page as an assumption. They give **194,400 MWh flat**, and **155,520 MWh** in the cheapest 80 percent of hours. The outputs are computed on the server and checked with keys `cop|...`:

| ISO | Flat load, USD | Flat, USD/MWh | Cheapest 80%, USD | Cheapest 80%, USD/MWh | Months behind it |
|---|---|---|---|---|---|
| ERCOT | 6.24 million | 32.10 | 4.01 million | 25.81 | 2025-10 to 2026-09 (12) |
| SPP | 5.94 million | 30.58 | 3.89 million | 25.03 | 2026-09 (96 hours) |
| ISO-NE | 7.73 million | 39.77 | 5.84 million | 37.57 | 2026-08 to 2026-09 |
| NYISO | 8.24 million | 42.39 | 6.05 million | 38.89 | 2026-08 to 2026-09 |
| CAISO | 9.20 million | 47.32 | 5.92 million | 38.08 | 2026-08 to 2026-09 |
| MISO | 15.28 million | 78.61 | 6.38 million | 41.05 | 2026-08 to 2026-09 |

Only ERCOT's defaults rest on 12 months. The other ISOs' rest on late August and September 2026, and the page says so. The reader's own inputs run in a client calculator on the same prices.

## Part C: verify and ship

- **Validator:** the three tables pass.
- **Coverage:** 82 tables; the three are public, derived, ISOs CAISO;ERCOT;ISO-NE;MISO;NYISO;SPP, sectors power, and power;carbon for the carbon table.
- **Archive:** 2,294 rows.
- **Supabase,** Part A only, whole, by the live set rule `^cost_of_power_(monthly|hourly_profile|carbon)$`:

  | Stage | Size |
  |---|---|
  | Before | 337.4 MB |
  | After the load and VACUUM FULL | **338.4 MB** |
  | After migration 012's index | **341.5 MB** |

  All three stages are under the 350 MB rule.
- **Redivis draft (public):** `count(*)` 977, 1,008 and 309, equal to the CSVs. Nothing released.
- **llms.txt:** the question row "What does a 100 MW datacenter pay for energy in ERCOT (or another ISO)" routes to the two tables, and a section describes all three. The chat spec is regenerated and `check_spec` passes.
- **check-values:** covers every number on the page. That is 83 values: 57 series keys, plus 26 `cop|` keys that recompute the calculator's defaults from Supabase in the script's own code (not `lib/cost.ts`).
- **check-routes:** covers `/cost-of-power` and `/data/methods/cost_of_power`.
- **`tests/`:** 72 of 72, including the new `tests/test_session37.py`: complete hours only, month lengths at clock changes, load weighting, and keys and scope of the built table.
- **Local and live checks:** routes 44 of 44, values 1,594 of 1,594.

## A fix beyond the prompt: migration 012

**The problem.** The first local build lost the grid pages' queue figures to a Supabase statement timeout, as the first 36C deploy had. `site/lib/grid.ts` reads queue positions with `entity_id like '<iso>_queue:%'`. Under the database's en_US collation the primary key cannot serve a prefix LIKE, so each read filtered all of energy_projects: 1.8 s warm, against the anon role's 3 s timeout. A build renders the seven grid pages at once.

**The fix.** `warehouse/supabase/migrations/012_entities_id_pattern.sql` adds an index on (table_name, entity_id text_pattern_ops):

- the read now takes 24 ms;
- the index is 3.2 MB;
- it is applied, and idempotent;
- dropping the index undoes it.

After it, local and live checks both show every grid page's queue values.

## Decisions made without a human

1. **Hourly price, then weight.** 15-minute prices are averaged to the hour, and an hour is used only when complete. Months are the ISO's local months (the price board's clocks). Hub price times the whole BA's demand; the method says a buyer elsewhere pays its own node.
2. **Partial months are written,** with `*_hours` and `hours_in_month`, and labelled on the page. Nothing is filled or scaled.
3. **The ranked bar uses the latest month every ISO holds** (2026-09, partial), not "the last complete month": only ERCOT has a complete month, and comparing ERCOT's August with the others' September would mix months. ERCOT's latest complete month is its own line under the history strip.
4. **Cost against carbon plots intensity of generation.** Intensity of demand, the buyer's measure, is in the table, but four ISOs miss a few CO2 hours in 2026-09.
5. **The calculator's definitions:**
   - flat = the mean price of every hour held in the last 12 months;
   - a month is 30 days and a year 365;
   - "cheapest 80 percent of hours" runs at the same MW x load factor only in the cheapest 80 percent of (month, hour-of-day) cells, taken by hours with the last cell in part. The facility then uses 80 percent of the flat energy. It is a plannable schedule, not perfect foresight.
6. **The builder is not in the daily run.** It needs the ERCOT history and the extracts, which are not on the runner. Months are carried over so nothing is lost.
7. **Migration 012,** as above: reversible, and needed for the live checks to pass whole.
8. **The nav entry sits in Prices,** after Markets.

## Open questions

1. **History for the other ISOs.** Their hub prices start about 2026-08-26, so their load-weighted months and the calculator's 12 months are one partial month and a few days. Pull a year of CAISO, MISO, NYISO, ISO-NE and SPP hub prices (and keep them past the rolling window)?
2. **Rerunning the builder.** When should it run? Its inputs roll, and September 2026 completes only if it runs again before the rolling tables drop 2026-09-01. Should it join the daily run once the extracts and the ERCOT history are on the runner?
3. **SPP real-time holds 96 hours.** Its connector's real-time table starts 2026-09-24. Is that expected?
4. **Node prices.** A datacenter pays its own node, not the hub. The zone tables of NYISO and ISO-NE could weight their zones.
5. **LCOE** needs capital, fuel and financing inputs, as the prompt says.

## Skipped

- LCOE and PJM, as instructed.
- A chat evaluation question for the new row: running the evaluation calls a model.
