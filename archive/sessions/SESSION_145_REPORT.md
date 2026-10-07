# Session 145 report: What a generator earns, one page

**Added after the chain's last landing (`5def74b`, checks run 37619232614, Vercel "Deployment has completed" at 12:19:26
UTC): its snapshot shows 10 differences, all on `/network`, all from that page's own hourly refresh at 12:05 UTC,**
which ran between the two snapshots (the workflow "hourly network", 12:05:02 to 12:06:09 UTC, before the merge at
12:17): the newest hour of flows moved from 5 October 03:00 UTC to 6 October 03:00 UTC, the newest demand hour from
09:00 to 10:00 UTC, with the refresh stamp and the source line. No checked number key differs (3,357 compared);
`/cost-of-power/battery` and `/storage` show 0 differences. That landing changed this report, three review pages'
files and metadata, and nothing `/network` reads. Not reverted. This paragraph is the only change of the landing that
carries it; that landing's own snapshot is in the session's e-mail line.

Run on 7 October 2026 (UTC), unattended, the last session of the chain 140 to 145 (added to the chain after it
began). The page is at `/cost-of-power/seller`, locked for visitors (`review`); `/cost-of-power/seller/v2` redirects
to it. An agent built it in a working copy of its own to a written brief; I merged, rebuilt its file with the new
zone prices, checked and landed it.

## Four things to know first

- **One reading of yours I had to choose: which hours of generation count.** The capture price uses the hours in
  which the fuel's own figure is held, not the energy mix's stricter flag that the whole hour's mix is sound. With
  the mix's flag, Texas's December 2025 holds 87 percent of its hours (EIA's file repeats the batteries' output under
  "other" on 6 to 14 December), so ERCOT's last twelve months would end in November 2025: solar minus 22.4 percent
  instead of minus 27.7. It is one line (`capture_price.py`), and it is in the Method note.
- **MISO's numbers left the page.** The old tab showed Indiana Hub's figures; by your rule MISO is blank, "paused
  while terms are reviewed", and an address that names MISO opens ERCOT. This is the one thing either page showed
  that is no longer shown.
- **"Combined" for the hybrid is two revenues added.** The solar plant's and the battery's, each priced as if alone
  at the grid's main hub over the same twelve months: no shared interconnection limit, no charging from the plant, no
  clipping recovered. The battery figure is the battery page's own, for ERCOT and CAISO only; other grids read "not
  modeled for this grid". No new battery model was built.
- **The capture file is rebuilt on a data machine, not on the runner.** Its builder rewrites the whole file from the
  tables on the machine; the runner, which holds no price history, would thin it. It is not scheduled.

## Verdict: ready to open, for ERCOT, CAISO, SPP North and New York. What is left, exactly

1. **Your ruling on the hours rule** (above).
2. **ISO-NE's zones and SPP South have no year yet** on this page either (session 140: ISO-NE's zone history is held
   internal; SPP South's pull is still running).
3. **A schedule for the capture file** needs a builder that keeps what the runner cannot rebuild. Not built.
4. `docs/platform-tools.md` and one older status document still name the v2 address.

## What each old page showed, and where it is now

**The seller's tab (session 51): nothing dropped but MISO's numbers.**

- The tabs and the Ask ERCOT link; the form (grid and hub, asset, size, the battery's size, debt service, fixed
  costs, the peaker's heat rate and variable cost), now the left panel "Your plant", with new fields for the hub or
  zone and, for solar, a battery; the cost defaults with their source.
- The monthly revenue sentences with their checked numbers, the monthly bars with the debt line, the table of every
  month, debt coverage with its checked numbers and its months under 1.0, the stress days (ERCOT): all kept, each
  chart now answering the mouse.
- "Merchant only", "How a lender should read this" (six bullets), the stress footnote and the chart captions: moved
  whole into the Method note. The hours above nameplate and the negative hours are a fold.

**Version 2 (session 107): nothing dropped.**

- The summary sentence, with a capture sentence added for solar and wind; revenue per kW as the first headline;
  revenue by year (now a chart that answers the mouse, incomplete years pale); the table of five rows by three
  spans, now for the battery too. "Long-run average" moved from a headline into the sentence and the table; debt
  coverage took its place.
- The folds "How it is measured" and "What this does not tell you": the Method note.
- Both old page files are kept, not routed. `/cost-of-power/seller/v2` answers 308 to `/cost-of-power/seller` with
  its query.

## What is new

- **(a) Capture price** (`warehouse/derived/capture_price.py`, `site/data/seller/capture.json`): for solar and wind
  at every public hub and zone held (39 places of five grids), the generation-weighted price over the hours price
  and generation are both held, against the flat average over the same hours, as a premium or discount in dollars
  and percent; the last twelve months and each year; real time where held and day-ahead beside it. The weights are
  the grid's own hourly solar and wind generation (EIA-930; California from CAISO's own supply after the join): a
  fleet's shape, not a site's. A month counts with 95 percent of its hours.
- **(b) Your contract:** a share of the energy and a price, held in the browser, never sent (a real browser shows no
  request, no change of address, nothing stored); revenue with and without, for solar and wind. It uses the buyer
  page's contract arithmetic, not a third version.
- **(c) Hybrid:** solar with a 2, 4 or 8 hour battery in ERCOT and CAISO: the plant alone, the battery alone (the
  battery page's figure, which the check compares with the live battery page), and the two added.
- **(d)** A link to the curtailment page's "where free energy is" for the hub chosen
  (`/curtailment?grid=...&place=...#free-energy`), which session 144 landed first.

## The capture price, last twelve months (October 2025 to September 2026), USD per MWh

| Main hub | Market | Solar: received against flat | Wind: received against flat |
|---|---|---|---|
| ERCOT hub average | real time | 23.27 against 32.17: minus 8.90 (minus 27.7 percent) | 27.60: minus 4.57 (minus 14.2 percent) |
| CAISO SP15 | real time | 13.86 against 28.53: minus 14.66 (minus 51.4 percent) | 25.88: minus 2.65 (minus 9.3 percent) |
| NYISO New York City | day-ahead | none: EIA-930's solar is zero in every hour | 77.93 against 73.10: plus 4.83 (plus 6.6 percent) |
| ISO-NE Internal Hub | day-ahead | 55.93 against 74.19: minus 18.26 (minus 24.6 percent) | 76.25: plus 2.06 (plus 2.8 percent) |
| SPP North | real time | 41.21 against 30.79: plus 10.42 (plus 33.8 percent) | 25.05: minus 5.75 (minus 18.7 percent) |

- **Widest solar discount:** in dollars the West Texas load zone, real time, 19.98 against 35.24 (minus 15.26, minus
  43.3 percent); in percent SP15. **Widest solar premium:** SPP North.
- **Widest wind discount:** ERCOT's West hub, real time, 23.86 against 30.63 (minus 22.1 percent). No hub pays wind a
  real-time premium.
- **By year, ERCOT hub average, real time, solar's premium or discount:** 2019 plus 27.55; 2020 plus 6.41; 2021 minus
  66.07; 2022 plus 19.19; 2023 plus 22.30; 2024 minus 3.95; 2025 minus 7.82; 2026 (nine months) minus 8.59. **Wind:**
  minus 10.61; minus 3.83; minus 77.64; minus 12.30; minus 14.40; minus 5.74; minus 4.77; minus 4.10.
- New York's and New England's main hubs have no twelve months of real time, so day-ahead is shown first there, and
  the page says which.
- The older model's capture figures (output per MW of nameplate, main hub, monthly) are unchanged and close: ERCOT
  solar 23.20 by the model, 23.27 by generation. Why they differ is in the Method note.
- After the rebuild with session 140's zone prices: 88 series of hub, market and fuel hold twelve months (63 before);
  New York's eleven zones answer from 2019.

## Every pull against its ceiling

- **No data pull.** The EIA-930 workbooks already on the data machine were read; nothing was downloaded.
- **No MISO request. No PJM request.**

## Model spend: none

- No model call. No cap was set for this session.

## The landing

- **Freeze: on**, ending today; the chain's prompt names the landing. `/cost-of-power/seller` stays `review`.
- The fully merged branch (with sessions 140 to 144) was built locally and all three pages' checks passed on that one
  build: this page 43 of 43, the curtailment page 102 of 102, the datacenter page 39 of 39; `check-routes` 0 failed.
- Checks passed on GitHub (run 37615544361); merged as `4a73738`. It also carries session 144's report to main.
- **Vercel built it:** "Deployment has completed" for `4a73738` at 11:49:03 UTC.
- **Snapshot before** (`145_before`, 11:39:02 UTC) **and after** (`145_after`, 11:49:17 UTC): **0 differences** on the 25
  live addresses, 3,357 checked number keys. No number moved on `/cost-of-power/battery`, `/network` or `/storage`.
  Nothing was reverted. (The snapshot reads four seller addresses as a visitor: each is the in-review page, before and
  after.)
- **On production, in the internal view, the page's check passes 43 of 43** (HTML and a real browser), and
  `/cost-of-power/seller/v2?grid=caiso&asset=solar` answers 308 to `/cost-of-power/seller?grid=caiso&asset=solar`.
- The files of the live battery page, the tabs, the battery model and the shared components are untouched (a test
  compares them with main).
- **SPP South has its twelve months with the last landing.** Its pull passed October 2025 at 11:53 UTC; the table was
  written again under the lock (`iso_zone_prices_history` 1,604,204 rows; validator, coverage, the archive and the
  Redivis draft exit 0; nothing released), and the three pages' files were rebuilt: SPP South day-ahead, October 2025
  to September 2026, USD 29.27 per MWh against SPP North's 33.51. All three pages' checks passed again on that build
  (39, 102 and 43), `check-routes` 0 failed. **The pull is still running in the background toward 2019** (one request
  at a time, under its ceiling; it stops by itself). When it has ended, session 140's "To finish" writes the rest.
- **One more landing follows this report**, the chain's last: this report, and the three pages' files rebuilt with
  SPP South's months as far as its pull had reached (session 140's "To finish"). Its snapshot is taken before and
  after as the rule says. **If it shows any difference, a line is added at the very top of this report; no such line
  means 0 differences.**

## Checks

- `tests/test_session145.py` and `site/scripts/test-capture.mjs`, on saved real samples: the generation-weighted
  price by hand on a real week; a plant that generates the same in every hour captures the flat average exactly; the
  premium in dollars and in percent agree; a month under 95 percent writes no figure; MISO has no number; the
  contract arithmetic equals the buyer page's; the combined figure is the sum of its two parts.
- `site/scripts/check-seller.mjs`, HTML and a real browser, on the final local build of the merged branch: 43 of 43
  (four charts answer the mouse; the contract makes no request; the redirect; a visitor sees the in-review page).
- Earlier tests moved to the one page, each named: `tests/test_session107.py` (reads the retired file; the battery
  added to the spans by hand; the redirect); `site/scripts/check-values.mjs` (its fourth seller view is SPP wind
  where it was MISO); `site/lib/audience.ts` (the version 2 menu entry removed).
- The whole suite in a clean copy of the merged branch: 1,772 tests, passed.

## The five numbers a renewables owner would find most useful

1. **California solar received USD 13.86 per MWh against a flat 28.53 at SP15: a 51 percent discount** (real time,
   October 2025 to September 2026).
2. **Texas solar: USD 23.27 against 32.17 at the hub average (minus 27.7 percent), and 18.47 against 30.63 at the West
   hub (minus 39.7 percent)**; the West load zone is the widest, minus 43.3 percent.
3. **Texas solar's premium turned into a discount in two years:** plus 22.30 in 2023, minus 3.95 in 2024, minus 7.82
   in 2025, minus 8.59 so far in 2026 (USD per MWh, hub average, real time).
4. **Wind in Texas: 27.60 against 32.17 (minus 14.2 percent) at the hub average, minus 22.1 percent at the West hub.**
   In SPP North wind is minus 18.7 percent while solar earns a 33.8 percent premium.
5. **A merchant Texas solar plant earned USD 59.85 per kW in the last twelve months against a 2023 to 2025 average of
   102.24, covering default debt 0.67 times;** a 4-hour battery beside it added USD 81.40 per kW of battery (perfect
   foresight, an upper bound, and added, not co-optimized).

## Decisions made without you

1. The hours rule for the capture price (above).
2. No warehouse table for the capture price: the site's file only.
3. California's months across the join of EIA's and CAISO's data are both used (the mix tool skips the join's month).
4. The contract's "without" is energy times the hub's capture price, so at the main hub it differs slightly from the
   headline model revenue; said in the Method note.
5. The hybrid's two figures are both at the main hub, whatever hub is chosen.
6. Both old page files are kept unrouted rather than deleted.
7. Built in a working copy of its own; landed last, after session 144, whose section its link points to.

## To finish

```bash
# on a data machine, when the price tables or EIA-930 have grown (no lock; a site file only):
python warehouse/derived/capture_price.py
cd site && node scripts/test-capture.mjs
```
