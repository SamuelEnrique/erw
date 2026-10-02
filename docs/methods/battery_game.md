# The home battery game: method

Energy Research Warehouse (ERW).

- **Session 38:** the game.
- **Session 46:** v1.1.
- **Session 50:** v2: settings, difficulties, the fleet call modeled on ERCOT's ADER pilot, the tutorial, the house animation, and the replay.
- **Session 63:** v3: money, Hard's grid emergency, the simple page.
- **Session 66:** v4: lights out costs money, the spiked price is labeled on the number, the end screen's three lines, and Hard's add-ons with rooftop solar.

The page is `/play/battery`. The rules live in `site/lib/battery.ts`, and the server's rescoring in `site/lib/game.ts` and `site/app/api/play/`.

## What is real and what is not

| Part | Real or assumed | Source |
|---|---|---|
| Prices | **Real.** ERCOT real-time settlement point prices at the hub average, HB_HUBAVG, every 15-minute interval of one operating day; on the two California days (session 56), CAISO SP15 real-time prices, `iso_hub_prices_history` | today's level: `iso_rtm_hub_prices` (Supabase); the famous days: `ercot_all_hub_prices_history`, frozen in `site/data/battery_levels.json` by `warehouse/derived/battery_levels.py` |
| The battery, home and brand | **Fictional.** "Mockingbird Home Battery" is made up | none |
| The fleet | **Fictional.** 10,000 homes | none; the page sets it beside ERCOT's real operating battery fleet from `storage_capacity` (EIA-860M) |
| The fleet call | **A game rule** modeled on ERCOT's ADER pilot | below |
| Hard's spiked price, the outage, the lights-out charge | **Game rules.** A spiked price is never shown as a real one: the number carries "game rule, not a real price" and the real price beside it | "Version 3" and "Version 4" below |
| The rooftop array (Hard's add-on) | **A game rule** (5 kW) on a **real shape**: the grid's solar fleet that day, output per MW installed | EIA-930 generation by fuel over EIA-860M nameplate, frozen in `site/data/battery_levels.json` by `warehouse/derived/battery_solar.py`; "Version 4" below |
| Real tariffs, retail rates, grid fees, real program terms | **Left out** | below |

## The California days (session 56)

Two levels use California's prices: CAISO's real-time price at the SP15 trading hub (`TH_SP15_GEN-APND`). They are the 15-minute means of CAISO's 5-minute prices (`lmp_rtm_15m_mean`), every interval of a Pacific-time operating day. They come from `iso_hub_prices_history`, frozen in `site/data/battery_levels.json` by `warehouse/derived/battery_levels.py`.

Each day is chosen by a stated rule from the complete days the table holds (393 days, 2025-09-01 to 2026-09-29, when chosen). A day is complete when every interval is present. Nothing is filled.

| Level | The rule | The day, and its rule's number |
|---|---|---|
| CAISO SP15: the cheapest midday | the lowest mean price over the intervals starting 10:00 to 14:45 Pacific (10:00 to 15:00) | 2026-04-27: a mean of -22.13 USD/MWh |
| CAISO SP15: the steepest evening ramp | the largest rise from the mean of 12:00 to 15:00 Pacific to the mean of 18:00 to 21:00 | 2026-07-24: from 53.37 to 462.27 USD/MWh, a rise of 408.90 |

**What stays the same.** The battery, its settings and difficulties, the fleet call, the perfect-foresight optimum, the leaderboard by preset and the server's rescoring all work on these days as on the ERCOT days. On the page, the levels are grouped by grid, and the debrief names the grid and links its grid page.

**The fleet call is unchanged.** It is still a game rule modeled on ERCOT's ADER pilot, applied to California's prices.

**One limit: levels are keyed by date.** The game keys a level by its date (`game_scores.level_date`), so a California day may not share its date with an ERCOT level. The builder stops rather than choose another day if it would.

**The ERCOT days are frozen.** A run of the builder keeps the five ERCOT days as written in session 38, unless it is run with `--rebuild-ercot`. One of their rules reads a table that grows every day, so a rebuild could move a level, and its leaderboard, to another date.

## The battery's settings

Each setting has a default and a range. The player may change any of them, and the server checks them (`validSettings`).

| Setting | Default | Range, step | Source of the default |
|---|---|---|---|
| Usable energy | 13.5 kWh | 5 to 30, 0.5 | assumption: one home battery's usable energy, the session 38 game's |
| Continuous power | 5 kW | 1 to 11.5, 0.5 | assumption, the session 38 game's. ERCOT's ADER governing document gives "+/-5kW maximum discharge/charge" as its example of a battery's rated dispatchable range |
| Round-trip efficiency | 90 percent | 75 to 95, 1 | assumption, inside the 88 to 91 percent Lazard gives for residential standalone storage (LCOS v10.0, 2025) |
| Backup reserve | 20 percent of usable energy | 0 to 50, 5 | assumption: the share kept back for an outage (the prompt's default). Enforced on Hard |
| Degradation cost | $0.11 per kWh discharged | 0 to 0.30, 0.01 | Lazard LCOS v10.0 (below). Charged on Hard |

**The fixed rules:**
- The battery starts half full.
- Efficiency is split evenly: the square root of the round trip on the way in, and again on the way out.
- Each 15-minute interval at full power moves kW x 0.25 kWh at the meter.

**The degradation cost.** Lazard, *Levelized Cost of Energy+*, June 2025 (LCOS v10.0), "Levelized Cost of Storage: Key Assumptions", column "Residential Standalone (0.006 MW/0.025 MWh)":
- usable energy 0.025 MWh;
- initial capital cost (DC) $721 to $1,338 per kWh;
- lifetime storage output 158 MWh (90 percent depth of discharge, one cycle a day, 350 days a year, 20 years);
- efficiency 91 to 88 percent.

The default spreads the low end of the capital cost over the energy Lazard assumes the battery delivers in its life: 721 x 25 / 158,000 = $0.114 per kWh, rounded to $0.11. This treats the battery's whole cost as wear, which overstates the marginal cost of one more cycle for a battery that would otherwise age anyway. The range lets a player set it lower or higher.

**How the cost is charged:** per kWh taken out of the battery (before the outbound efficiency loss), so a kWh charged and later discharged is one kWh cycled.

**Not used:** NREL's Annual Technology Baseline residential battery page was the first choice, but its servers (atb.nrel.gov, docs.nrel.gov) did not resolve from this machine on 2026-10-01.

## Difficulties

| | Easy | Normal | Hard |
|---|---|---|---|
| Prices ahead | the next three hours as a band: each clock hour's lowest to highest real price | none | none |
| Backup reserve | not enforced | not enforced | enforced: discharge stops at it |
| Degradation cost | not charged | not charged | charged per kWh discharged |
| Settings | usable energy, power and efficiency apply | the same | all five apply |

- **Normal with the default battery is the session 38 game:** the same actions score the same (a test checks this). Every leaderboard row before v2 is of that preset.
- **Easy's band is real prices, not a forecast model:** it shows the range of each coming hour's real prices. A real forecast is noisier, so Easy is easier than real life.

## Version 3 (session 63): money, Hard's grid emergency, the simple page

Every rule in this section is a **game rule**, not a market rule. The prices stay ERCOT's (or CAISO's) real prices; on Hard the emergency changes them, and the page says so while it lasts. The rules live in `site/lib/battery.ts` (`START_MONEY`, `EMERGENCY`, `emergencyOf`, `outageDraw`, `simulate`, `optimum`; `RULES_VERSION = "v3"`).

- **Money.** Every play starts with $5 (`START_MONEY`). Money is $5 plus the market cash, less the degradation cost, plus the fleet bonus. In the first interval where it falls below $0 the game ends ("out of money"); the intervals after it count for nothing. The score is unchanged in meaning: what was earned, the money less the $5.
- **Hard's grid emergency, the spike.** In the day's VPP hour (the clock hour with the highest mean real price, `vppHour`), the price climbs toward the cap: interval k of the hour is `p + (5000 - p) x r_k`, with r = 0.25, 0.5, 0.75, 0.9 and p the real price. USD 5,000/MWh is ERCOT's offer cap since 2023; the game uses it on every grid, CAISO's days included. The fleet call keeps its hour, so the spike and the call coincide.
- **Hard's grid emergency, the outage.** The eight intervals (two hours) after the spike, clipped at the day's end, the grid is down: nothing can be bought or sold, whatever the player presses, and the house draws 1.5 kW from the battery. Each interval takes `1.5 x 15 / 60 / sqrt(round-trip)` kWh of charge, the same outbound loss as a sale; the backup reserve can be used, since this is what it is for.
- **Lights out.** If the battery holds less than one interval's draw at the start of an outage interval, the lights go out and the round ends there. The score so far stands. The page then says how much charge the outage needed (eight intervals' draw, or fewer if clipped) and how much the battery held when it began.
- **The perfect battery plays by the same rules.** The DP gains terminal states: a path that goes bankrupt or dark ends with the score it had, and competes with every path that continues. In the outage the only move is the forced draw. The brute-force test (all 3^12 sequences of each toy day) runs under these rules on all four presets, and new checks cover going bankrupt, the optimum never doing so, the spike's formula, the outage window, lights out and the ignored actions.
- **What the optimum did with lights out under version 3.** Since ending the round gave up only the rest of the day, the perfect battery sometimes chose it: with the default battery on Hard, on 2 of the 7 famous days (Uri, 2021-02-15, and the CAISO duck day, 2026-07-24) it sold into the spike and let the lights go out, because the later intervals were worth less than the extra charge sold at the spike. Version 4 (below) makes lights out cost money, and the perfect battery no longer does this.
- **The leaderboard.** A v3 preset ends `-v3` (`normal:13.5-5-90-v3`); plays are ranked only against the same preset, so a v3 play never meets a v2 one. A board from before reads "(v2 rules)". Migration `018_game_v3_digest_sends.sql` allows the suffix; the server parses and rescored every posted play with `simulate` and `optimum` under v3, as before.
- **The simple page.** `/play/battery` is now a page for a class: one sentence of instructions, the day, a Start button, then two big buttons (Charge, Sell), the battery and the price. It plays Normal with the default battery (no emergency), skips the tutorial, and shows only the score and the perfect battery's. The settings, the difficulties, the replay, the fleet map, the leaderboard and these notes are behind "More" (`/play/battery?more=1`, the full game). Each simple play is kept in the research record like any play (the default Normal preset); the simple page has no leaderboard form, so it posts no public score.

## Version 4 (session 66)

Every rule in this section is a **game rule**, not a market rule, and the page labels each as one. The rules live in `site/lib/battery.ts` (`LIGHTS_OUT`, `SPIKE_LABEL`, `shownPrices`, `worstHour`, `ADDONS`, `SOLAR`, `solarKwh`; `RULES_VERSION = "v4"`). The server's scorer (`site/lib/game.ts`, `scoreOn`), the perfect battery and the page all call the same `simulate` and `optimum`, as in version 3.

### Lights out costs money

- **The rule.** Lights out still ends the round (version 3's rule stands). In version 4 it also costs money: every remaining interval of the outage, the one the lights went out in included, charges the house's unserved energy, 1.5 kW for the interval (0.375 kWh), at **6 times the price cap**, USD 30,000/MWh. That is USD 11.25 for each fifteen minutes, and USD 90.00 for a whole two-hour outage.
- **Why.** A home without power in a grid emergency is the outcome the battery exists to prevent. Under version 3 the perfect battery let the house go dark on 2 of the 7 famous days (Uri and the CAISO duck day), because ending the round cost only the rest of the day. The game then taught that abandoning the house in a blackout is the best play.
- **Why 6 times the cap, and not the cap.** The rule was first priced at the cap itself, USD 5,000/MWh. The test (`site/scripts/test-battery.mjs`, "Part A") then asks, for each case where the lights can be kept on, whether the perfect battery still ends in lights out:

| Multiple of the cap | Cases where the perfect battery still goes dark |
|---|---|
| 1 (the cap itself) | 2: Winter Storm Uri (2021-02-15) on Hard with the default battery; the toy day "flat" with the 5 kWh test battery |
| 2, 3, 4, 5 | 1: Winter Storm Uri |
| 6 | none |

- **Why Uri is the hard case.** Its real prices sat near USD 9,000/MWh all day (ERCOT's cap in 2021), above the game's USD 5,000 cap, and the fleet bonus pays that price again. Keeping the lights on costs the perfect battery USD 10.92 of earnings that day (USD 155.71 lit, against USD 166.63 before any charge when it sells more and goes dark in the outage's last interval). Going dark there cost USD 1.88 at the cap and USD 9.38 at 5 times the cap, both less than USD 10.92; at 6 times it costs USD 11.25. 6 is the smallest whole multiple at which the perfect battery keeps the lights on in every case; the test finds it, and fails if `LIGHTS_OUT.multiple` is any other number.
- **The cases.** Each famous day on Hard with the default battery (and with rooftop solar where the level holds a shape), and every toy day with an outage under each Hard preset of the test, with and without the roof. "The lights can be kept on" means: for a famous day, the optimum under a prohibitive penalty stays lit; for a toy day, at least one of the 3^12 plays does.
- **What the rule does not promise.** The multiple is fixed for the cases above. A battery set far from the default (a much larger inverter, a tiny battery) on a day like Uri can still find going dark in the outage's last minutes worth it; the leaderboard ranks such presets only against themselves.
- **Money.** The charge can take the money below USD 0. The round has already ended at lights out, so the out-of-money rule has nothing left to end; the page says the charge took the money below USD 0.
- **With the rooftop array,** the unserved energy of each interval is the house's need less what the roof makes in it (never below zero).

### The spike is labeled on the number

- On Hard the dearest hour's prices are the game's, not the market's (version 3's spike). Wherever such a price is shown, the number itself carries "game rule, not a real price", and the real price of that interval is shown beside it: the big price number, the chart (the spiked stretch is drawn in the accent color with the label on it and the real price dashed beneath, and the label at the "now" line reads the same), the replay's price line, the end screen's hour, and the share text (which shows no price, and says the dearest hour's price is a game rule).
- **One source.** `shownPrices` writes every such text. A price is labeled when the price played differs from the real one. On Uri the dearest hour is already above the cap, so the game leaves it unchanged: those prices are real, and shown plain.
- **The test.** Every spiked price of the 7 famous days and the toy days carries the label and its real price, every other price is plain, and nothing is labeled off Hard. The page's source is also checked: `Game.tsx` never formats a played price itself.

### The end screen: three lines

After a play, on the simple page and in the full game:

1. what you earned;
2. what the perfect battery earned on the same day under the same rules;
3. the one clock hour where you lost the most against the perfect battery, what it did in that hour (charged, sold or held: what it did in most of the hour's intervals) and the average price of those intervals.

Every number comes from `simulate` (the play's result and the perfect plan's result) and from `worstHour`, which only sums the two results' own per-interval earnings (`gain`) by hour. The per-interval earnings add up to the score (a test checks it).

### Hard's add-ons: rooftop solar

- **Add-ons** are optional switches on Hard, off by default. The first is rooftop solar. A later one needs a key in `ADDONS`, its rule in `simulate` and `optimum`, and no new migration.
- **The rule.** A 5 kW rooftop array (a game rule). Each interval it makes 5 kW times the real hourly output per MW installed of that grid's solar fleet on the level's day.
- **Where the power goes.** While the battery charges, the roof's power goes into the battery for free, up to the battery's power and capacity limits, and what does not fit is sold at that interval's price. While the battery holds or sells, the roof's power is sold at that interval's price. In money this comes to one thing: the roof's power earns the interval's price whatever the battery does, since a kWh from the roof that charges the battery is a kWh not bought. A negative price is paid too.
- **In the outage** the roof carries the house first. What is left over charges the battery (up to its power and its room; the rest is lost, since the grid is down). What the roof does not cover comes from the battery.
- **Why charging is the player's choice.** A roof that always filled the battery on its own would move the battery's charge by a different amount each interval, and the perfect battery could no longer be computed exactly: the number of states of charge it must follow would grow past what a browser can do. With this rule the states stay as few as without the roof, and the optimum still equals brute force (the test runs it under two Hard presets with the roof).
- **The fleet call's bonus** counts the battery's deliveries only, not the roof's.
- **The source of the shape.** The same one the cost-of-power seller tab uses for a solar farm (`warehouse/derived/merchant_revenue.py`, whose functions the builder calls): EIA-930 hourly generation by fuel (the balancing authority's "Adjusted SUN Gen") over the solar nameplate installed in that balancing authority that month (EIA-860M operating and retired generators). ERCOT levels read ERCO, California levels CISO. `warehouse/derived/battery_solar.py` writes each level's shape into `site/data/battery_levels.json` (`solar`, one value per interval, each hour's value on its four intervals; `solar_source`).
- **It is the whole fleet's shape, not one roof's,** and the page says so. A fleet of plants across a state is smoother than one roof under one cloud, and utility plants track the sun.
- **Between 0 and 1.** The values are kept as EIA reports them. The game uses each between 0 and 1: a roof draws nothing at night (EIA reports a fleet's station use as negative output), and makes no more than its rating (EIA-860M lists new plants late, so a growing fleet can read above its nameplate).
- **Real data only.** A level gets a shape only when every hour of its day is held. Where it is not, the add-on is unavailable for that level and the page says so; the server refuses such a play. Nothing is filled. Today's level has no shape (the live set holds none), so the add-on is unavailable on it.

### Presets, boards and the schema

- A version 4 preset ends `-v4`; on Hard the add-ons that are on come just before it: `normal:13.5-5-90-v4`, `hard:13.5-5-90-r20-d0.11-v4`, `hard:13.5-5-90-r20-d0.11-solar-v4`.
- A board ranks only plays with the same rules and add-ons. `parsePreset` still reads version 2 and version 3 presets, and their boards are labeled "(v2 rules)" and "(v3 rules)".
- Migration `warehouse/supabase/migrations/019_game_v4.sql` lets the preset checks of `game_scores` and `game_plays` take `-v4` and the add-on words. Constraints only.

## The leaderboard: presets

- **What a preset is:** the difficulty, the usable energy, the power and the round-trip efficiency, plus, on Hard, the reserve and the degradation cost (`presetOf`). For example `normal:13.5-5-90` or `hard:13.5-5-90-r20-d0.11`.
- **How it is used:** a play is ranked only against plays of the same level and the same preset. The page also lists the other presets played that day.
- **What the server does:** it recomputes every score and the perfect-foresight score under the posted settings and difficulty. It refuses settings outside their ranges.

## The perfect-foresight optimum

- **The DP:** dynamic programming over every state of charge the three actions can reach, each state its exact value. Two paths that meet at one state keep the better.
- **The objective:** market cash, less the degradation cost, plus the fleet bonus. The reserve is enforced inside `step`, so no path crosses it.
- **The test** (`site/scripts/test-battery.mjs`):
  - On 12-interval toy days, every one of the 3^12 action sequences is simulated, and the best must equal the DP's score.
  - It runs under six presets: Hard with the default battery, Hard with a small battery whose reserve binds early, Easy with a large battery, Normal, and (session 66) the two Hard presets again with rooftop solar on a toy shape.
  - Replaying the DP's actions must score the same, and the reserve must never be crossed.
- **Timing:** on the five famous days the DP takes 20 to 42 ms.

## The fleet call, and ERCOT's ADER pilot

**The real program the call is modeled on.** ERCOT, *Aggregate Distributed Energy Resource (ADER) Pilot Project Governing Document, Phase 3.3* (updated 2026-06-02; https://www.ercot.com/files/docs/2026/03/02/ADER-Pilot-Project-Governing-Document-Phase-3.3.docx, from https://www.ercot.com/mktrules/pilots/ader, read 2026-10-01):
- It defines an ADER as "a Resource consisting of multiple Premises or devices connected at the distribution system level that has the ability in aggregate to respond to ERCOT Dispatch Instructions".
- Each Premise has "the capability of 1 MW or less".
- An ADER participating as an Aggregate Load Resource is dispatched through Security-Constrained Economic Dispatch (SCED). Its energy is settled at a market price: "the Load Zone price will be used for Settlement of energy". An injection is valued "as negative Load".
- Qualified ADERs may provide ERCOT Contingency Reserve Service (ECRS) and Non-Spinning Reserve (Non-Spin). Phase 3 is limited to "no greater than 500 MW system wide", with at most 100 MW of each of those services.
- The deployment test "will last for at least one full 15-minute Settlement Interval".

**The game's call, and what it simplifies:**

| | The game | The pilot |
|---|---|---|
| When | the day's dearest clock hour (the earliest on a tie), known to the game | whenever SCED (every five minutes) or an ancillary-service deployment calls for it; nobody knows the dearest hour in advance |
| Notice | 15 minutes: one interval's warning, then the hour | none set out for SCED energy dispatch |
| Length | one hour (four intervals) | as long as the instruction; the test lasts at least one 15-minute interval |
| Energy | every kWh sold earns the hub's real-time price | settled at the Load Zone price; the game uses the hub average |
| Bonus | each kWh delivered in the call hour earns the hour's mean price again (never below zero) | no such bonus. ADERs may earn ECRS and Non-Spin payments, whose prices the warehouse does not hold, and a home's own payment is set by its retailer or aggregator, not by ERCOT. **The bonus is the game's stand-in, labelled so** |
| Reserve | on Hard, never discharged below, even in the call | the pilot document sets no household reserve; a home's backup reserve is the owner's or the aggregator's setting |
| Fleet | 10,000 homes, 50 MW | Phase 3 limit 500 MW system-wide |

**Left out of the game:** the pilot's telemetry and metering rules, qualification, Base Point Deviation, ancillary-service awards and their prices, the Distribution Service Provider's review, and the Logical Resource Node pricing the pilot studies.

## The replay

- **What plays back:** after a game, the perfect battery's day (the same battery and rules, every price known) beside the player's, as two states of charge over the day. There is a cursor, a scrubber and a 20-second playback.
- **The reasons:** at each switch of the perfect plan, one line read from the prices (`explain`):
  - **charged or sold** "the cheapest (dearest) N of the night, morning, afternoon or evening", when the run is exactly that period's cheapest (dearest) intervals; otherwise "cheaper (dearer) than P percent of the day's prices";
  - **"; the fleet call"**, added when a sale overlaps the call hour;
  - **held:** "reserve" (at the backup reserve, on Hard), "full, waiting to sell at HH:MM", "empty, waiting to charge at HH:MM", or "no price before HH:MM pays for the round trip".

## The tutorial and the animation

- **The tutorial:** four cards of about 7.5 seconds each (30 seconds), skippable. It is shown on the first visit and remembered in the browser's own storage (`erw.battery.tutorial.v2`), wrapped in try/catch: where storage is blocked it shows again, and nothing else changes.
- **The last settings and difficulty** are remembered the same way. Nothing is sent anywhere.
- **The house and its battery** (SVG):
  - charge flows in from a pylon along the wire, and discharge flows out;
  - the battery fills with its state of charge, and the reserve line is drawn on Hard;
  - motion stops under `prefers-reduced-motion`.

## What the game leaves out

- **The customer's side:** retail electricity rates and time-of-use tariffs, transmission and distribution charges, and fixed fees. The battery buys and sells at the wholesale real-time price, which no household does.
- **Real program terms:** ERCOT's ADER pilot is the model, but the bonus, the notice, the hour and the reserve rule are the game's.
- **Taxes and incentives:** the federal storage tax credit and any utility incentive.
- **Physics the model skips:**
  - the home's own load outside Hard's outage, and any rooftop solar outside Hard's add-on (which uses a fleet's shape, not a roof's);
  - inverter limits beyond the continuous power;
  - temperature effects and calendar aging;
  - the state of charge's effect on efficiency.
- **Settlement detail:** the 5-minute dispatch inside each 15-minute interval, and Load Zone versus hub price differences.

## What is stored

Unchanged from session 38:
- **Public scores:** the level, an optional nickname, the score, the perfect-foresight score and the time.
- **Session 50 adds** the preset and the difficulty.
- **The research record of each play** (never shown): the actions, the score, and since session 50 the preset, the difficulty and the settings. No IP, no nickname.
- **The schema:** migration `warehouse/supabase/migrations/014_game_v2.sql` (columns only); session 63's `018_game_v3_digest_sends.sql` lets a preset end `-v3`; session 66's `019_game_v4.sql` lets it end `-v4` with the add-ons before it. The add-ons of a play are stored in its preset.
