# Session 50 report: the battery game v2

Energy Research Warehouse (ERW), session 50, run 2026-10-01 from 09:29 to about 10:25 UTC. **Wall time about 56 minutes.**

**API spend: USD 0.00, confirmed.** No model call, no data pull. Reading ERCOT's governing document and Lazard's study counts as reading sources, not pulls. No force push. Nothing released on Redivis, and no new Supabase table.

## Supabase, before and after the vacuum

- **The vacuum:** the weekly-vacuum workflow was dispatched once, as approved: run 36843123681 at 09:30 UTC, success.
  - **359.4 MB to 356.6 MB.** The workflow recorded the sizes in `run_status.csv` (e5662ad, merged).
  - The prompt expected about 394 MB, but session 49's own dispatch had already brought it to 356.2.
- **The game tables gained columns, no table:** migration `014_game_v2.sql` adds `preset` and `difficulty` to `game_scores`, and `preset`, `difficulty` and `settings` (JSON) to `game_plays`.
  - The defaults fill the earlier rows with the v1 preset, `normal:13.5-5-90`.
  - The anon key may insert them and read them on `game_scores`, and still cannot read `game_plays`.
- **At the end: 356.6 MB.**

## What changed, and why

1. **The battery's settings** (`site/lib/battery.ts` `SETTINGS`). Usable kWh, continuous kW, round-trip efficiency, backup reserve and degradation cost per kWh discharged.
   - Each has a default, a range, a step and a source; the panel shows all of them, and every one is editable within its range.
   - The DP optimum, the server's rescoring and the leaderboard all use them.
   - The server refuses settings out of range or off their step.
2. **Difficulties.**
   - **Easy:** the next three hours as a band, each coming clock hour's lowest to highest real price.
   - **Normal:** the session 38 game, with no reserve and no wear. The same actions score the same; a test checks it.
   - **Hard:** no forecast; the reserve is enforced and every kWh discharged pays the degradation cost.
3. **The leaderboard groups by preset** (`presetOf`): the difficulty, the kWh, kW and efficiency, plus, on Hard, the reserve and the wear.
   - A play is ranked only against plays of the same level and preset.
   - The page lists the other presets played that day.
4. **The fleet call, modeled on ERCOT's ADER pilot:**
   - a 15-minute warning before the call hour;
   - a page section, "The fleet call: how it mirrors ERCOT's ADER pilot", that quotes the governing document and lists each simplification.
   - The bonus rule is unchanged and labelled as the game's stand-in.
5. **A 30-second first-run tutorial:** four cards of about 7.5 seconds, skippable, remembered in browser storage behind try/catch.
   - The last settings and difficulty are remembered the same way.
   - "How to play (30 seconds)" brings the tutorial back.
6. **The house-and-battery animation** (SVG):
   - charge flows in from a pylon along the wire, discharge flows out;
   - the battery fills with its charge, and the reserve line shows on Hard;
   - "Held: the battery is at its backup reserve" appears when Sell is held at the reserve;
   - no motion under `prefers-reduced-motion`.
7. **The replay.** After a game, the perfect battery's day (the same battery and rules) plays back beside the player's.
   - Both states of charge are shown over 20 seconds, with a scrubber and the day's price faint behind them.
   - At each switch of the perfect plan there is one line read from the prices (`explain`): "charged: the cheapest two hours of the morning", "sold: dearer than 92 percent of the day's prices; the fleet call", "held: reserve, until it can charge at HH:MM", "held: full, waiting to sell at HH:MM".
   - Every switch is listed below the chart. Today's level had 23.
8. **Mobile polish at 380 px:**
   - the game scrolls into view when it starts;
   - the forecast label shortens on narrow screens;
   - the house and the state of charge stack.
   - Measured: nothing on the page is wider than the window (scrollWidth 380), mid-game and after it.
9. **The loop's self-reference** (a lint error since v1, react-hooks/immutability) now goes through a ref.
10. **Docs:** `docs/methods/battery_game.md` (the method) and `docs/reviews/henry-questions.md` (the ten questions).

## Every assumption, with its source

| Assumption | Value | Source |
|---|---|---|
| Usable energy | 13.5 kWh (5 to 30) | assumption, the session 38 game's |
| Continuous power | 5 kW (1 to 11.5) | assumption, the session 38 game's; the ADER governing document's own example of a battery is "+/-5kW maximum discharge/charge" |
| Round-trip efficiency | 90 percent (75 to 95), split evenly in and out | assumption, inside Lazard's 91 to 88 percent for residential standalone storage |
| Backup reserve | 20 percent (0 to 50), on Hard | assumption, the prompt's default |
| Degradation cost | $0.11 per kWh discharged (0 to 0.30), on Hard | Lazard, *Levelized Cost of Energy+*, June 2025, LCOS v10.0, Key Assumptions, Residential Standalone (0.006 MW / 0.025 MWh): initial capital cost (DC) $721 to $1,338 per kWh; lifetime storage output 158 MWh. 721 x 25 / 158,000 = $0.114, rounded |
| Start of day | half full | assumption, session 38 |
| The fleet | 10,000 homes, 50 MW | fictional |
| The brand | "Mockingbird Home Battery" | fictional |
| Prices | ERCOT HB_HUBAVG real-time, every interval | real: `iso_rtm_hub_prices`, `ercot_all_hub_prices_history` |

- **The degradation cost is a whole-battery proxy:** capital over lifetime throughput, which overstates the cost of one more cycle. The method says so, and question 3 of the review asks Henry for a better one.
- **NREL's Annual Technology Baseline**, the first choice for the cost, could not be read: atb.nrel.gov and docs.nrel.gov did not resolve from this machine.
- **Lazard's PDF** is saved in the scratchpad only. Its terms forbid redistribution, so only two cited figures are quoted.

## Reading ERCOT's ADER pilot, and the simplifications

**The source:** ERCOT, *Aggregate Distributed Energy Resource (ADER) Pilot Project Governing Document, Phase 3.3* (updated 2026-06-02), https://www.ercot.com/files/docs/2026/03/02/ADER-Pilot-Project-Governing-Document-Phase-3.3.docx, linked from https://www.ercot.com/mktrules/pilots/ader. Read as text on 2026-10-01; every quotation below was checked against it.

**What it says that the game uses:**
- An ADER is "a Resource consisting of multiple Premises or devices connected at the distribution system level that has the ability in aggregate to respond to ERCOT Dispatch Instructions"; its Premises have "the capability of 1 MW or less".
- As an Aggregate Load Resource it is dispatched through SCED, and "the Load Zone price will be used for Settlement of energy"; an injection is valued "as negative Load".
- Qualified ADERs may provide ECRS and Non-Spin.
- Phase 3's total registered capacity must be "no greater than 500 MW system wide", with at most 100 MW of each service.
- The deployment test "will last for at least one full 15-minute Settlement Interval".

**The game's simplifications, each on the page and in the method:**
- **When:** the call hour is the day's dearest clock hour, known to the game. Real dispatch is SCED's, every five minutes, unknown in advance.
- **Notice:** a 15-minute warning, the game's choice. The document sets out none for energy dispatch.
- **Length:** one hour. The real length is the instruction's.
- **Energy price:** the hub average, not the battery's Load Zone price.
- **The bonus** (the hour's mean price per kWh delivered) is the game's stand-in for what an aggregator may pass on. The pilot pays ancillary-service awards whose prices the warehouse does not hold, and a home's own payment is its retailer's or aggregator's.
- **The reserve rule** is the game's. The pilot sets no household reserve.
- **Left out:** telemetry, qualification, Base Point Deviation and ancillary-service awards.

## The questions file

`docs/reviews/henry-questions.md` holds ten questions for a former Tesla battery engineer. Each is tied to one setting or rule and ends with "*Decides:*" and the line of code it would change:
1. kWh and kW defaults and bounds;
2. the efficiency split;
3. the degradation proxy;
4. where wear is charged;
5. whether the call may dip into the reserve;
6. the start of day;
7. the call's notice and length;
8. how Texas VPP homes are actually paid;
9. power taper near full and empty;
10. which missing piece (home load, solar, retail rates) to add first.

## Verify and ship

**The DP against brute force with reserve and degradation** (`site/scripts/test-battery.mjs`):
- Every one of the 3^12 action sequences on four toy days, under four presets:
  - Hard, default battery;
  - Hard, 5 kWh / 2.5 kW / 85 percent / reserve 30 / wear $0.20;
  - Easy, 20 kWh / 10 kW / 92 percent;
  - Normal, default battery.
- The DP equals brute force in all 16 cases, its actions replay to the same score, and no path crosses the reserve.
- Normal with the default battery scores as v1. The settings check, the presets and the reasons are tested too.
- The DP takes 20 to 42 ms on the five famous days.

**Server rescoring under each preset** (`site/scripts/play-battery.mjs`, plays marked as ERW checks), local and live: one play each on Easy, Normal, Hard and a custom Hard battery, on 2023-08-10.

| Preset | Server score | Library score | Server optimum | Library optimum |
|---|---|---|---|---|
| Easy (default battery) | 41.5991 | 41.5991 | 60.971 | 60.9710 |
| Normal (default battery) | 41.5991 | 41.5991 | 60.971 | 60.9710 |
| Hard (default battery) | 24.2025 | 24.2025 | 52.7028 | 52.7028 |
| Hard, custom | 8.9809 | 8.9809 | 37.1156 | 37.1156 |

- Easy scores as Normal: the band changes what you see, not the rules.
- The stored presets are the ones played.
- A setting out of range and an unknown difficulty are refused (HTTP 400).

**Frame time** (`site/scripts/frametime-battery.mjs`):

| Run | Window | Frames | Mean | 99th percentile | Longest |
|---|---|---|---|---|---|
| Visible Chrome window, Easy game playing, 1280 px | visible | 288 in 20 s | 33.33 ms | 33.9 ms | 34.9 ms |
| Headless, full 90-second game, local, 380 px | | 2,889 | 33.34 ms | 34.1 ms | 49.9 ms |
| Headless, live site, 380 px | | 902 in 15 s | 16.67 ms (60 Hz) | | 17.5 ms |

- **The visible run:** 288 frames over 20 s means the window was covered partway; all of them were measured while the game played (its clock read 02:30), and none were over 50 ms. On this machine Chrome ran the visible window at 30 frames a second, so frames are 33.3 ms by the display's pacing, not the game's cost.
- **The browser extension's own window:** it reported `visibilityState` "hidden" throughout, so it could not be used. A separate visible Chrome window was started instead; on several launches Windows opened it behind other windows (hidden, no frames).
- **Other checks:**
  - After a full game, the end screen and the replay render (23 switches), and the server verified the score.
  - No page errors in the runs that captured them.
  - **One unexplained stall:** in one of about ten automated runs the game stayed at 00:00 with no error. It did not recur in six more runs.

**check-routes and check-values:**
- check-routes now covers `/data/methods/battery_game`. Local and live: 60 of 60 routes.
- check-values: local 2,466 of 2,466, live 2,381 of 2,381.

**Tests:**
- `tests/test_session50.py`, 7 tests: test-battery under each preset, the Lazard trace, the v1 defaults, migration 014 adding columns only, the docs and their quotes, and the storage guards.
- With sessions 38 and 46: 15 tests, OK.

**Deploy:** pushed e5662ad..57dd30c. The live page shows the ADER section.

## Decisions made without a human

1. **Normal and Easy do not enforce the reserve or the wear.** The prompt describes Hard as "reserve enforced, degradation on" and Normal "as now", so the reserve and degradation settings apply on Hard only, and the panel says so beside them. Usable energy, power and efficiency apply on every difficulty.
2. **Easy's band is real prices:** each coming hour's real range, not a forecast model. It is labelled so.
3. **The degradation default is from Lazard,** not NREL (unreachable). It uses the low end of Lazard's capital range.
4. **The bonus is kept:** the same rule as v1, relabelled as a stand-in, so v1 scores stay comparable on Normal.
5. **Old leaderboard rows** were filled with the v1 preset by the migration's default: they were all played on Normal with the default battery.
6. **Frame time came from a separate visible Chrome window,** started by a script, because the extension's window was hidden.

## Open questions

1. **Henry's answers** decide the reserve-in-call rule, the degradation proxy and the call's timing. See the questions file.
2. **The leaderboard on the pick screen** lists the initial preset (Normal, default battery) until you post. Should it reload for the chosen preset? That needs a small read route.
3. **Frame time at the display's full rate** was measured headless at 60 Hz. The visible window here ran at 30 Hz. A check on a phone would settle it.
4. **The one stalled automated run** (clock at 00:00, no error) did not recur. Watch for reports of a game that does not start.
