# Session 36B report: Historical Event Analyzer v0, Winter Storm Uri (ERCOT, February 2021)

Energy Research Warehouse (ERW), session 36B, run 2026-09-30 from about 06:05 to 07:10 UTC. **Wall time about 65 minutes,** against the 60-minute target. Most of the time went to one validator pass, which covers every table.

**API spend: USD 0.00.** No model call; the cost ledger has no session 36B row.

- **No pull.** Every row comes from tables already held (`ercot_all_hub_prices_history`, `eia930_all_emissions`) and one saved file: the ERCO workbook extract of session 34.
- **Nothing released or deleted:** nothing released on Redivis, nothing deleted from it, no force push.
- **Deployed and checked live:** routes 41 of 41, values 1,498 of 1,498.

## 1. The table: event_window_daily

**What it is:** tier derived, public; written by `warehouse/derived/event_window.py`; method `docs/methods/events.md`.

**556 rows,** none left out: every day of the three windows was complete (96 real-time intervals, 24 day-ahead hours, 24 EIA hours).

| Variables | Entity | Rows |
|---|---|---|
| `rt_mean`, `rt_max`, `da_mean`, `da_max` (USD/MWh) | `ercot:HB_HUBAVG` | 4 x 54 |
| `demand_mwh`, `demand_min_mw`, `demand_max_mw`, `net_generation_mwh`, `intensity_generation` | `eia930:ERCO` | 5 x 54 |
| `demand_mwh_vs_baseline`, `net_generation_mwh_vs_baseline` (event day minus the 2019 and 2020 mean) | `eia930:ERCO` | 2 x 18 |
| `demand_mwh_day_change`, `net_generation_mwh_day_change` (event day minus the day before) | `eia930:ERCO` | 2 x 17 |

**Days and baseline.** 54 days in all: ERCOT operating days (Central time) 2021-02-07 to 2021-02-24, and the same calendar days of 2019 and 2020 as the baseline.

**Columns.** Partition columns are `ba` (erco) and `event` (uri_2021). `event` joins the reserved partition columns as decision 31 of `docs/datastandard.md`, and the validator accepts it.

**Sources:**

- **Prices:** ERCOT's NP6-785-ER (real-time, 15-minute) and NP4-180-ER (day-ahead, hourly) settlement point prices at the hub average, read from `ercot_all_hub_prices_history` in one streamed pass.
- **Demand served and net generation:** EIA's per-BA workbook for ERCO (sheet Published Hourly Data), from the extract `warehouse/raw/eia930_emissions/20260930T000657Z/erco_hours.csv`. `eia930_all_demand` and `_generation` keep only 30 days. The extract will be pruned from this machine after 14 days; the rows stay in the table, the archive and Redivis.
- **CO2:** `eia930_all_emissions`.

**Two additions beyond the prompt's variables:** the day-to-day changes and the comparisons with the baseline. They let the page state "the largest drop" by reading a row rather than computing one. They also showed that the drop against the baseline and the drop during the outages are different things (below).

## 2. The pages

- **`/events`:** the index.
- **`/events/uri-2021`:**
  - a short framing cited to EIA (Today in Energy, id=46836: "ERCOT began implementing rotating outages at midnight on February 15"; the page's summary sentence paraphrases that article's title);
  - a note that demand during load shed is demand served;
  - four charts: 2021 against 2019 and 2020, on the same calendar days;
  - tier chips, citations and a method link on every block.
- **Nav:** a new "Events" entry.

**The headline numbers, each a row of `event_window_daily` with its check key:**

| Chart | Line on the page | Row |
|---|---|---|
| Price | Highest 15-minute real-time price **9,051.55 USD/MWh on 2021-02-17**; the highest on the same days of 2019 and 2020 was 1,691.63 (2020-02-10) | `ercot:HB_HUBAVG` `rt_max` 2021-02-17 and 2020-02-10. Cross-checked: the maximum of the raw 15-minute rows is 9,051.55 on 2021-02-17 |
| Demand served | Lowest hour of demand served in the window **27,719 MW on 2021-02-24**, after the storm; on 2021-02-15, the first day of rotating outages, the lowest hour was **43,776 MW** | `eia930:ERCO` `demand_min_mw` 2021-02-24 and 2021-02-15. Cross-checked: the extract's minimum hour is 27,719 at 2021-02-24 09:00 UTC |
| Net generation | Largest day-to-day fall **-308,863 MWh on 2021-02-15**; largest shortfall against the 2019 and 2020 average **-186,530.50 MWh on 2021-02-21**, after the storm | `net_generation_mwh_day_change` 2021-02-15; `net_generation_mwh_vs_baseline` 2021-02-21 |
| Carbon intensity | Highest daily intensity in 2021's window: **479.44 kg CO2/MWh on 2021-02-09** | `intensity_generation` 2021-02-09 |

**Why the page gives two lines for demand and generation.** The literal "lowest demand hour" and "largest drop against baseline" both fall after the storm (2021-02-24 and 2021-02-21). During the outages, demand served and net generation stayed above the 2019 and 2020 average. The table holds no weather to say why. So each chart also names the outage-day figure: 2021-02-15's lowest hour, and the day-to-day fall that morning.

## 3. Verify and ship

- **Validator:** 79 of 79 tables pass, through the reports path of session 36A.
- **Coverage:** 79 tables; `event_window_daily` is public, derived, sector power;carbon, ISO ERCOT.
- **Archive:** 556 rows.
- **Supabase,** this table only (live set rule `^event_window_daily$`, whole): **376.5 MB before, 376.7 MB after** the load and vacuum.
- **Redivis draft** (public dataset): `count(*)` 556, equal to the CSV. Nothing released. The license check passed on its second try (the first timed out connecting to Redivis).
- **llms.txt:** describes the table and routes the Uri question to it; the chat spec is regenerated and `check_spec` passes.
- **`tests/`:** 65 of 65.
- **check-routes and check-values** now cover `/events` and `/events/uri-2021`: 7 value checks on the Uri page.
  - Local: 41 of 41 routes, 1,498 of 1,498 values.
  - **Live:** the same.
- **One bug fixed before the push.** The page matched 2021-02-15's row by an exact `...Z` time, but Supabase returns `+00:00`, so that one figure showed "not held". It now matches on the date and is checked.

## Decisions made without a human

1. **Days are ERCOT operating days (Central time)** for every variable, including the EIA hours, so the four charts line up. Intensity is the day's CO2 over its net generation: `carbon_intensity_daily`'s formula over the local day, not its UTC days.
2. **The baseline of a day** is the mean of 2019's and 2020's values for the same calendar day. The charts show both years, not the mean.
3. **Day-to-day changes and baseline differences** are stored as rows, so the page reads them rather than computes them.
4. **The event's end date is not on the page.** Only the start of rotating outages is sourced (EIA); the window, 2021-02-07 to 02-24, is the ERW's choice and is stated as such.
5. **`event_window.py` is not in the daily run.** The history table is never on the runner, and the table is a fixed record. On the runner, coverage carries it over and the Supabase loader leaves its rows alone.

## Open questions

1. **Keys across events.** The key is (entity, variable, ts_utc), so an event whose days, or baseline days, overlap another's would fail the build. That includes a February 2019 or 2020 event against Uri's baseline. Add `event` to the key, or keep events apart?
2. **Load shed amounts.** ERCOT published how much load it shed; the warehouse does not hold it, so the page cannot show what customers lost. Pull ERCOT's event data in a later session?
3. **Weather.** `weather_obs_hourly` starts in 2026. Historical NWS observations for February 2021 would explain the demand curve.
4. **Supabase** is still at 376.7 of 400 MB (session 36A's question).

## Skipped

- Nothing asked for.
- Other events, as instructed.
