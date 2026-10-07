# Session 144 report: Curtailment, one page

Run on 7 October 2026 (UTC), unattended, in the chain 140 to 145. The page is at `/curtailment`, locked for visitors
(`review`); `/curtailment/v2` redirects to it. Three agents built it to written briefs (the data, the Texas pull, the
page); I wrote the tables under the lock, merged, checked and landed it.

## Five things to know first

- **"Texas, years not days" cannot be met as you wrote it.** ERCOT openly publishes the high sustained limit for
  about nine days only, system-wide; by region it publishes output and no limit; the reports' history sits behind an
  account. Held: 219 hours from 28 September 2026, growing daily from now. No estimate by month, by year or by region
  exists, and none was made up from installed capacity or a forecast. The yearly workbooks of hourly output (2023 to
  2025, no limit) were pulled as well.
- **The months that read "not computable" were not the ones named.** They were December 2019 and January to
  September 2026 (the daily report's output had been read for only 9 to 29 days a month). All ten now have a share,
  from CAISO's own Today's Outlook supply by fuel. CAISO: 149 of 149 months.
- **CAISO's two output sources disagree in 2026**, by 11 to 20 percent a month for solar. Today's Outlook is above the
  Daily Renewable Report on the same days; in 2025 Today's Outlook and CAISO's workbook agreed within 1 percent. The
  shares rest on Today's Outlook. Which is CAISO's settled figure is open, and it is said in the Method note.
- **The "small map" is a schematic, not a map.** No hub or zone coordinate is held anywhere in the warehouse, and
  none was invented: the places are tiles shaded by their count, captioned as a schematic. A true map needs a person
  to choose the points.
- **ISO-NE publishes a monthly series and it was not pulled; NYISO publishes none as data.** ISO-NE's file ("Aggregate
  Monthly DDG Undelivered Energy", yearly workbooks, no login) sits under the legal notice you have twice ruled on;
  about 1,000 rows, USD 0, needs your ruling. NYISO prints a monthly figure in a PDF report only.

## Verdict: ready to open, for what it holds. What is left, exactly

1. **Your ruling on ISO-NE's monthly file** (pull and show, pull and hold, or leave).
2. **A true map**: someone chooses a point for each hub and zone, or the schematic stays.
3. **Texas fills by itself from now**: the daily run reads ERCOT's list each day (scheduled tonight; the runner
   restores the table first). October 2026 is the first month that can reach 95 percent of its hours. The history
   before 28 September 2026 needs ERCOT's archive, which needs an account.
4. **The page's three computed files (shares, free energy, worth) are rebuilt on a data machine, not on the runner**:
   the runner holds no price history and would thin them. Not scheduled. Commands under "To finish".
5. **SPP's worth and its battery comparison read "not held yet"**: SPP's curtailment is held by day, and the
   five-minute files were not kept.
6. `check-values` shows 5 values that differ from Supabase, none on this page (four catalogue counts on the home
   page, one figure on `/deals`); session 138 reported the same kinds of difference.

## What each old page showed, and where it is now

**`/curtailment` (session 18): nothing dropped.**

- The lead; the daily chart of the last 90 days (now a chart that answers the mouse, for the grid chosen); the total
  over those days with its checked numbers; the monthly chart (all months, with the share on a second axis); the
  13-month table with its checked numbers: all kept.
- "% of available output" over the 90 days: replaced for CAISO by the share of the months (one definition; the old
  figure rested on the daily report's output and overstated). Kept for ERCOT as "percent of the limit".
- "not computable": gone. A month without a share reads "not held yet" with its reason on hover.
- Each grid's paragraph of meaning, the MISO paragraph, the paragraph on NYISO, ISO-NE and PJM: moved whole into the
  Method note. The face keeps one line per grid saying what its number is.

**`/curtailment/v2` (session 98): nothing dropped.**

- The period chooser; the summary sentence; the three headline numbers; curtailment by hour of the day; by month
  from the five-minute record; by reason, with the two tables; against battery charging (three numbers, the average
  day, the months): all kept, each chart answering the mouse.
- "The data does not say where", the two folds of method and every chart note: moved into the Method note.
- Both old page files are kept, not routed. `/curtailment/v2` answers 308 to `/curtailment` with its query.

## What is new

- **(b) Every share.** A month's share is curtailed energy over curtailed plus wind and solar output, over the days
  both are held, written only when those days hold 95 percent of the month's hours. CAISO 149 of 149 months (2026 so
  far 6.79 percent; April 2026 the highest, 15.81). SPP 97 months from September 2018, on EIA-930's hourly output
  (2024: 12.36 percent; April 2024 the highest, 18.82); 54 earlier months read "not held yet" (EIA-930 has no
  generation by source before July 2018).
- **(c) Texas.** The ERW's estimate for the nine whole days held: 183,816 MWh below the limit of 4,020,917 MWh, 4.57
  percent (wind 5.31, solar 3.54); by hour and by day; output by ERCOT's five wind and six solar regions ("no limit
  published" for an estimate by region); output by year 2023 to 2025.
- **(d) Where free energy is** (`#free-energy`): 39 hubs and zones of five grids; hours below zero and under USD 5 in
  the last month and the last twelve months; the hour-of-day by month heatmap of the place chosen; the schematic
  tiles; the gap between the cheapest and dearest place. The summary sentence calls out West Texas against Houston
  and California north against south.
- **(e) What it is worth** (`#worth`): curtailed energy at the hub's price of its hours; what a flat load paid in
  those hours against all hours; a battery of 2, 4 or 8 hours against what the fleet charged. California in full;
  Texas for its nine days, labelled the ERW's estimate; SPP "not held yet".
- **(f)** NYISO and ISO-NE checked (above). PJM "licensed source needed"; MISO "paused while terms are reviewed": named,
  not selectable, no number, no request.
- **(g)** One line per grid on the face; every caveat in the Method note (`docs/methods/curtailment.md`, 75 to 166
  lines). A test reads the face for method words.

## Every pull against its ceiling

| Pull | Ceiling | Read | Kept |
|---|---|---|---|
| ERCOT's hourly wind and solar reports | 2,000,000 rows | **59,088** (3 percent); 35 requests, 11.9 MB | `ercot_wind_solar_hsl_hourly` 3,285 rows (219 hours); `ercot_wind_solar_output_hourly` 52,608 rows (2023 to 2025) |

- **No other pull.** ISO-NE's monthly file was not pulled. A research step downloaded its two 2026 workbooks into a
  scratch folder to read their columns; nothing of them is in the repository or the warehouse.
- **No MISO request. No PJM request.**
- Terms: ERCOT's ("raw data provided in public portions of this website may be used, reproduced, and redistributed in
  compilations, charts, and analyses without maintaining such notices."); NYISO's and ISO-NE's notices are quoted in
  the Method note with what each publishes.
- The hourly table summed by day equals the daily table within 0.12 MWh on sums near 200,000 (ERCOT's two reports
  print output 0.01 to 0.02 MW apart).

## Model spend: none

- No model call. No cap was set for this session.

## The landing

- **Freeze: on**, ending today; the chain's prompt names the landing. `/curtailment` stays `review`.
- The whole suite passed in a clean copy of the merged branch (1,755 tests). Checks passed (run 37613688730); merged
  as `b128930`. It also carries session 143's report to main.
- **Vercel built it:** "Deployment has completed" for `b128930` at 11:31:22 UTC.
- **Snapshot before** (`144_before`, 11:22:38 UTC) **and after** (`144_after`, 11:31:40 UTC): **0 differences** on the 25
  live addresses, 3,357 checked number keys. No number moved on `/cost-of-power/battery`, `/network` or `/storage`.
  Nothing was reverted.
- **On production, in the internal view, the page's check passes 102 of 102** (HTML and a real browser), and
  `/curtailment/v2?period=2024-04` answers 308 to `/curtailment?period=2024-04`.
- No shared component, token or file that the three live pages read was changed. `iso_curtailment_monthly` gained its
  share rows on this machine and in the Redivis draft; nothing was loaded into Supabase by this session, and only
  `/curtailment` reads that table.

## Checks

- `tests/test_session144.py` 22 tests, `test_session144_ercot.py` 21, `test_session144_page.py` 21, on saved real
  samples: the monthly sums equal the daily sums; a share never exceeds 100 percent; a negative-price hour is counted
  once (in "under 5" and in "negative", once each; an hour held in two tables read once); a month under 95 percent
  writes no share; MISO has no number.
- `site/scripts/test-freeenergy.mjs`: 56 assertions on the three real files.
- `site/scripts/check-curtailment.mjs`, HTML and a real browser, on the final local build of the merged branch: 102
  of 102 (16 chart tooltips, a tile's hover and click, the redirect, a visitor sees the in-review page).
- `check-routes`: 8 live pages and 125 in review asked as a visitor, 0 failed.
- The whole suite in a clean copy of the merged branch: 1,755 tests, passed.
- The validator on the three tables written: exit 0. Coverage, the archive and the Redivis drafts: exit 0, row counts
  equal. Nothing released. Nothing loaded into Supabase by this session.

## The five most interesting numbers

1. **California's curtailed energy in 2026 was worth less than nothing where it was made.** 5.12 TWh in nine months,
   valued at SP15's real-time price of its own hours: minus USD 31.5 million, 81.5 percent of it in hours priced
   below zero. The same energy at NP15's prices: plus USD 20.4 million.
2. **April 2026: California curtailed 15.81 percent of its available wind and solar (1.46 TWh), its highest month,
   while its batteries took in 1.54 TWh in the same hours.** A 4-hour fleet on a simple rule could have absorbed 67.7
   percent of what the fleet actually charged in those hours; an 8-hour fleet 93.5 percent.
3. **West Texas: 1,503 hours under USD 5 in twelve months at the load zone (908 below zero) against Houston's 280.**
   The West hub had 1,678. In ERCOT the West hub is the cheapest of eight places (30.66) and the West load zone the
   dearest (35.27): a load there pays the zone, and a generator earns the hub.
4. **SPP curtails a larger share than California**: 12.36 percent of its available wind and solar in 2024 against
   CAISO's 4.47, and 18.82 percent in April 2024.
5. **New York's cheapest and dearest zones are USD 12.94 per MWh apart over twelve months** (West 60.16, New York
   City 73.10, day-ahead), three times the gap inside ERCOT (4.61) or California (4.79), with almost no cheap hours
   anywhere in it (17 under USD 5 in the city).

## Things that look implausible, flagged and not changed

- Texas solar output stands above the system-wide limit every morning (44 of 219 hours, up to 2,921 MW) and below it
  every evening: 29,190 MWh above against 59,578 below. Part of the solar estimate may be timing, not curtailment.
- The report type 13483 that the daily connector calls NP4-745-CD is NP4-737-CD; the source registry's row carries
  the same slip. Not changed in the older connector.
- CAISO's two output sources in 2026 (above).

## Decisions made without you

1. The shares for 2026 rest on Today's Outlook, not on the daily report's output.
2. The yearly workbooks of output were pulled although they hold no limit (the only open hourly output before 2026).
3. The page shows one grid at a time (the old page stacked three); the grid, period, place, window and battery
   duration are in the address.
4. The gap compares hubs and load zones together, as the prices are held.
5. A year's share is computed on the page from the months' own megawatt-hours, by the same definition.
6. The daily run now reads ERCOT's hourly reports each day and rebuilds the Texas file; the runner restores the table
   first (ERCOT lists a week: a lapse loses hours for good).
7. Built in a working copy of its own; its tables written from the main copy under the lock.

## To finish

```bash
# on a data machine, when a price table or a curtailment table has grown (no lock; site files only):
python warehouse/derived/curtailment_shares.py
python warehouse/derived/free_energy.py
python warehouse/derived/curtailment_worth.py
python warehouse/derived/ercot_estimate_page.py
cd site && node scripts/test-freeenergy.mjs
```
