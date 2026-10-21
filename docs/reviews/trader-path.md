# The trader path, click by click

Roadmap "This week", item 8, "First users ready": the path the two traders the roadmap names, Pirro Prifti and Christian Mira, take through the generator page, the battery page and the price board. Written by session 382 (21 October 2026, about 02:30 to 03:00 UTC) from a walk in a real browser, at 1280 and at 390 px wide, on a local production build of `wip/382-trader-path` at `c5c3b806` (main at `dc4d5ba6` plus this session's one fix, below). Every page is in review, so the walk opened the internal view first (the form at `/internal/open`; the token posted, never in an address). **Not yet walked by its users**: their feedback goes in the last section.

The shots are in [`docs/brand/review-382/`](../brand/review-382/), two a step (`<step>_1280.png`, `<step>_390.png`). Each shows the part of the page the step is about: the top of the page after a click that changes the inputs, the section named otherwise. The walk is `docs/brand/review-382/walk-382.mjs` (`node docs/brand/review-382/walk-382.mjs http://localhost:3382 <json-dir>` with `npx next start -p 3382` running in `site/`): it makes every click below, takes the shots, and writes what each step showed (address, every checked figure in view with its key and its value as read) to `walk-1280.json` and `walk-390.json`, kept beside the shots. Steps 15 and 16 were taken again with their clicks corrected (the first walk's filter click missed, and the week's group was folded); their records are `walk-1280-15-board-ercot-hubs+16-board-week.json` and its 390 twin, and the two steps' records in `walk-1280.json` and `walk-390.json` are the first, wrong ones. (A list of steps as a third argument retakes only those, every earlier click still made.)

## How to read a step

- **Address**: where the reader is after the step (what the address bar shows).
- **Does**: the click.
- **Sees**: the figure to check, as the page prints it, with its check key. The key is the `data-check` attribute `site/scripts/check-values.mjs` recomputes:
  - `cap|<grid>|<hub>|<market>|<fuel>|<span>|<stat>`: a capture price, hub average or capture rate, from the capture file (`data/seller/capture.json`);
  - `mr|<inputs>|<stat>` and `ms|<inputs>|<span>|<stat>`: the generator model (`merchant_revenue_monthly`, the page's snapshot), `<inputs>` beginning `iso=<grid>`;
  - `bs|<inputs>|<stat>`: the battery model, recomputed from `battery_stack_monthly` in Supabase; `bsa|<strategy>_<N>h|<stat>`: the line beside ERCOT's real awards (`data/battery_awards_beside.json`);
  - the board's figures carry `data-n` keys, not `data-check`: `site/scripts/check-board-v4.mjs` checks each against `data/board.json`. `/board` has a floor of 0 in `site/scripts/check-values-floor.json` (no Supabase key on it).
- **A trader would ask**: what the page does not answer. Listed, not built.

## The generator page, `/cost-of-power/seller`

### Step 01: the page as it opens

- Address: `/cost-of-power/seller`
- Does: opens "What a generator earns" (Economics menu, or the tab of that name on any cost-of-power page).
- Sees: a 100 MW solar plant in ERCOT at the hub average. The summary sentence and three headline figures:
  - revenue, last twelve months (Oct 2025 to Sep 2026): **59.85** USD/kW, `ms|iso=ercot&asset=solar&mw=100&mwh=0&ds=7078769&hr=10.725&vom=4.25&fom=12.5|twelve|revenue`;
  - price received at the hub average: **23.27** USD/MWh against a flat average of **32.17**, a capture rate of **72** percent: `cap|ercot|HB_HUBAVG|rt|solar|l12|price`, `...|flat`, `...|rate`;
  - debt coverage: **0.67** times, over debt payments of USD **7.08 million** a year: `mr|iso=ercot&asset=solar&...|ttm_last` and `...|ds`.
  - At 390 px the first screen holds the menu, the title and the top of "Your plant"; the first checked figure begins about 2,375 px down (the page is 11,481 px tall), below the whole form.
- A trader would ask:
  - Why do the last twelve months end in September 2026 on 21 October? (The model's months end there; the page says the span, not why it stops.)
  - What did it earn at its own node, not at the hub? The headline is at a hub or load zone; a node enters only scenarios A and B, as a percentile of ERCOT's wind nodes' day-ahead basis to the hub average (under the form), and moves no headline figure.
  - Day-ahead or real time? The headline capture price is real time; the revenue is the model's. There is no switch to price the same plant on day-ahead.
  - What is the forward view? Every figure is historical; no forward curve or futures settle is held (the board's curve column says "licensed source needed").
- Shots: [01-seller_1280.png](../brand/review-382/01-seller_1280.png), [01-seller_390.png](../brand/review-382/01-seller_390.png)

### Step 02: a wind plant

- Address: `/cost-of-power/seller?iso=ercot&asset=wind&hub=HB_HUBAVG`
- Does: under "Your plant", Asset, clicks **Wind** (the page opens the new address at once; no Show needed).
- Sees: revenue **83.57** USD/kW (`ms|iso=ercot&asset=wind&mw=100&mwh=0&ds=11192257&hr=10.725&vom=4.25&fom=32.25|twelve|revenue`); price received **27.60** USD/MWh against **32.17**, capture rate **86** percent (`cap|ercot|HB_HUBAVG|rt|wind|l12|price`, `flat`, `rate`); debt coverage **0.46** times over USD **11.19 million** a year (`mr|...|ttm_last`, `mr|...|ds`).
- A trader would ask:
  - The plant is ERCOT's whole wind fleet by the hour, scaled to 100 MW, not one site (the page says so under the income table). A trader with a site wants its profile: "Your plant's own year" takes a pasted year of output, priced at the main hub only.
  - What would a hedge have paid against the merchant revenue, month by month? The scenarios hold a contract (a share, a price, and a shape: as generated or a flat block) for the NPV and the coverage, not a monthly hedge settlement.
- Shots: [02-seller-wind_1280.png](../brand/review-382/02-seller-wind_1280.png), [02-seller-wind_390.png](../brand/review-382/02-seller-wind_390.png)

### Step 03: another hub

- Address: `/cost-of-power/seller?iso=ercot&hub=HB_WEST&asset=wind&mw=100&bmw=100&dur=4&strat=foresight`
- Does: Settlement point, chooses **West hub (HB_WEST)**, clicks **Show**.
- Sees: "priced at the West hub (real-time prices)": price received **23.86** USD/MWh against **30.63**, capture rate **78** percent (`cap|ercot|HB_WEST|rt|wind|l12|price`, `flat`, `rate`); debt coverage **0.36** times (`mr|iso=ercot&asset=wind&...&fom=32.25&hub=HB_WEST&market=rt|ttm_last`). The revenue, **72.23** USD/kW, carries no check key at a hub other than the main one (the page writes it as plain text there), and the spans table below gives the same twelve months' capture price as **23.85**, against the headline's 23.86 (the headline is the capture file, the table the hub model).
- A trader would ask:
  - Why do the headline and the table differ by a cent for the same twelve months? (Two sources, not said on the page.)
  - What is the West to Hub average basis by month and by hour of day? The capture table gives the twelve months and the years; the shape within the day is not shown.
  - Curtailment at West: the page links to the curtailment page's free energy for the hub; the revenue does not count curtailed hours.
- Shots: [03-seller-west_1280.png](../brand/review-382/03-seller-west_1280.png), [03-seller-west_390.png](../brand/review-382/03-seller-west_390.png)

### Step 04: the capture price by year and by hub

- Address: `/cost-of-power/seller?iso=ercot&hub=HB_WEST&asset=wind&mw=100&bmw=100&dur=4&strat=foresight` (unchanged)
- Does: scrolls to "What it earned per MWh against the hub average".
- Sees: the chart of capture price against the hub average by year, 2019 to 2026 and the last twelve months (2021 the outlier, a capture rate of 45 percent), and the table of every hub and zone of ERCOT. Its first row: Hub average, real time, **27.60** against **32.17**, **86** percent (`cap|ercot|HB_HUBAVG|rt|wind|l12|...`), then each year's rate (2019 **70**, 2021 **48**, 2025 **85**, 2026 **87**: `cap|ercot|HB_HUBAVG|rt|wind|<year>|rate`); AEN load zone, day-ahead, **34.09** against **38.72**, **88** percent (`cap|ercot|LZ_AEN|da|wind|l12|...`). At 390 px the chart and the table scroll sideways inside their frames; the page itself does not.
- A trader would ask:
  - Why is one row real time and the next day-ahead? Each hub or zone is shown in the one market the ERW holds for it; a like-for-like comparison needs both markets for every row.
  - The chart does not say which hub it is drawn for (the hub chosen, West); the table's first row is the hub average.
  - Capture by month of year (the spring and summer shape) is not on the page.
- Shots: [04-seller-capture_1280.png](../brand/review-382/04-seller-capture_1280.png), [04-seller-capture_390.png](../brand/review-382/04-seller-capture_390.png)

### Step 05: CAISO

- Address: `/cost-of-power/seller?iso=caiso&asset=wind`
- Does: Grid, clicks **CAISO** (opens at once; the hub returns to the grid's default, SP15, and the size to 100 MW).
- Sees: "CAISO holds one full year, 2025: USD 94.68. There is no long-run average yet." Revenue **64.04** USD/kW (`ms|iso=caiso&asset=wind&mw=100&mwh=0&ds=11192257&hr=10.725&vom=4.25&fom=32.25|twelve|revenue`); price received at SP15 **25.88** against **28.53**, **91** percent (`cap|caiso|TH_SP15_GEN-APND|rt|wind|l12|price`, `flat`, `rate`); debt coverage **0.28** times (`mr|iso=caiso&...|ttm_last`). The "Ask ERCOT about this view" button is not shown for CAISO.
- A trader would ask:
  - Why does CAISO hold one full year only? (Its prices are held from August 2023.)
  - NP15 and ZP26: the grid lists 3 hubs and zones; no node, and no congestion component apart.
  - Resource adequacy: a CAISO plant earns capacity payments the page does not count (the battery page says CAISO's RA prices are not yet in the warehouse).
- Shots: [05-seller-caiso_1280.png](../brand/review-382/05-seller-caiso_1280.png), [05-seller-caiso_390.png](../brand/review-382/05-seller-caiso_390.png)

### Step 06: scenario B as a PPA

- Address: `/cost-of-power/seller?iso=caiso&asset=wind&bn=100&bp=100.32&v=b`
- Does: under "Is it worth building?", clicks **Make B a PPA**.
- Sees: scenario B holds the whole plant under contract at its own breakeven price, rounded up to the cent, USD 100.32 per MWh; the results table, A against B: debt coverage **0.28** against **1.93** times; NPV at the hurdle rate USD **-148.55 million** against USD **12,385**; IRR "none" against **12.0** percent; "Breakeven PPA price" USD **100.31** in both columns, for a 30-year term; the contract price at which coverage reaches 1.25 times, USD **69.51**. These are computed in the browser from the page's figures and carry no check key; the inputs (capital cost 2,100 USD/kW, 60 percent debt at 8 percent, hurdle 12 percent, from Lazard's LCOE+ of June 2025) are each printed with their source.
- A trader would ask:
  - What do CAISO wind PPAs actually price at? A breakeven of USD 100 per MWh against a capture price near USD 26 needs a market reference beside it (the page's cross-checks cite Berkeley Lab's PPA indexes in the method note, not on the face).
  - The PPA settles at SP15; CAISO has no node choice, so the basis between the plant and the hub is not in B (ERCOT's scenarios take a node percentile, CAISO's do not).
  - Tax credits are fields of the scenarios (investment and production credit, both 0 by default: "The page holds no figure for whether this project qualifies"); a trader would want the breakeven with the credit the project expects beside the one without.
- Shots: [06-seller-ppa_1280.png](../brand/review-382/06-seller-ppa_1280.png), [06-seller-ppa_390.png](../brand/review-382/06-seller-ppa_390.png)

## The battery page, `/cost-of-power/battery`

### Step 07: the page as it opens

- Address: `/cost-of-power/battery`
- Does: clicks the tab **What a battery earns** above the title.
- Sees: a 100 MW, 4-hour battery in ERCOT at HB_HUBAVG, perfect foresight. "Over the last twelve months a 100 MW, 4-hour battery in ERCOT earned USD 81.40 per kW, 33 percent of it from ancillary services, and covered its debt 2.63 times." Headline: **USD 81.40** per kW (`bs|grid=ercot&dur=4&strat=foresight&mw=100&fom=22&ds=2261119|l12_kw:total`; USD **8.14 million**, `...|l12:total`); a bad month, the 10th percentile of the last 36, **USD 475,477** (December 2024; `...|p10_36`, of `...|n36` = 36 months); debt coverage **2.63** times (`...|cover`) over USD **2.26 million** a year (`...|ds`). At 390 px the first figure begins about 2,264 px down, below the Assumptions box.
- A trader would ask:
  - Perfect foresight is the default: what does a realistic dispatch earn? (Step 10's day-ahead schedule is the other strategy; there is no bid-based or forecast-error case.)
  - Revenue at the battery's own node, not the hub (the page gives the storage nodes' spread beside it, step 08, and adds it to no figure).
- Shots: [07-battery_1280.png](../brand/review-382/07-battery_1280.png), [07-battery_390.png](../brand/review-382/07-battery_390.png)

### Step 08: the line beside ERCOT's real awards

- Address: `/cost-of-power/battery` (unchanged)
- Does: scrolls under the income table to the line on ancillary services.
- Sees: "Day-ahead ancillary services, January 2026 to July 2026: this model takes USD **2.25** per kW a month; ERCOT's storage resources were awarded USD **0.40** per kW of their power a month; the model is **5.66** times the awards." (`bsa|foresight_4h|model`, `bsa|foresight_4h|fleet`, `bsa|foresight_4h|ratio`). Beside it: Winter Storm Uri alone is **57** percent of everything this battery earned in the 105 months held (`bs|...|top_share`), and the storage nodes' four-hour day-ahead spread (`series|node_basis_summary|ercot:HB_HUBAVG|...`).
- A trader would ask:
  - If the model takes 5.66 times what the fleet was awarded, what is the headline with ancillary revenue scaled to the awards? The page states the gap but no figure uses it.
  - Ancillary price depth: how much of each product the market procures against the storage fleet's MW (saturation), by month.
  - Real-time ancillary and energy-plus-AS co-optimisation after ERCOT's RTC go-live: not modelled.
- Shots: [08-battery-awards_1280.png](../brand/review-382/08-battery-awards_1280.png), [08-battery-awards_390.png](../brand/review-382/08-battery-awards_390.png)

### Step 09: two hours

- Address: `/cost-of-power/battery?grid=ercot&dur=2&strat=foresight`
- Does: Duration, clicks **2 hours**.
- Sees: USD **58.63** per kW, 46 percent from ancillary services, debt coverage **3.82** times (`bs|grid=ercot&dur=2&strat=foresight&mw=100&fom=11.2&ds=1242597|l12_kw:total`, `l12_share:ancillary`, `cover`); a bad month USD **364,767** (December 2024, `p10_36`); debt payments USD **1.24 million** a year.
- A trader would ask:
  - Revenue per kWh as well as per kW, to compare durations on the energy bought.
  - The marginal value of the third and fourth hour (4-hour less 2-hour, per added MWh).
- Shots: [09-battery-2h_1280.png](../brand/review-382/09-battery-2h_1280.png), [09-battery-2h_390.png](../brand/review-382/09-battery-2h_390.png)

### Step 10: four hours on the day-ahead schedule

- Address: `/cost-of-power/battery?grid=ercot&dur=4&strat=dayahead&mw=100`
- Does: clicks **4 hours**, then Strategy **Day-ahead schedule**, then **Show**.
- Sees: USD **73.00** per kW against step 07's 81.40 under perfect foresight, 35 percent from ancillary services, debt coverage **2.26** times (`bs|grid=ercot&dur=4&strat=dayahead&mw=100&fom=22&ds=2261119|l12_kw:total`, `l12_share:ancillary`, `cover`); a bad month USD **411,520** (February 2024).
- A trader would ask:
  - The gap between the two strategies, as a figure (here 8.40 per kW, about 10 percent) on the page rather than by two clicks.
  - Real-time re-optimisation on top of the day-ahead schedule (the DA/RT spread a trader would capture) is not a strategy.
- Shots: [10-battery-4h-dayahead_1280.png](../brand/review-382/10-battery-4h-dayahead_1280.png), [10-battery-4h-dayahead_390.png](../brand/review-382/10-battery-4h-dayahead_390.png)

### Step 11: CAISO

- Address: `/cost-of-power/battery?grid=caiso&dur=4&strat=dayahead&mw=100`
- Does: Grid, **CAISO**, then **Show**.
- Sees: "a 100 MW, 4-hour battery in CAISO earned USD 65.22 per kW, 51 percent of it from ancillary services, and covered its debt 1.91 times." (`bs|grid=caiso&dur=4&strat=dayahead&mw=100&fom=22&ds=2261119|l12_kw:total`, `l12_share:ancillary`, `cover`); a bad month USD **459,656** (November 2025). NYISO and SPP are offered "in review"; PJM, ISO-NE and MISO are greyed with their reasons.
- A trader would ask:
  - Resource adequacy, the larger part of a California battery's income, is "not held".
  - SP15 only; no NP15 or ZP26 battery.
- Shots: [11-battery-caiso_1280.png](../brand/review-382/11-battery-caiso_1280.png), [11-battery-caiso_390.png](../brand/review-382/11-battery-caiso_390.png)

### Step 12: income by stream, and CAISO's market monitor

- Address: `/cost-of-power/battery?grid=caiso&dur=4&strat=dayahead&mw=100` (unchanged)
- Does: scrolls to "Income by stream".
- Sees: the table by stream for the last twelve months and each year: energy USD **3.2 million** (`bs|...caiso...|l12:energy`), ancillary services USD **3.33 million** (`l12:ancillary`), of which Regulation Down USD **2.04 million**; capacity "Not held"; total USD **6.52 million**, **65.22** per kW. Under it, the market monitor's fleet beside the model for 2025: the model takes USD **42.50** per kW from energy and USD **42.32** from regulation (`bs|...|year_kw:2025:energy`, `year_kw:2025:regup+regdn`); the monitor reports about USD 35 and USD 9 for real batteries (its 2025 annual report, June 2026). The "Leave out" boxes list the stress events, the last "5 to 8 October 2026", though the months shown end in September 2026.
- A trader would ask:
  - Regulation at nearly five times what the fleet earned (42.32 against about 9): what is the figure with regulation capped at the market's requirement?
  - The months end in September; the stress list already holds 5 to 8 October. When does October arrive?
- Shots: [12-battery-income_1280.png](../brand/review-382/12-battery-income_1280.png), [12-battery-income_390.png](../brand/review-382/12-battery-income_390.png)

## The price board, `/board`

### Step 13: the board as it opens

- Address: `/board`
- Does: clicks **Price board** (Economics menu).
- Sees: "built 20 Oct 2026". The twelve numbers to check first, each with its date and its day and week moves: ERCOT Hub average day-ahead **43.95** USD/MWh, **15 Oct 2026** (`top|ercot-hb-hubavg-da|last`, day **-12.49**, week **-20.50**); ERCOT real time **50.22**, 14 Oct; CAISO SP15 day-ahead **45.01**, 20 Oct; SPP North day-ahead **24.76**, 20 Oct; Henry Hub **3.22** USD/MMBtu, 14 Oct; ERCOT spark spread, indicative, **4.81**, 10 Oct; WTI **101.91**, Brent **126.55** USD/bbl, 14 Oct. Under them: lowest grid day-ahead **35.00** (CAISO SP15, 14 Oct), highest **64.57** (SPP North, 14 Oct), Brent minus WTI **24.64** USD/bbl. These keys are checked by `check-board-v4.mjs` against `data/board.json` (12 of 12 tonight), not by `check-values.mjs`.
- A trader would ask:
  - Why is ERCOT's day-ahead dated 15 October when the week table on the same page (step 16) holds ERCOT Hub average day-ahead for 20 October (**30.98**)? (A fault in the data, reported below.)
  - Why do "lowest grid" and "highest grid" compare 14 October while CAISO and SPP hold 20 October? (The comparison is on the newest common day; the tile says the date, not why.)
  - Brent minus WTI at 24.64 USD/bbl is far outside its usual range: is it right? (EIA's spot series; not checked against the source tonight: no pulls.)
  - Forward curves (the curve column says "licensed source needed") and intraday prices.
- Shots: [13-board_1280.png](../brand/review-382/13-board_1280.png), [13-board_390.png](../brand/review-382/13-board_390.png)

### Step 14: a row in the markets workbench

- Address: `/board?s=ercot-hb-hubavg-da`
- Does: clicks the first tile, **ERCOT Hub average, day-ahead**.
- Sees: the workbench opens beside the table ("ERCOT Hub average, day-ahead, 43.95 USD/MWh on 15 Oct 2026"), the week of hourly prices with the real-time overlay and the spread between them (average 3.53), and the row in the table: **43.95**, day **-12.49**, week **-20.50**, month **+14.14**, year **+8.93**, 7-day average **38.58**, 30-day **42.61**, one-year range **9.08** to **654.03** (`ercot-hb-hubavg-da|last`, `d`, `w`, `m`, `y`, `avg7`, `avg30`, `lo`, `hi`). At 390 px the workbench takes the screen.
- A trader would ask:
  - The hourly chart runs to 16 October while the daily row stops at 15 October: which is the last complete day?
  - An export of the window shown: the CSV button gives the row's file; a chosen window is not cut.
- Shots: [14-board-workbench_1280.png](../brand/review-382/14-board-workbench_1280.png), [14-board-workbench_390.png](../brand/review-382/14-board-workbench_390.png)

### Step 15: every ERCOT hub

- Address: `/board?s=ercot-hb-hubavg-da&power.grid=ERCOT&power.scope=all`
- Does: in "Power, by hub and zone", Grid **ERCOT**, Show **Every hub and zone**.
- Sees: 12 rows: hub average, bus average, Houston, North, South and West, each day-ahead (15 Oct) and real time (14 Oct): Houston real time **56.95**, West day-ahead **41.78** (`ercot-hb-west-da|last`). The load zones are not among them (the seller page holds them).
- A trader would ask:
  - Load zones on the board (LZ_HOUSTON and the rest), as the seller page has them.
  - The hub spreads (North to Houston, West to North) as rows of their own.
- Shots: [15-board-ercot-hubs_1280.png](../brand/review-382/15-board-ercot-hubs_1280.png), [15-board-ercot-hubs_390.png](../brand/review-382/15-board-ercot-hubs_390.png)

### Step 16: the week, by hub

- Address: `/board?s=ercot-hb-hubavg-da&power.grid=ERCOT&power.scope=all` (unchanged)
- Does: opens the group **The week, by hub** (its title).
- Sees: 31 rows: ERCOT Hub average day-ahead, latest **30.98** on **20 Oct** (`week|ercot-hb-hubavg|last`), the week's mean **32.84** (-9.01), on-peak **38.06**, off-peak **30.29**, RT minus DA **-0.10**, heat rate **11.08**; CAISO SP15 **45.01**; NYISO New York City **49.25** (20 Oct); the ISO-NE rows below. The download line under the board says "iso_hub_prices_history held: license needed".
- A trader would ask:
  - Which figure for ERCOT is today's: 43.95 on 15 October (step 13) or 30.98 on 20 October (here)?
  - NYISO's and ISO-NE's prices are shown here on 21 October, while the same page's download line says their history is "license needed" (reported below).
- Shots: [16-board-week_1280.png](../brand/review-382/16-board-week_1280.png), [16-board-week_390.png](../brand/review-382/16-board-week_390.png)

## What the walk found

1. **Fixed (no ruling needed)**: from 21 October 00:00 UTC every `mr|` and `ms|` figure of the generator page read "license needed" on ERCOT, CAISO and SPP, as on ISO-NE and NYISO (18 held on the default page, 21 on the battery view, every model figure blank, while the summary sentence above them still printed the revenue). The license hold of the owner's ruling of 12 October holds `merchant_revenue_monthly` grid by grid; `components/Num.tsx` looked for the grid only as an entity (`iso:ercot`), and these keys name it as an input (`iso=ercot`). `lib/license.ts` now reads it (`gridEntityOfKey`); NYISO's figures stay held (11 on a NYISO wind view). `tests/test_session382.py`. After the fix, `check-values` on the generator page: 240 of 240 (63 of them `mr|` and `ms|`).
2. **Not fixed, for the data machine**: the board's ERCOT rows stop on 15 October (day-ahead) and 14 October (real time) while its week table holds 20 October; the twelve top tiles show the older figure. `data/board.json` was built at 06:22 UTC on 20 October.
3. **Not fixed, it ends by itself**: `data/board.json` was written before the hold began, so NYISO's and ISO-NE's prices are still on the board on 21 October (80 and 54 rows marked ok). The daily run's rebuild of the file applies the hold (`warehouse/derived/board_page.py`, `ls.held_grids()`).
4. **Not fixed, already fixed on a branch**: two downloads on the board answer 502 tonight (`/api/download?table=ercot_as_prices` and `?table=eia_fuel_spot_prices`, "Supabase series: HTTP 500", statement timeouts); session 368's keyset download (`task/367-372`, not yet on main) removes the row count that times out.
5. **For a ruling**: on a phone the first checked figure of the generator and battery pages is 2,140 to 2,375 px down (two and a half screens), below the whole form; on the board it is at 319 px.

## The On.Energy walkthrough: what is needed to write it

`docs/reviews/` holds no scope for it, so it is not written. To write it in this form, a session needs:

- **Who and what**: the person at On.Energy who will walk it, their role (developer, operator, trader of its fleet) and the decision the walk serves (a site, an offtake, a bid strategy). The ERW's owner list (`site/data/storage_owners.json`, EIA-860) names an owner "On Energy Storage"; nothing in the repository says it is the company the roadmap means.
- **Which pages**: the battery page surely; whether `/storage`, `/network`, `/cost-of-power/seller?asset=battery` or `/grid/ercot` belong in it.
- **Which grids and assets**: ERCOT only, or CAISO too; the duration and size of their projects, so the walk opens on their case rather than the default.
- **How they will see it**: every page is in review. An outside reader needs either the internal view (a token given to a person outside the project: a ruling) or the pages it uses set live (a ruling, with rule 8's snapshot).
- **What may be shown to them**: the license hold of 21 October holds ISO-NE's, MISO's and NYISO's figures; whether a walk for a company counts as republishing any other table (`docs/licenses.md`).
- **When**: the date of the walk, so the figures can be read and checked the same day.

## Feedback

To be filled when each user has walked the path: one row a remark, with the step.

| Date | Who | Step | What they said | What was done |
|---|---|---|---|---|
| | Pirro Prifti | | | |
| | Christian Mira | | | |
