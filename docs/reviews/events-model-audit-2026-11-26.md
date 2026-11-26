# The events pages (`/events`): their figures audited as a hostile expert would

Session 10225, chain 710 part D, 26 November 2026, the old laptop. Read as a grid reliability analyst and an economist who write about these events and want to find the pages wrong. Platform tool: the Historical Event Analyzer, `/events` and its nine event pages. Three views taken whole: **Winter Storm Uri** (`/events/uri-2021`, the index's first card, so its default event), **the August 2020 heat wave in CAISO** (`/events/caiso-heat-2020`) and **Winter Storm Elliott** (`/events/elliott-2022`), with the index's three cards for them. Earlier reads are not repeated: the faults file of 16 November (`docs/reviews/events-faults-2026-11-16.md`: the hold that draws every EIA-930 figure "license needed", the COVID-19 baseline words, ERCOT's September record), the cross-check (`events-crosscheck-2026-11-16.md`), the ruling alternatives of 17 November (`ruling-alternatives-events-2026-11-17.md`: the temperature column for Elliott's days, Uri's offer cap count, FERC's SPP peak) and the regions read of 19 November. Window F's `/events/covid-2020` phone fix is not redone.

- Nothing changed on main but this file and its evidence folder (`docs/reviews/events-model-audit-2026-11-26/`). No table written, no lock taken, no default moved, no model called, no live service asked.
- Each finding has its own branch, `wip/audit-events-<n>`. The words-only fixes are for landing; the figure fixes carry a test only and wait for the owner.
- **Out of bounds: the paper's.** "The whole country" section's net imports columns, the hover that sets a region's pairs against its net imports, and the table "Power between regions, pair by pair" (who sent and who took) are the ground of the donor grids paper, Samuel's own work by hand: not restated, not audited, not touched.

## In short

(Written last; see the end of the file while this draft is open.)

## The ground: each file and what it does

| File | What it does |
|---|---|
| `site/app/events/page.tsx` | The index: nine cards, each with its window, grids and one figure, the highest (COVID-19: the lowest from the week of 2020-03-22) row of one variable in the window; under each, "Regions reached N of M" (`RegionsReached`); downloads; the link to the Flex Alert scorecard; the shared decisions. No address input: there is no default event, so the first card (Uri) is taken as the default |
| `site/app/events/uri-2021/page.tsx` | Uri, its own page (the first event, before the template): four charts on the 2021 calendar against 2019 and 2020 (ERCOT hub average real-time price, demand served, net generation, carbon intensity), seven picked figures, the event study (ERCOT's demand and the hub price), the whole country (Texas first), the decisions |
| `site/app/events/EventWindow.tsx` | The template of the seven later pages: the peak hour against the same weekdays 364 and 728 days earlier, all grids; per grid its daily highest hour with the two baseline years and one line (the peak against the baseline and its MW, the window's highest hour, the highest carbon intensity); carbon intensity, all grids; ERCOT's hub; other hubs. It picks rows and computes no value |
| `site/app/events/caiso-heat-2020/page.tsx` | CAISO 2020 on the template, with the bold sentence "Not on the outage days" (14 and 15 August against 18 August) and the Root Cause Analysis quoted |
| `site/app/events/elliott-2022/page.tsx` | Elliott on the template, six grids and ERCOT's hub; PJM against its report's 136,000 MW; ISO-NE "barely moved"; SPP's date that does not match |
| `site/components/EventStudy.tsx`, `site/lib/eventstudy.ts` | "What the estimates say": per grid a regression of daily demand served (and ERCOT's hub price) on the window, weekday and year effects, fitted at build time; the pooled effect and its 95 percent interval, the percent of the expected, the temperature-controlled estimate (degree days at 65 F and their squares at the grid's airports) and "the weather terms account for N percent"; each event day's effect for the lead grid |
| `site/app/events/WholeCountry.tsx`, `site/lib/countryfiles.ts` | "The whole country": EIA's thirteen regions over the window against the file's baseline: demand in GWh and percent, the highest hour and the baseline then, net imports (out of bounds), generation by source less the baseline, the pair table (out of bounds), charts of one or two regions; the index's "Regions reached" (5 percent from the baseline, either way) |
| `site/app/events/Decisions.tsx` | Fifteen decisions (thirteen on these pages), each with its default, source and session on hover |
| `site/data/regions/events/<event>.json` | The region files, built 2026-11-21 by the data machine from `eia930_region_hourly`, `eia930_region_fuel_hourly`, `eia930_region_pair_hourly` |
| `warehouse/derived/event_window.py` | `event_window_daily`: per event, entity and local day: demand served (sum, lowest, highest hour), net generation, carbon intensity (EIA's CO2 x 1000 over net generation), the comparisons with the baseline, ERCOT's hub prices, the stations' temperatures and degree days. Complete days only. The impossible-hours rule and California's hydro gap are written in and **held** (`impossible_hours.HELD`) |
| `warehouse/derived/event_study.py` | `event_study_estimates`, the Python twin of `lib/eventstudy.ts` |
| Notes | `docs/methods/events.md`, `event_study.md`, `impossible_hours.md` (the hydro gap), `regions_pages.md` |
| Inputs on this machine | `event_window_daily.csv` (run 20261019T094329Z, the build the replication of 16 November read), in the main copy's `warehouse/output`, read only; the region files in the worktree |

## The three views re-done, to the digit

`restate.py` reads `event_window_daily.csv` and the region files with none of the site's code and computes every figure from the rules as the pages and notes state them: each pick (the highest, the lowest, the named day; the earlier of equal values), each regression with numpy's least squares and its own HC1 (not the site's Gauss-Jordan), each region figure. `site/scripts/events-pages.mjs` draws the ten pages with the site's own components, once as a visitor's build draws them and once with the hold stood aside (`EVENTS_DRAW_UNHELD=1`, so the held figures are drawn as numbers to be compared). `compare.py` sets each drawn figure beside its restatement: it agrees when the restated value, rounded to the page's decimals, is the page's number and the raw values agree to 1e-9.

| View | Figures drawn and restated | Agree | Differ | Out of bounds (not compared) |
|---|---|---|---|---|
| `/events/uri-2021` | 246 | 246 | 0 | 101 (net imports, pairs) |
| `/events/caiso-heat-2020` | 213 | 213 | 0 | 99 |
| `/events/elliott-2022` | 275 | 275 | 0 | 101 |
| `/events`, the three cards and their "Regions reached" | 9 | 9 | 0 | 0 |

As a visitor's build draws them today, the hold of 21 October leaves 9, 0 and 10 of those figures as numbers on the three pages (ERCOT's hub prices and their estimates; the region section's figures are drawn as numbers too, outside the checked-number component) and every EIA-930 figure "license needed" (fault 1 of 16 November, a ruling, not repeated).

The figures a reader meets first, restated:

| Page | Figure | Restated |
|---|---|---|
| Index, Uri | highest 15-minute real-time price | 9,051.55 USD/MWh, 2021-02-17 |
| Index, CAISO 2020 | peak hour, highest against the baseline | 23.50 percent (23.4955), 2020-08-18 |
| Index, Elliott | PJM's highest hour | 135,328 MW, 2022-12-23 |
| Index | regions reached (5 percent) | Uri 9 of 13; CAISO 2020 2 of 13 (California, the Southwest); Elliott 10 of 13 |
| Uri | highest price, and the baseline's | 9,051.55 (2021-02-17); 1,691.63 (2020-02-10) |
| Uri | lowest hour of demand served; on 2021-02-15 | 27,719 MW (2021-02-24); 43,776 MW |
| Uri | largest day-to-day fall; largest shortfall against the baseline | -308,863 MWh (2021-02-15); -186,530.50 MWh (2021-02-21) |
| Uri | highest carbon intensity | 479.44 kg/MWh (2021-02-09) |
| Uri | event study, ERCOT demand | +155,794.96 MWh a day (53,420.68 to 258,169.25), 16.24 percent of 959,584.70; with temperature +30,283.66 (-28,962.93 to 89,530.26); "the weather terms account for 80.56 percent"; 54 days |
| Uri | event study, hub price | +2,293.84 USD/MWh (686.08 to 3,901.61), 9,850.47 percent of the expected; with temperature 287.79 |
| CAISO 2020 | the peak against the baseline; its MW; the window's highest hour; highest carbon intensity | 23.50 percent (2020-08-18); 46,643 MW; 46,643 MW; 305.93 kg/MWh (2020-08-18) |
| CAISO 2020 | 14 and 15 August | 10.74 and 21.58 percent |
| CAISO 2020 | event study | +83,812.35 MWh a day (46,905.66 to 120,719.05), 11.47 percent of 730,917.50; with temperature 24,746.88 (900.28 to 48,593.49); "70.47 percent"; 42 days |
| Elliott | each grid: the peak against the baseline (day, MW) | PJM 41.76 (12-23, 135,328); MISO 39.61 (12-23, 101,533); SPP 50.45 (12-23, 45,146); NYISO 17.18 (12-24, 22,004); ISO-NE 10.80 (12-24, 17,382); ERCOT 65.01 (12-23, 73,976) |
| Elliott | SPP's highest hour; on 2022-12-23 | 47,026 MW (12-22); 45,146 MW |
| Elliott | ERCOT hub: highest 15 minutes, highest daily mean, highest day-ahead hour | 3,701.72 (12-23); 557.53 (12-23); 2,539.16 (12-24) |
| Elliott | event study, PJM | +386,999.95 MWh a day (256,963.62 to 517,036.28), 17.73 percent of 2,182,817.32; with temperature 134,170.93 (24,428.52 to 243,913.35); "65.33 percent"; 33 days |

Every figure, its key, the page's text and the restatement: `compare.json`; the drawn pages' text, both ways: `drawn/`.

### One rule changed at a time

`measures.py`, on the same rows and files.

| Rule | The page | Changed to | Measured worth |
|---|---|---|---|
| Where the weather terms are fitted | the pooled regression, event days and baseline days together | the baseline days alone, as each day's estimate on the same block is fitted (the window's mean of those day effects) | Uri, ERCOT demand: with temperature +30,284 becomes -92,180 MWh a day, so "80.56 percent" becomes no share; Uri hub price 87.45 percent becomes 0.63; Elliott PJM +134,171 becomes +742,712, "65.33 percent" becomes no share; MISO 46.92 becomes 1.16; ERCOT 73.11 becomes 25.25; SPP 67.97 becomes 42.90; ISO-NE 62.97 becomes 25.58; NYISO 76.13 becomes 63.87; CAISO 2020 70.47 becomes 63.86 |
| The weather's range | event days at any degree days | only days inside the baseline days' range | Uri: 9 of 18 event days colder than any baseline day (heating degree days to 50.0 against 30.0); Elliott: PJM 6 of 11 (55.2 against 38.2), ERCOT 7, MISO 4, SPP 3, NYISO 3, ISO-NE 2; CAISO 2020: 8 of 14 hotter than any (cooling degree days to 22.0 against 13.8) |
| The window | the page's | the days its own account names: Uri the storm part of the window (14 to 17 February), CAISO the report's days (14 to 19 August), Elliott FERC's (21 to 26 December) | pooled effect on demand: Uri +155,795 becomes +269,649 MWh a day (16.24 to 28.43 percent); CAISO +83,812 becomes +135,437 (11.47 to 18.69); PJM +387,000 becomes +498,085 (17.73 to 23.28) |
| The peak measure on the outage days | each day's highest hour of CAISO's demand served, against its baseline days | California's net demand (demand less solar and wind, the region file; CAL holds CAISO and four smaller authorities), each day's highest hour | 14 August 54,390 MW at 18:00 PDT, 15 August 52,166, 17 August 51,456, 18 August 52,013, 19 August 50,210: by net demand the first outage day is the highest of the five. CAISO's own gross peaks: 46,024 (14th) against 46,643 (18th), 619 MW apart |
| California's hydro | net generation as EIA filed it (no hydro in CAISO's hours from 2019-10-01 to 2020-08-24) | the ERW's own rule (`impossible_hours.without_hydro_gap`, held) | every one of the window's 14 days of CAISO's carbon intensity is left out; the page's "highest carbon intensity" 305.93 kg/MWh and the carbon chart go. The window's mean is 281.32 kg/MWh against 204.95 (2018) and 184.98 (2019) on the baseline days, which hold hydro; the region file's California hydro is 1,273 MW in the window against 4,461 in the baseline (4.2 against 15.8 percent of net generation) |
| Uri's price | every interval as settled | the days the price did not move | 2021-02-16 to 18: the daily mean 8,970.14, 9,002.04, 8,989.10 USD/MWh against highest intervals of 9,000.85, 9,051.55, 9,006.13 (within 0.6 percent): the price sat at the market's ceiling for three days; the five days 15 to 19 February each touch it |

(The rest of the file is written as the branches are made.)
