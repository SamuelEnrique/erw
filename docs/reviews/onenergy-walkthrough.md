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
