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

Second half of session 182, 10 October 2026, branch `wip/182-flow` (worktree `erw-144`), from main at `1885332c`. No
request to any outside host, no model call (USD 0 of 0), no migration, nothing under the data lock, nothing pushed.
Outputs under `runs/session182/`, every file prefixed `flow_`.

### Read these first (part 4)

- **One flow, two steps, on `/analysis` under "Ask for an analysis".** It takes the place of "Ask for a finding", of
  the impact study's own section and of "Template gallery". Step one lists 18 entries: 7 findings (3 of them with two
  versions, so 10 of the catalogue's 11 ids), the impact study (the 11th id), and the 10 weekly templates.
- **A template is not a request.** The weekly run already computes each public template for every choice of its
  inputs (647 combinations, 301 of them with data, last run 2026-10-05). The flow shows that result at once, in the
  chosen form, and says that nothing is queued. Chosen, not on demand: the worker and `run.py` are untouched, and
  Sunday's Roundup reads exactly what it read.
- **The tenth template is listed and not drawn.** Chokepoint transits reads a table licensed internal (session 8's
  ruling). It was never in the gallery: the page named it in one sentence. The flow lists it with its three inputs
  and its method, and says why no chart is drawn. So "each of the ten templates reachable and drawn" holds for nine;
  the tenth is reachable and, by its license, not drawn.
- **The chart form travels in the address, not in the queue.** No migration 030, no change to the route or the
  worker. A request carries what it carried. A card already computed is re-shown in another form with no new request.
- **The word on the page is "Default for this analysis"**, never "recommended": see "Decisions made without you".

### What to review (internal view first: `https://erw-flame.vercel.app/internal/open`)

`https://erw-flame.vercel.app/analysis`, then scroll to "Ask for an analysis" (or open
`https://erw-flame.vercel.app/analysis#ask`).

1. **Step 1: what to analyze.** Three groups of buttons: Findings (7), Impact study (1), Weekly chart templates (10).
   The first is pressed: "Batteries and price spikes (Batteries ate their own lunch?)". Under them, "Inputs": a
   "Version" choice (Five grids (current); One ERCOT hub (the earlier card)) and "First year".
2. **Step 2: how to show it.** Previous, Next, "1 of 2: Small multiples". Two tiles, each a small live drawing of the
   committed card: "Small multiples" (pressed, labeled "Default for this analysis") and "Lines". Hover a drawing: it
   reads values.

**Worked example 1: a finding in a form that is not its default.**

1. Press "How often gas sets the price (Gas sets the price less often?)". Inputs appear: Heat rate 7, First year 2019.
2. Step 2 shows three tiles: "Paired bars" (pressed, "Default for this analysis"), "Lines", "Small multiples".
3. Press **Next**. The counter reads "2 of 3: Lines", the Lines tile is pressed, "Back to the default" appears, and
   the address ends `?analysis=gas_sets_price&form=lines`.
4. Press **"Show the card computed 2026-10-10"**. The card "GAS SETS THE PRICE LESS OFTEN?" is drawn as lines. Its
   callouts are unchanged: ERCOT 2019 38.8%, 2025 40.9%; ISO-NE 2019 18.6%, 2025 5.5%. Hover 2021: ERCOT 52.0
   percent of hours, ISO-NE 16.2. CAISO, NYISO and SPP are single points at 2026 (their earlier years are not held).
5. Press **Next** again: "3 of 3: Small multiples", five panels, the same values. No request was made.
6. Reload the page: the same analysis, the same form. Copy the address to share the view.
7. To ask for inputs that are not computed: set Heat rate to 8 and press **"Ask the warehouse"**. The note reads
   "queued at ... (request ...)", the address gains `request=<id>`, the request appears in "Requests" below, and the
   card arrives under the button, drawn in the chosen form, in about a minute while the worker runs.
8. "The card's own address, in this form" opens `https://erw-flame.vercel.app/analysis/card/gas_sets_price?form=lines`:
   the card alone, with a row "Shown as" (Paired bars (default), Lines, Small multiples).

**Worked example 2: a template folded in.**

1. Press "Day-ahead minus real-time, by hour" under Weekly chart templates.
2. Inputs: Grid ERCOT, Hub ERCOT North Hub, Window (days) 30. Under them: "Computed by the weekly run for every choice
   of these inputs (last 2026-10-05), from public tables only: the chart is shown at once and no request is queued",
   then the template's method. There is no Ask button.
3. Step 2: two tiles, "Paired bars" (default) and "Lines", each drawn from this hub's own weekly chart.
4. The chart is below at once: "ERCOT HB_NORTH: day-ahead minus real-time by hour", its two facts (highest in the
   hour starting 21:00, 10.57 USD/MWh; lowest at 18:00, -12.67 USD/MWh), its source line, "Computed 2026-10-05
   01:28:09 UTC by the weekly run", and a link to the chart's data (JSON).
5. Press the **Lines** tile: the same 24 values as a line. The address ends
   `?analysis=template%3Ada_rt_spread_by_hour&i.iso=ercot&i.hub=HB_NORTH&i.window=30&form=lines`.
6. Set Grid to CAISO: the hub moves to CAISO NP15 (the first CAISO hub that holds a chart) and the chart follows.
   The hub list holds every hub the gallery listed for CAISO, the three that hold a chart first, the rest marked
   "(not held)". Pick one of those: the page prints the weekly run's reason and draws nothing.

**Also look at.**

- "Impact of an event on a series": its own inputs (series, control, event or date, window), then step 2, then "Ask
  the warehouse" and Reset. Forms: Lines (default), Paired bars, Small multiples; the days after the event stay shaded.
- "Tanker transits at the chokepoints (internal: not drawn on the site)": three inputs listed, the method, no chart.
- "Findings" now shows 9 cards, not 11. Under "BATTERIES ATE THEIR OWN LUNCH? FIVE GRIDS" and under "THE PEAK HOUR
  MOVED: FIVE GRIDS" a line links the earlier single-grid card (`/analysis/card/batteries_lunch`,
  `/analysis/card/peak_hour_moved`). Each card with more than one form has a row "Shown as".
- "Requests": the list as it was, with "show the card". "Found by the scanner", "This week's results" and "Archive:
  the chart of each week" are unchanged.
- On a phone (390 px): step one is one column of buttons; the tiles stand two to a row; Previous and Next are above
  them; every press target is at least 44 px high; nothing scrolls sideways.

### The ten templates

| Template | Where it was | Where it is now | What it offers now | Proof it is reachable |
|---|---|---|---|---|
| Peak premium by time of day | Template gallery, first choice | Step 1, Weekly chart templates | Grid, hub, window: 154 combinations, 60 with data. Paired bars (default), small multiples | `flow_check_flow_final.out`: "peak_premium_block: reachable, with the gallery's inputs at their defaults"; drawn in 2 forms with the weekly file's data |
| Day-ahead minus real-time, by hour | Template gallery | same group | Grid, hub, window: 192, 76 with data. Paired bars (default), lines | same file, `da_rt_spread_by_hour`; also the CAISO choice and a choice not held |
| Demand forecast error | Template gallery | same group | Balancing authority, window: 16 of 16. Lines (default), paired bars | same file, `forecast_error` |
| Curtailment against midday prices | Template gallery | same group | Hub, window: 6 of 6. Points (the only form) | same file, `curtailment_midday` |
| Implied heat rate | Template gallery | same group | Grid, hub, window: 78 of 78. Lines (default), paired bars | same file, `implied_heat_rate` |
| Batteries and the evening peak | Template gallery | same group | Window: 2 of 2. Lines (default), small multiples (two units, never paired) | same file, `storage_evening_peak` |
| Negative-price hours by month | Template gallery | same group | Grid, hub, months: 192, 56 with data. Paired bars (default); lines once two months are held (one month is held today) | same file, `negative_price_hours` |
| Deals by month and type | Template gallery | same group | Months, deals counted: 4 of 4. Stacked bars (default), lines, paired bars | same file, `deals_by_month` |
| Datacenter facilities by state | Template gallery | same group | States shown: 3 of 3. Stacked bars (default), paired bars, small multiples | same file, `datacenters_by_state` |
| Tanker transits at the chokepoints | Not in the gallery (internal): one sentence under the week's results | same group, marked internal | Its three inputs and its method, listed. Not drawn: license | same file: "the tenth template (chokepoint transits) is listed with its three inputs and its method, and is not drawn: internal" |

- Every combination is choosable: `test-analysis-flow.mjs` walks all 647 and reaches each (`flow_node_test_final.out`).
- Kept from the gallery: the title, the subtitle, the facts, the source line, the computed time, the method sentence,
  the chart's PNG button (the chart's own toolbox). Added: a link to the chart's data (JSON). The gallery had no
  other download.
- The weekly recomputation is untouched: `git diff 1885332c -- warehouse .github docs/analysis site/next.config.ts
  site/lib/release.ts site/app/api` is empty. The week's results table and the archive stay on the page.
- The gallery was a section of `/analysis`, never an address: no redirect, no line added to `next.config.ts`, and
  `release.ts` is unchanged (`/analysis` stays `review`).
- `AnalysisGallery.tsx` moved to `site/app/_retired/analysis-gallery/` (nothing imports it).

### The forms and the default rule

- Five forms (`site/lib/chartforms.ts`): Lines, Paired bars, Stacked bars, Small multiples, Points with a fitted line.
- **Fit rule.** Lines: an ordered axis (months, years, days, hours) with two positions or more; series in different
  units only in the analysis's own drawing. Paired bars: one unit, at most 31 positions. Stacked bars: parts of one
  whole. Small multiples: two to six series or grids. Points: pairs of two measures, and then no other form. A
  scanner draft (a flagged point, reference lines) keeps its own form.
- **Default rule.** The form the analysis's own code declares, its chart kind: a timeline or the hours of a day as
  lines, groups side by side as paired bars, parts of a whole as stacked bars, many grids as small multiples, two
  measures of each day as points. For a template: the form the weekly run drew.
- What each analysis is offered, default first:

| Analysis | Offered |
|---|---|
| Batteries ate their own lunch, five grids | small multiples, lines |
| the same, one ERCOT hub | lines, small multiples (three units: never paired bars) |
| Gas sets the price | paired bars, lines, small multiples |
| Till queue do us part | stacked bars, paired bars, small multiples (technologies are not an ordered axis: no lines) |
| The peak hour moved, five grids | small multiples, lines, paired bars |
| the same, ERCOT and CAISO by hour | lines, paired bars, small multiples |
| Who rescues whom | paired bars, small multiples |
| Negative prices march west | lines, paired bars, small multiples |
| Batteries and curtailment, day by day | points |
| the same, hour by hour | lines, paired bars, small multiples |
| Impact study | lines, paired bars, small multiples |

- The rules are in the Method note (`docs/methods/automated_analysis_findings.md`, "The request flow and the chart
  forms"), stated a second time in Python in the test, and read from the site's own code by the browser check.
- In its default form a card is drawn by the code that drew it before. In another form the same values are redrawn;
  a card of many grids then shows one measure at a time (a row of toggles), and the hover names series, value and
  unit without the extra counts of the default's hover.

### What a request carries

- The queue row is what it was: the finding and its inputs (`POST /api/analysis`, migration 027). The check against
  the stand-in reads the queued row: no `form` in it.
- The address carries the rest: `analysis`, `version` (where an analysis has two), `i.<input>` (a finding's inputs
  that are off their defaults; all of a template's), `form` (when it is not the default), `request` (once asked),
  `card=1` (the committed card shown in the flow).
- On a card's own page the form is `?form=<form>`; on a card of a list it is `form.<card id>=<form>`.
- A form that does not fit a card that arrives (an impact study of two series in different units, asked as paired
  bars) is not forced: the card is drawn in its own form and a line says so.
- When the machine is off: the page says the request stays queued with the time it was asked and runs when the
  machine wakes, as before. A queued request is shown as "queued: it waits for the data machine", never as running.

### What was built (part 4)

- New: `site/lib/chartforms.ts`, `site/lib/analysisflow.ts`, `site/components/analysis/RequestFlow.tsx`,
  `FormPicker.tsx`, `FormChart.tsx`, `FlowHost.tsx`, `site/scripts/check-analysis-flow.mjs`,
  `site/scripts/test-analysis-flow.mjs`, `tests/test_session182_flow.py`.
- Changed: `site/app/analysis/page.tsx` (the flow, the list of requests, the superseded cards out of the list and
  linked), `site/app/analysis/card/[id]/page.tsx` (`?form=`), `FindingCard.tsx` (the chart in a chosen form; the
  renderer's frame keeps the old markup, so no picture changes), `ImpactForm.tsx` (hosted by the flow; 44 px buttons),
  `RequestForm.tsx` (`listOnly`: the list of requests alone), `site/scripts/check-analysis.mjs`,
  `tests/test_session170.py` (one path: the gallery component moved), the Method note, `docs/platform-tools.md` (one
  sentence in tool 26's row).
- Moved: `site/components/AnalysisGallery.tsx` to `site/app/_retired/analysis-gallery/AnalysisGallery.tsx`.
- Not touched: the worker, `run_finding.py`, `run.py`, `watch.py`, the templates, the route, the workflows,
  `next.config.ts`, `release.ts`, `site/app/network/`, `site/app/cost-of-power/`, `run_daily.sh`, the scanner.

### Checks (part 4; each run alone, exit code read; outputs in `runs/session182/`)

- Site build (mutex): six builds. `flow_build1.out` exit 1 (a type error in my new file, fixed); `flow_build2.out` to
  `flow_build6.out` exit 0. Every check below ran on the sixth. `tsc --noEmit`: exit 0 (`flow_tsc3.out`).
- `python -m unittest tests.test_session182_flow`: exit 0, 19 tests (`flow_test_flow_final.out`).
- The neighbours with it (`test_session170`, `173`, `174`, `181`, `181_worker`, `182`, `182_flow`): exit 0, 184 tests,
  3 skipped (`flow_test_neighbours_final.out`).
- The whole suite (`python -m unittest discover -s tests`): exit 0, 3,008 tests, 220 skipped (`flow_test_suite1.out`).
- `node scripts/test-analysis-flow.mjs`: exit 0, 180 of 180 (`flow_node_test_final.out`): every form drawn for every
  card it fits with the card's own numbers, every template's forms with the weekly file's data, all 647 combinations.
- `node scripts/check-analysis-flow.mjs http://localhost:3183` (real browser, the real read path): exit 0, 225 of 225
  (`flow_check_flow6.out`). With `--stub 54383` against the stand-in: exit 0, 233 of 233 (`flow_check_flow_final.out`):
  the same, and the queue. Runs 1 to 3 (`flow_check_flow1.out` to `3.out`) exit 1, each on one fault: the impact
  study's picker was not drawn (a cloned element; now a context), a selector of mine, and a hub kept across a change
  of grid (now moved).
- `node scripts/check-analysis.mjs`: exit 0, 261 of 261 (`flow_check_analysis3.out`). Runs 1 and 2 exit 1, 259 of
  261: my new assertion asked the server's HTML for a link that the browser draws in the internal view. The
  assertion now reads the line and the title there; the link is proven in the browser by the flow check. No number
  check was weakened: the two superseded cards are read at their own addresses with the same assertions.
- `node scripts/check-findings-grids.mjs`: run 1 exit 1, 160 of 163 (`flow_check_grids1.out`): three render frames
  had grown, because a wrapper of mine broke `render.css`'s sibling selectors. Fixed (the frame keeps its markup).
  Run 2 on the sixth build: exit 0, 163 of 163 (`flow_check_grids2.out`).
- `node scripts/check-internal-findings.mjs http://localhost:3183 54383` (stand-in): exit 0, 114 of 114
  (`flow_check_internal1.out`), unchanged.
- `node scripts/check-security.mjs`: exit 0, 48 of 48 (`flow_check_security1.out`).
- `node scripts/check-csp.mjs`: exit 0, 84 pages, 0 enforced and 0 report-only violations (`flow_check_csp1.out`).
- `node scripts/check-routes.mjs`: exit 0 at the first run, no page answered 404 (`flow_check_routes1.out`).
- `node scripts/check-values.mjs`, whole: exit 0 at the first run, 6,926 of 6,957 match, 31 latest prices superseded,
  0 failed (`flow_check_values1.out`). No second run was needed.
- Pictures of the flow at 1280 px and 390 px: `runs/session182/flow_shots/` (five PNGs), looked at.
- `eslint` on this part's files: exit 1, 4 errors, all in code as it was (`AnalysisGallery.tsx`, moved not edited, and
  `MultiChart.tsx`), none in a new file (`flow_eslint1.out`). Lint is not a gate of any workflow.
- No model call in any of them. The only "Ask the warehouse" pressed was against the stand-in.

### Decisions made without you (part 4)

- **"Default for this analysis", not "recommended".** The paragraph says "recommended form". The standing rule is
  that a tool never recommends. A default chart form is how the author of the analysis drew it, not advice about
  energy, but the neutral word costs nothing and cannot be read as advice. The test and the browser check fail on
  "recommend" anywhere on the page.
- **Templates shown from the weekly result, not computed on request.** The honest fold-in inside two hours: nothing
  new to compute, nothing shown as running, the Roundup's inputs untouched. The limit is the gallery's own: inputs
  outside the weekly grid cannot be asked. A template on demand through the worker is a later step if wanted.
- **The curtailment finding's two versions are both current.** The hourly card stands beside the daily one (it is not
  in `SUPERSEDED`), so "Day by day" is first in the Version choice and both cards stay in the list of findings.
- **The superseded cards leave the list of findings.** Reachable three ways: the line under each five-grid card, the
  card's own address, the Version choice in the flow. The count on the page goes from 11 cards to 9.
- **The committed card is shown in the flow on a press, not by itself.** Otherwise the page would carry the first
  card twice in its HTML and the list's number checks could be satisfied by the copy.
- **No lines for an axis of names.** Technologies and balancing authorities are not ordered, so no line joins them.
- **Step one is a list of buttons, not a menu.** On a phone it is 18 rows (about 1,000 px) above the inputs: long,
  but every analysis is visible and pressable without opening anything. A grouped menu would be shorter; say if wanted.
- **A change of grid moves the hub.** The gallery kept "ERCOT North Hub" when the grid became CAISO and printed "not
  available". The flow moves the hub to the first that holds a chart; a hub with no chart can still be picked.
- **Every card of a list carries the "Shown as" row** (where more than one form fits), not only cards in the flow.
- **The first commit of this part holds only the gallery's move.** Its `git add` stopped on a path that had moved;
  the third commit holds the files its message names and says so. History was not rewritten.

### For the coordinator (part 4)

- Nothing under the data lock. No migration. No table written. No scheduled task. No request to approve.
- In order:
  1. Merge `wip/182-flow` into main's line (it is main `1885332c` plus this part's commits; no overlap is expected
     unless `site/app/analysis/page.tsx` or `FindingCard.tsx` changed since).
  2. `mkdir C:/Users/lossa/Documents/erw/runs/build.lock`, then in `site/`: `npm run build`, then `rmdir` the lock.
  3. `python -m unittest tests.test_session182_flow tests.test_session170 tests.test_session173 tests.test_session174
     tests.test_session181 tests.test_session181_worker tests.test_session182`
  4. `node site/scripts/test-analysis-flow.mjs` (from `site/`: `node scripts/test-analysis-flow.mjs`)
  5. Start the server (`npx next start -p <port>`), then, each alone:
     `node scripts/check-analysis-flow.mjs <base>`, `node scripts/check-analysis.mjs <base>`,
     `node scripts/check-findings-grids.mjs <base>`, `node scripts/check-security.mjs <base>`,
     `node scripts/check-csp.mjs <base>`, `node scripts/check-routes.mjs <base>`, `node scripts/check-values.mjs <base>`
     (twice if the first differs).
  6. Stop it and start it against the stand-in, the real checks first because the stand-in answers no rows:
     `SUPABASE_URL=http://localhost:54383 SUPABASE_ANON_KEY=local npx next start -p <port>`, then
     `node scripts/check-internal-findings.mjs <base> 54383` and
     `node scripts/check-analysis-flow.mjs <base> --stub 54383` (the only run that presses "Ask the warehouse"; it
     writes to the stand-in, never to production).
  7. Rule 8: `/analysis` and its cards are in review and no live page reads a file this part changes, so the snapshot
     comparison should list 0 differences.
  8. After the deploy, on production: `node site/scripts/check-analysis-flow.mjs https://erw-flame.vercel.app` (no
     `--stub`: it queues nothing) and `node site/scripts/check-analysis.mjs https://erw-flame.vercel.app`.
- The renders are not to be remade: the renderer's frame keeps the markup it had (`check-findings-grids.mjs` measures
  the frames: 163 of 163).
- Sunday's Roundup (11 October, 23:00 UTC) reads `run.py`'s outputs and the workflow, both untouched.

### To finish (part 4)

- Nothing is held.
- Not proven by a check: one press of "Ask the warehouse" on production (the check never writes to the production
  queue). After the deploy, example 1's step 7 is that proof, and costs one request of the day's count.
- Not exercised in a browser: the line that says a card's data does not fit the chosen form (no fixture of such a
  card exists); it is in `FormChart.tsx` (`data-form-unfit`).
- The stand-in was the last server run on my build, so my worktree's `.next` may hold pages built with no rows: the
  landing builds fresh.
- If wanted later: a template computed on request for inputs outside the weekly grid; a grouped menu in place of
  the 18 buttons on a phone.

## The landing

Written by the chain's coordinator, 10 October 2026. The session landed in two pushes: the three cards first (they
were ready before session 181), then the request flow on top of session 181.

### Parts (1) to (3): the three cards

- From `wip/182-land` (`origin/main` and `wip/182-findings` merged, no conflict). Two things added at the landing:
  - **Sunday's Roundup restores the same tables as before.** The three new modules say `DATA_MACHINE_ONLY = True` and
    `run_finding.py --tables` leaves their histories out (16 tables, as on main, in place of 20 and about 500 MB more
    on the runner). The cards are computed on this machine; their files are in git. If one of the three is chosen for
    the Roundup, the runner says "not computed, a table is missing" and the Roundup falls back to the rule's pick,
    labeled, as it does for any finding it cannot compute. The Python downloads follow their modules (one line each).
  - `tests/test_session156.py` failed on main after the daily run of 16:18 UTC (a pinned figure the run moves): one
    assertion unpinned (`a19f1b45`), as session 159 ruled for its neighbour.
- In the main copy at the merged tree: tests 182, 170, 173, 174, 176, 156: 131 OK; `npm run build` exit 0;
  `check-analysis` 233 of 233; `check-findings-grids` 163 of 163; `check-routes` 0 failed; `check-values`: first run
  6,942 of 6,957 (the 15 were October so far on five battery addresses, the local build's stale cache after the day's
  load), second run **6,957 of 6,957**; the whole suite in the clean worktree: 2,912 tests OK, 232 skipped.
- No freeze. `182a_before` at 17:33:03 UTC; pushed as `task/182-findings`; run 38072208317 success; merge `6ba5bfcf`;
  Vercel production completed 17:40:36 UTC; `182a_after` at 17:41:00 UTC; comparison: **0 differences on the 25 pages**
  (`compare_182a.out`). On production: `check-findings-grids` 163 of 163.

### Part (4): the request flow

- From `wip/182b-land` (session 181's landing, `origin/main` and `wip/182-flow` merged, no conflict).
- In the main copy at the merged tree: tests 182 flow, 170, 173, 174, 181, 181 worker, 182, 177: 212 OK;
  `npm run build` exit 0; `test-analysis-flow.mjs` all passed; `check-analysis-flow` 225 of 225; `check-analysis` 282
  of 282; `check-findings-grids` 163 of 163; `check-security` 48 of 48; `check-routes` 0 failed on the first run;
  `check-values` 6,927 of 6,927; `check-csp` in a real browser: 84 pages, 0 violations; against the stand-in:
  `check-internal-findings` 114 of 114 and `check-analysis-flow --stub` 233 of 233; the whole suite in the clean
  worktree: 3,008 tests OK, 233 skipped.
- No freeze. `182b_before` at 19:14:43 UTC; pushed as `task/182-flow`; run 38079034461 success; merge `d363ef26`;
  Vercel production completed 19:22:54 UTC; `182b_after` at 19:23:18 UTC; comparison: **0 differences on the 25 pages**
  (`compare_182b.out`).
- On production: `check-analysis-flow` 225 of 225 and `check-analysis` 261 of 261 (`prod_flow2.out`,
  `prod_analysis2.out`). The first run of the two failed 3 and 17 assertions, and the fault was on this machine, not
  on production: the worker had written the card of the coordinator's proof request into `site/data/findings/` as an
  untracked file, both checks count the cards in that folder, and production (what git holds) rightly drew one fewer.
  With the four untracked files moved to `runs/session181/worker_card/`, both pass.
- **One real request through production's own route, end to end** (`runs/session182/prod_request.mjs`,
  `prod_request2.out`): the internal view opened by the form; `POST /api/analysis` for `queue_divorce`, 2005 to 2018,
  answered `{"ok":true,"id":"20261010T192556Z-9eb252"}`; queued at 19:25:57 UTC; **done at 19:26:33 UTC** (37 seconds)
  by the worker on this machine; the card ("TILL QUEUE DO US PART", three callouts) read back from the request's row
  through the route. A first try with a year the form does not offer was refused by the route ("First request year:
  not a choice"), as it should be.
- **For your ruling: where the worker writes a requested card.** It writes the card's JSON and its three downloads into
  `site/data/findings/` and `site/public/findings/` of the main copy, as untracked files. `/analysis` draws every card
  file in that folder, so a build on this machine shows cards production does not have, and the two checks above then
  disagree with production. Since migration 029 the page reads a requested card from its queue row, so the files are
  not needed for the card to be seen. Options: the worker writes requested cards under `runs/` (one line, `--out-dir`),
  or each requested card is committed by a person. Tonight the coordinator's two proof cards were moved to
  `runs/session181/worker_card/` and `runs/session182/worker_card/`; nothing was committed.
