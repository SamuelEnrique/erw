# The home battery game: method

Energy Research Warehouse (ERW).

- **Session 38:** the game.
- **Session 46:** v1.1.
- **Session 50:** v2: settings, difficulties, the fleet call modeled on ERCOT's ADER pilot, the tutorial, the house animation, and the replay.

The page is `/play/battery`. The rules live in `site/lib/battery.ts`, and the server's rescoring in `site/lib/game.ts` and `site/app/api/play/`.

## What is real and what is not

| Part | Real or assumed | Source |
|---|---|---|
| Prices | **Real.** ERCOT real-time settlement point prices at the hub average, HB_HUBAVG, every 15-minute interval of one operating day | today's level: `iso_rtm_hub_prices` (Supabase); the famous days: `ercot_all_hub_prices_history`, frozen in `site/data/battery_levels.json` by `warehouse/derived/battery_levels.py` |
| The battery, home and brand | **Fictional.** "Mockingbird Home Battery" is made up | none |
| The fleet | **Fictional.** 10,000 homes | none; the page sets it beside ERCOT's real operating battery fleet from `storage_capacity` (EIA-860M) |
| The fleet call | **A game rule** modeled on ERCOT's ADER pilot | below |
| Real tariffs, retail rates, grid fees, real program terms | **Left out** | below |

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

## The leaderboard: presets

- **What a preset is:** the difficulty, the usable energy, the power and the round-trip efficiency, plus, on Hard, the reserve and the degradation cost (`presetOf`). For example `normal:13.5-5-90` or `hard:13.5-5-90-r20-d0.11`.
- **How it is used:** a play is ranked only against plays of the same level and the same preset. The page also lists the other presets played that day.
- **What the server does:** it recomputes every score and the perfect-foresight score under the posted settings and difficulty. It refuses settings outside their ranges.

## The perfect-foresight optimum

- **The DP:** dynamic programming over every state of charge the three actions can reach, each state its exact value. Two paths that meet at one state keep the better.
- **The objective:** market cash, less the degradation cost, plus the fleet bonus. The reserve is enforced inside `step`, so no path crosses it.
- **The test** (`site/scripts/test-battery.mjs`):
  - On 12-interval toy days, every one of the 3^12 action sequences is simulated, and the best must equal the DP's score.
  - It runs under four presets: Hard with the default battery, Hard with a small battery whose reserve binds early, Easy with a large battery, and Normal.
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
  - the home's own load and any rooftop solar;
  - inverter limits beyond the continuous power;
  - temperature effects and calendar aging;
  - the state of charge's effect on efficiency.
- **Settlement detail:** the 5-minute dispatch inside each 15-minute interval, and Load Zone versus hub price differences.

## What is stored

Unchanged from session 38:
- **Public scores:** the level, an optional nickname, the score, the perfect-foresight score and the time.
- **Session 50 adds** the preset and the difficulty.
- **The research record of each play** (never shown): the actions, the score, and since session 50 the preset, the difficulty and the settings. No IP, no nickname.
- **The schema:** migration `warehouse/supabase/migrations/014_game_v2.sql` (columns only).
