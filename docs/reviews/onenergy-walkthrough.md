# The On.Energy walkthrough, click by click (first walk, 6 November 2026)

Energy Research Warehouse (ERW), session 1498, chain 158 (`queue/done/158-day-6-november-code-replications-explorers-paths.md`, the owner's file of 5 November 2026). Roadmap item 8 asks for "the trader path and the On.Energy walkthrough written click by click under docs/reviews/, each walked by its user, the feedback logged there". `docs/reviews/trader-path.md` listed what was needed to write this one. The owner's file of 5 November gives its scope: the battery tool, a merchant battery in ERCOT and one in CAISO, scenarios A and B with a contract share, the saved comparison, the downloads.

**How it was walked.** On 6 November 2026, about 10:00 UTC, on a local production build of main at `04623251`, in the internal view (every page is in review), in a real browser (`site/scripts/walk-paths-1497.mjs`; the steps in `docs/reviews/paths/onenergy-1497.json`). Each step has its screenshot of the first screen at 1280 px, and the first also at 390 (`docs/brand/review-1497/onenergy-<step>-1280.png`, `onenergy-01-390.png`). Scenario B's figures were read from the page's own cells (`data-cell="b|..."`) and the downloads fetched as a reader fetches them. Every figure below is the page's; none is typed here.

**What is still the owner's to settle before On.Energy walks it** (from `trader-path.md`): who at On.Energy walks it and for which decision; how they see a page in review (the internal view given to a person outside the project, or the battery page set live: both rulings); and what may be shown under the license hold of 21 October.

## Step 1: a merchant battery in ERCOT, as the page opens

- Address: `/cost-of-power/battery` (ERCOT, 4 hours, perfect foresight, 100 MW; scenario A at the page's defaults).
- What the reader sees first: the last twelve months (October 2025 to September 2026) earned **USD 81.40 per kW**, 33 percent of it from ancillary services, covering the debt **2.63 times**. USD 8.14 million for 100 MW; a bad month of USD 475,477 among 36.
- Shots: [onenergy-01-1280.png](../brand/review-1497/onenergy-01-1280.png), [onenergy-01-390.png](../brand/review-1497/onenergy-01-390.png).
- Broken: none (at 390 px the page fits: scroll width 390).

## Step 2: the same battery on the day-ahead schedule

- Address: `/cost-of-power/battery?grid=ercot&dur=4&strat=dayahead&mw=100`.
- What it shows: USD **73.00 per kW**, 35 percent ancillary, coverage 2.26 times; USD 7.3 million; a bad month 411,520. Perfect foresight is the bound; the day-ahead schedule is what a battery bidding a day ahead could have taken.
- Shot: [onenergy-02-1280.png](../brand/review-1497/onenergy-02-1280.png). Broken: none.

## Step 3: a merchant battery in CAISO

- Address: `/cost-of-power/battery?grid=caiso&dur=4&strat=dayahead&mw=100`.
- What it shows: USD **65.22 per kW**, 51 percent ancillary, coverage 1.91 times; USD 6.52 million; a bad month 459,656.
- Shot: [onenergy-03-1280.png](../brand/review-1497/onenergy-03-1280.png). Broken: none.

## Step 4: ERCOT, scenario B with half the power contracted

- Address: `/cost-of-power/battery?grid=ercot&dur=4&strat=foresight&mw=100&bn=50&bp=10&v=b`. Scenario B's contract share (`bn`) is 50 percent and its contract price (`bp`) USD 10 per kW-month; `v=b` opens on B.
- What the scenarios show, side by side:

| | A, merchant | B, half contracted at USD 10 per kW-month |
|---|---|---|
| revenue of the last twelve months, USD per kW | 81.40 | 81.40 (the market's, before the contract) |
| debt coverage, times | 2.63 | **3.48** |
| NPV at the hurdle rate, USD million for 100 MW | -69.78 | **-51.13** |
| IRR, percent a year | -8.8 | **0.7** |
| breakeven toll, USD per kW-month | 4.19 | 4.19 |

- Shot: [onenergy-04-1280.png](../brand/review-1497/onenergy-04-1280.png). Broken: none.

## Step 5: CAISO, the same contract in B

- Address: `/cost-of-power/battery?grid=caiso&dur=4&strat=dayahead&mw=100&bn=50&bp=10&v=b`.

| | A, merchant | B, half contracted at USD 10 per kW-month |
|---|---|---|
| revenue of the last twelve months, USD per kW | 65.22 | 65.22 |
| debt coverage, times | 1.91 | **3.12** |
| NPV at the hurdle rate, USD million for 100 MW | -80.19 | **-56.34** |
| IRR, percent a year | none (no rate makes the NPV zero) | **-0.8** |
| breakeven toll, USD per kW-month | 4.19 | 4.19 |

- Shot: [onenergy-05-1280.png](../brand/review-1497/onenergy-05-1280.png). Broken: none.

## Step 6: the saved comparison

- The comparison is saved by its address: both scenarios are written into it (`site/app/cost-of-power/battery/ViewState.tsx`, `lib/battery/view.ts`), so step 4's address, kept and opened again, draws the same two columns. Opened again in a fresh load: the same figures (81.40, 2.63 and 3.48, the same NPVs).
- Shot: [onenergy-06-1280.png](../brand/review-1497/onenergy-06-1280.png). Broken: none.

## Step 7: the downloads

- **Every month of the battery the address names**: `/cost-of-power/battery/months.csv?grid=ercot&dur=4&strat=foresight&mw=100`, `text/csv`, 5 lines of provenance and 107 lines of header and months.
- **The default case's hours**: `/battery/erw_2026_battery_dispatch.csv`, `text/csv`, 4,266,963 bytes. Its replication a reader runs is `replication/battery/` in the repository (22 of 22 of the page's figures met, session 1487).
- Broken: none.

## What the walk found

1. At 390 px the page fits (scroll width 390, measured with a phone's device metrics; a first reading of 481 px with a headless window alone was the script's, and corrected).
2. **Not fixed, for the data machine**: the last twelve months are still October 2025 to September 2026 on 6 November (the trader path's row 2 of the same day).
3. Nothing else: every step loaded with no error, every scenario figure is the page's keyed cell, and both downloads answer.

## Feedback

To be filled when On.Energy has walked it: one row a remark, with the step.

| Date | Who | Step | What they said | What was done |
|---|---|---|---|---|

## Walked 13 November 2026 (session 1885)

Session 1885 walked the seven steps again, click by click, at about 00:11 UTC on 13 November 2026 (the file times of its records), in the internal view, on a local production build of the chain's newest code (main at `ad73c5e9b` plus the unlanded board, periodicals and records branches) served on port 3885. The clicks were made in a real browser by `runs/s1885/walk.mjs` (`node runs/s1885/walk.mjs http://localhost:3885 onenergy 1280`); every step's record (address, the keyed figures and the scenario cells in view, the visible text) is in `runs/s1885/onenergy-1280.json`, and its shot in `runs/s1885/shots/onenergy-<step>-1280.png` (`runs/` is not in git: the shots stay on the code machine). At step 04 the walk's typing did not reach the two contract boxes ("NOT FOUND: ^Contract share", "NOT FOUND: ^Contract price": the boxes carry their names as `aria-label`, not a label element, which the script looked for), so its 04, 04b and 05 show scenario B equal to A. The contract was then typed by `runs/s1885/probe-contract.mjs` (ERCOT; the first run, `probe-contract.out`, put the price in the wrong box, the second, `probe-contract2.out`, set both, shot `onenergy-04c-ercot-b-typed-1280.png`) and `runs/s1885/probe-contract-caiso.mjs` (the same, then CAISO; `probe-contract-caiso.out`, shot `onenergy-05b-caiso-b-kept-1280.png`), each reading the page's own cells (`data-cell="a|..."` and `"b|..."`). No page threw an error; every page is 1265 px wide in a 1280 window (the scroll bar). Where the page has moved since 6 November the step says so; every figure quoted is the page's own.

### The battery, merchant

- **01.** Click the tab **What a battery earns** (`/cost-of-power/battery`; ERCOT, 4 hours, perfect foresight, 100 MW). "Over the last twelve months a 100 MW, 4-hour battery in ERCOT earned USD 81.40 per kW, 33 percent of it from ancillary services, and covered its debt 2.63 times." USD **8.14 million**, "October 2025 to September 2026"; a bad month USD **475,477** (December 2024), "One month in ten of the 36 months held from October 2023 to September 2026"; debt payments USD **2.26 million** a year. All as on 6 November: the window has not moved. The year chart: 2021 **3,431**, 2023 530, 2024 148, 2025 **87**, and 2026 **66** labelled "10 months" (fault 1). The grid row names the other five grids in words: "PJM license needed", NYISO and SPP "in review", "ISO-NE held, not shown: license needed", "MISO held, not shown: license needed". Shot: `onenergy-01-battery-1280.png`.
- **02.** Strategy **Day-ahead schedule**, **Show** (`?grid=ercot&dur=4&strat=dayahead&mw=100`). USD **73.00** per kW, **35** percent ancillary, coverage **2.26** times, USD 7.3 million, a bad month **411,520** (February 2024), "October 2025 to September 2026": as on 6 November. The year chart's 2026 reads **60**, "10 months". Shot: `onenergy-02-dayahead-1280.png`.
- **03.** Grid **CAISO**, **Show** (`?grid=caiso&dur=4&strat=dayahead&mw=100`). "...a 100 MW, 4-hour battery in CAISO earned USD 65.96 per kW, 53 percent of it from ancillary services, and covered its debt 1.94 times", USD **6.6 million**, now "November 2025 to October 2026" (65.22, 51 percent, 1.91 times and USD 6.52 million on 6 November); a bad month **459,656** (November 2025), of the 36 months from November 2023 to October 2026. The year chart: 2023 **54** ("5 months"), 2024 **110**, 2025 **86**, 2026 **59** ("10 months"). CAISO's window has moved a month; ERCOT's has not. Shot: `onenergy-03-caiso-1280.png`.

### Scenarios A and B

- **04.** Grid **ERCOT**, **Perfect foresight**, **Show**; in the box, open **Financing**, click **Scenario B** (the address gains `&v=b`). The walk's typing missed the two boxes (above), so the A and B table shows B equal to A: 81.40, 2.63 times, USD -69.78 million, -8.8 percent, toll USD 4.19 in both columns (shots `onenergy-04-ercot-b-1280.png`, `onenergy-04b-ercot-b-table-1280.png`). Typed by the probe, Contract share **50**, Contract price **10** (the address becomes `/cost-of-power/battery?bn=50&bp=10&v=b`), the table reads, as on 6 November:

| | A, merchant | B, half contracted at USD 10 per kW-month |
|---|---|---|
| revenue of the last twelve months, USD per kW | 81.40, "October 2025 to September 2026" | 81.40 (the market's, before the contract) |
| debt coverage, times | 2.63 | **3.48** ("contract 50 percent at USD 10 per kW-month") |
| NPV at the hurdle rate, USD million for 100 MW | -69.78 (USD -697.80 per kW at 12 percent) | **-51.13** (USD -511.34 per kW) |
| IRR, percent a year | -8.8 | **0.7** |
| breakeven toll, USD per kW-month | 4.19 | 4.19 |

  The column heads say each scenario's contract ("contract 0%, contract USD 0/kW-month" against "contract 50%, contract USD 10/kW-month"), and the row "What differs" reads "B: contract share 50 percent against 0; contract price USD 10 per kW-month against 0." The row above it, "Merchant tail after the contract": USD **0**, "0 years: the term and the life are both 20 years". The probe's first run, with the share at 50 and the price left at 0, gave B **0.83** times, USD **-95.95 million**, IRR "none": half the battery contracted for nothing. Shot: `onenergy-04c-ercot-b-typed-1280.png`.
- **05.** With B contracted, Grid **CAISO**, **Day-ahead schedule**, **Show**. The contract is kept: "after Show: /cost-of-power/battery?grid=caiso&dur=4&strat=dayahead&mw=100&bn=50&bp=10&v=b".

| | A, merchant | B, half contracted at USD 10 per kW-month |
|---|---|---|
| revenue of the last twelve months, USD per kW | 65.96, "November 2025 to October 2026" | 65.96 |
| debt coverage, times | 1.94 | **3.14** |
| NPV at the hurdle rate, USD million for 100 MW | -79.71 (USD -797.08 per kW) | **-56.1** (USD -560.98 per kW) |
| IRR, percent a year | none ("no rate from -99 to 1,000 percent sets NPV to zero") | **-0.7** |
| breakeven toll, USD per kW-month | 4.19 | 4.19 |

  On 6 November: 65.22; 1.91 against 3.12; -80.19 against -56.34; none against -0.8. The stress test above the table names CAISO's own event: "Default 0. USD 7.70 per kW a repeat, 15 to 17 August 2023" (ERCOT's: USD 3,105.51, Winter Storm Uri, February 2021). Under the table: USD **109.73** per kW in 2024 (scenario A's NPV USD -51.56 million), the highest whole year, and **85.59** in 2025 (USD -67.09 million), the lowest. Shots: `onenergy-05-caiso-b-1280.png` (the walk's, B equal to A), `onenergy-05b-caiso-b-kept-1280.png` (the probe's).

### The saved comparison and the downloads

- **06.** Open `/cost-of-power/battery?grid=ercot&dur=4&strat=foresight&mw=100&bn=50&bp=10&v=b` in a fresh load. The same two columns as step 04: 81.40 and 81.40; **2.63** against **3.48** times; USD **-69.78** against **-51.13** million; -8.8 against 0.7 percent; toll 4.19. Under the table: USD **3,430.56** per kW in 2021 (scenario A's NPV USD 2.08 billion), the highest whole year, and **87.44** in 2025 (USD -65.9 million), the lowest. Shot: `onenergy-06-saved-1280.png`.
- **07.** The downloads, each fetched as a reader fetches it:
  - **Every month, CSV**, `/cost-of-power/battery/months.csv?grid=ercot&dur=4&strat=foresight&mw=100&bn=50&bp=10&v=b` (the link carries the scenario): 200, `text/csv; charset=utf-8`, 10,174 characters, 113 lines as the script counts them (on 6 November, 5 lines of provenance and 107 of header and months); first line "# Energy Research Warehouse (ERW): every month of "What a battery earns", ERCOT, 4-hour, perfect for...".
  - **the table, CSV** (the stress days, not among the two of 6 November), `/api/download?table=battery_stack_stress_daily`: 200, `text/csv`, 469,810 characters, 1,910 lines; "the battery revenue stack on stress days, per MW and local day".
  - **CSV**, `/battery/erw_2026_battery_dispatch.csv`: 200, `text/csv`, 4,266,963 characters (the size of 6 November), 26,320 lines; "the battery model's hourly dispatch; the default case of /cost-of...".
  - Shot: `onenergy-07-downloads-1280.png`.

### Faults found

1. **Battery page, ERCOT, steps 01, 02, 04 and 06**: the last twelve months still end September 2026 on 13 November ("October 2025 to September 2026"; the 36 months "from October 2023 to September 2026"), while CAISO's end October ("November 2025 to October 2026", step 03); ERCOT's year chart labels 2026 "10 months" (66 per kW under perfect foresight, 60 on the day-ahead schedule), one month beyond the headline. 6 November's walk listed the same window as not fixed. Should: October whole in `battery_stack_monthly` (the data machine's), and a month the headline treats as incomplete not counted in the year chart's "10 months" (site code fix). The trader path's fault 2 of the same walk. State: the site part fixed (`8268452b3`, session 1892: a month not whole and newer than every whole month is not held, so the year chart and the income table end with the headline); October whole in `battery_stack_monthly` is the data machine's.
