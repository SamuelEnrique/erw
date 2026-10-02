# Session 63 report: battery game v3 and the digest guard

Energy Research Warehouse (ERW), session 63, third of the overnight run, on the portable laptop (role data, code work on the branch `task/063-battery-game-v3`), 2026-10-02 about 10:05 to 11:00 UTC. **Model spend: USD 0.00** (the cap was USD 0). No paid service. No force push. Nothing released on Redivis. The data lock was taken for the session (migration 018 and the live checks write to Supabase) and released at its end; `scripts/sync.py --refresh` ran before the migration (99 tables, all matching coverage).

## In plain words

**The game has new rules, each labeled on the page as a game rule.**
- **Money.** Every play starts with $5. If the money falls below $0, the game ends there ("out of money"). The score still means what was earned.
- **Hard's grid emergency.** In the day's dearest hour the price climbs toward USD 5,000/MWh (ERCOT's offer cap), a quarter, a half, three quarters and nine tenths of the way from the real price. Then the grid goes down for two hours: nothing can be bought or sold, and the house draws 1.5 kW from the battery.
- **Lights out.** If the battery runs dry in the outage, the round ends, the score so far stands, and the page says how much charge the outage needed and how much the battery held when it began.
- **The perfect battery and the server play by the same rules.** The DP optimum still equals brute force on every toy day, under every preset; the server rescores every posted play with the same code.
- **A simple page for a class.** `/play/battery` is now one sentence of instructions, the day, a Start button, then two big buttons (Charge, Sell), the battery and a big price number. Everything else (settings, difficulties, Hard's emergency, the replay, the leaderboard, the notes) is behind "More" (`/play/battery?more=1`).

**The digest cannot go out twice.** Each send now claims its day in Supabase (a new table, `digest_sends`) before the first email leaves. A second send the same day, or a resend of the same issue on another day, is skipped with the reason, whether it comes from the schedule, a retry or a manual dispatch. If a send fails before any email left, the claim is released so a retry can send; if it fails part way, the claim stays, so nobody gets the issue twice.

**One thing a person should decide.** Because lights out only ends the round (it costs the rest of the day, nothing more), the perfect battery sometimes chooses it: on 2 of the 7 famous days on Hard (Uri and the CAISO duck day) it sells everything into the spike and lets the lights go out. The prompt asked for exactly this rule, so it stands; a lights-out penalty would be a v4 rule.

## What changed

| File | Change |
|---|---|
| `site/lib/battery.ts` | `START_MONEY = 5`, `EMERGENCY` (cap 5,000, ramp 0.25/0.5/0.75/0.9, 8 outage intervals, house 1.5 kW), `emergencyOf`, `outageDraw`, `RULES_VERSION = "v3"`; `simulate` returns the money, the end interval and why (`bankrupt`, `lights_out`), the outage's charge at its start and its need; the DP gains terminal states for bankrupt and lights out and the forced outage draw; presets end `-v3`; `parsePreset` reads v2 presets (labeled "v2 rules") and v3 ones |
| `site/app/play/battery/Game.tsx` | the `simple` mode; the state from `simulate` after each interval (the server's own scorer, so the two cannot differ); Money in the HUD; banners for the spike and the outage; the outage shaded "grid down"; buttons disabled in the outage; the early-end messages |
| `site/app/play/battery/page.tsx` | the simple page by default; the full game at `?more=1` with a new section "The game's rules (version 3)" |
| `site/app/api/play/top/route.ts` | its error message's example presets are v3 |
| `warehouse/supabase/migrations/018_game_v3_digest_sends.sql` | the preset checks of `game_scores` and `game_plays` allow `-v3`; the table `digest_sends` (unique `(kind, day)` and `(kind, issue)`, service key only). **Applied** |
| `warehouse/news/email_digest.py` | `claim`, `settle`, `deliver`, `AlreadySent`, `send_day`; `main` records a second send as skipped, not failed |
| `docs/methods/battery_game.md` | the section "Version 3 (session 63)" |
| `site/scripts/test-battery.mjs` | v3 checks (below) |
| `site/scripts/check-values.mjs`, `check-routes.mjs` | `/play/battery?more=1` added |
| `site/scripts/play-battery.mjs` | reads today's level from `?more=1` (the simple page does not name the day) |
| `tests/test_session63.py` | 11 tests of the guard; `tests/test_session34.py` stubs the guard; `tests/test_session50.py` asserts the v3 preset line |

## The new rules in detail

- **Money** = $5 + market cash - degradation cost + fleet bonus. The game ends in the first interval it is below $0; the actions after it count for nothing.
- **Spike** (Hard only): the four intervals of the VPP hour (`vppHour`, the clock hour with the highest mean real price) become `p + (5000 - p) x r`, r = 0.25, 0.5, 0.75, 0.9. The fleet call keeps its hour, so the call and the spike coincide.
- **Outage** (Hard only): the 8 intervals after the spike, clipped at the day's end. Actions are ignored; each interval draws `1.5 kW x 0.25 h / sqrt(round trip)` = 0.395 kWh with the default battery (3.16 kWh for the whole outage); the backup reserve can be used.
- **Lights out**: the battery holds less than one interval's draw at the start of an outage interval.
- **Leaderboard**: v3 presets (`normal:13.5-5-90-v3`) are ranked only among themselves; old boards read "(v2 rules)".
- **The simple page** plays Normal with the default battery (no emergency), skips the tutorial, keeps each play in the research record and posts no public score.

The perfect battery on Hard, default battery, on the famous days:

| Day | Optimum, USD | Ends | Charge at the outage's start, kWh (need 3.16) | Optimum on Normal, USD |
|---|---|---|---|---|
| 2021-02-15 Uri | 166.80 | lights out | 2.70 | 240.23 |
| 2023-08-10 ERCOT heat | 49.01 | full day | 5.59 | 60.97 |
| 2026-04-26 calm | 29.49 | full day | 3.85 | 0.44 |
| 2026-08-29 solar | 29.61 | full day | 3.85 | 0.93 |
| 2025-01-05 negative | 29.72 | full day | 8.23 | 0.79 |
| 2026-04-27 CAISO solar noon | 29.71 | full day | 8.23 | 0.83 |
| 2026-07-24 CAISO duck | 34.38 | lights out | 2.96 | 12.98 |

Hard now pays more than Normal on calm days: the spike is worth more than the reserve and the wear cost. That is the emergency's point (the battery earns most in the hour the grid needs it), and it is a game rule, not a market forecast.

## Test results

- **`site/scripts/test-battery.mjs`: all pass.** The DP optimum equals brute force over all 3^12 action sequences on four toy days under four presets (Hard default, Hard with a 5 kWh battery, Easy 20 kWh, Normal), with the outage and lights out in play on Hard; the reserve is never crossed before an outage. New checks: charging at USD 2,000/MWh runs out of money in interval 2 (money -2.50); the optimum never goes bankrupt; the spike's formula and the outage window; selling everything into the spike gives lights out at the outage's first interval with the need 1.581 kWh (the 5 kWh test battery); outage actions buy nothing; v3 presets round trip, v2 boards read, "-v3-v3" refused.
- **Python: 250 tests, all pass** (`python -m unittest discover -s tests`), among them `tests/test_session63.py` (11): the first send claims and settles; a second send the same day is skipped (a newer brief, as a manual dispatch would send); the same issue on another day is skipped; the next day sends; the daily and the Roundup do not block each other; a failure before any message releases the claim and the retry sends; a failure part way keeps the claim as partial and the retry is skipped; no Supabase key, no send; nothing configured, nothing claimed; `main` reports the second send as skipped; the Roundup's day runs to Monday 03:00 UTC.
- **TypeScript** (`tsc --noEmit`), **eslint** (no warnings after keeping the simple page on the defaults), **`npm run build`**: pass.
- **Local site** (the build, port 3063): check-values 4,647 of 4,647 values match Supabase, `/play/battery?more=1` included; check-routes 66 of 66 pages pass.
- **`site/scripts/play-battery.mjs`** against the local site: every check passed except "today's level on the page", which read the simple page; after pointing it at `?more=1` that check passed (today's level 2026-09-30). The second run then hit the API's own limit (30 game requests an hour from one address) on the later checks; the first run had passed them all: the server's score equals `lib/battery.ts` under v3 for Easy, Normal, Hard and a custom Hard battery, stored under the `-v3` presets (which migration 018 now allows), and bad input refused.

## Live check

- **The guard, live on Supabase:** a test claim (kind roundup, day 2000-01-02, so no real send could be blocked) answered 201; the same day again 409; the same issue on another day 409; the anon key 401 (no grant); the row deleted after.
- **The merge:** the branch passed the code-branch workflow (run 36996591705: the Python tests, the site build and check-routes) and merged to main as `a49ca9c`.
- **The deployed site** (https://erw-flame.vercel.app), about a minute after the merge:
  - `/play/battery` serves the simple page ("you start with $5, and the game ends if you go below $0", the "More" link);
  - `/play/battery?more=1` serves the full game with "The game's rules (version 3)" and the lights-out rule;
  - `/api/play/top` answers 200 for a v3 preset and for a v2 one;
  - check-routes: 66 of 66 pages pass on production;
  - in Chrome, Start on the simple page played today's level (2026-09-30): the big price, the two big buttons, the battery and Money $5.00, the clock moving. The tab was closed mid-play, so nothing was posted.

## Errors and decisions

- **A shell quirk** collapsed `\\` inside a heredoc, so a scripted edit failed its own assertion (nothing was written); the edit ran from a file instead.
- **The test address in the session 63 tests** is the reserved `erw-test+...@example.invalid` (session 59's rule); nothing was sent.
- **The shadow digest** (`warehouse/news/shadow.py`, the Haiku comparison to the owner only, expiring 2026-10-06) is not behind the guard: it is one address and expires in four days.
- **Decision:** the guard's day for the Roundup is the UTC date three hours earlier, since its window (session 61) runs to Monday 03:00 UTC. A send without the Supabase service key is refused: an unguarded send could repeat.
- **Decision:** the guard also keys on the issue, so a stale brief (the day's brief failed) is not sent again the next day.
- **Decision:** the simple page plays Normal with the default battery and stores nothing in the browser.
