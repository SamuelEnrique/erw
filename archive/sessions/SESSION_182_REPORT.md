# Session 182 report: parts (1) to (3), three finding cards

Run on 10 October 2026 (UTC), 16:22 to about 17:20, unattended, in the worktree `erw-144` on `wip/182-findings`
(`CHAIN_OCT10B_PROMPT.md`, session 182, parts (1), (2) and (3) only). Not pushed, not landed. No pull, no request to
any outside host, no model call (USD 0 of 0). Outputs under `runs/session182/`. Part (4), the one flow for requests,
is not in this branch: it is built by a later step on top of it.

## Read these first

- **Three cards more, each to session 170's standard**, computed on the data machine and committed with their CSV,
  Python, Stata do-file and two renders: "Batteries ate their own lunch? Five grids", "The peak hour moved: five
  grids", "By how much do batteries cut curtailment, hour by hour". The daily curtailment card gains the correlation
  coefficient (r = 0.30) and keeps its 32 other numbers to the last digit.
- **What the data said.** Lunch: only ERCOT shows spikes shrinking with its fleet (multiple 126.6x in 2019, 12.1x in
  2025; minus 10.76 per GW, p under 0.001). CAISO, with 17,094 MW, goes against the title in the two years held
  (3.3x in 2025, 26.0x in 2026 to date) and NYISO, with 269 MW, rose (8.8x to 20.9x). Peak hour: the evening share
  rose in ERCOT (24.9 to 71.0 percent) and also in NYISO (43.3 to 62.5 percent) on 2,886 MW of counted solar.
  Curtailment by the hour: minus 0.092 MW curtailed per MW charged with net load, hour and month held fixed (SE 0.011),
  but the residual in charging hours is above zero in 4 of 8 years; r = 0.39.
- **The cards are drawn on `/analysis` without a change to its page.** `/analysis` now draws ten cards: the two
  five-grid cards stand where the single-grid cards stood, and the two superseded cards are at the end of the list
  (dropping them from the list needs `site/app/analysis/page.tsx`, which this half does not touch;
  `SUPERSEDED` in `site/lib/findings.ts` is there for the later step). Every card is reachable at its own address.
- **CAISO, ISO-NE and SPP real-time prices are held from 2024-09-01 only**: their panels start there, one full year
  each (2025). The years in which California built its fleet are not on the chart, and the cards say so.
- **Two things that are not this session's, for the coordinator.** (a) The whole suite in this worktree is 2,911
  tests with 1 failure, `test_session156.TheNodeTests` (step 18 of `site/scripts/test-ask-ready.mjs`: Texas's
  curtailment share reads 4.46 where `site/data/curtailment/ercot.json` says 4.45); none of its inputs is in this
  branch's diff (`runs/session182/suite.out`). I did not run it at main's head, so "fails there too" is inferred
  from the diff, not observed. (b) `check-values.mjs` passed whole at 17:07 UTC and then failed on 2 values of
  `/learn/problems/networks-and-money` at 17:11 and 17:13 on the same build: the live rows changed under a built page.

## What to review (internal view first: `https://erw-flame.vercel.app/internal/open`)

1. **BATTERIES ATE THEIR OWN LUNCH? FIVE GRIDS**: `https://erw-flame.vercel.app/analysis/card/batteries_lunch_grids`
   - He should see five panels stacked on one month axis from 2019-01 (ERCOT, CAISO, NYISO, ISO-NE, SPP): a blue line
     (the worst-interval multiple) and a green shaded fleet; CAISO, ISO-NE and SPP begin at 2024-09. Under the chart,
     greyed: "MISO: paused while terms are reviewed", "PJM: licensed source needed".
   - The line above the chart states the axes: the measure on each grid's own scale, the fleet on one shared scale.
   - Hover 2021-02 on the ERCOT panel: every grid's value and fleet for that month ("not held" for the three short ones).
   - Click "Hours at or above USD 1,000/MWh": the panels change measure; the address gains `lunch_grid_measure=hours_ge_1000`.
   - Click "ERCOT": one large chart (the old ERCOT card's), callouts 126.6x to 12.1x, 26 to 2 hours, 87 to 18,204 MW,
     a three-row table (minus 10.76, minus 1.25, minus 1.93 per GW), one sentence and its caveat. The address is now
     `https://erw-flame.vercel.app/analysis/card/batteries_lunch_grids?lunch_grid=ercot`: open it in a new tab, ERCOT is shown.
   - Click "CAISO": 3.3x in 2025, 26.0x in 2026 to date; the caveat says 24 months leave 9 degrees of freedom.
   - Click "All grids": the address is clean again. Downloads and the two renders are under the paragraph.
2. **THE PEAK HOUR MOVED: FIVE GRIDS**: `https://erw-flame.vercel.app/analysis/card/peak_hour_grids`
   - Five panels on one year axis, 2019 to 2026: the percent of days peaking 17:00 to 21:59 and the solar fleet, both
     on shared scales (stated above the chart). Hover 2024 on CAISO: "CAISO: 39.7 % of days (121 days)", a partial year said as such.
   - Click "Median peak hour (local)", then "NYISO": the 24-hour chart for 2019, 2025 and 2026 to date, callouts
     hour 16 to 17, 43.3 to 62.5 percent, 525 to 2,886 MW. Address: `...?peak_grid=nyiso`.
3. **BY HOW MUCH DO BATTERIES CUT CURTAILMENT, HOUR BY HOUR**:
   `https://erw-flame.vercel.app/analysis/card/batteries_curtailment_hourly`
   - Three lines over the 24 Pacific hours of 2025: curtailed MW observed, what net load alone predicts, battery
     charging. Callouts: 925 predicted against 812 observed; r 0.39 and R2 0.16; 76 hours (2021) to 171 hours (2025)
     at the charging ceiling with curtailment on. The table has three rows: 0.23, minus 0.13, minus 0.09.
4. **The daily card**: `https://erw-flame.vercel.app/analysis/card/batteries_curtailment`: the paragraph now reads
   "Day by day the two correlate at r = 0.30 (R2 0.09, charging alone)"; nothing else moved.
5. **The old cards stay**: `.../analysis/card/batteries_lunch` and `.../analysis/card/peak_hour_moved`.
6. `https://erw-flame.vercel.app/analysis`: ten cards, in this order: lunch five grids, gas sets the price, queue,
   peak hour five grids, who rescues whom, negative prices, curtailment daily, curtailment hourly, then the two
   superseded cards. `https://erw-flame.vercel.app/data/methods/automated_analysis_findings`: findings 8 to 10.
7. Renders, for example `https://erw-flame.vercel.app/findings/batteries_lunch_grids_1600x900.png` (five panels side
   by side) and `.../findings/peak_hour_grids_1080x1350.png` (five rows).
8. On a phone (390 px): the five panels stack as rows of 120 px in a chart 358 px wide, each with a short title
   ("ERCOT: hub average, from 2019-01"); the controls wrap; no sideways scroll on any view.

## Card 1: what the data says

- **ERCOT (HB_HUBAVG, 15-minute, 2019-01 to 2026-10-08, 272,348 intervals).** Multiple 126.6x (2019) to 12.1x (2025);
  hours at or above USD 1,000 26 to 2; fleet 87 MW (2019-01) to 18,204 MW (2026-08). Regression: minus 10.76 per GW
  (SE 2.32, p under 0.001, 92 months, R2 0.25). Equal to the old card on all 33 numbers and all 102 CSV rows.
- **Against the title or flat.** CAISO (SP15, from 2024-09): 3.3x in 2025, 26.0x in 2026 to date, fleet 10,912 to
  17,094 MW; plus 1.02 per GW (SE 1.02, p 0.343, 24 months). NYISO (N.Y.C. zone, hourly, from 2019-01): 8.8x to
  20.9x, hours at or above USD 1,000 0 to 9, fleet 8 to 269 MW; plus 26.62 per GW (SE 12.58, p 0.038, 92 months), an
  extrapolation of four times its fleet. ISO-NE (internal hub, from 2024-09): 8.2x in 2025 (90.7 percent of the
  year's intervals held), 13.3x in 2026 to date, fleet 415 to 1,022 MW; minus 4.02 (SE 9.87, p 0.693). SPP (North
  Hub, from 2024-09): 40.2x and 32.7x, fleet 30 to 490 MW; plus 37.50 (SE 23.34, p 0.143).
- **Subtitle, chosen by the data:** "In Texas the spikes shrank as the fleet grew. No other grid shows it, CAISO with
  a fleet nearly as large included". The three 24-month regressions are printed as descriptions (9 degrees of
  freedom), not tests. Nothing separates a fleet from the years it arrived in.

## Card 2: what the data says

- **ERCOT.** Evening share (17:00 to 21:59) 24.9 percent in 2019, 71.0 in 2025; median peak hour 15 to 19; solar
  2,592 to 30,018 MW. Equal to the old card on all 59 numbers and all 384 CSV rows (ERCOT and CAISO).
- **NYISO moved too, on little counted solar.** 43.3 to 62.5 percent, median hour 16 to 17, solar 525 to 2,886 MW
  (EIA-860M counts plants of 1 MW and more: rooftops are outside it, so the card does not say how much is panels).
- **Flat or the other way on the short panels (2025 against 2026 to date).** CAISO 34.3 and 33.9 percent, median 17
  and 17, most common peak hour 6; ISO-NE 55.0 and 41.3, median 17 and 16; SPP 36.4 and 39.8, median 15 and 16.
  Subtitle: "The dearest hour walked into the evening in ERCOT and NYISO; NYISO counts 2,886 MW of solar, rooftops
  not in the count".

## Card 3: what the data says (CAISO, hourly, 2019-01-01 to 2026-10-02, 66,696 hours, 2,779 days)

- **The model.** OLS of hourly curtailment (MW, solar plus wind, `caiso_curtailment_intervals`) on charging MW;
  on charging, net load (GW) and its square; on those with 23 hour-of-day and 93 month-of-sample dummies; and the
  last without charging, whose fitted value is "what net load alone predicts". Net load is the sum of the thirteen
  sources of `caiso_fuel_supply_history` and `caiso_fuel_supply` less solar and wind. Errors are cluster-robust by
  Pacific day (2,779 clusters, Stata's `vce(cluster)` factor), because the hours of a day are not independent.
- **The numbers.** r = 0.394 (r squared 0.155, the R2 of charging alone). Per MW charged: plus 0.230 alone (SE
  0.012); minus 0.129 with net load (SE 0.010, R2 0.39); minus 0.092 with hour and month (SE 0.011, p under 0.001, R2
  0.45). Residual in charging hours: minus 113 MW in 2025 (925 predicted, 812 observed), plus 151 MW in 2026 to date,
  above zero in 4 of 8 years. 88.9 percent of curtailed energy falls in charging hours. The coefficient is an
  association: charging is chosen when prices are low, which is when solar is turned down.
- **The ceiling.** Against the trailing 30-day maximum (at 90 percent), hours at the ceiling with curtailment on:
  19 (2019), 32, 76, 99, 78, 142, 171 (2025: 171,897 MWh, 4.6 percent of the year's), 175 (2026 to 2 October:
  276,041 MWh, 5.5 percent). Against EIA-860M nameplate: 0 hours in the sample; the largest hour of 2025 was 9,289 MW,
  70.1 percent of the fleet. Both measures are on the card.
- **The daily card.** r = 0.304 (r squared 0.093) added to its numbers, paragraph, footnote, CSV header and do-file;
  rebuilt from its committed rows, `computed_at` unchanged; its CSV hash is now `21d62f1e...`, its two renders new.

## What is not held

- CAISO, ISO-NE and SPP real-time hub prices before 2024-09-01 (`iso_hub_prices_history` begins there).
- ISO-NE's zone history from 2019 is an internal table (`isone_zone_prices_history`) and is not used on a public card.
- SPP real-time before 2024-09 (`iso_zone_prices_history` holds SPP day-ahead only).
- An EIA-860M fleet figure after 2026-08: September and October 2026 carry none and are out of the regressions.
- Rooftop solar (plants under 1 MW) for any grid; CAISO's own load before 2021-09-17; charging by plant or node.
- MISO (paused) and PJM (licensed): placeholders on both cards, no row in any download, nothing requested.
- Stata was not run (none on the machine): the do-files are checked against the rules and their CSV's layout.

## What was built

- `warehouse/analysis/findings/batteries_lunch_grids.py`, `peak_hour_grids.py`, `batteries_curtailment_hourly.py`;
  `batteries_curtailment.py` (r; its do-file reads past the comment lines).
- `site/data/findings/`: three cards, the daily card, `catalogue.json` (ten findings).
- `site/public/findings/`: per card the CSV, `.py`, `.do` and two PNGs. `erw_2026_caiso_curtailment_hourly.csv` is
  2.97 MB (66,696 rows, 7 columns).
- `site/components/analysis/MultiChart.tsx` (small multiples, one grid large, the choice in the address);
  `site/scripts/check-findings-grids.mjs` (the cards in a real browser, both widths, both picture frames).
- `tests/test_session182.py` (41 tests); `docs/methods/automated_analysis_findings.md` (findings 8 to 10).
- **Shared files, lines added only:** `run_finding.py` (1 line), `site/lib/findings.ts` (8 lines),
  `site/app/analysis/card/render.css` (40 lines at its end), `catalogue.json` (3 entries at its end), the method
  note (40 lines, and 1 sentence of its License section extended). **One shared file changed:**
  `site/components/analysis/CardChart.tsx` (a 10-line file, now a dispatcher: 9 lines added, 1 changed).
- Not touched: `worker.py`, `site/app/analysis/page.tsx`, `view.tsx`, `api/analysis/route.ts`, `run_daily.sh`, the
  workflows, migrations, `release.ts` (the cards are under `/analysis`, which is `review`).
- The do-files' import form: `import delimited "<csv>", varnames(5) rowrange(6) stringcols(_all) clear` (names on
  line 5, data from line 6, past four `#` lines), on the three new ones and the daily card's.

## Pulls and model spend

- Requests to outside hosts: 0. Model calls: 0. Spend: USD 0 of 0.
- Reads: the main copy's `warehouse/output` with `--in-dir`, read only. Supabase: the checks' anon reads only.

## Checks (each run alone, exit code read; outputs in `runs/session182/`)

- `npm ci`: exit 0 (`npm_ci.out`). `npm run build` on the final tree, under the mutex: exit 0 (`build.out`).
- `tests.test_session182`: exit 0, 41 tests (`test182.out`). `test_session170` exit 0 (29), `173` exit 0 (9), `174`
  exit 0 (9) (`test170.out`, `test173.out`, `test174.out`).
- The whole suite (`python -m unittest discover -s tests`): exit 1, 2,911 tests, 1 failure, not of this session
  (see the top) (`suite.out`). It ran before the last wording commit; the four modules above ran after it.
- `render-cards.mjs` for the four cards: exit 0, 8 pictures, no font fallback (`render.out`).
- `check-findings-grids.mjs`: exit 0, 163 of 163 (`check_findings_grids.out`; pictures in `shots/`).
- `check-analysis.mjs`: exit 0, 233 of 233 (`check_analysis.out`).
- `check-csp.mjs`: exit 0, 83 pages, 0 enforced and 0 report-only violations (`check_csp.out`).
- `check-routes.mjs`: exit 0 (`check_routes.out`). `check-security.mjs`: exit 0, 46 of 46 (`check_security.out`).
- `check-values.mjs`, whole, on the final build, three runs. First (17:07 UTC): exit 0, 6,926 of 6,957 match, 31
  latest prices superseded, 0 failed (`check_values_1.out`). Second (17:11) and third (17:13): exit 1, 6,924 match,
  the same 2 values failed both times, on `/learn/problems/networks-and-money` (`net|ties|ERCO|2026-10-09T03:00:00Z`:
  page 1, Supabase 2; `net|maxflow|ERCO|...`: page 526, Supabase 812) (`check_values_2.out`, `check_values_3.out`).
  The same build passed them four minutes earlier, so the live rows behind that page changed at about 17:08 UTC and
  the built page still holds what it read; nothing of that page or its table is in this branch. Not a failure of
  these cards; it is for the coordinator to read at the landing. On an earlier build of this session a first run
  failed on 15 values of the battery page's current month and they passed on the next build (the stale fetch cache
  COMMON.md names).
- `scripts/test-render-fonts.mjs`, named in `render-cards.mjs`, is not in the repository: the font proof is
  `tests/test_session170.py`'s, which passed.

## Decisions made without you

- **ERCOT's hub is HB_HUBAVG**, the old card's, not the North Hub the session's note named: the test that the ERCOT
  numbers equal the old card's governs.
- **NYISO is read hourly from 2019** (`iso_zone_prices_history`) and not as 15-minute prices from 2024-09: seven full
  years against one. Its level is not comparable with the 15-minute grids, said on the card.
- **A full year** holds 90 percent of its intervals (card 1; ISO-NE's 2025 holds 90.7) or 300 days (card 2, the old
  card's own rule). A grid with one full year is compared with the year to date, labeled so.
- **Axes:** card 1 the measure on each grid's own scale and the fleet shared; card 2 both shared. Stated on the chart.
- **The old cards were not recomputed:** their tables have not changed since they were computed, and the new cards
  equal them as committed. They move to the end of the list and are not removed.
- **The words:** the peak card's first subtitle read New York's shift as "panels are not the whole story"; the design
  does not carry that (rooftops are uncounted), so it now states the count. Titles keep the old cards' with ": FIVE
  GRIDS".
- **Card 3 was built by a second agent of this session** (a fork, same worktree, no commit of its own); its tests are
  in `tests/test_session182.py` under the `C3` names; notes in `runs/session182/card3_notes.md`.
- The daily card's do-file was corrected to the new import form because this session touches that card.

## For the coordinator

- Nothing under the data lock. No migration. No table written. No request to approve.
- Merge: `wip/182-findings` (last commit below) onto the branch that holds session 181. Expected overlaps:
  `site/data/findings/catalogue.json` (keep both sets of entries; `run_finding.py --list` rewrites it, and
  `test_session170` wants its ids equal to `FINDINGS`), `run_finding.py` (my one `FINDINGS +=` line), and
  `CardChart.tsx` or `findings.ts` if session 181 edited them.
- After the merge, in order: `npm run build` (mutex); `python -m unittest tests.test_session182 tests.test_session170
  tests.test_session173 tests.test_session174`; start the server; `node site/scripts/check-analysis.mjs <base>`;
  `node site/scripts/check-findings-grids.mjs <base>`; `node site/scripts/render-cards.mjs <base> --only
  batteries_lunch_grids,peak_hour_grids,batteries_curtailment_hourly,batteries_curtailment` only if a card's JSON or
  the card component changed in the merge (the pictures are committed).
- Rule 8 at the landing: `/analysis` and its cards are in review; no live page reads anything this branch changes,
  so the snapshot comparison should list 0 differences.
- **The Roundup's restore grows:** `run_finding.py --tables` now also names `iso_zone_prices_history`,
  `eia930_daily_demand`, `caiso_curtailment_intervals` and `caiso_fuel_supply_history` (about 500 MB together), so
  Sunday's `roundup.yml` restores them on the runner. A failed restore does not stop the Roundup. If that is not
  wanted, the three cards can be left out of `--tables`: a change to `run_finding.py`, not made here.
- Part (4) builds on this branch: `SUPERSEDED` (findings.ts) says which cards the flow should offer in place of
  which; the three new findings are in the catalogue, so the request form already lists them.

## To finish

- Nothing held from parts (1) to (3).
- At the landing, on a fresh build: `node site/scripts/check-values.mjs <base>` (twice if the first differs). The two
  values of `/learn/problems/networks-and-money` above should match once the page is built after the rows changed;
  if they still differ, it is that page's question, not these cards'.
- The one failing test of the whole suite (`test_session156`, Texas's curtailment share 4.46 against 4.45) fails
  without this branch's files; it wants a look before a `task/` push runs the suite on GitHub.

## Part (4)

## The landing
