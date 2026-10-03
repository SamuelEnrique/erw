# Session 66 prompt: home battery game v4

Energy Research Warehouse (ERW), session 66. Game code only. Read CLAUDE.md, docs/methods/battery_game.md and archive/sessions/SESSION_63_REPORT.md first.

**Expected model spend: USD 0.00. Hard cap: USD 0.00.** No paid service, no pulls, no force push. Expected wall time about 1 hour 30 minutes; no time cap.

## Where this runs (read carefully)

This session runs in a separate git worktree, `C:\Users\samen\Documents\erw-game`, on the branch `wip/066-battery-game-v4`. Another session may be working in `C:\Users\samen\Documents\erw` at the same time.

1. **Never read from, write to or run git commands in `C:\Users\samen\Documents\erw`.** The one exception: you may call its Python interpreter by path (`C:\Users\samen\Documents\erw\.venv\Scripts\python.exe`) to run Python tests from this folder. Run `npm ci` in this folder's `site/` for the site.
2. **Push only to `wip/066-battery-game-v4`.** Never push to main. Never push to any `task/` branch: a push there triggers code-branch.yml, which merges to main and deploys.
3. **No Supabase writes.** Write migration 019 as a file; do not apply it. Reading public tables with the anon key is fine.
4. **Do not take the data lock.** Do not run any warehouse builder that writes a table.
5. **Do not run the finish step** (last section).

## Why this session

Version 3 has two problems found in review, and the game is being shown to a battery expert on Monday.
- On Hard, the perfect battery lets the house go dark on 2 of the 7 famous days (Uri and the CAISO duck day), because lights out only ends the round. The game then teaches that abandoning the house in a blackout is the best play.
- The Hard spike is an invented price shown on a real day. It must never be readable as a real price.

## Part A: lights out costs money

Keep Samuel's rule that lights out ends the round. Add a cost: when the lights go out, every remaining interval of the outage charges the house's unserved energy (1.5 kW for the interval) at the price cap, 5,000 USD/MWh. It is a game rule and is labeled as one on the page, with one sentence on why (a home without power in a grid emergency is the outcome the battery exists to prevent).

**Required result, as a test:** under version 4 the DP optimum does not end in lights out on any of the 7 famous days, on today's level, or on any toy day where keeping the lights on is feasible from the starting charge. If the cap-priced penalty does not achieve that, do not tune silently: report the days where it fails and the smallest whole multiple of the cap that fixes them, apply that multiple, and state it on the page and in the methods doc.

The server scorer, the DP and the page all use the same code, as in version 3. Money can fall below USD 0 from the penalty; the existing out-of-money rule then applies.

## Part B: the spike is labeled on the number

Wherever a spike-interval price is shown (the big price number, the chart, the replay, the end screen, any share text), the number itself carries "game rule, not a real price", and the real price for that interval is shown beside it. Add a test that no rendered spike price appears without the label.

## Part C: an end screen a high school student can read

On the simple page (`/play/battery`) and in the full game, after a play ends show three lines in plain words:
1. what you earned;
2. what the perfect battery earned on the same day under the same rules;
3. the one hour where you lost the most against the perfect battery, and what it did in that hour (charged, sold or held) and at what price.

No jargon. Every number comes from `simulate` and the DP, not from a second calculation.

## Part D: Hard mode add-ons, starting with rooftop solar

Hard mode gains an "Add-ons" section of optional switches, off by default. Build the mechanism so more add-ons can follow, and ship one: **rooftop solar**.

- **The rule:** a 5 kW rooftop array (a game rule, stated as one). Each interval it produces 5 kW times the real hourly output per MW installed of that grid's solar fleet on the level's day, from the table the cost-of-power seller tab already uses for its solar shape. The energy charges the battery for free, up to the battery's power and capacity limits; what does not fit is sold at that interval's price. During the outage it can also carry the house.
- **Real data only.** Read the shape read-only. The page says it is the whole fleet's shape, not one roof. If a level's day has no solar shape held, the add-on is unavailable for that level and the page says so. Never fill.
- **If serving the shape to the game needs a new or changed table,** write the builder and its tests, do not run it, and list it in the finish step. The add-on then works on the toy days in tests and is switched on for real levels at the finish.
- **Presets and boards:** the preset string encodes the add-ons (for example `hard:13.5-5-90-solar-v4`). A board ranks only plays with the same rules and add-ons.

## Part E: version 4 plumbing

- `RULES_VERSION = "v4"`; presets end `-v4`; `parsePreset` still reads v2 and v3 presets, labeled "(v2 rules)" and "(v3 rules)".
- `warehouse/supabase/migrations/019_game_v4.sql`: the preset checks of `game_scores` and `game_plays` allow `-v4` and the add-on segment. **Written, not applied.**
- `docs/methods/battery_game.md`: a section "Version 4 (session 66)" with each rule, the penalty and why, and the solar rule and its source.

## Tests

- `site/scripts/test-battery.mjs`: the DP optimum equals brute force over all action sequences on the toy days under every preset, including Hard with solar, the outage and the penalty in play. Part A's required result. Part B's label test. Presets round trip; v2 and v3 boards read.
- Python tests pass (run with the main folder's interpreter by path). `tsc --noEmit`, eslint and `npm run build` pass.
- Local site: check-routes passes. Posting a v4 score will be refused by the database until migration 019 is applied; that is expected. Do not post scores. Confirm instead that the server's scorer and `lib/battery.ts` agree under v4 by calling the scoring function directly.

## Report: `archive/sessions/SESSION_66_REPORT.md`

Same form as session 63. Put "To finish" first, with the exact commands: take the data lock, apply migration 019, run any builder from Part D, merge the branch to main, release the lock, then the live checks (post one v4 play per difficulty, both add-on states). Then "In plain words", the table of the perfect battery on the 7 famous days under v4 (Hard, Hard with solar, Normal) with how each ends, test results, errors and decisions, and "For Samuel" with only what needs a person. No em dashes anywhere. Commit after every working step, push the wip branch, reply "REPORT READY" and stop.
