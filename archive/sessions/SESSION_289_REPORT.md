# Session 289 report: the battery game, one page with three modes (version 5)

14 October 2026, from 22:46 UTC, unattended, on samueloldlaptop (the code machine), the second session of the afternoon chain. Branch `wip/games-v2` (session 288's landing merged first), pushed, **not landed** (Samuel approves from the screenshots). Model spend USD 0. No pull, no warehouse data written.

## Read these first

- **`/play/battery` is one page.** A mode picker (Easy, Normal, Hard; Easy chosen), the play area, then the rules, the share card and the leaderboard. The simple page and `?more=1` are gone; `?more=1` lands on `?mode=normal` (checked in the browser).
- **Hard's first play no longer goes dark by following the screen.** The reserve is 25 percent (3.38 kWh against the outage's 3.16), and the notice fifteen minutes before names the emergency and says "sell down to the reserve line". Screenshot `289/after/07-hard-status-1-1280.png`.
- **A database migration must be applied before this ships:** `warehouse/supabase/migrations/033_game_v5.sql` (written, not applied). Until then the database refuses a v5 play and the page says "Not stored".
- **Easy shows the whole day ahead** (solid: the day so far; dashed: the rest), and every play opens with five seconds of the day at a glance: lowest, average, highest.

## What to review

The screenshots, before and after, at 1280 and 390 px: https://github.com/SamuelEnrique/erw/tree/wip/games-v2/docs/reviews/games-2026-10-14/289

1. Before: `before/01-simple-pick-1280.png` (the simple page), `before/10-full-pick-1280.png` (the full game).
2. After, Easy: `after/01-easy-pick-1280.png`, `after/02-easy-glance-390.png` (the day at a glance), `after/03-easy-playing-1280.png` (the whole day ahead, the fleet line under the money), `after/04-easy-done-1280.png`.
3. After, Normal: `after/05-normal-pick-390.png`.
4. After, Hard: `after/06-hard-pick-1280.png` (the need against the reserve before the day starts), `after/07-hard-status-1-1280.png` (the notice), `after/07-hard-status-2-1280.png` (the emergency), `after/08-hard-done-1280.png`.

To play it locally: in `C:\Users\lossa\Documents\erw-279\site`, `npx next start -p 3289` (the build is there), open http://localhost:3289/internal/unlock?token=<INTERNAL_COSTS_TOKEN>, then http://localhost:3289/play/battery ; press "Hard", pick "A summer scarcity day, 2023-08-10", Start, hold S from about 13:00.

## What was done

- **Ruling 16, one page:** `site/app/play/battery/page.tsx` reads `?mode=` (easy by default) and redirects `?more=` to `?mode=normal`; `Game.tsx` has the mode picker at the top and puts the mode in the address as it changes.
- **Ruling 1a:** `SETTINGS.reserve.def` 0.25 in `site/lib/battery.ts`; the rules section states the reserve against the need.
- **Ruling 2a:** on Hard the notice reads "In 15 minutes: the grid emergency and the fleet call ... The house will need 3.16 kWh from the battery in the outage; your backup reserve holds 3.38 kWh, enough by itself, so sell down to the reserve line." The emergency's own line says the same and that each kWh sold that hour earns the fleet bonus. With a reserve set lower it says "keep at least X kWh".
- **Ruling 3a:** "fleet of 10,000 homes: $X" under the money while playing; the fleet's total beside the perfect battery's fleet at the end.
- **Kelsey's asks 1 to 3:** less on screen (one list of days, settings folded, the tutorial on request only, no house drawing or fleet map on Easy); Easy's forecast is the whole day; the day at a glance, five seconds, "Start now" skips it.
- **Presets end "-v5"** (`RULES_VERSION`); v4 boards, add-ons included, stay readable and say "(v4 rules)". Settings are remembered under a new browser key, so an old 20 percent does not override the new default.
- **Two layout fixes found by the screenshots:** the add-ons fieldset was 663 px wide at 390 (a fieldset's default minimum width); Easy's "fleet call" label sat on "highest".
- **Kept in step:** `docs/methods/battery_game.md` (a "Version 5" section), `docs/battery_game_demo.md` (the five-minute guide, figures from the model: Hard's perfect battery $48.36, with the roof $88.34), `site/scripts/check-battery-game.mjs` (the browser check plays the four modes of the one page and checks the glance and the notice), `test-battery.mjs`, `check-scorer.mjs`, `check-lights.mjs`, `play-battery.mjs`, the page lists of `check-values.mjs` and `check-routes.mjs` (`?mode=hard` for `?more=1`) and the floor file, the API's example presets.
- **Tests:** `tests/test_session289.py` (13); five older tests (sessions 50, 56, 66, 70, 111) follow v5, each line marked.

## Checks

| Check | Exit | Notes |
|---|---|---|
| `scripts/precheck.py` | 0 | |
| `npx tsc --noEmit`, `eslint` on the game | 0, 0 | one lint error fixed on the way (a memo's dependencies) |
| `node scripts/test-battery.mjs` | 0 | DP equals brute force on every toy day; the reserve covers the need |
| The game's Python tests (19 files) and `test_session289` | 0 | 265 and 13 tests |
| `npm run build` (worktree) | 0 | no "statement timeout" |
| `check-values.mjs`, Games pages | 0 | 105 of 105 (`/play/battery` now carries 9 keys) |
| Screenshots, after | 0 | 22, no sideways overflow, no page error |

Not run: the clean-copy suite and the snapshot (nothing lands); `check-battery-game.mjs` against a server (its plays take eight minutes a width; the screenshot run played Easy and Hard at both widths instead).

## Decisions made without you

- **`?more=1` goes to `?mode=normal`**, not to Easy: it was the full game's address.
- **The day at a glance shows the day's own lowest, average and highest real price**, read as Kelsey's "the day's price history"; on Normal and Hard that tells the player the range but not when. Reversible: one component (`Preview`).
- **Easy plays the default battery** and shows no settings; its plays post under the Easy preset.
- **The tutorial opens only on request** (it opened itself on a first visit).
- **The migration is 033** (the next free number), with its rollback.
- **The demo guide was rewritten for v5** rather than left stale: its figures are tested against the model.

## For Samuel's ruling

- Whether the day at a glance should be the day's own figures (as built) or the days before it.
- Whether Easy should post to the leaderboard at all.

## To finish (when the games branch lands)

1. Apply the migration before the deploy: `.venv\Scripts\python.exe warehouse\supabase\apply.py --only 033` (a person, on the data machine).
2. Then land as usual.

## Files

- New: `tests/test_session289.py`, `warehouse/supabase/migrations/033_game_v5.sql`, `warehouse/supabase/rollbacks/033_game_v5.sql`, `docs/reviews/games-2026-10-14/289/` (20 before, 22 after), this report.
- Changed: `site/app/play/battery/Game.tsx`, `page.tsx`, `site/lib/battery.ts`, `site/app/api/play/top/route.ts`, `docs/methods/battery_game.md`, `docs/battery_game_demo.md`, `site/scripts/{check-battery-game,check-lights,check-routes,check-scorer,check-values,play-battery,test-battery}.mjs`, `site/scripts/check-values-floor.json`, `tests/test_session{50,56,66,70,111}.py`.
