# The lab's path, click by click (first walk, 6 November 2026)

Energy Research Warehouse (ERW), session 1499, chain 158 (`queue/done/158-day-6-november-code-replications-explorers-paths.md`). The path a lab's energy team takes when it asks what power will cost a datacenter, where, and how soon. It covers the datacenter tool, its All grids tab as the desktop's chains leave it, the datacenter tracker as the personal laptop's chains leave it, and Ask. Each page was read as it stood at the hour of the walk: another chain is changing the All grids tab and the tracker, so this walk records them as they were.

**How it was walked.** On 6 November 2026, about 10:03 UTC, on a local production build of main at `04623251`, in the internal view, in a real browser (`site/scripts/walk-paths-1497.mjs`; the steps in `docs/reviews/paths/lab-1497.json`). Each step has its screenshot of the first screen at 1280 px, and the first also at 390 (`docs/brand/review-1497/lab-<step>-1280.png`, `lab-01-390.png`). Every figure below is the page's keyed figure.

## Step 1: What a datacenter pays, as it opens

- Address: `/cost-of-power` (ERCOT's LZ_NORTH, a flat load bought in real time, 100 MW).
- What the reader sees first: the last twelve months (November 2025 to October 2026) cost **USD 34.07 per MWh**, USD 29.84 million for 100 MW, **USD 0.0691 a GPU-hour**. Beside them, the hub average's day-ahead basis band of November 2025: p10 -6.93, median -0.42, p90 8.66.
- Shots: [lab-01-1280.png](../brand/review-1497/lab-01-1280.png), [lab-01-390.png](../brand/review-1497/lab-01-390.png).
- Broken: none (at 390 px the page fits: scroll width 390).
- The replication a reader runs: `replication/datacenter/` (13 of 14 of the page's figures; the one difference is the carbon over the hourly window, session 1491).

## Step 2: bought day-ahead

- Address: `/cost-of-power?buy=da`.
- What it shows: **USD 35.70 per MWh**, USD 31.27 million, USD 0.0724 a GPU-hour.
- Shot: [lab-02-1280.png](../brand/review-1497/lab-02-1280.png). Broken: none.

## Step 3: the All grids tab

- Address: `/cost-of-power?view=allgrids` (the desktop's chains 155 and 157 are wiring it; read as it stood).
- What it shows: one table of 48 hubs and zones and ERCOT's nodes, each with energy, transmission, capacity and the time to connect. CAISO's NP15, for one: energy 34.07 USD per MWh day-ahead and 32.67 in real time; "transmission: not held"; "no capacity market" (California has none); connection, the median months for generation in CAISO. 41 cells say "license needed": the held grids, as the hold of 21 October says.
- Shot: [lab-03-1280.png](../brand/review-1497/lab-03-1280.png). Broken: none read here. The tab's open cells are the desktop's to fill.

## Step 4: the datacenter tracker, the facilities

- Address: `/datacenters` (the personal laptop's chain 156 is extending the tracker; read as it stood).
- What it shows first: ERCOT's large-load interconnection status (the report of 19 June 2026): 8,927 MW asking to energize, observed peaks of 3,900 and 3,675 MW; and the month before, 9,062 MW. 5 notes "license needed".
- Shot: [lab-04-1280.png](../brand/review-1497/lab-04-1280.png). Broken: none.

## Step 5: the tracker by grid

- Address: `/datacenters?view=grids`.
- What it shows first: ERCOT, 2 sites (2 stating MW, 191.26 MW asked); 1,169 active queue positions, 298,606 MW; the power price at the Houston zone 34.01 and at Austin Energy's 39.01 USD per MWh.
- Shot: [lab-05-1280.png](../brand/review-1497/lab-05-1280.png). Broken: none.

## Step 6: Ask the warehouse

- Address: `/ask`. The page was read without asking a question: no model call was made in this walk.
- What it shows first: the Lower 48's demand at its newest hours (495,243 MW at 23:00 UTC on 4 November; 499,384 a week before), generation and carbon beside them; the form to ask. The page's first heading is "The Lower 48 states", the panel's, above the form.
- Shot: [lab-06-1280.png](../brand/review-1497/lab-06-1280.png). Broken: none. The board's five questions, asked through the same loop by session 1486 that morning, were 5 of 5 right.

## What the walk found

1. At 390 px the page fits (scroll width 390, measured with a phone's device metrics; a first reading of 481 px with a headless window alone was the script's, and corrected).
2. **For the owner's reading**: the Ask page's first heading is the data panel's ("The Lower 48 states"), not the page's own name. A reader arriving from the menu sees a grid's name first.
3. Nothing else: every step loaded with no error, and every figure read is the page's keyed figure.

## Feedback

To be filled when a lab's team has walked it: one row a remark, with the step.

| Date | Who | Step | What they said | What was done |
|---|---|---|---|---|
