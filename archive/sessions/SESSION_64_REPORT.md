# Session 64 report: data extensions

Energy Research Warehouse (ERW), session 64, the last of the overnight run, on the portable laptop (role data), 2026-10-02 about 10:44 to 13:40 UTC. **Model spend: USD 0.00** (the cap was USD 0). No paid service. No force push. Nothing released on Redivis: the changed tables are in the draft only.

## In plain words

**A second year of hub prices is in the warehouse.** The six hubs outside ERCOT (CAISO SP15 and NP15, MISO Indiana, NYISO New York City, ISO-NE Internal Hub, SPP North) now have prices from 2024-09-01, two years instead of one.
- **Rows:** 231,566 new rows, against a ceiling of 1,500,000. The table holds 483,508 rows in all.
- **Where it lives:** the history table is in the Redivis draft only. It is still out of Supabase: no live-set rule matches it.
- **One obstacle:** SPP no longer serves 2024's daily files at their usual addresses. It keeps the whole year as one archive (5.15 GB for real-time prices). The connector now reads just the needed daily file out of that archive, a few megabytes per day, so SPP is complete too.

**Cost of power and merchant revenue are rebuilt on two years.**
- **The cost-of-power calculator's defaults did not change.** By design (session 49) they use the latest month every ISO holds complete, still August 2026.
- **What the second year shows:** the flat real-time price a year earlier was lower in MISO, NYISO, ISO-NE and SPP, and higher in CAISO (table below).
- **The seller tab's defaults did change.** They summarize every month held, so the non-ERCOT ISOs now draw on 25 months (ISO-NE 18 to 20, NYISO 23), not 9 to 13. Most annual revenue figures fell, because the first year's prices were lower.

**Two new events, chosen from the data.** I looked for the highest hours of demand in the year the new prices cover. Both events fall in that year, so they are the first events with hub prices beyond ERCOT's.
- **The January 2025 cold** (2025-01-17 to 01-26), six grids. PJM, MISO, NYISO and ISO-NE all hit their winter peak hour on 2025-01-21 or 22.
- **The June 2025 heat** (2025-06-20 to 06-28), four eastern grids. PJM, NYISO and ISO-NE hit their highest hour of the whole year on 2025-06-23 or 24. New York City's real-time price reached 2,960.11 USD/MWh on 2025-06-24.

Each event has an event study and a page (`/events/cold-2025`, `/events/east-heat-2025`), and both are on the index.

**The tight-evening forecast is built and backtested. It is internal only:** not a warehouse table, not on the site, not in Supabase or Redivis.
- **What it does:** it reuses the Flex Alert scorecard's load model to predict each summer evening's peak demand a day ahead, then flags a "tight" evening above a threshold learned from earlier years.
- **How well it ranks evenings:** it tells CAISO's alert days from the others very well. Across 2020 to 2025, an alert day's predicted peak was higher than a normal day's 96 percent of the time (AUC 0.958).
- **How well the flag works:** a single threshold catches only 13 of 34 alert days. When it does flag a day, it is right 72 percent of the time.
- **Why the flag misses:** the alerts of 2021 to 2024 came on evenings that were less hot than those of 2020 and 2022.

**One thing a person should know.** The production site was still serving cached pages (hourly revalidation) when I checked. A fresh local build matched every value: check-values 4,777 of 4,777.

## The pull: rows against the ceiling

Approved pull: 2024-09-01 to 2025-08-31, ceiling 1,500,000 rows. Run as six parallel backfills (`hub_history.py backfill --start 2024-09-01 --until 2025-09-01`), each in its own directory, merged by key.

| ISO | Hubs | New rows | Days not complete (left out) |
|---|---|---|---|
| CAISO | SP15, NP15 | 87,350 | 1 day-ahead, 1 real-time (2024-11-03, the autumn clock change: OASIS left out its last hour, as on 2025-11-02 in session 49) |
| MISO | Indiana Hub | 17,520 | none |
| NYISO | N.Y.C. | 41,784 | 21 real-time days (missing or late time stamps, e.g. 2024-10-23) |
| ISO-NE | .H.INTERNAL_HUB | 41,112 | 28 real-time days (missing 5-minute intervals, e.g. 2024-09-09) |
| SPP | SPPNORTH_HUB | 43,800 (21,725 + 22,075) | none |
| **All** | | **231,566 of 1,500,000** | each a gap row in `run_status.csv` |

- **The table:** `iso_hub_prices_history`, 483,508 rows, 2024-09-01 to 2026-10-03 (the daily run keeps appending).
- **Validator:** pass.
- **Redivis draft:** uploaded, count 483,508.
- **Out of Supabase:** no live-set rule matches it, and `tests/test_session49.py` checks that.

**SPP's 2024 archive.** For 2024, SPP's file browser answers HTTP 404 for every daily file (`/2024/09/By_Day/DA-LMP-SL-202409010100.csv`). It serves each finished year as one zip instead: `<report>?path=/2024/2024.zip`, 294 MB for day-ahead and 5,151,618,687 bytes for real-time. The zip holds the same By_Day daily files, and the server answers byte ranges. So `hub_history.spp_archive()` does this:
- it wraps `pandas.read_csv` for SPP backfills only;
- a daily file that answers 404 is read from its year's archive: the zip's directory once, then that member's bytes (about 0.6 MB for day-ahead, 7 MB for real-time), checked against its CRC;
- the rows' `source_url` is the archive's URL, and the header says so.

The first SPP run, before the fallback existed, wrote nothing for September to December 2024, and I stopped it. The rerun wrote all 181 days of 2024-09 to 2025-02, both markets. Four tests cover the fallback (`tests/test_session64.py`):
- a member is read by range from an in-memory zip;
- a 404 falls back to the archive;
- other errors and other URLs pass through untouched;
- a member that is absent is an error, never a fill.

## Cost of power: old against new defaults

**The calculator's defaults are unchanged.** They use the ranked month: the latest month every ISO holds complete, else 90 percent of its hours (session 49). That is still 2026-08, so every default is identical before and after:

| Hub | Flat price, 2026-08 (the default), USD/MWh |
|---|---|
| CAISO SP15 | 55.33 |
| ERCOT hub average | 35.45 |
| ISO-NE Internal Hub | 53.66 |
| MISO Indiana | 44.58 |
| NYISO N.Y.C. | 54.88 |
| SPP North | 38.90 |

**What the two years show** (`cost_of_power_monthly`, real-time, weighted by the hours held):

| Hub | Flat, 2024-09 to 2025-08 | Flat, 2025-09 to 2026-08 | Load-weighted, year 1 | Load-weighted, year 2 |
|---|---|---|---|---|
| CAISO SP15 | 31.28 | 28.43 | 31.90 | 28.71 |
| CAISO NP15 | 37.43 | 32.81 | 38.24 | 33.28 |
| ERCOT | 30.02 | 31.52 | 31.05 | 32.82 |
| ISO-NE | 60.18 | 70.37 | 63.61 | 74.10 |
| MISO Indiana | 38.70 | 47.19 | 40.55 | 49.55 |
| NYISO N.Y.C. | 61.94 | 68.61 | 66.15 | 72.49 |
| SPP North | 23.31 | 30.63 | 24.45 | 32.60 |

The second year's flat prices equal session 62's `ai_power_regions`, which used the same months: an independent check.

**The seller tab's defaults** (`/cost-of-power/seller`, 100 MW, or 100 MW / 400 MWh for the battery; Lazard midpoints). They summarize every held month, so they moved. Annualized mean revenue, USD a year, before and after:

| ISO | Months held | Solar | Wind | Battery | Gas peaker |
|---|---|---|---|---|---|
| CAISO | 13 to 25 | 3,100,376 to 3,223,426 | 6,554,593 to 8,177,556 | 4,868,966 to 5,242,120 | 4,407,101 to 4,672,262 |
| ISO-NE | 9 or 10 to 18 to 20 | 2,144,268 to 1,988,785 | 24,477,678 to 18,813,906 | 6,861,454 to 6,450,604 | 28,082,561 to 23,486,542 |
| MISO | 13 to 25 | 8,021,948 to 7,519,139 | 13,578,100 to 12,399,724 | 11,274,698 to 8,989,730 | 14,296,232 to 11,125,146 |
| NYISO | 13 to 23 | none held (no solar shape) | 14,925,026 to 14,268,711 | 7,063,986 to 6,834,835 | 22,767,496 to 20,723,988 |
| SPP | 13 to 25 | 10,227,205 to 8,523,271 | 8,088,556 to 7,000,425 | 10,026,117 to 8,829,827 | 8,582,290 to 6,868,225 |
| ERCOT | 99 (2018 on) | 12,209,577 to 12,212,983 | 10,661,515 to 10,663,738 | 10,845,854 to 10,848,748 | 21,788,309 to 21,789,461 |

- **Coverage of debt service:** the trailing-twelve-month figures exist now for CAISO, MISO and SPP: 14 points each, where there were 2.
- **ERCOT** moved only by the last days of September 2026.
- **Row counts:** `merchant_revenue_monthly` went from 5,984 to 8,120 rows, `cost_of_power_monthly` from 1,593 to 2,241, `cost_of_power_carbon` from 495 to 699. `cost_of_power_hourly_profile` is unchanged at 4,032 rows (the last 12 months).

## The two events

Both events use the Elliott template: each grid's local day, against the same weekdays 364 and 728 days earlier, with the peak-hour variables. The method is in `docs/methods/events.md`, in a new section.

**Why these two.** They are the days of the highest winter and summer hours of demand served, in EIA's hourly data, over the year the new prices cover (2024-09 to 2025-08):

| Grid | Highest winter hour | Highest summer hour |
|---|---|---|
| PJM | 144,420 MW, 2025-01-22 | 160,560 MW, 2025-06-23 |
| MISO | 104,434 MW, 2025-01-21 | 118,106 MW, 2025-07-29 |
| NYISO | 23,521 MW, 2025-01-22 | 31,857 MW, 2025-06-24 |
| ISO-NE | 19,582 MW, 2025-01-21 | 25,898 MW, 2025-06-24 |

They are also the first events whose hubs beyond ERCOT have prices. The event builder gains `hubs`: each hub's daily real-time and day-ahead mean and highest price, from `iso_hub_prices_history`. These hubs have no baseline days (the history starts 2024-09-01), so the event study gives them no estimate. `event_study.py` and the TypeScript twin both skip such a series.

**cold_2025, 2025-01-17 to 01-26** (PJM, MISO, SPP, NYISO, ISO-NE, ERCOT)

| Grid | Pooled effect on daily demand, percent of the counterfactual | 95 percent interval, MWh a day |
|---|---|---|
| PJM | +17.51 | 230,840 to 593,352 |
| ERCOT | +21.63 | 132,117 to 363,965 |
| SPP | +13.70 | 63,044 to 157,117 |
| MISO | +12.73 | 100,317 to 363,415 |
| NYISO | +9.68 | 23,267 to 59,020 |
| ISO-NE | +9.46 | 14,519 to 50,218 |

- **ERCOT's hub stayed calm.** Its highest 15 minutes were 192.08 USD/MWh, and the pooled effect on its daily mean price (+4.93 USD/MWh) has an interval that spans zero.
- **The other hubs rose:**
  - NYISO N.Y.C. 714.25 USD/MWh (2025-01-21);
  - SPP North 800.22 (2025-01-23);
  - ISO-NE 456.57 (2025-01-17);
  - MISO Indiana 393.10 for an hour (2025-01-21).

**east_heat_2025, 2025-06-20 to 06-28** (PJM, NYISO, ISO-NE, MISO)

- **Pooled effects on daily demand:**
  - PJM +15.35 percent (interval 195,313 to 566,376 MWh a day);
  - NYISO +9.98;
  - MISO +8.53;
  - ISO-NE +6.75, an interval that spans zero; its peak day, 2025-06-25, is missing an hour in EIA's data.
- **On 2025-06-24,** daily demand stood 39.93 percent above the baseline in ISO-NE, 35.23 in NYISO and 35.05 in PJM.
- **Prices:** every hub's highest came on 2025-06-24:
  - NYISO N.Y.C. 2,960.11 USD/MWh (15 minutes);
  - ISO-NE 1,240.24;
  - MISO Indiana 1,202.05 for an hour.

**Pages:** `/events/cold-2025` and `/events/east-heat-2025` both use the shared `EventWindow`, with a new hubs section, and the event study. Both are on the `/events` index, in check-values and check-routes, in `llms.txt` and the chat spec, and in the replication notebook.

**Not held:** weather for these windows. A temperature-controlled estimate would need a new NOAA pull, which was not in the approved list.

## The tight-evening forecast and its backtest (internal)

- **Code and output:** `warehouse/derived/caiso_tight_evening.py`. It writes `warehouse/output/analysis_internal/caiso_tight_evening_backtest.csv`, which is gitignored and not a warehouse table. The method is in the module docstring.
- **The model:** the scorecard's per-hour OLS of CISO demand, fit on the weather and the calendar, using non-alert days only.
- **The evening peak:** the highest predicted hour from 16:00 to 20:00 Pacific.
- **The flag:** "tight" when that peak is at or above a threshold. The threshold is the one that maximizes F1 on the training seasons.
- **The backtest:** season by season, 2020 to 2025, each season forecast only from the seasons before it.
- **Two weather inputs:**
  - **observed:** the day's own weather, standing for a perfect weather forecast, so an upper bound on skill (no weather forecast is held);
  - **persistence:** the same hour of the day before, which is known without any forecast.

| Weather input | Alert days | Flagged tight | Hits | Misses | False alarms | Precision | Recall | AUC | Evening-peak error, non-alert days |
|---|---|---|---|---|---|---|---|---|---|
| Observed (upper bound) | 34 | 18 | 13 | 21 | 5 | 72.2% | 38.2% | 0.958 | MAE 1,215 MW, bias 0 |
| Persistence | 34 | 26 | 11 | 23 | 15 | 42.3% | 32.4% | 0.928 | MAE 1,620 MW |

**Per season, observed weather:**

| Season | Alert days | Hits | Misses | False alarms | AUC | Threshold |
|---|---|---|---|---|---|---|
| 2020 | 11 | 4 | 7 | 0 | 0.967 | 44,536 MW |
| 2021 | 8 | 0 | 8 | 0 | 0.946 | 44,487 MW |
| 2022 | 11 | 9 | 2 | 2 | 0.986 | 43,911 MW |
| 2023 | 3 | 0 | 3 | 1 | 0.939 | 43,952 MW |
| 2024 | 1 | 0 | 1 | 0 | 0.929 | 44,160 MW |
| 2025 | 0 | 0 | 0 | 2 | none | 44,292 MW |

**What it says:**
- The predicted evening peak ranks alert days very well: an AUC of 0.93 to 0.99 in every season with alerts.
- A demand threshold misses the alerts that were not about record demand, such as 2021's eight, which came on evenings below the threshold.
- A useful tool would report the ranking, the peak against the threshold, and supply-side signals, not a yes or no.
- It stays internal until a person decides otherwise.

## Tests and checks

- **Python:** `python -m unittest discover -s tests`, 258 tests, all pass after these fixes:
  - `tests/test_session64.py` is new (8 tests).
  - `tests/test_session56.py` applies the California rules' stated window, and its day count is a lower bound (the daily append adds a day each day).
- **Event study parity (TypeScript against Python):** 2,211 estimates compared, 0 mismatched.
- **Validator:** pass for every changed table.
- **Coverage:** 99 tables.
- **Site:** `npm run build` passes; tsc and eslint are clean.
- **check-values, fresh local build:** 4,777 of 4,777 values match Supabase.
- **check-routes, production:** 68 of 68 pages pass.
- **check-values, production:** 4,288 of 4,411 matched at 13:20 UTC. The 123 that did not are the hourly page cache:
  - pages built before the load, still showing the old cost-of-power, seller and COVID numbers;
  - latest prices, which move every 15 minutes, and the catalogue.
  - The fresh build matched them all.
- **Live:** both event pages render the new data on production (PJM 160,560 MW; New York City 2,960.11 USD/MWh).

## Errors, decisions and what moved

1. **SPP 2024 is archived.** Fixed with the range-read fallback (above).
2. **A season-only weather station.** Session 60 added Fresno (FAT) for the Flex Alert scorecard and marked it `SEASON_ONLY` in `noaa_isd.py`, but the event builder never checked that flag. A rebuild therefore averaged FAT into CAISO's degree days, and the TypeScript twin, which does not know FAT, no longer matched. The builder now leaves season-only stations out, so CAISO's event estimates are as published.
3. **One published estimate moved, by design.** COVID-19's CAISO temperature-controlled pooled effect went from -20,589 to -22,557 MWh a day.
   - **Why:** session 60's season pull added Los Angeles observations for May 2018 to 2020, which fall inside COVID's weather days. They were left out in session 49 to stay under its ceiling.
   - **What did not change:** every other row of the older events (checked row by row).
4. **California game levels.** "The lowest midday price of any day held" stopped being true once the history reached 2024: 2025-03-29 is lower (-45.53 USD/MWh against -22.13).
   - **Kept:** both levels, whose dates key the leaderboards, and their rules, which already said "from 2025-09-01".
   - **Changed:** `battery_levels.py` now applies that window (`CA_FROM`), and both levels' sentences say "of any day held from 2025-09-01 on". The duck day is still the largest rise over both years.
5. **The data lock.**
   - Taken at 10:44.
   - Released at 11:02, ahead of the 14:00 daily; my pulls wrote only to scratch directories.
   - Retaken at 11:33 for the merge and all writes, and released at 13:16, before the daily.
6. **Sync before the writes.** `sync.py --refresh` replaced my merged tables with Redivis's copies, as the rule intends. The cloud's history was newer by the daily's appended days. So I redid the merge from the six scratch directories on top of it, and rebuilt everything from there.
7. **A chained command ran past a failure.** `build_coverage.py | tail` hid the coverage error, and the loader ran once with the old coverage (about 12:40). It loaded the same rows the later runs confirmed identical. The 15-minute job had already loaded a `sources` row I then removed (`erw:tight_evening`), and `load.py --prune` deleted it.
8. **The forecast's license.** Coverage requires a derived table's license to follow its inputs, which are public. "Internal only" therefore means unpublished, not licensed internal. The output moved to `analysis_internal/`, the precedent for internal outputs.
9. **Production cache:** see "Tests and checks".

## Not done

- No weather for the two new events (a new pull).
- The second year's lower midday day (2025-03-29) is not a new game level; that would be a game change.
