# Session 3600: the battery game's rulings

Energy Research Warehouse (ERW). Personal laptop (portable-laptop), 6 November 2026, Opus 5.5, a fourth window: no site build, no landing gate, no data lock, nothing sent, no model calls. Prompt: `queue/done/205-day-6-november-portable-batterygame.md`.

- **Session number 3600**: the highest number in use on `origin/main` and on any branch was in the 3400s (`wip/3400-attention`, sessions 3400 to 3410 in commit messages); nothing at 3600 or above. Queue number 205: `queue/next` ended at 204 and `queue/done` at 202, with no 205 on any branch.
- **Branch** `wip/3600-batterygame`, cut from `origin/main`, head `029c2d69e`, pushed. Landing request row 13 in `docs/state/landing_request_portable.md` (task `3600-batterygame`, port 3360), pushed to main alone.
- Precheck passed; `scripts/freeze.py status`: no freeze.

## Which rulings already held (read before any change)

- **(1) Easy truly easy**: held. Session 289 made Easy show the whole day's real prices ahead as a dashed forecast (`DIFFICULTIES.easy.forecastHours` 24).
- **(2) The day before play**: partly held. Session 289's `Preview` showed the lowest, average and highest real price for 5 seconds in every mode. The variance was missing (only the range).
- **(3) The end table of three scenarios**: held. Session 290's `EndTable` has the player, the perfect battery and no battery in every mode. The perfect battery is `optimum()` in `site/lib/battery.ts`, a pure dynamic program, already checked against brute force on toy days (`scripts/test-battery.mjs`). There was no test on a hand-worked day.
- **(4) $5, game over below $0, Hard's grid-constrained moment**: held in the rules. `START_MONEY` is 5, and play ends when money goes below $0. Hard's outage (two hours after the dearest hour) is one window where the player's action is ignored and nothing can be sold or bought. The words under the buttons were "nothing to buy or sell": they did not say plainly that the battery cannot discharge, or until when.
- **(5) Rooftop solar**: held. It is a Hard-only add-on, off by default. Its shape is the grid's solar fleet output per MW installed: EIA-930 hourly generation by fuel (Adjusted SUN Gen, raw workbooks under `warehouse/raw/eia930_emissions/`) over EIA-860M solar nameplate (`warehouse/output/eia860m_operating_generators.csv`), written by `warehouse/derived/battery_solar.py` into `site/data/battery_levels.json`. All seven frozen days have a shape. Today's level has none, so its switch says it is not available. No "coming" switch was needed.
- **Prices' source as a hover**: missing. The prices were real stored rows, but no shown price carried its source.

## What was done

- **`site/lib/battery.ts`**:
  - `glance(prices)`: the lowest, mean, highest and standard deviation, plus the typical range (mean plus or minus one SD, kept within the day's lowest and highest). It returns null for an empty or non-numeric day, so nothing is filled in.
  - `gridDownWords(from, to)`: the plain sentence.
  - `priceHover(prices, level)`: the market, date, publisher's report, retrieval time and ERW table. A field the level lacks is left out.
- **`Game.tsx`, inside the existing structure** (no layout change):
  - The preview reads `glance()` and adds one line, "most prices: X to Y", with its meaning as a hover. The typical range is shaded on the existing bar.
  - The preview's numbers and the price-now number carry the source hover.
  - During Hard's outage the line under the buttons now reads, for example: "The grid is down from 19:00 to 21:00: your battery cannot sell (discharge to the grid) or buy until it is back. It runs your house instead."
- **`page.tsx`**: passes each level's `table`, `source` and `retrieved_at` to the game.
- **Tests**:
  - `site/scripts/test-battery-rulings.mjs` (`node --test`) has one block per ruling plus one for the hover: 6 of 6 pass.
  - `tests/test_session3600_batterygame.py` runs it and checks the edited files for dashes.
  - `tests/test_session289.py`'s preview assertion was updated to the new `glance()` call and `hover` prop.
  - The battery and games tests (38, 50, 55, 56, 66, 70, 111, 177, 289, 290, 294, 3600): 118 passed, 1 skipped, 1 failed in the joint run. The failure was `test_session294` (the EV game) reading a stale `__pycache__`; run alone with the cache provider off it passes, 8 passed and 1 skipped.

## The hand-worked day (ruling 3)

- **The battery**: a toy one, 2 kWh, 1 kWh an interval, lossless, starting at 1 kWh, $5, no reserve, no wear.
- **Prices, USD/MWh**: -10, 30, 300, 50, 20, 10, 100, 40.
- **The fleet call** is hour 1, at a mean of 92.5. Each MWh sold in it earns 92.5 more, so its sell values are 82.5, 122.5, 392.5 and 142.5.
- **The best plan, by hand**: charge at -10 (+10); hold at 30 (the battery is full); sell at 392.5 and 142.5; charge at 20 and 10 (-30); sell at 100 and 40 (+140).
  - Total 655, so USD 0.655: cash USD 0.470 plus the bonus USD 0.185.
  - State of charge: 1, 2, 2, 1, 0, 1, 2, 1, 0.
- **Rivals, by hand**:
  - Selling at 30 instead: 525 for hour 1, against 545.
  - Idling at -10 and charging at 30: 505.
  - Keeping 1 kWh past hour 1: 532.5.
- **Checks**: `optimum()` gives 0.655, and brute force over all 3^8 plays agrees.
- **End table**: bought 3 kWh at an average of 6.67, sold 4 kWh at 122.5. No battery: USD 0.

## Decisions made without you

- **The grid-constrained moment** is Hard's existing outage, not a new single interval. The outage is already one window in which the battery cannot discharge to the grid, and a second constraint would change the scorer and every v5 board. What was missing was the plain words, so the words were added.
- **The variance** is shown as the average plus or minus one standard deviation ("most prices"), with the SD itself in the hover. A population SD is used, since the day is the whole set.
- **The "price history" shown before play** is this day's own spread, not earlier days'. Earlier days would have needed new data in the page, and the day's own figures are what give the player an expectation.
- **No site build and no type check**: the prompt forbids the build, and this machine has no `node_modules`. The landing gate's build is the first compile of the `Game.tsx` changes.
- **The queue file** was pushed to main before the freeze check. That push holds a prompt only and changes no page; the freeze check, run right after it, found no freeze.

## For Samuel's ruling

- Should Hard keep its two-hour outage as the one grid-constrained moment, or gain a separate interval where only selling is blocked (an export limit, with the house still on the grid)? The second would mean rules v6 and new boards.
- The "most prices" line: keep that wording, or say "typical range"?
