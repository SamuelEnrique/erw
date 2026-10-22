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

## Walked again on a build, 22 October 2026 (session 585)

Session 585 walked the sixteen steps above again on 22 October 2026, about 00:45 to 01:30 UTC, in the internal view (the token posted by the form at `/internal/open`), at 1280 and at 390 px wide, on a local production build of `wip/585-s` (`origin/wip/506-combined` at `6f49d45d`, which holds main at `76037cec` and chain 023), served on port 3585. The walk is `docs/brand/review-585/walk-585.mjs`, session 382's script with the same clicks, which also records the source lines in view, the held figures of the page, its empty charts and the height of its first checked figure; its shots and records (`walk-1280.json`, `walk-390.json`) are in [`docs/brand/review-585/`](../brand/review-585/). `sources-585.mjs` lists, for each page of the path, every heading with the checked figures under it and the source lines in the same span (`sources-585.json`). Every step was made at both widths (32 of 32), no page logged an error, no page was wider than the window at 390, and the 139 same-origin links of the three pages each answered 200 (their anchors are left to session 581's link check).

| Step | What the page showed (1280) | The step's promise | Broken |
|---|---|---|---|
| 01 | 59.85 USD/kW; 23.27 against 32.17, 72 percent; 0.67 times over 7.08 million; Oct 2025 to Sep 2026 | held, every figure as on 21 October | none |
| 02 | 83.57; 27.60 against 32.17, 86 percent; 0.46 times over 11.19 million | held | none |
| 03 | West hub: 23.86 against 30.63, 78 percent; 0.36 times; revenue 72.23 as plain text; the spans table still gives 23.85 | held | none (the cent between the capture file and the hub model stays a question, as above) |
| 04 | capture rates at the hub average 2019 70, 2021 48, 2025 85, 2026 87; the table of every hub and zone | held | none |
| 05 | CAISO: "CAISO holds one full year, 2025: USD 94.68"; 64.04; 25.89 against 28.54, 91 percent (25.88 and 28.53 on 21 October: the capture file was rebuilt since); 0.28 times | held | none |
| 06 | B as a PPA at 100.32: coverage 0.28 against 1.93; NPV -148.55 million against 12,385; IRR none against 12.0 percent; breakeven 100.31; 69.51 for 1.25 times | held | none |
| 07 | 81.40 per kW, 33 percent ancillary, 2.63 times; 8.14 million; a bad month 475,477 of 36; debt 2.26 million | held | none |
| 08 | the awards line: 2.25 against 0.40, 5.66 times, January to July 2026; Uri 57 percent of 105 months; the storage nodes' band: 335 days, 34.24, 48.90 and 65.84 against 47.26 at the hub, 57.7 percent wider | held | **fixed**: the page's source line named neither table these two draw from (`ercot_storage_dam_awards_monthly`, `node_basis_summary`) |
| 09 | 2 hours: 58.63, 46 percent, 3.82 times, 364,767 | held | none |
| 10 | 4 hours, day-ahead: 73.00, 35 percent, 2.26 times, 411,520 | held | none |
| 11 | CAISO: 65.22, 51 percent, 1.91 times, 459,656; NYISO and SPP "in review", ISO-NE and MISO "held, not shown: license needed", PJM "license needed" | held | none |
| 12 | by stream: energy 3.2 million, ancillary 3.33 million, Regulation Down 2.04 million, capacity not held, total 6.52 million, 65.22 per kW; the monitor's fleet 35 and 9 against the model's 42.50 and 42.32; "Leave out" ends with 5 to 8 October 2026 while the months end in September | held | none |
| 13 | built 21 Oct 2026: ERCOT Hub average day-ahead 42.21, 21 Oct (day +11.23, week -14.22); real time 26.56, 20 Oct; SP15 51.62 and SPP North 52.37, 21 Oct; Henry Hub 3.22, WTI 101.91, Brent 126.55, 14 Oct; spark 4.57, 18 Oct; lowest 42.21, highest 52.37, Brent minus WTI 24.64; the tables read, with their licenses, under the title | held | none (21 October's fault 2 is gone: the tile and the week now agree) |
| 14 | the workbench: 42.21 on 21 Oct, month -15.88, year -0.02, 7-day 30.81, 30-day 39.29, range 9.08 to 654.03; the hourly chart runs to 22 Oct, the spread's average 0.39; NYISO and ISO-NE rows read "licensed source needed" | held | none |
| 15 | ERCOT, every hub and zone: 12 rows; Houston real time 27.74 (20 Oct); West day-ahead 44.21 (21 Oct); no load zones | held | none |
| 16 | the week: 31 rows; ERCOT Hub average 42.21 on 21 Oct, week 30.81 (-10.70), on-peak 39.51, off-peak 28.95, RT minus DA -0.43, heat rate 11.08; NYISO New York City 52.60 on 22 Oct | held for ERCOT, CAISO and SPP | **not fixed**: see 2 below |

On a phone the first checked figure is 2,379 px down on the generator page (of 11,596), 2,268 on the battery page (of 7,376) and 569 on the board (of 5,667; 319 on 21 October, before the tables' line under the title).

What this walk found:

1. **Fixed (no ruling needed)**: the battery page's one source line (`SourceLine`, `components/tool/ToolPage.tsx`) named the five tables of its model and prices, but not the two tables of figures drawn under the income table on ERCOT: the awards line (`bsa|` keys, `data/battery_awards_beside.json`, whose `fleet_table` is `ercot_storage_dam_awards_monthly`) and the storage nodes' band (`series|node_basis_summary|...`). `app/cost-of-power/battery/page.tsx` now adds each to the line whenever its figures are drawn; CAISO's line is unchanged. Shots before and after at 1280 and 390: `docs/brand/review-585/foot-battery-*_{before,after}_{1280,390}.png`, the lines in `foot-before.json` and `foot-after.json`. No figure moved: `check-values` on every battery address, 748 of 748. `tests/test_session585.py`.
2. **Not fixed, for Samuel and the data machine**: the board's week table and its "week's highest real-time intervals" draw NYISO's (11 rows) and ISO-NE's (9 rows) prices, and 20 of the 40 intervals, on 22 October, while the power table above writes those grids as "licensed source needed". They come from `iso_trader_daily` and `iso_rt_top_intervals`, both "license needed from 2026-10-21" in `docs/licenses.md`; `build_week` in `warehouse/derived/board_page.py` does not consult `ls.held_grids()` as the rows' builder does, so 21 October's item 3 cleared the rows and not the week. The board's line of tables read and its downloads leave the two tables out (`board.json`'s sources do not name them, and `scripts/page_tables.py` reads the page's tables from there), and `check-holds.mjs` reads `data-check` keys, not the board's `data-n`, so it did not see them. How a held figure is drawn on the board and whether the check reads `data-n` wait on session 505's two items.
3. **Not fixed, for the data machine**: the awards line covers January to July 2026 while `ercot_storage_dam_awards_monthly` holds August 2026 since 21 October (`data/battery_awards_beside.json` was built on 10 October).
4. **Gone since 21 October**: the board's stale ERCOT rows (item 2 above), NYISO's and ISO-NE's rows in the power table (item 3: now "licensed source needed"), and the two downloads that answered 502 (item 4: `/api/download?table=ercot_as_prices` and `?table=eia_fuel_spot_prices` answer 200).
5. **Still for a ruling**: the first checked figure on a phone (item 5 above), and every "A trader would ask" above, none of which this walk built.

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
