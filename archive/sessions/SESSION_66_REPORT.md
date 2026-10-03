# Session 66 report: home battery game v4

Energy Research Warehouse (ERW), session 66, in the separate worktree `C:\Users\samen\Documents\erw-game` on the branch `wip/066-battery-game-v4`, 2026-10-02 about 17:30 to 20:45 UTC. Game code only. **Model spend: USD 0.00** (the cap was USD 0.00). No paid service, no pulls, no model calls, no force push. No Supabase write, migration 019 written and **not applied**, the data lock not taken, no builder run, nothing pushed to main or to any `task/` branch. The main folder (`C:\Users\samen\Documents\erw`) was not read, written or used for git; only its Python interpreter was called by path. The finish step below was **not run**.

## To finish

Run these on the machine that holds the raw EIA-930 workbooks and `warehouse/output` (the main folder), after session 65 is done with it. Version 4 is not live until step 4.

**1. Take the data lock** (in the main folder):

```bash
python warehouse/lock.py acquire --task "session 66 finish: migration 019, battery solar shapes" --minutes 90 --wait 30
```

**2. Apply migration 019** (in the main folder, with a copy of the branch's file; `apply.py` applies every migration in order and each is idempotent):

```bash
git fetch origin
git show origin/wip/066-battery-game-v4:warehouse/supabase/migrations/019_game_v4.sql > warehouse/supabase/migrations/019_game_v4.sql
python warehouse/supabase/apply.py
rm warehouse/supabase/migrations/019_game_v4.sql
```

The copy is removed after it is applied so that the merge in step 4, which brings the same file, finds nothing in its way.

It only replaces the preset checks of `game_scores` and `game_plays`. Old v2 and v3 rows stay valid. Until it is applied the database refuses a v4 play, and the page says the play was not stored.

**3. Run the Part D builder** (from this worktree, reading the main folder's data; it writes only `site/data/battery_levels.json` here):

```bash
cd C:/Users/samen/Documents/erw-game
C:/Users/samen/Documents/erw/.venv/Scripts/python.exe warehouse/derived/battery_solar.py --data-root C:/Users/samen/Documents/erw --dry-run
C:/Users/samen/Documents/erw/.venv/Scripts/python.exe warehouse/derived/battery_solar.py --data-root C:/Users/samen/Documents/erw
C:/Users/samen/Documents/erw/.venv/Scripts/python.exe -m unittest tests.test_session66 tests.test_session38 tests.test_session56 tests.test_session50
git add site/data/battery_levels.json
git commit -m "Session 66: the famous days' solar shapes (EIA-930 over EIA-860M), written by battery_solar.py"
```

Read the dry run first: it prints, per level, the shape's highest and lowest hour, or why a level has no shape. A level without every hour of its day gets none, and the rooftop add-on stays unavailable for it. The add-on is switched on for a real level by this step and nothing else.

**4. Merge the branch to main** (a push to a `task/` branch runs code-branch.yml: the tests, the site build and check-routes, then the merge and the deploy):

```bash
git push origin wip/066-battery-game-v4:task/066-battery-game-v4
```

**5. Release the lock** (in the main folder):

```bash
python warehouse/lock.py release
```

**6. The live checks**, once the deploy is up (about a minute after the merge):

```bash
cd site
node scripts/check-routes.mjs https://erw-flame.vercel.app
node scripts/check-lights.mjs https://erw-flame.vercel.app
node scripts/play-battery.mjs https://erw-flame.vercel.app
```

- `check-lights.mjs` reads the levels the site serves, today's level included, and checks that the perfect battery never ends in lights out. It posts nothing.
- `play-battery.mjs` posts one v4 play per difficulty (Easy, Normal, Hard, a custom Hard battery) and both add-on states on Hard: off (section 4) and rooftop solar on (section 6, on a famous day that holds a shape), each marked as an ERW check so it stays off the boards. It also checks that the roof is refused on a day without a shape, and that v2 and v3 boards still read. It makes more than 30 requests, the API's hourly floor from one address: if the later checks answer HTTP 429, wait an hour and run it again.
- In a browser: play Hard on 2026-07-24 and watch the spike hour (the number reads "game rule, not a real price" with the real price beside it), then the end screen's three lines.

## In plain words

**Lights out now costs money.** The round still ends when the lights go out. Now every fifteen minutes left of the outage also charges the house's unserved energy (1.5 kW, 0.375 kWh) at 6 times the USD 5,000/MWh price cap: USD 11.25 for each fifteen minutes, USD 90.00 for a whole outage. The page says it is a game rule and why: a home without power in a grid emergency is the outcome the battery exists to prevent.

**Why 6 times the cap and not the cap.** Priced at the cap itself, the perfect battery still let the house go dark on Winter Storm Uri, and on one test day. The prompt's rule for that case was followed: the failing days are reported below, the smallest whole multiple that fixes them is 6, it is applied, and the page and the method state it. A test finds the multiple and fails if the code holds any other number.

**The spiked price can no longer be read as real.** Wherever a spike price is shown, the number itself says "game rule, not a real price" and shows the real price beside it: the big price number, the chart (the spiked stretch in red, the real price dashed under it), the replay, the end screen, and the share text.

**The end screen is three plain lines,** on the simple page and in the full game: what you earned; what the perfect battery earned on the same day under the same rules; and the one hour where you lost the most, with what the perfect battery did then and at what price.

**Hard has an "Add-ons" section, with one add-on: rooftop solar.** A 5 kW array (a game rule) that follows the real hourly output of the grid's whole solar fleet on the level's day. It is off by default. **It is unavailable on every level until step 3 above is run**, because the shape is not served to the game yet; the page says so on each level, and the server refuses such a play. Nothing is filled.

**One bug from version 3 was found and fixed.** During a Hard game the page scored the whole day after every interval, as if the player did nothing for the rest of it. So the charge shown had the coming outage already taken out (6.75 kWh read as 3.59), and a player who sold down early, meaning to recharge, would have had the round ended on the spot. It was seen in the browser, fixed, and tested.

## The perfect battery on the 7 famous days under v4

Default battery. "Hard with solar" cannot be computed yet: no level holds a solar shape until step 3.

| Day | Hard, USD | Hard ends | Charge at the outage's start, kWh (need 3.16) | Hard with solar | Normal, USD | Normal ends |
|---|---|---|---|---|---|---|
| 2021-02-15 Uri | 155.71 | whole day, lights on | 4.02 | no shape held yet | 240.23 | whole day |
| 2023-08-10 ERCOT heat | 49.01 | whole day, lights on | 5.59 | no shape held yet | 60.97 | whole day |
| 2026-04-26 calm | 29.49 | whole day, lights on | 3.85 | no shape held yet | 0.44 | whole day |
| 2026-08-29 solar | 29.61 | whole day, lights on | 3.85 | no shape held yet | 0.93 | whole day |
| 2025-01-05 negative | 29.72 | whole day, lights on | 8.23 | no shape held yet | 0.79 | whole day |
| 2026-04-27 CAISO solar noon | 29.71 | whole day, lights on | 8.23 | no shape held yet | 0.83 | whole day |
| 2026-07-24 CAISO duck | 34.33 | whole day, lights on | 3.32 | no shape held yet | 12.98 | whole day |

- Under version 3 Uri earned 166.80 and the duck day 34.38, both ending in lights out. Keeping the house lit costs the perfect battery USD 11.09 on Uri and USD 0.05 on the duck day.
- Today's level as the live site serves it (2026-09-30): Hard 29.58 USD, a whole day, 3.85 kWh at the outage's start.
- After step 3, `node scripts/test-battery.mjs` prints this table with the solar column filled (its lines begin "v4,").

**Part A, the days where the cap-priced penalty failed** (15 cases: the 7 famous days on Hard, and the 8 toy days with an outage under the four Hard test presets; the lights can be kept on in all 15):

| Multiple of the cap | The perfect battery still ends in lights out on |
|---|---|
| 1 | Uri (2021-02-15), Hard, default battery; the toy day "flat" with the 5 kWh test battery |
| 2, 3, 4, 5 | Uri |
| 6 | none (nor at 7, 8, 9 or 16) |

Uri is the hard case because its real prices sat near USD 9,000/MWh, above the game's USD 5,000 cap, and the fleet bonus pays the price again. Going dark in the outage's last fifteen minutes cost USD 1.88 at the cap; staying lit costs USD 10.92 of earnings.

## What changed

| File | Change |
|---|---|
| `site/lib/battery.ts` | `RULES_VERSION = "v4"`; `LIGHTS_OUT` (multiple 6), the penalty in `simulate` and in the DP's lights-out terminal; `SPIKE_LABEL`, `shownPrices`; `worstHour`; `ADDONS`, `SOLAR`, `validAddons`, `validSolar`, `solarKwh`; `Result` gains `penalty`, `unservedKwh`, `solar`, `solarKwh`, `gain`; `simulate` takes the solar shape and `upto`; presets end `-v4` and carry the add-ons; `parsePreset` returns the version and reads v2 and v3 |
| `site/lib/game.ts` | `scoreOn` (the scorer, callable without the database), add-ons checked, the roof refused where the level has no shape |
| `site/lib/levels.ts` | a level may hold `solar` and `solar_source` |
| `site/app/api/play/*/route.ts` | the body's `addons`; v4 examples |
| `site/app/play/battery/Game.tsx` | `EndLines`, `EarlyEnd`, `PriceNow`; the Add-ons section; the labeled chart; mid-game scoring of the intervals played only |
| `site/app/play/battery/page.tsx` | "The game's rules (version 4)"; the level's shape passed to the game |
| `warehouse/supabase/migrations/019_game_v4.sql` | the preset checks take `-v4` and the add-on words. **Written, not applied** |
| `warehouse/derived/battery_solar.py` | each famous day's solar shape, from the seller tab's own functions. **Written, not run** |
| `site/scripts/test-battery.mjs` | v4 checks (below) |
| `site/scripts/check-scorer.mjs`, `alias-loader.mjs`, `alias-register.mjs` | the server's scorer against the library, called directly |
| `site/scripts/check-lights.mjs` | Part A on the levels a running site serves |
| `site/scripts/play-battery.mjs` | the add-on's live checks (for step 6) |
| `docs/methods/battery_game.md` | "Version 4 (session 66)" |
| `tests/test_session66.py`, `tests/test_session50.py` | 17 new tests; the v4 preset line |

## Test results

- **`site/scripts/test-battery.mjs`: all pass.** The DP optimum equals brute force over all 3^12 action sequences on the four toy days under six presets: Hard default, Hard with a 5 kWh battery, Easy, Normal, and the two Hard presets with rooftop solar on a toy shape, with the outage and the penalty in play. Part A's required result and the multiple. Part B: 40 spiked prices each carry the label and the real price, 680 real prices are plain, nothing is labeled off Hard, and `Game.tsx` formats no played price itself. Part C's hour. The roof's rules. Presets round trip; v2 and v3 boards read.
- **Python: 275 tests, all pass, 30 skipped** (`python -m unittest discover -s tests`, the main folder's interpreter by path). The skips are tests that read `warehouse/output` tables, which this worktree does not hold. `tests/test_session66.py` adds 17.
- **The server's scorer and `lib/battery.ts` agree under v4** (`check-scorer.mjs`, calling `scoreOn` directly, nothing posted): 84 plays on the 7 famous days (three plays under each of four presets), 3 on a toy day with the roof and with lights out, and 14 refusals.
- **`tsc --noEmit`: pass. `npm run build`: pass.**
- **eslint: the files this session touched pass with no warning. The whole site does not:** `npx eslint` reports 8 errors and 5 warnings in 9 files this session did not touch (`app/about/page.tsx`, `app/companies/CompaniesTable.tsx`, `app/internal/costs/page.tsx`, `app/severance/Calculator.tsx`, `components/AnalysisGallery.tsx` and others). They are on main as it stands; they were left alone as outside this session's scope.
- **Local site** (the build, port 3066): check-routes 68 of 68 pages pass. This folder has no Supabase key, so there was no baseline and the pages that read Supabase showed "no data".
- **In Chrome, on the local site:** Hard on 2026-07-24 played through: the spike's label on the big number and on the chart, the outage banner, the three end lines (the hour lost most was 19:00 to 20:00, its price labeled). The simple page on 2023-08-10: the three lines, the real price plain. The Add-ons switch shows as unavailable with its reason. The page's own end-of-game call to `/api/play/finish` ran; with no key in this folder nothing could be stored.
- **Not checked:** the rooftop add-on switched on in the real page, since no level holds a shape. It is covered by the library tests, the scorer check and brute force on toy days only. `check-values.mjs` was not run (it needs the Supabase key).

## Errors and decisions

- **Decision, the largest: the roof charges the battery only while the player charges.** The prompt says the roof's energy charges the battery for free and what does not fit is sold. A roof that charged the battery by itself in every interval would move the charge by a different amount each time, and the perfect battery could no longer be computed exactly in a browser (the states it must follow multiply with every sunny interval; this was reasoned, not measured). The prompt also requires the DP to equal brute force with solar. So: while the battery charges, the roof's power goes in first for free; otherwise it is sold at that interval's price. In money the roof then earns the interval's price whatever the battery does. It still matters in the outage, where it runs the house first. Reversible: it is one rule in `simulate` and `optimum`.
- **Decision:** the roof's sales at a negative price are paid, as the prompt's wording says ("sold at that interval's price"). A real inverter would curtail.
- **Decision:** with the roof on, the unserved energy of a dark interval is the house's need less what the roof makes. Without the roof it is the prompt's 1.5 kW for the interval.
- **Decision:** the fleet's output per MW is used between 0 and 1 (EIA reports station use at night as negative output, and new plants can push a fleet above its listed nameplate). The file keeps the values as reported.
- **Decision:** add-ons exist on Hard only, and the preset keeps Hard's reserve and wear: `hard:13.5-5-90-r20-d0.11-solar-v4`, not the prompt's shorter example.
- **Decision:** the fleet call's bonus counts the battery's deliveries only, not the roof's.
- **Decision:** the shape is frozen into `site/data/battery_levels.json` by a new builder, as the levels' prices are. The seller tab's table holds monthly figures only, so no existing table could serve an hourly shape. No new warehouse table was made.
- **Decision:** today's level has no shape (the live set holds none), so the add-on is unavailable on it.
- **Decision:** a price is labeled when the price played differs from the real one. Uri's dearest hour is already above the cap and is left unchanged by the game, so it is real and shown plain.
- **Decision:** today's level was read once from the public live page (a GET of `/play/battery?more=1`, nothing posted) to check Part A on it, since this folder has no Supabase key.
- **Error:** scripted edits first failed on Windows line endings; nothing was written, and the edits were rerun with a script that keeps them.
- **Error:** a local server started from the wrong folder and served nothing, so one route check read 0 of 68; it was restarted from `site/` and passed 68 of 68.

## For Samuel

1. **Run the finish step** (above). Until step 3 the rooftop add-on is shown but unavailable on every level; until step 2 no v4 play is stored. For Monday both need doing.
2. **Look at the dry run in step 3 before writing.** It is the first time real shapes reach the game. If the workbook does not cover a day (the newest are 2026-08-29 and 2026-07-24), that level simply has no add-on.
3. **The penalty is 6 times the cap, USD 30,000/MWh, and Uri alone sets it.** Without Uri the multiple would be 2. A battery expert may ask why. The honest answer is on the page: it is the smallest number at which the perfect battery never gives up the house on these days. If you would rather keep the cap-priced penalty and treat Uri apart, that is a rule change for you to make.
4. **The guarantee covers the default battery and the test presets, not every setting.** With a much larger inverter on a day like Uri the perfect battery can still choose the dark for the outage's last minutes, because the charge only counts the time left. A flat charge for the whole outage would close that; it is a different rule from the one asked for.
5. **The roof rule differs from the prompt's wording in one case** (the first decision above): the roof fills the battery only while you charge. Say if you want the other reading; the perfect battery would then be approximate.
6. **The site's lint has 8 errors on main** in files outside the game. They do not block the merge (code-branch.yml runs the tests, the build and check-routes, not eslint), but the prompt asked for eslint to pass and, for the whole site, it does not.
